from unittest import TestCase

from orange_cb_recsys.content_analyzer.ratings_manager.sentimental_analysis import \
    TextBlobSentimentalAnalysis


class TestTextBlobSentimentalAnalysis(TestCase):
    def test_calculate_score(self):
        file_path = '../../../datasets/test_sentiment_analysis.json'
        try:
            with open(file_path):
                pass
        except FileNotFoundError:
            file_path = 'datasets/test_sentiment_analysis.json'

        confront_list = [1.0, 0.9, -0.6999999999999998, 0.8, 0.8125, 0.48333333333333334, 0.4166666666666667, 0.7666666666666666, 0.0, -0.15000000000000002, 0.0, 0.0, 0.0, 0.9, 0.39, 1.0, 0.16666666666666666, 0.3444444444444444, 0.3666666666666667, 0.525]
        test_list: list = TextBlobSentimentalAnalysis().fit()
        self.assertEqual(test_list, confront_list)
