from typing import List, Set, Iterable, Union
from orange_cb_recsys.recsys.graphs.graph import BipartiteGraph
import pandas as pd
import networkx as nx

from orange_cb_recsys.recsys.graphs.graph import UserNode, ItemNode
from orange_cb_recsys.utils.const import logger


class NXBipartiteGraph(BipartiteGraph):
    """
    Class that implements a Bipartite graph through networkx library.
    It supports 'user' node and 'item' node only.
    It creates a graph from an initial rating frame
    EXAMPLE::
            _| from_id | to_id | score|
            _|   u1    | Tenet | 0.6  |

        Becomes:
                u1 -----> Tenet
        where 'u1' becomes a 'user' node and 'Tenet' becomes a 'item' node,
        with the edge weighted and labelled based on the score column and on the
        'default_score_label' parameter

    Args:
        source_frame (pd.DataFrame): the initial rating frame needed to create the graph
        default_score_label (str): the default label of the link between two nodes.
            Default is 'score'
        default_weight (float): the default value with which a link will be weighted
            Default is 0.5

    """
    def __init__(self, source_frame: pd.DataFrame,
                 default_score_label: str = 'score', default_weight: float = 0.5):
        self.__graph: nx.DiGraph = None
        super().__init__(source_frame,
                         default_score_label, default_weight)

    def create_graph(self):
        """
        Instantiates the networkx DiGraph
        """
        self.__graph = nx.DiGraph()

    @property
    def user_nodes(self) -> Set[UserNode]:
        """
        Returns a set of all 'user' nodes in the graph
        """
        return set(node for node in self._graph.nodes if isinstance(node, UserNode))

    @property
    def item_nodes(self) -> Set[ItemNode]:
        """
        Returns a set of all 'item' nodes in the graph
        """
        return set(node for node in self._graph.nodes if isinstance(node, ItemNode))

    def add_user_node(self, node: Union[object, List[object]]):
        """
        Adds a 'user' node to the graph.
        If a list is passed, then every element of the list will be added as a 'user' node

        Args:
            node: node(s) that needs to be added to the graph as 'user' node(s)
        """
        if not isinstance(node, list):
            node = [node]

        for n in node:
            self._graph.add_node(UserNode(n))

    def add_item_node(self, node: Union[object, List[object]]):
        """
        Adds a 'item' node to the graph.
        If a list is passed, then every element of the list will be added as a 'item' node

        Args:
            node: node(s) that needs to be added to the graph as 'item' node(s)
        """
        if not isinstance(node, list):
            node = [node]

        for n in node:
            self._graph.add_node(ItemNode(n))

    def add_link(self, start_node: object, final_node: Union[object, List[object]], weight: float = None,
                 label: str = None):
        """
        Creates a weighted link connecting the 'start_node' to the 'final_node'
        Both nodes must be present in the graph before calling this method

        'weight' and 'label' are optional parameters, if not specified default values
        will be used.

        Args:
            start_node (object): starting node of the link
            final_node (object): ending node of the link
            weight (float): weight of the link, default is 0.5
            label (str): label of the link, default is 'score_label'
        """
        if label is None:
            label = self.get_default_score_label()

        if weight is None:
            weight = self.get_default_weight()

        if not isinstance(final_node, list):
            final_node = [final_node]

        for final in final_node:

            if self.node_exists(start_node) and self.node_exists(final):

                # We must to this so that if the 'final' node passed is 'i1' and in the graph it's a 'ItemNode'
                # we get its instance and link the start node to the instance, otherwise networkx
                # links 'start' node to the string 'i1' and not the ItemNode!!
                nodes_list = list(self._graph.nodes)
                index_first = nodes_list.index(start_node)
                index_second = nodes_list.index(final)

                self._graph.add_edge(nodes_list[index_first], nodes_list[index_second], weight=weight, label=label)
            else:
                logger.warning("One of the nodes or both don't exist in the graph! Add them before "
                               "calling this method.")

    def remove_link(self, start_node: object, final_node: object):
        """
        Removes the link connecting the 'start_node' to the 'final_node'.
        If there's no link between the two nodes, than a warning is printed

        Args:
            start_node (object): starting node of the link to remove
            final_node (object): ending node of the link to remove
        """
        try:
            self._graph.remove_edge(start_node, final_node)
        except nx.NetworkXError:
            logger.warning("No link exists between the start node and the final node!\n"
                           "No link will be removed")

    def get_link_data(self, start_node: object, final_node: object):
        """
        Get link data such as weight, label, between the 'start_node' and the 'final_node'.
        Returns None if said link doesn't exists

        Remember that this is a directed graph so the result differs if 'start_node' and 'final_node'
        are switched.

        Args:
            start_node (object): node where the link starts
            final_node (object): node where the link ends
        """
        return self._graph.get_edge_data(start_node, final_node)

    def get_predecessors(self, node: object) -> List[object]:
        """
        Returns a list containing the successors of the node passed.
        Returns None if the node doesn't exists in the graph.

        Taken from networkx library:
        "A predecessor of n is a node m such that there exists a directed
        edge from m to n"

        EXAMPLE:
                I1 <-- U1
                ↑
                U2

            get_successors(I1) ---> [U1, U2]

        Args:
            node(object): node of which we want to calculate predecessors
        """
        if not self.node_exists(node):
            logger.warning("The node specified is not in the graph! Return None")
        else:
            return list(self._graph.predecessors(node))

    def get_successors(self, node: object) -> List[object]:
        """
        Returns a list containing the successors of the node passed.
        Returns None if the node doesn't exists in the graph.

        Taken from networkx library:
        "A successor of n is a node m such that there exists a directed
        edge from n to m"

        EXAMPLE:
                U1 --> I2
                ↓
                I1

            get_successors(u1) ---> [I1, I2]


        Args:
            node(object): node of which we want to calculate successors
        """
        if not self.node_exists(node):
            logger.warning("The node specified is not in the graph! Return None")
        else:
            return list(self._graph.successors(node))

    def node_exists(self, node: object) -> bool:
        """
        Returns True if the node passed exists in the graph, False otherwise

        Args:
            node(object): node to check whether it's present in the graph
        """
        r = self._graph.nodes.get(node)
        return r is not None

    def is_user_node(self, node: object) -> bool:
        """
        Returns True if the node passed is a 'user' node, False otherwise

        Args:
            node(object): node to check whether it's a 'user' node or not
        """
        return node in self.user_nodes

    def is_item_node(self, node: object) -> bool:
        """
        Returns True if the node passed is a 'item' node, False otherwise

        Args:
            node(object): node to check whether it's a 'item' node or not
        """
        return node in self.item_nodes

    def degree_centrality(self):
        """
        Calculate the degreee centrality for every node in the graph
        """
        return nx.degree_centrality(self._graph)

    def closeness_centrality(self):
        """
        Calculate the closeness centrality for every node in the graph
        """
        return nx.closeness_centrality(self._graph)

    def dispersion(self):
        """
        Calculate the dispersion for every node in the graph
        """
        return nx.dispersion(self._graph)

    @property
    def _graph(self):
        """
        PRIVATE USAGE ONLY!

        In case some metrics needs to be performed on the newtowrkx graph
        """
        return self.__graph

    def _remove_nodes_from_graph(self, nodes_to_remove: Iterable):
        """
        PRIVATE USAGE ONLY

        Used in the Feature Selection process to remove certain nodes from the graph

        Args:
            nodes_to_remove (Iterable): iterable object containing the nodes to remove from the graph
        """
        self.__graph.remove_nodes_from(nodes_to_remove)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.get_default_score_label() == other.get_default_score_label() and \
                self.get_default_weight() == other.get_default_weight() and \
                nx.algorithms.isomorphism.is_isomorphic(self._graph, other._graph)
        else:
            return False
