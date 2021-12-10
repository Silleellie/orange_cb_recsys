from abc import ABC, abstractmethod
from typing import List

import pandas as pd

from orange_cb_recsys.recsys.partitioning import Split

from orange_cb_recsys.evaluation.exceptions import AlreadyFittedRecSys
from orange_cb_recsys.recsys.recsys import RecSys
from orange_cb_recsys.utils.const import progbar


class Metric(ABC):
    """
    Abstract class that generalize metric concept

    Every metric may need different kind of "prediction": some (eg. NDCG, MRR, etc.) may need recommendation lists in
    which the recsys ranks every unseen item, some (eg. MAE, RMSE, etc.) may need a score prediction where the recsys
    must predict the rating that a user would give to an unseen item.
    So a Metric category (subclass of this class) must implement the "eval_fit_recsys(...)" specifying its needs,
    while every single metric (subclasses of the metric category class) must implement the "perform(...)" method
    specifying how to execute the metric computation
    """

    @abstractmethod
    def __str__(self):
        raise NotImplementedError


class IndividualMetric(Metric):

    @abstractmethod
    def perform(self, pred_user: pd.DataFrame, truth_user: pd.DataFrame):
        """
        Method that execute the metric computation

        Args:
              split (Split): single split containing two DataFrames, the first has predictions for every user,
                the second has the 'Ground Truth' for every user
        """
        raise NotImplementedError


class AllSetMetric(Metric):
    pass


class RankingNeededMetric(Metric):
    """
    Metric category which act as a superclass for all those metrics which evaluate rankings.
    Examples of such metrics are NDCG, MRR, etc.

    This class takes care of the implementation of the "eval_fit_recsys(...)" method usually called by the
    PredictionCalculator of the EvalModel pipeline, so that every metric that requires rankings can just derive this
    class and implement the "perform(...)" method which effectively execute the metric computation
    """
    rank_truth_list: List[Split] = []

    @classmethod
    def eval_fit_recsys(cls, recsys: RecSys, split_list: List[Split], test_items_list: List[pd.DataFrame]):
        """
        Method which is usually called by the 'PredictionCalculator' module that generates recommendation lists. For
        every user, items that will be ranked are specified by the 'test_items_list' parameter.

        Rankings generated will be stored into a class attribute (rank_truth_list), which is a list that contains
        Split objects: every object has two DataFrames, the first one has recommendation lists for every user,
        the second one has the 'ground truth' for every user.

        If the class attribute is non-empty, then the 'AlreadyFittedRecSys' exception is raised, so remember to
        clean the class attribute by calling the private method '_clean_pred_truth_list(...)' upon every new evaluation

        Args:
            recsys (RecSys): Recommender system which will generate predictions that will later be evaluated
            split_list (List[Split]): List of Split objects where every Split contains two DataFrames, the first has
                the 'train set' for every user, the second has the 'test set' for every user
            test_items_list (List[pd.DataFrame]): List of DataFrames, one for every Split object inside the split_list
                parameter, where every DataFrame contains for every user the list of items that must be ranked

        Raises:
            AlreadyFittedRecSys exception when the class attribute 'rank_truth_list' is non-empty, meaning that
            recommendation lists are already been calculated
        """

        if len(cls.rank_truth_list) != 0:
            raise AlreadyFittedRecSys

        for counter, (split, test_items_frame) in enumerate(zip(split_list, test_items_list), start=1):

            train = split.train
            test = split.test

            rank_truth = Split()
            rank_truth.truth = test

            frame_to_concat = []
            user_list_to_fit = set(train.from_id)

            for user in progbar(user_list_to_fit,
                                prefix='Calculating rank for user {} - split {}'.format('{}', counter),
                                substitute_with_current=True):

                user_ratings_train = train.loc[train['from_id'] == user]

                test_items = list(test_items_frame.query('from_id == @user').to_id)

                result = recsys._eval_fit_rank(user_ratings_train, test_items)

                frame_to_concat.append(result)

            rank_truth.pred = pd.concat(frame_to_concat)

            cls.rank_truth_list.append(rank_truth)

    @classmethod
    def _get_pred_truth_list(cls):
        return cls.rank_truth_list

    @classmethod
    def _clean_pred_truth_list(cls):
        RankingNeededMetric.rank_truth_list = []


class ScoresNeededMetric(Metric):
    """
    Metric category which act as a superclass for all those metrics which evaluate score predictions.
    Examples of such metrics are MAE, RMSE, etc.

    This class takes care of the implementation of the "eval_fit_recsys(...)" method usually called by the
    PredictionCalculator of the EvalModel pipeline, so that every metric that requires score prediction can just derive
    this class and implement the "perform(...)" method which effectively execute the metric computation
    """
    score_truth_list: List[Split] = []

    @classmethod
    def eval_fit_recsys(cls, recsys: RecSys, split_list: List[Split], test_items_list: List[pd.DataFrame]):
        """
        Method which is usually called by the 'PredictionCalculator' module that predicts, for every user, the rating
        that a user would give to every item specified in the 'test_items_list' parameter.

        Score predictions generated will be stored into a class attribute (score_truth_list), which is a list that
        contains Split objects: every object has two DataFrames, the first one has score predictions lists for every
        user, the second one has the 'ground truth' for every user.

        If the class attribute is non-empty, then the 'AlreadyFittedRecSys' exception is raised, so remember to
        clean the class attribute by calling the private method '_clean_pred_truth_list(...)' upon every new evaluation

        Args:
            recsys (RecSys): Recommender system which will generate predictions that will later be evaluated
            split_list (List[Split]): List of Split objects where every Split contains two DataFrames, the first has
                the 'train set' for every user, the second has the 'test set' for every user
            test_items_list (List[pd.DataFrame]): List of DataFrames, one for every Split object inside the split_list
                parameter, where every DataFrame contains for every user the list of items that must be score predicted

        Raises:
            AlreadyFittedRecSys exception when the class attribute 'rank_truth_list' is non-empty, meaning that
            recommendation lists are already been calculated
        """
        if len(cls.score_truth_list) != 0:
            raise AlreadyFittedRecSys

        for counter, (split, test_items_frame) in enumerate(zip(split_list, test_items_list), start=1):

            train = split.train
            test = split.test

            score_truth = Split()
            score_truth.truth = test

            frame_to_concat = []
            user_list_to_fit = set(train.from_id)

            for user in progbar(user_list_to_fit,
                                prefix='Calculating score predictions for user {} - split {}'.format('{}', counter),
                                substitute_with_current=True):

                user_ratings_train = train.loc[train['from_id'] == user]

                test_items = test_items_frame.query('from_id == @user').to_id

                result = recsys._eval_fit_predict(user_ratings_train, test_items)

                frame_to_concat.append(result)

            score_truth.pred = pd.concat(frame_to_concat)

            cls.score_truth_list.append(score_truth)

    @classmethod
    def _get_pred_truth_list(cls):
        return cls.score_truth_list

    @classmethod
    def _clean_pred_truth_list(cls):
        ScoresNeededMetric.score_truth_list = []
