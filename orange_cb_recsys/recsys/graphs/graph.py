import os
import pickle
import lzma
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import List, Set, Union, Iterable
import pandas as pd

from orange_cb_recsys.recsys.graphs.graph_metrics import GraphMetrics
from orange_cb_recsys.utils.load_content import load_content_instance

from orange_cb_recsys.content_analyzer.content_representation.content import Content
from orange_cb_recsys.utils.const import logger, progbar


class Node(ABC):
    """
    Abstract class that generalizes the concept of a Node

    The Node stores the actual value of the node in the 'value' attribute

    If another type of Node must be added to the graph (EX. Context), create a subclass for
    this class and create appropriate methods for the new Node in the Graph class
    """

    def __init__(self, value: object):
        self.__value = value

    @property
    def value(self):
        return self.__value

    def __hash__(self):
        return hash(self.__value)

    def __eq__(self, other):
        # If we are comparing self to an instance of the 'Node' class
        # then compare the value stored of self with the value stored
        # of the other instance and check if they are of the same class (UserNode == UserNode),
        # else compare the stored value of self directly to the other object
        if isinstance(other, Node):
            return self.value == other.value and type(self) is type(other)
        else:
            return self.value == other

    def __lt__(self, other):
        if isinstance(other, Node):
            return self.value < other.value
        else:
            return self.value < other

    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError


class UserNode(Node):
    """
    Class that represents 'user' nodes

    Args:
        value (object): the value to store in the node
    """

    def __init__(self, value: object):
        super().__init__(value)

    def __str__(self):
        return "User " + str(self.value)

    def __repr__(self):
        return "User " + str(self.value)


class ItemNode(Node):
    """
    Class that represents 'item' nodes

    Args:
        value (object): the value to store in the node
    """

    def __init__(self, value: object):
        super().__init__(value)

    def __str__(self):
        return "Item " + str(self.value)

    def __repr__(self):
        return "Item " + str(self.value)


class PropertyNode(Node):
    """
    Class that represents 'property' nodes

    Args:
        value (object): the value to store in the node
    """

    def __init__(self, value: object):
        super().__init__(value)

    def __str__(self):
        return "Property " + str(self.value)

    def __repr__(self):
        return "Property " + str(self.value)


