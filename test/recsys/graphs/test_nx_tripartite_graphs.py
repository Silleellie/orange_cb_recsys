from orange_cb_recsys.content_analyzer.ratings_manager import Ratings
from orange_cb_recsys.content_analyzer.ratings_manager.rating_processor import NumberNormalizer
from orange_cb_recsys.content_analyzer.raw_information_source import CSVFile
from orange_cb_recsys.recsys.graphs.graph import Node
from orange_cb_recsys.recsys.graphs.nx_tripartite_graphs import NXTripartiteGraph
import os
import pandas as pd
import numpy as np

from test import dir_test_files
from test.recsys.graphs.test_nx_bipartite_graphs import TestNXBipartiteGraph

ratings_filename = os.path.join(dir_test_files, 'new_ratings_small.csv')
movies_dir = os.path.join(dir_test_files, 'complex_contents', 'movies_codified/')


class TestNXTripartiteGraph(TestNXBipartiteGraph):

    def setUp(self) -> None:
        self.df = pd.DataFrame.from_dict({'from_id': ["1", "1", "2", "2", "2", "3", "4", "4"],
                                          'to_id': ["tt0112281", "tt0112302", "tt0112281", "tt0112346",
                                                    "tt0112453", "tt0112453", "tt0112346", "tt0112453"],
                                          'score': [0.8, 0.7, -0.4, 1.0, 0.4, 0.1, -0.3, 0.7]})

        self.g: NXTripartiteGraph = NXTripartiteGraph(self.df, movies_dir,
                                                      item_exo_representation="dbpedia",
                                                      item_exo_properties=['film director'])

    def test_populate_from_dataframe_w_labels(self):
        df_label = pd.DataFrame.from_dict({'from_id': ["1", "1", "2", "2", "2", "3", "4", "4"],
                                           'to_id': ["tt0112281", "tt0112302", "tt0112281", "tt0112346",
                                                     "tt0112453", "tt0112453", "tt0112346", "tt0112453"],
                                           'score': [0.8, 0.7, -0.4, 1.0, 0.4, 0.1, -0.3, 0.7],
                                           'label': ['score_df', 'score_df', 'score_df', 'score_df',
                                                     'score_df', 'score_df', 'score_df', 'score_df']
                                           })

        g: NXTripartiteGraph = NXTripartiteGraph(df_label, movies_dir,
                                                 item_exo_representation="dbpedia",
                                                 item_exo_properties=['film director'])

        for user, item, score in zip(df_label['from_id'], df_label['to_id'], df_label['score']):
            expected = {'label': 'score_df', 'weight': score}
            result = g.get_link_data(user, item)

            self.assertEqual(expected, result)

    def test_graph_created(self):
        # Simple assert just to make sure the graph is created
        self.assertGreater(len(self.g.user_nodes), 0)
        self.assertGreater(len(self.g.item_nodes), 0)
        self.assertGreater(len(self.g.property_nodes), 0)

    def test_add_property(self):
        # Add 'property' node
        self.assertFalse(self.g.is_property_node('Nolan'))
        self.g.add_property_node('Nolan')
        self.assertTrue(self.g.is_property_node('Nolan'))

        # Add a list of 'property' nodes
        list_nodes = ['prop1', 'prop2', 'prop3']
        self.g.add_property_node(list_nodes)
        for n in list_nodes:
            self.assertTrue(self.g.is_property_node(n))

        # Add 'property' node but it already exists as
        # a 'user' node
        self.assertTrue(self.g.is_user_node('1'))
        self.g.add_property_node('1')
        self.assertTrue(self.g.is_property_node('1'))
        self.assertTrue(self.g.is_user_node('1'))

    def test_add_link_item_prop(self):
        # Link existent 'item' node to existent 'property' node
        self.g.add_item_node('Tenet')
        self.g.add_property_node('Nolan')
        self.g.add_link('Tenet', 'Nolan', weight=0.5, label='Director')
        result = self.g.get_properties('Tenet')
        expected = [{'Director': 'Nolan'}]
        self.assertEqual(expected, result)

        # Link existent 'item' node to a list of existent 'property'
        self.g.add_item_node('i_list')
        properties_list = ['prop1', 'prop2', 'prop3']
        self.g.add_property_node(properties_list)
        self.g.add_link('i_list', properties_list, weight=0.5, label='starring')
        result = self.g.get_properties('i_list')
        expected = [{'starring': 'prop1'}, {'starring': 'prop2'}, {'starring': 'prop3'}]
        self.assertEqual(expected, result)

        # Link existent 'property' node to existent 'item' node
        self.g.add_property_node('Nolan')
        self.g.add_item_node('Inception')
        self.g.add_link('Nolan', 'Inception', weight=0.5, label='Director of')
        result = self.g.get_link_data('Nolan', 'Inception')
        expected = {'label': 'Director of', 'weight': 0.5}
        self.assertEqual(expected, result)

        # Link existent 'property' node to a list of existent 'item' node
        self.g.add_property_node('prop_list')
        items_list = ['i1_list', 'i2_list', 'i3_list']
        self.g.add_item_node(items_list)
        self.g.add_link('prop_list', items_list, weight=0.5, label='Director of')
        for item in items_list:
            result = self.g.get_link_data('prop_list', item)
            expected = {'label': 'Director of', 'weight': 0.5}
            self.assertEqual(expected, result)

        # Try to link non-existent 'item' node and non-existent 'property' node,
        # so no link is created
        self.assertFalse(self.g.node_exists('i_new'))
        self.assertFalse(self.g.node_exists('prop_new'))
        self.g.add_link('i_new', 'prop_new', weight=0.5, label="PropertyNew")
        self.assertFalse(self.g.is_item_node('i_new'))
        self.assertFalse(self.g.is_property_node('prop_new'))
        self.assertIsNone(self.g.get_link_data('i_new', 'prop_new'))

    def test_add_link_user_property(self):
        # Try to link existent 'user' node to existent 'property' node
        self.g.add_user_node('u1')
        self.g.add_property_node('Nolan')
        self.g.add_link('u1', 'Nolan', weight=0.5, label='Friend')
        result = self.g.get_properties('u1')
        expected = []
        self.assertEqual(expected, result)

        # Try to link existent 'property' node to existent 'user' node
        self.g.add_property_node('Nolan')
        self.g.add_user_node('u2')
        self.g.add_link('Nolan', 'u2', weight=0.5, label='Friend')
        self.assertIsNone(self.g.get_link_data('Nolan', 'u2'))

        # Try to link non-existent 'user' node and non-existent 'property' node,
        # so no link is created
        self.assertFalse(self.g.node_exists('u_new'))
        self.assertFalse(self.g.node_exists('prop_new'))
        self.g.add_link('u_new', 'prop_new', weight=0.5, label="PropertyNew")
        self.assertFalse(self.g.is_user_node('u_new'))
        self.assertFalse(self.g.is_property_node('prop_new'))
        self.assertIsNone(self.g.get_link_data('u_new', 'prop_new'))

    def test_add_item_tree(self):
        # Add 'item' tree, so add 'item' node and its properties to the graph
        self.assertFalse(self.g.is_item_node('tt0114709'))
        self.assertFalse(self.g.is_property_node('http://dbpedia.org/resource/John_Lasseter'))
        self.g.add_item_tree('tt0114709')
        self.assertTrue(self.g.is_item_node('tt0114709'))
        self.assertTrue(self.g.is_property_node('http://dbpedia.org/resource/John_Lasseter'))

        # Try to add 'user' tree
        self.g.add_user_node('20')
        self.assertTrue(self.g.is_user_node('20'))
        self.g.add_item_tree('20')
        expected = []
        result = self.g.get_properties('20')
        self.assertEqual(expected, result)
        self.assertTrue(self.g.is_item_node('20'))

    def test_graph_creation(self):
        # Test multiple graph creation possibilities

        # Import ratings as DataFrame
        ratings = Ratings(
            source=CSVFile(ratings_filename),
            user_id_column='user_id',
            item_id_column='item_id',
            score_column='points',
            timestamp_column='timestamp',
            score_processor=NumberNormalizer()
        )
        ratings_frame = ratings.to_dataframe()

        # Create graph using the property 'starring' from representation '0' ('dbpedia')
        g = NXTripartiteGraph(ratings_frame, movies_dir,
                              item_exo_representation=0, item_exo_properties=['starring'])

        # Simple assert just to make sure the graph is created
        self.assertGreater(len(g.user_nodes), 0)
        self.assertGreater(len(g.item_nodes), 0)
        self.assertGreater(len(g.property_nodes), 0)

        # Create graph specifying only the exo representation
        g = NXTripartiteGraph(ratings_frame, movies_dir,
                              item_exo_representation="dbpedia")

        # Simple assert just to make sure the graph is created
        self.assertGreater(len(g.user_nodes), 0)
        self.assertGreater(len(g.item_nodes), 0)
        self.assertGreater(len(g.property_nodes), 0)

        # Create graph specifying only the exo representation
        g = NXTripartiteGraph(ratings_frame, movies_dir,
                              item_exo_properties=['starring'])

        # Simple assert just to make sure the graph is created
        self.assertGreater(len(g.user_nodes), 0)
        self.assertGreater(len(g.item_nodes), 0)
        self.assertGreater(len(g.property_nodes), 0)

        # Create graph specifying without properties
        g = NXTripartiteGraph(ratings_frame)

        # Simple assert just to make sure the graph is created
        self.assertGreater(len(g.user_nodes), 0)
        self.assertGreater(len(g.item_nodes), 0)
        self.assertEqual(len(g.property_nodes), 0)

    def test_convert_to_dataframe(self):
        converted_df = self.g.convert_to_dataframe()
        self.assertNotIn('label', converted_df.columns)
        for user, item in zip(converted_df['from_id'], converted_df['to_id']):
            self.assertIsInstance(user, Node)
            self.assertIsInstance(item, Node)

        converted_df = converted_df.query('to_id not in @self.g.property_nodes')
        result = np.sort(converted_df, axis=0)
        expected = np.sort(self.df, axis=0)
        self.assertTrue(np.array_equal(expected, result))

        converted_df = self.g.convert_to_dataframe(only_values=True, with_label=True)
        self.assertIn('label', converted_df.columns)
        for user, item in zip(converted_df['from_id'], converted_df['to_id']):
            self.assertNotIsInstance(user, Node)
            self.assertNotIsInstance(item, Node)

        converted_df = converted_df.query('to_id not in @self.g.property_nodes')[['from_id', 'to_id', 'score']]
        result = np.sort(converted_df, axis=0)
        expected = np.sort(self.df, axis=0)
        self.assertTrue(np.array_equal(expected, result))
