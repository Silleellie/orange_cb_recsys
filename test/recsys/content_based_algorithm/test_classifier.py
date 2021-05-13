from unittest import TestCase

import pandas as pd
import os

from orange_cb_recsys.recsys.content_based_algorithm.classifier import ClassifierRecommender, \
    KNN, RandomForest, GaussianProcess, LogReg, DecisionTree, SVM
from orange_cb_recsys.utils.const import root_path

contents_path = os.path.join(root_path, 'contents')


class TestClassifierRecommender(TestCase):

    def setUp(self) -> None:
        self.ratings = pd.DataFrame.from_records([
            ("A000", "tt0114576", 1, "54654675"),
            ("A000", "tt0112453", -0.2, "54654675"),
            ("A001", "tt0114576", 0.8, "54654675"),
            ("A001", "tt0112896", -0.4, "54654675"),
            ("A000", "tt0113041", 0.6, "54654675"),
            ("A002", "tt0112453", -0.2, "54654675"),
            ("A002", "tt0113497", 0.5, "54654675"),
            ("A003", "tt0112453", -0.8, "54654675")],
            columns=["from_id", "to_id", "score", "timestamp"])

        self.filter_list = ['tt0112641', 'tt0112760', 'tt0112896']

        self.movies_dir = os.path.join(contents_path, 'movies_multiple_repr/')

    def test_gaussian_process(self):
        alg = ClassifierRecommender({'Plot': '0'}, GaussianProcess(), 0)
        alg.initialize(self.ratings, self.movies_dir)

        pred_result = alg.fit_predict('A000', self.filter_list)
        self.assertEqual(len(pred_result), len(self.filter_list))

        rank_result = alg.fit_rank('A000', recs_number=5)
        self.assertEqual(len(rank_result), 5)

        alg = ClassifierRecommender({"Plot": ["0", "1"],
                                     "Genre": ["0", "1"],
                                     "Director": "1"},
                                    GaussianProcess(),
                                    0)
        alg.initialize(self.ratings, self.movies_dir)
        pred_result = alg.fit_predict('A000', self.filter_list)
        self.assertEqual(len(pred_result), len(self.filter_list))

        rank_result = alg.fit_rank('A000', recs_number=5)
        self.assertEqual(len(rank_result), 5)

    def test_random_forest(self):
        alg = ClassifierRecommender({'Plot': '0'}, RandomForest(), 0)
        alg.initialize(self.ratings, self.movies_dir)

        pred_result = alg.fit_predict('A000', self.filter_list)
        self.assertEqual(len(pred_result), len(self.filter_list))

        rank_result = alg.fit_rank('A000', recs_number=5)
        self.assertEqual(len(rank_result), 5)

        alg = ClassifierRecommender({"Plot": ["0", "1"],
                                     "Genre": ["0", "1"],
                                     "Director": "1"},
                                    RandomForest(),
                                    0)
        alg.initialize(self.ratings, self.movies_dir)
        pred_result = alg.fit_predict('A000', self.filter_list)
        self.assertEqual(len(pred_result), len(self.filter_list))

        rank_result = alg.fit_rank('A000', recs_number=5)
        self.assertEqual(len(rank_result), 5)

    def test_logistic_regression(self):
        alg = ClassifierRecommender({'Plot': '0'}, LogReg(), 0)
        alg.initialize(self.ratings, self.movies_dir)

        pred_result = alg.fit_predict('A000', self.filter_list)
        self.assertEqual(len(pred_result), len(self.filter_list))

        rank_result = alg.fit_rank('A000', recs_number=5)
        self.assertEqual(len(rank_result), 5)

        alg = ClassifierRecommender({"Plot": ["0", "1"],
                                     "Genre": ["0", "1"],
                                     "Director": "1"},
                                    LogReg(),
                                    0)
        alg.initialize(self.ratings, self.movies_dir)
        pred_result = alg.fit_predict('A000', self.filter_list)
        self.assertEqual(len(pred_result), len(self.filter_list))

        rank_result = alg.fit_rank('A000', recs_number=5)
        self.assertEqual(len(rank_result), 5)

    def test_knn(self):
        alg = ClassifierRecommender({'Plot': '0'}, KNN(), 0)
        alg.initialize(self.ratings, self.movies_dir)

        pred_result = alg.fit_predict('A000', self.filter_list)
        self.assertEqual(len(pred_result), len(self.filter_list))

        rank_result = alg.fit_rank('A000', recs_number=5)
        self.assertEqual(len(rank_result), 5)

        alg = ClassifierRecommender({"Plot": ["0", "1"],
                                     "Genre": ["0", "1"],
                                     "Director": "1"},
                                    KNN(n_neighbors=3),
                                    0)
        alg.initialize(self.ratings, self.movies_dir)
        pred_result = alg.fit_predict('A000', self.filter_list)
        self.assertEqual(len(pred_result), len(self.filter_list))

        rank_result = alg.fit_rank('A000', recs_number=5)
        self.assertEqual(len(rank_result), 5)

    def test_svm(self):
        alg = ClassifierRecommender({'Plot': '0'}, SVM(), 0)
        alg.initialize(self.ratings, self.movies_dir)

        pred_result = alg.fit_predict('A000', self.filter_list)
        self.assertEqual(len(pred_result), len(self.filter_list))

        rank_result = alg.fit_rank('A000', recs_number=5)
        self.assertEqual(len(rank_result), 5)

        alg = ClassifierRecommender({"Plot": ["0", "1"],
                                     "Genre": ["0", "1"],
                                     "Director": "1"},
                                    SVM(),
                                    0)
        alg.initialize(self.ratings, self.movies_dir)
        pred_result = alg.fit_predict('A000', self.filter_list)
        self.assertEqual(len(pred_result), len(self.filter_list))

        rank_result = alg.fit_rank('A000', recs_number=5)
        self.assertEqual(len(rank_result), 5)

    def test_decision_tree(self):
        alg = ClassifierRecommender({'Plot': '0'}, DecisionTree(), 0)
        alg.initialize(self.ratings, self.movies_dir)

        pred_result = alg.fit_predict('A000', self.filter_list)
        self.assertEqual(len(pred_result), len(self.filter_list))

        rank_result = alg.fit_rank('A000', recs_number=5)
        self.assertEqual(len(rank_result), 5)

        alg = ClassifierRecommender({"Plot": ["0", "1"],
                                     "Genre": ["0", "1"],
                                     "Director": "1"},
                                    DecisionTree(),
                                    0)
        alg.initialize(self.ratings, self.movies_dir)
        pred_result = alg.fit_predict('A000', self.filter_list)
        self.assertEqual(len(pred_result), len(self.filter_list))

        rank_result = alg.fit_rank('A000', recs_number=5)
        self.assertEqual(len(rank_result), 5)

    def test_empty_frame(self):

        # Only positive available
        self.ratings = pd.DataFrame.from_records([
            ("A000", "tt0112281", 1, "54654675")],
            columns=["from_id", "to_id", "score", "timestamp"])

        alg = ClassifierRecommender({'Plot': '0'}, DecisionTree(), 0)
        alg.initialize(self.ratings, self.movies_dir)

        result = alg.fit_predict('A000')
        self.assertTrue(result.empty)

        # Only negative available
        self.ratings = pd.DataFrame.from_records([
            ("A000", "tt0112281", -1, "54654675")],
            columns=["from_id", "to_id", "score", "timestamp"])

        alg = ClassifierRecommender({'Plot': '0'}, DecisionTree(), 0)
        alg.initialize(self.ratings, self.movies_dir)

        result = alg.fit_predict('A000')
        self.assertTrue(result.empty)

        # Non Existent Item avilable locally
        self.ratings = pd.DataFrame.from_records([
            ("A000", "non existent", 0.5, "54654675")],
            columns=["from_id", "to_id", "score", "timestamp"])

        alg = ClassifierRecommender({'Plot': '0'}, DecisionTree(), 0)
        alg.initialize(self.ratings, self.movies_dir)

        result = alg.fit_predict('A000')
        self.assertTrue(result.empty)

    def test_ino(self):
        ratings = pd.DataFrame.from_records([
            ("A000", "tt0114576", 1, "54654675"),
            ("A000", "tt0112453", 1, "54654675"),
            ("A000", "tt0112896", -1, "54654675"),
            ("A000", "tt0113041", -1, "54654675"),
            ("A000", "tt0113497", -1, "54654675")],
            columns=["from_id", "to_id", "score", "timestamp"])

        candidate_list = ratings.to_id

        alg = ClassifierRecommender({'Plot': ['0', '1']}, SVM(), threshold=0)
        alg.initialize(ratings, self.movies_dir)

        print(alg.fit_predict('A000', candidate_list))