class Graph(ABC):
    """
    Abstract class that generalizes the concept of a Graph

    Every Graph "is born" from a dataframe which contains
    """

    def __init__(self, source_frame: pd.DataFrame,
                 default_score_label: str = 'score', default_weight: float = 0.5):

        self.__default_score_label = default_score_label

        self.__default_weight = default_weight

        self.create_graph()
        self.populate_from_dataframe(source_frame)

    @abstractmethod
    def populate_from_dataframe(self, source_frame: pd.DataFrame):
        """
        Populate the graph using a DataFrame if it is of the format requested by
        _check_columns()
        """
        raise NotImplementedError

    @staticmethod
    def _check_columns(df: pd.DataFrame):
        """
        Check if there are at least least 'from_id', 'to_id', 'score' columns in the DataFrame

        Args:
            df (pandas.DataFrame): DataFrame to check

        Returns:
            bool: False if there aren't 'from_id', 'to_id', 'score' columns, else True
        """
        if 'from_id' not in df.columns or 'to_id' not in df.columns or 'score' not in df.columns:
            return False
        return True

    def get_default_score_label(self) -> str:
        """
        Getter for default_score_label
        """
        return self.__default_score_label

    def get_default_weight(self) -> float:
        """
        Getter for default_weight
        """
        return self.__default_weight

    @abstractmethod
    def create_graph(self):
        """
        Instantiate the empty graph
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def user_nodes(self) -> Set[UserNode]:
        """
        Returns a set of 'user' nodes
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def item_nodes(self) -> Set[ItemNode]:
        """
        Returns a set of 'item' nodes'
        """
        raise NotImplementedError

    @abstractmethod
    def add_user_node(self, node: object):
        """
        Add a 'user' node to the graph
        """
        raise NotImplementedError

    @abstractmethod
    def add_item_node(self, node: object):
        """
        Add a 'item' node to the graph
        """
        raise NotImplementedError

    @abstractmethod
    def add_link(self, start_node: object, final_node: object,
                 weight: float, label: str):
        """
        Adds an edge between the 'start_node' and the 'final_node',
        Both nodes must be present in the graph otherwise no link is created
        """
        raise NotImplementedError

    @abstractmethod
    def remove_link(self, start_node: object, final_node: object):
        """
        Remove the edge between the 'start_node' and the 'final_node',
        If there's no edge between the nodes, a warning is printed
        """
        raise NotImplementedError

    @abstractmethod
    def get_link_data(self, start_node: object, final_node: object):
        """
        Get data of the link between two nodes
        It can be None if does not exist
        """
        raise NotImplementedError

    @abstractmethod
    def get_predecessors(self, node: object) -> List[Node]:
        """
        Get all predecessors of a node
        """
        raise NotImplementedError

    @abstractmethod
    def get_successors(self, node: object) -> List[Node]:
        """
        Get all successors of a node
        """
        raise NotImplementedError

    @abstractmethod
    def node_exists(self, node: object) -> bool:
        """
        Returns True if node exists in the graph, false otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def is_user_node(self, node: object) -> bool:
        """
        Returns True if node is a 'user' node, false otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def is_item_node(self, node: object) -> bool:
        """
        Returns True if node is a 'item' node, false otherwise
        """
        raise NotImplementedError

    def get_voted_contents(self, node: object) -> List[Node]:
        """
        Get all voted contents of a specified node

        Given a node, all voted contents of said node are his successors that are
        'item' nodes or 'user' nodes (In case a user votes another user for example)

        Args:
            node (object): the node from which we want to extract the voted contents

        Returns:
            List of nodes representing the voted contents for the node passed as
            parameter
        """
        voted_contents = []
        if self.node_exists(node):
            for succ in self.get_successors(node):
                # We append only if the linked node is a 'to_node'
                # or a 'from_node' because if it is for example
                # a 'property_node' then it isn't a voted content but a property
                if self.is_user_node(succ) or self.is_item_node(succ):
                    voted_contents.append(succ)
        return voted_contents

    @property
    @abstractmethod
    def _graph(self):
        """
        PRIVATE
        Return the beneath implementation of the graph.

        Useful when is necessary to calculate some metrics for the graph
        """
        raise NotImplementedError

    @abstractmethod
    def _remove_nodes_from_graph(self, nodes_to_remove: Iterable):
        """
        PRIVATE USAGE ONLY

        Used in the Feature Selection process to remove certain nodes from the graph

        Args:
            nodes_to_remove (Iterable): iterable object containing the nodes to remove from the graph
        """
        raise NotImplementedError

    def convert_to_dataframe(self, only_values: bool = False, with_label: bool = False) -> pd.DataFrame:
        """
        Convert the graph into a DataFrame containing all interactions between the nodes

        Args:
            only_values (bool): if True, the value of the node will be inserted into the dataframe. Otherwise,
                the node itself will be inserted (given the user 'u1', only_values = True -> 'u1' vs
                only_values = False -> UserNode('u1'))
            with_label (bool): if True, the resulting DataFrame will contain the 'label' column in which the label of
                every interaction will be inserted
        """

        result = {'from_id': [], 'to_id': [], 'score': []}
        if with_label:
            result['label'] = []

        node_list = list(self.user_nodes) + list(self.item_nodes)

        for node in node_list:
            succ_list = self.get_successors(node)
            for succ in succ_list:
                link_data = self.get_link_data(node, succ)

                if only_values:
                    result['from_id'].append(node.value)
                    result['to_id'].append(succ.value)
                else:
                    result['from_id'].append(node)
                    result['to_id'].append(succ)
                result['score'].append(link_data['weight'])
                if with_label:
                    result['label'].append(link_data['label'])

        return pd.DataFrame(result)

    def copy(self):
        """
        Make a deep copy the graph
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo = {id(self): result}
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def serialize(self, output_directory: str = ".", file_name: str = 'graph.xz'):
        """
        Serialize the graph with the pickle.dump() method

        Args:
            output_directory (str): location where the graph will be serialized
            file_name (str): name of the file which will contain the graph serialized
        """
        if not os.path.exists(output_directory):
            os.mkdir(output_directory)

        if not file_name.endswith('.xz'):
            file_name += '.xz'

        path = os.path.join(output_directory, file_name)
        with lzma.open(path, 'wb') as f:
            pickle.dump(self, f)


class BipartiteGraph(Graph, GraphMetrics):
    """
    Abstract class that generalizes the concept of a BipartiteGraph

    A BipartiteGraph is a Graph containing only 'user' and 'item' nodes.

    Attributes:
        source_frame (pandas.DataFrame): must contains at least 'from_id', 'to_id', 'score' columns. The graph will be
            generated from this DataFrame
        default_score_label (str): the default label of the link between two nodes.
            Default is 'score'
        default_weight (float): the default value with which a link will be weighted
            Default is 0.5
    """

    def __init__(self, source_frame: pd.DataFrame,
                 default_score_label: str = 'score', default_weight: float = 0.5):
        super().__init__(source_frame,
                         default_score_label, default_weight)

    def populate_from_dataframe(self, source_frame: pd.DataFrame):
        """
        Populate the graph using a DataFrame.
        It must have a 'from_id', 'to_id' and 'score' column.

        This method will iterate for every row, and create a weighted link for every user and item in the rating frame
        based on the score the user gave the item, creating the nodes if they don't exist.

        Args:
            source_frame (pd.DataFrame): the rating frame from where the graph will be populated
        """
        if self._check_columns(source_frame):
            for row in progbar(source_frame.to_dict('records'),
                               max_value=source_frame.__len__(),
                               prefix="Populating Graph:"):
                self.add_user_node(row['from_id'])
                self.add_item_node(row['to_id'])
                if 'label' in source_frame.columns:
                    label = row['label']
                else:
                    label = self.get_default_score_label()
                self.add_link(UserNode(row['from_id']), ItemNode(row['to_id']), row['score'],
                              label=label)
        else:
            raise ValueError('The source frame must contains at least \'from_id\', \'to_id\', \'score\' columns')


class TripartiteGraph(BipartiteGraph):
    """
    Abstract class that generalize the concept of a TripartiteGraph

    A TripartiteGraph is a Graph containing 'user', 'item' and 'property' nodes, but the latter ones
    are only allowed to be linked to 'item' nodes.

    Attributes:
        source_frame (pandas.DataFrame): must contains at least 'from_id', 'to_id', 'score' columns. The graph will be
            generated from this DataFrame
        item_contents_dir (str): the path containing items serialized
        item_exo_representation (str): the exogenous representation we want to extract properties from
        item_exo_properties (list): the properties we want to extract from the exogenous representation
        default_score_label (str): the default label of the link between two nodes.
            Default is 'score'
        default_weight (float): the default value with which a link will be weighted
            Default is 0.5
    """

    def __init__(self, source_frame: pd.DataFrame, item_contents_dir: str = None,
                 item_exo_representation: Union[str, int] = None, item_exo_properties: List[str] = None,
                 default_score_label: str = 'score', default_weight: float = 0.5):

        self.__item_exogenous_representation: str = item_exo_representation

        self.__item_exogenous_properties: List[str] = item_exo_properties

        self.__item_contents_dir: str = item_contents_dir

        super().__init__(source_frame,
                         default_score_label, default_weight)

    def populate_from_dataframe(self, source_frame: pd.DataFrame):
        """
        Populate the graph using a DataFrame.
        It must have a 'from_id', 'to_id' and 'score' column.

        It will iterate for every row, and create a weighted link for every user and item in the rating frame
        based on the score the user gave the item, creating the nodes if they don't exist.
        We also add properties to 'item' nodes if the item_contents_dir is specified

        Args:
            source_frame (pd.DataFrame): the rating frame from where the graph will be populated
        """
        if self._check_columns(source_frame):
            for row in progbar(source_frame.to_dict('records'),
                               max_value=source_frame.__len__(),
                               prefix="Populating Graph:"):
                self.add_user_node(row['from_id'])

                # If the node already exists then we don't add it and more importantly
                # we don't retrieve its exo prop if specified, since they are already been retireved
                # previously.
                if not self.node_exists(ItemNode(row['to_id'])):
                    self.add_item_node(row['to_id'])
                    if self.get_item_contents_dir() is not None:
                        self._add_item_properties(row)

                if 'label' in source_frame.columns:
                    label = row['label']
                else:
                    label = self.get_default_score_label()

                self.add_link(UserNode(row['from_id']), ItemNode(row['to_id']), row['score'],
                              label=label)

        else:
            raise ValueError('The source frame must contains at least \'from_id\', \'to_id\', \'score\' columns')

    def _add_item_properties(self, row: dict):
        """
        Private method that given a row containing the 'to_id' field, tries to load the content
        from the item_contents_dir and if succeeds, extract properties presents in the content loaded
        based on the 'item_exo_representation' and 'item_exo_properties' parameters passed in
        the constructor as such:

        'item_exo_representation' was passed, 'item_exo_properties' was passed:
        ---------> Extract from the representation passed, the properties passed
            EXAMPLE:
                item_exo_representation = 0
                item_exo_properties = ['producer', 'director']

                will extract the 'producer' and 'director' property from the representation '0'

        'item_exo_representation' was passed, 'item_exo_properties' was NOT passed:
        ---------> Extract from the representation passed, ALL properties present in said representation
            EXAMPLE:
                    item_exo_representation = 0

                    will extract ALL properties from the representation '0'

        'item_exo_representation' was NOT passed, 'item_exo_properties' was passed:
        ---------> Extract from ALL representations, the properties passed
            EXAMPLE:
                item_exo_properties = ['producer', 'director']

                will extract the 'producer' and 'director' property from ALL exogenous representations
                of the content

        Args:
            row (dict): dict-like parameter containing at least a 'to_id' field
        """
        content = load_content_instance(self.__item_contents_dir, row['to_id'])
        if content is not None:
            # Provided representation and properties
            if self.get_item_exogenous_representation() is not None and \
                    self.get_item_exogenous_properties() is not None:
                self._prop_by_rep(content, ItemNode(row['to_id']),
                                  self.get_item_exogenous_representation(), self.get_item_exogenous_properties(),
                                  row)

            # Provided only the representation
            elif self.get_item_exogenous_representation() is not None and \
                    self.get_item_exogenous_properties() is None:
                self._all_prop_in_rep(content, ItemNode(row['to_id']),
                                      self.get_item_exogenous_representation(),
                                      row)

            # Provided only the properties
            elif self.get_item_exogenous_representation() is None and \
                    self.get_item_exogenous_properties() is not None:
                self._prop_in_all_rep(content, ItemNode(row['to_id']),
                                      self.get_item_exogenous_properties(),
                                      row)

    def _prop_by_rep(self, content: Content, node: object, exo_rep: str, exo_props: List[str], row: dict):
        """
        Private method that extracts from the 'content' loaded, the 'exo_props' passed
        from the 'exo_rep' passed, then creates a link between the 'node' passed and properties
        extracted.

            EXAMPLE:
                exo_rep = 0
                exo_props = ['producer', 'director']

                will extract the 'producer' and 'director' property from the representation '0'
                in the 'content' parameter and creates a link from the 'node' passed to said
                properties

        Args:
            content (Content): content loaded
            node (object): node to add properties to
            exo_rep (str): representation from where to extract the 'exo_props'
            exo_props (list): the properties list to extract from 'content'
            row (dict): dict-like object containing eventual score for the properties
        """
        properties = None
        try:
            properties = content.get_exogenous_representation(exo_rep).value
        except KeyError:
            logger.warning("Representation " + exo_rep + " not found for content " + content.content_id)

        if properties is not None:
            for prop in exo_props:
                if prop in properties.keys():
                    preference = self.get_preference(prop, row)
                    self.add_property_node(properties[prop])
                    self.add_link(node, properties[prop], preference, prop)
                else:
                    # logger.warning("Property " + prop + " not found for content " + content.content_id)
                    pass

    def _all_prop_in_rep(self, content, node, exo_rep, row):
        """
        Private method that extracts from the 'content' loaded, ALL properties
        from the 'exo_rep' passed, then creates a link between the 'node' passed and properties
        extracted.

            EXAMPLE:
                exo_rep = 0

                will extract ALL properties from the representation '0' in the 'content' parameter and
                creates a link from the 'node' passed to said properties

        Args:
            content (Content): content loaded
            node (object): node to add properties to
            exo_rep (str): representation from where to extract the 'exo_props'
            row (dict): dict-like object containing eventual score for the properties
        """
        properties = None

        try:
            properties = content.get_exogenous_representation(exo_rep).value
        except KeyError:
            logger.warning("Representation " + exo_rep + " not found for content " + content.content_id)

        if properties is not None:
            for prop_key in properties.keys():
                preference = self.get_preference(prop_key, row)
                self.add_property_node(properties[prop_key])
                self.add_link(node, properties[prop_key], preference, prop_key)

            # if len(properties) == 0:
            #     logger.warning("The chosen representation doesn't have any property!")

    def _prop_in_all_rep(self, content, node, exo_props, row):
        """
        Private method that extracts from the 'content' loaded, the 'exo_props' passed from
        ALL exo representation of the content, then creates a link between the 'node' passed and properties
        extracted. To avoid conflicts with multiple representations containing same properties, the
        properties extracted will be renamed as name_prop + exo_rep:

            EXAMPLE:
                exo_props = ['producer', 'director']

                will extract 'producer' and 'director' properties from ALL exogenous representation in the 'content'
                parameter and creates a link from the 'node' passed to said properties.
                The properties will be renamed as 'producer_0', 'director_0', 'producer_1', 'director_1'
                if for example the content has those two properties in the 0 exogenous representation
                and 1 exogenous representation


        Args:
            content (Content): content loaded
            node (object): node to add properties to
            exo_props (list): the properties list to extract from 'content'
            row (dict): dict-like object containing eventual score for the properties
        """
        internal_id_list = content.exogenous_rep_container.get_internal_index()
        external_id_list = content.exogenous_rep_container.get_external_index()
        for prop in exo_props:
            # property_found = False
            for id_int, id_ext in zip(internal_id_list, external_id_list):
                if prop in content.get_exogenous_representation(id_int).value:
                    # property_found = True

                    # edge_label = director#0#dbpedia, director#1#datasetlocal
                    # OR edge_label = director#0, edge_label = director#1 if external id is NaN
                    edge_label = "{}#{}".format(prop, str(id_int))
                    if pd.notna(id_ext):
                        edge_label += '#{}'.format(id_ext)

                    property_node = content.get_exogenous_representation(id_int).value[prop]

                    # search preference for the property in the original frame source
                    preference = self.get_preference(prop, row)

                    self.add_property_node(property_node)
                    self.add_link(node, property_node, preference, edge_label)

            # if not property_found:
            #     logger.warning("Property {} not found in any representation of content {}".format(prop, content.content_id))

    def get_item_exogenous_representation(self) -> str:
        """
        Getter for item_exogenous_representation
        """
        return self.__item_exogenous_representation

    def get_item_exogenous_properties(self) -> List[str]:
        """
        Getter for item_exogenous_properties
        """
        return self.__item_exogenous_properties

    def get_item_contents_dir(self) -> str:
        """
        Getter for item_contents_dir
        """
        return self.__item_contents_dir

    def get_preference(self, label: str, preferences_dict: dict) -> float:
        """
        Get the score of the label in the preferences_dict.
        Returns the default 'not_rated_value' if the label is not present

        EXAMPLE:
            preferences_dict:
            {'from_id': 'u1', 'to_id': 'i1', 'score': 0.6, 'director': 'Nolan', 'director_score': 0.8}

            get_preference('director', preferences_dict) ---> 0.8

        Args:
            label(str): label we want to search in the preferences_dict
            preferences_dict (dict): dict-like parameter containing some information about 'from'
                                    and 'to' nodes.
        """
        ls = '{}_score'.format(label.lower())
        if ls in preferences_dict.keys():
            return preferences_dict[ls]
        return self.get_default_weight()

    @property
    @abstractmethod
    def property_nodes(self) -> Set[object]:
        """
        Returns a set of 'property' nodes
        """
        raise NotImplementedError

    @abstractmethod
    def add_property_node(self, node: object):
        """
        Add a 'property' node to the graph
        """
        raise NotImplementedError

    def add_item_tree(self, item_node: object):
        """
        Add a 'item' node if is not in the graph and load properties from disk if the node has some.

        The method will try to load the content from the 'item_contents_dir' and extract
        from the loaded content the properties specified in the constructor (item_exo_representation,
        item_exo_properties)

        Args:
            item_node (object): 'item' node to add to the graph with its properties
        """
        self.add_item_node(item_node)

        if self.get_item_contents_dir() is not None:
            self._add_item_properties({'to_id': item_node})
        else:
            logger.warning("The dir is not specified! The node will be added with no "
                           "properties")

    def get_properties(self, node: object) -> List[object]:
        """
        Get all properties of a specified node

        Given a node, all properties of said node are his successors that are
        'property' nodes

        Args:
            node (object): the node from which we want to extract the properties

        Returns:
            List of nodes representing the properties for the node passed as
            parameter
        """
        properties = []
        if self.node_exists(node):
            for succ in self.get_successors(node):
                if self.is_property_node(succ):
                    link_data = self.get_link_data(node, succ)
                    prop: dict = {link_data['label']: succ}
                    properties.append(prop)
        return properties

    @abstractmethod
    def is_property_node(self, node: object) -> bool:
        """
        Returns True if the node is a 'property' node, False otherwise
        """
        raise NotImplementedError


class FullGraph(TripartiteGraph):
    """
    Abstract class that generalize the concept of a FullGraph

    A FullGraph is a Graph containing 'user', 'item', 'property' nodes, and every other type of node that may be
    implemented, with no restrictions in linking.

    Attributes:
        source_frame (pandas.DataFrame): must contains at least 'from_id', 'to_id', 'score' columns. The graph will be
            generated from this DataFrame
        user_contents_dir (str): the path containing users serialized
        item_contents_dir (str): the path containing items serialized
        user_exo_representation (str): the exogenous representation we want to extract properties from for the users
        user_exo_properties (list): the properties we want to extract from the exogenous representation for the users
        item_exo_representation (str): the exogenous representation we want to extract properties from for the items
        item_exo_properties (list): the properties we want to extract from the exogenous representation for the items
        default_score_label (str): the default label of the link between two nodes.
            Default is 'score'
        default_weight (float): the default value with which a link will be weighted
            Default is 0.5
    """

    def __init__(self, source_frame: pd.DataFrame, user_contents_dir: str = None, item_contents_dir: str = None,
                 user_exo_representation: Union[str, int] = None, user_exo_properties: List[str] = None,
                 item_exo_representation: Union[str, int] = None, item_exo_properties: List[str] = None,
                 default_score_label: str = 'score', default_weight: float = 0.5):

        self.__user_exogenous_representation: str = user_exo_representation

        self.__user_exogenous_properties: List[str] = user_exo_properties

        self.__user_contents_dir: str = user_contents_dir

        super().__init__(source_frame, item_contents_dir,
                         item_exo_representation, item_exo_properties,
                         default_score_label, default_weight)

    def populate_from_dataframe(self, source_frame: pd.DataFrame):
        """
        Populate the graph using a DataFrame.
        It must have a 'from_id', 'to_id' and 'score' column.

        The method will iterate for every row, and create a weighted link for every user and item in the rating frame
        based on the score the user gave the item, creating the nodes if they don't exist.
        We also add properties to 'item' nodes if the item_contents_dir is specified,
        and add properties to 'user' nodes if the user_contents_dir is specified.

        Args:
            source_frame (pd.DataFrame): the rating frame from where the graph will be populated
        """
        if self._check_columns(source_frame):
            for row in progbar(source_frame.to_dict('records'),
                               max_value=source_frame.__len__(),
                               prefix="Populating Graph:"):

                # If the node already exists then we don't add it and more importantly
                # we don't retrieve its exo prop if specified, since they are already been retireved
                # previously.
                if not self.node_exists(UserNode(row['from_id'])):
                    self.add_user_node(row['from_id'])
                    if self.get_user_contents_dir() is not None:
                        self._add_usr_properties(row)

                # If the node already exists then we don't add it and more importantly
                # we don't retrieve its exo prop if specified, since they are already been retireved
                # previously.
                if not self.node_exists(ItemNode(row['to_id'])):
                    self.add_item_node(row['to_id'])
                    if self.get_item_contents_dir() is not None:
                        self._add_item_properties(row)

                if 'label' in source_frame.columns:
                    label = row['label']
                else:
                    label = self.get_default_score_label()

                self.add_link(UserNode(row['from_id']), ItemNode(row['to_id']), row['score'],
                              label=label)
        else:
            raise ValueError('The source frame must contains at least \'from_id\', \'to_id\', \'score\' columns')

    def _add_usr_properties(self, row):
        """
        Private method that given a row containing the 'from_id' field, tries to load the content
        from the user_contents_dir and if succeeds, extract properties presents in the content loaded
        based on the 'user_exo_representation' and 'user_exo_properties' parameters passed in
        the constructor as such:

        'user_exo_representation' was passed, 'user_exo_properties' was passed:
        ---------> Extract from the representation passed, the properties passed
            EXAMPLE:
                user_exo_representation = 0
                user_exo_properties = ['gender', 'birthdate']

                will extract the 'gender' and 'birthdate' property from the representation '0'

        'user_exo_representation' was passed, 'user_exo_properties' was NOT passed:
        ---------> Extract from the representation passed, ALL properties present in said representation
            EXAMPLE:
                    user_exo_representation = 0

                    will extract ALL properties from the representation '0'

        'user_exo_representation' was NOT passed, 'user_exo_properties' was passed:
        ---------> Extract from ALL representations, the properties passed
            EXAMPLE:
                user_exo_properties = ['gender', 'birthdate']

                will extract the 'gender' and 'birthdate' property from ALL exogenous representations
                of the content

        Args:
            row (dict): dict-like parameter containing at least a 'from_id' field
        """
        content = load_content_instance(self.__user_contents_dir, row['from_id'])

        if content is not None:
            # Provided representation and properties
            if self.get_user_exogenous_representation() is not None and \
                    self.get_user_exogenous_properties() is not None:
                self._prop_by_rep(content, UserNode(row['from_id']),
                                  self.get_user_exogenous_representation(), self.get_user_exogenous_properties(),
                                  row)

            # Provided only the representation
            elif self.get_user_exogenous_representation() is not None and \
                    self.get_user_exogenous_properties() is None:
                self._all_prop_in_rep(content, UserNode(row['from_id']),
                                      self.get_user_exogenous_representation(),
                                      row)

            # Provided only the properties
            elif self.get_user_exogenous_representation() is None and \
                    self.get_user_exogenous_properties() is not None:
                self._prop_in_all_rep(content, UserNode(row['from_id']),
                                      self.get_user_exogenous_properties(),
                                      row)

    def get_user_exogenous_representation(self) -> str:
        """
        Getter for user_exogenous_representation
        """
        return self.__user_exogenous_representation

    def get_user_exogenous_properties(self) -> List[str]:
        """
        Getter for user_exogenous_properties
        """
        return self.__user_exogenous_properties

    def get_user_contents_dir(self) -> str:
        """
        Getter for user_contents_dir
        """
        return self.__user_contents_dir

    def add_user_tree(self, user_node: object):
        """
        Add a 'user' node if is not in the graph and load properties from disk
        if the node has some
        The method will try to load the content from the 'user_contents_dir' and extract
        from the loaded content the properties specified in the constructor (user_exo_representation,
        user_exo_properties)

        Args:
            user_node (object): 'user' node to add to the graph with its properties
        """
        self.add_user_node(user_node)

        if self.get_user_contents_dir() is not None:
            self._add_usr_properties({'from_id': user_node})
        else:
            logger.warning("The dir is not specified! The node will be added with no "
                           "properties")
