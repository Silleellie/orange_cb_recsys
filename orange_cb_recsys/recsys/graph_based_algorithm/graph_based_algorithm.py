import abc
from typing import Dict, List

from orange_cb_recsys.content_analyzer.ratings_manager.ratings import Interaction
from orange_cb_recsys.recsys.algorithm import Algorithm
from orange_cb_recsys.recsys.graph_based_algorithm.feature_selection.feature_selection import FeatureSelectionAlgorithm

from orange_cb_recsys.recsys.graphs.graph import FullGraph, UserNode, PropertyNode

import pandas as pd


class GraphBasedAlgorithm(Algorithm):
    """
    Abstract class for the graph-based algorithms

    Args:
    feature_selection (FeatureSelectionAlgorithm): a FeatureSelectionAlgorithm algorithm if the graph needs to be
        reduced
    """
    def __init__(self, feature_selection: FeatureSelectionAlgorithm = None):
        self.__feature_selection: FeatureSelectionAlgorithm = feature_selection

    @property
    def feature_selection(self):
        return self.__feature_selection

    @feature_selection.setter
    def feature_selection(self, feature_selection: FeatureSelectionAlgorithm):
        self.__feature_selection = feature_selection

    def clean_result(self, graph: FullGraph, result: Dict, user_id: str,
                     remove_users: bool = True,
                     remove_profile: bool = True,
                     remove_properties: bool = True) -> Dict:
        """
        Cleans the result from all the nodes that are not requested.

        It's possible to remove:
        * user nodes (remove_users),
        * item nodes rated by the user (remove_profile),
        * property nodes (remove_properties).

        This produces a cleaned result with only the desired nodes inside it.
        Args:
            graph (FullGraph): graph from which the profile of the user will be extracted if it needs to be removed
                from the result
            result (dict): dictionary representing the result (keys are nodes and values are their score prediction)
            user_id (str): id of the user used to extract his profile
            remove_users (bool): boolean value, set to true if 'User' nodes need to be removed from the result dict
            remove_profile (bool): boolean value, set to true if 'Item' nodes rated by the user
                need to be removed from the result dict
            remove_properties (bool): boolean value, set to true if 'Property' nodes need to be removed from the
                result dict
        Returns:
            new_result (dict): dictionary representing the cleaned result
        """
        def is_valid(node: object, user_profile):
            valid = True
            if remove_users and isinstance(node, UserNode) or \
                remove_profile and node in user_profile or \
                remove_properties and isinstance(node, PropertyNode):

                valid = False

            return valid

        extracted_profile = self.extract_profile(graph, user_id)
        new_result = {k: result[k] for k in result.keys() if is_valid(k, extracted_profile)}

        return new_result

    @staticmethod
    def filter_result(result: Dict, filter_list: List[str]) -> Dict:
        """
        Method which filters the result dict returning only items that are also in the filter_list

        Args:
            result (dict): dictionary representing the result (keys are nodes and values are their score prediction)
            filter_list (list): list of the items to predict, if None all unrated items will be predicted
        """

        filtered_result = {k: result[k] for k in filter_list if result.get(k) is not None}

        return filtered_result

    @staticmethod
    def extract_profile(graph: FullGraph, user_id: str) -> Dict:
        """
        Extracts the user profile (the items that the user rated, or in general the nodes with a link to the user).

        Returns a dictionary containing the successor nodes as keys and the weights in the graph for the edges between
        the user node and his successors as values

        EXAMPLE::
             graph: i1 <---0.2--- u1 ---0.4---> i2

            > print(extract_profile('u1'))
            > {'i1': 0.2, 'i2': 0.4}

        Args:
            graph (FullGraph): graph from which the profile of the user will be extracted
            user_id (str): id for the user for which the profile will be extracted
        Returns:
            profile (dict): dictionary with item successor nodes to the user as keys and weights of the edge
                connecting them in the graph as values
        """
        succ = graph.get_successors(UserNode(user_id))
        profile = {a: graph.get_link_data(UserNode(user_id), a)['weight'] for a in succ}

        return profile  # {t: w for (f, t, w) in adj}

    @abc.abstractmethod
    def predict(self, user_id: str, graph: FullGraph, filter_list: List[str] = None) -> List[Interaction]:
        """
        |  Abstract method that predicts the rating which a user would give to items
        |  If the algorithm is not a PredictionScore Algorithm, implement this method like this:

        def predict():
            raise NotPredictionAlg

        One can specify which items must be predicted with the filter_list parameter,
        in this case ONLY items in the filter_list will be predicted.
        One can also pass items already seen by the user with the filter_list parameter.
        Otherwise, ALL unrated items will be predicted.

        Args:
            user_id (str): id of the user of which predictions will be calculated
            graph (FullGraph): graph containing interactions between users and items (and optionally other types of
                nodes)
            filter_list (list): list of the items to predict, if None all unrated items will be score predicted
        Returns:
            pd.DataFrame: DataFrame containing one column with the items name,
                one column with the score predicted
        """
        raise NotImplementedError

    @abc.abstractmethod
    def rank(self, user_id: str, graph: FullGraph, recs_number: int = None,
             filter_list: List[str] = None) -> List[Interaction]:
        """
        |  Rank the top-n recommended items for the user. If the recs_number parameter isn't specified,
        |  all items will be ranked.
        |  If the algorithm is not a Ranking Algorithm, implement this method like this:

        def rank():
            raise NotRankingAlg

        One can specify which items must be ranked with the filter_list parameter,
        in this case ONLY items in the filter_list will be ranked.
        One can also pass items already seen by the user with the filter_list parameter.
        Otherwise, ALL unrated items will be ranked.

        Args:
            user_id (str): id of the user of which predictions will be calculated
            graph (FullGraph): graph containing interactions between users and items (and optionally other types of
                nodes)
            filter_list (list): list of the items to predict, if None all unrated items will be score predicted
        Returns:
            pd.DataFrame: DataFrame containing one column with the items name,
                one column with the rating predicted, sorted in descending order by the 'rating' column
        """
        raise NotImplementedError
