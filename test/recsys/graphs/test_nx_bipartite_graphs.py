import unittest
from unittest import TestCase

import pandas as pd
import os
import lzma
import pickle
from orange_cb_recsys.recsys.graphs import NXBipartiteGraph
import networkx as nx
import numpy as np

from orange_cb_recsys.recsys.graphs.graph import Node

@unittest.skip("Skip temporarily graph tests")
class TestNXBipartiteGraph(TestCase):

    def setUp(self) -> None:
        self.df = pd.DataFrame.from_dict({'from_id': ["u1", "u1", "u2", "u2", "u2", "u3", "u4", "u4"],
                                          'to_id': ["i1", "i2", "i1", "i3", "i4", "i4", "i3", "i4"],
                                          'score': [0.8, 0.7, -0.4, 1.0, 0.4, 0.1, -0.3, 0.7]})
        # Graph that will be used by all tests
        self.g: NXBipartiteGraph = NXBipartiteGraph(self.df)

    def test_populate_from_dataframe_w_labels(self):
        df_label = pd.DataFrame.from_dict({'from_id': ["u1", "u1", "u2", "u2", "u2", "u3", "u4", "u4"],
                                           'to_id': ["i1", "i2", "i1", "i3", "i4", "i4", "i3", "i4"],
                                           'score': [0.8, 0.7, -0.4, 1.0, 0.4, 0.1, -0.3, 0.7],
                                           'label': ['score_df', 'score_df', 'score_df', 'score_df',
                                                     'score_df', 'score_df', 'score_df', 'score_df']})

        # Graph that will be used by all tests
        g: NXBipartiteGraph = NXBipartiteGraph(df_label)

        for user, item, score in zip(df_label['from_id'], df_label['to_id'], df_label['score']):
            expected = {'label': 'score_df', 'weight': score}
            result = g.get_link_data(user, item)

            self.assertEqual(expected, result)

    def test_graph_created(self):
        # Simple assert just to make sure the graph is created
        self.assertGreater(len(self.g.user_nodes), 0)
        self.assertGreater(len(self.g.item_nodes), 0)

    def test_add_user(self):
        # Add 'user' node
        self.assertFalse(self.g.is_user_node('u0'))
        self.g.add_user_node('u0')
        self.assertTrue(self.g.is_user_node('u0'))

        # Add a list of 'user' nodes
        list_nodes = ['u1_list', 'u2_list', 'u3_list']
        self.g.add_user_node(list_nodes)
        for n in list_nodes:
            self.assertTrue(self.g.is_user_node(n))

        # Add 'user' node but it already exists as
        # an 'item' node, so it exists as both
        self.g.add_item_node('i0')
        self.assertTrue(self.g.is_item_node('i0'))
        self.g.add_user_node('i0')
        self.assertTrue(self.g.is_user_node('i0'))
        self.assertTrue(self.g.is_item_node('i0'))

    def test_add_item(self):
        # Add 'item' node
        self.assertFalse(self.g.is_item_node('i0'))
        self.g.add_item_node('i0')
        self.assertTrue(self.g.is_item_node('i0'))

        # Add a list of 'item' nodes
        list_nodes = ['i1_list', 'i2_list', 'i3_list']
        self.g.add_item_node(list_nodes)
        for n in list_nodes:
            self.assertTrue(self.g.is_item_node(n))

        # Add 'item' node but it already exists as
        # a 'user' node, so it exists as both
        self.g.add_user_node('u0')
        self.assertTrue(self.g.is_user_node('u0'))
        self.g.add_item_node('u0')
        self.assertTrue(self.g.is_item_node('u0'))
        self.assertTrue(self.g.is_user_node('u0'))

    def test_add_link_user_item(self):
        # Link existent 'user' node to an existent 'item' node
        self.g.add_user_node('u0')
        self.g.add_item_node('Tenet')
        self.assertIsNone(self.g.get_link_data('u0', 'Tenet'))
        self.g.add_link('u0', 'Tenet')
        expected = {'label': 'score', 'weight': 0.5}
        result = self.g.get_link_data('u0', 'Tenet')
        self.assertEqual(expected, result)

        # Link existent 'user' node to a list of existent 'item' node
        self.g.add_user_node('u_list')
        items_list = ['i1_list', 'i2_list', 'i3_list']
        self.g.add_item_node(items_list)
        self.g.add_link('u_list', items_list)
        for item in items_list:
            result = self.g.get_link_data('u_list', item)
            expected = {'label': 'score', 'weight': 0.5}

            self.assertEqual(expected, result)

        # Link existent 'item' node to an existent 'user' node
        self.g.add_item_node('Tenet')
        self.g.add_user_node('1')
        self.assertIsNone(self.g.get_link_data('Tenet', '1'))
        self.g.add_link('Tenet', '1', 0.5)
        self.assertFalse(self.g.is_user_node('Tenet'))
        self.assertFalse(self.g.is_item_node('1'))
        self.assertIsNotNone(self.g.get_link_data('Tenet', '1'))

        # Link existent 'item' node to a list of existent 'user' node
        self.g.add_item_node('i_list')
        users_list = ['u1_list', 'u2_list', 'u3_list']
        self.g.add_user_node(users_list)
        self.g.add_link('i_list', users_list)
        for user in users_list:
            result = self.g.get_link_data('i_list', user)
            expected = {'label': 'score', 'weight': 0.5}

            self.assertEqual(expected, result)

        # Try to Link non-existent 'user' node and non-existent 'item' node,
        # so no link is created
        self.assertFalse(self.g.node_exists('u_new'))
        self.assertFalse(self.g.node_exists('i_new'))
        self.g.add_link('u_new', 'i_new', 0.5)
        self.assertFalse(self.g.is_user_node('u_new'))
        self.assertFalse(self.g.is_item_node('i_new'))
        self.assertIsNone(self.g.get_link_data('u_new', 'i_new'))

    def test_pred_succ(self):
        # Get predecessors of a node
        self.g.add_user_node('u0')
        self.g.add_user_node('u1')
        self.g.add_item_node('i0')
        self.g.add_link('u0', 'i0', 0.5)
        self.g.add_link('u1', 'i0', 0.5)
        result = self.g.get_predecessors('i0')
        expected = ['u0', 'u1']
        self.assertEqual(expected, result)

        # Get successors of a node
        self.g.add_user_node('u0')
        self.g.add_item_node('i0')
        self.g.add_item_node('i1')
        self.g.add_link('u0', 'i0', 0.5)
        self.g.add_link('u0', 'i1', 0.5)
        result = self.g.get_successors('u0')
        expected = ['i0', 'i1']
        self.assertEqual(expected, result)

        # Get voted contents of a node
        result = self.g.get_voted_contents('u0')
        expected = ['i0', 'i1']
        self.assertEqual(expected, result)

    def test_metrics(self):
        # We calculate some metrics, simple assert to make sure they are
        # calculated
        self.assertGreater(len(self.g.degree_centrality()), 0)
        self.assertGreater(len(self.g.closeness_centrality()), 0)
        self.assertGreater(len(self.g.dispersion()), 0)

    def test__graph(self):
        # Simple assert just to test the _graph method
        self.assertIsInstance(self.g._graph, nx.DiGraph)

    def test__remove_nodes_from_graph(self):
        graph_to_test = self.g.copy()
        node_to_remove = list(graph_to_test.user_nodes)[0]
        graph_to_test._remove_nodes_from_graph([node_to_remove])
        self.assertTrue(len(graph_to_test.user_nodes) == len(self.g.user_nodes) - 1)
        self.assertTrue(node_to_remove not in graph_to_test.user_nodes)

    def test_convert_to_dataframe(self):
        converted_df = self.g.convert_to_dataframe()
        self.assertNotIn('label', converted_df.columns)
        for user, item in zip(converted_df['from_id'], converted_df['to_id']):
            self.assertIsInstance(user, Node)
            self.assertIsInstance(item, Node)

        result = np.sort(converted_df, axis=0)
        expected = np.sort(self.df, axis=0)
        self.assertTrue(np.array_equal(expected, result))

        converted_df = self.g.convert_to_dataframe(only_values=True, with_label=True)
        self.assertIn('label', converted_df.columns)
        for user, item in zip(converted_df['from_id'], converted_df['to_id']):
            self.assertNotIsInstance(user, Node)
            self.assertNotIsInstance(item, Node)

        converted_df = converted_df[['from_id', 'to_id', 'score']]
        result = np.sort(converted_df, axis=0)
        expected = np.sort(self.df, axis=0)
        self.assertTrue(np.array_equal(expected, result))

    def test_copy(self):

        copy = self.g.copy()

        self.assertEqual(copy, self.g)

        copy.add_user_node('prova')

        self.assertNotEqual(copy, self.g)

    def test_serialize(self):

        self.g.serialize(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_serialize'), 'test_graph')

        with lzma.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_serialize/test_graph.xz'), 'rb') \
                as graph_file:
            graph = pickle.load(graph_file)

        self.assertEqual(self.g, graph)
