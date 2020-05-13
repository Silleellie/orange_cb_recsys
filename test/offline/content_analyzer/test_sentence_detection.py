from unittest import TestCase

from src.offline.content_analyzer.sentence_detection import NLTKSentenceDetection


class TestNLTKSentenceDetection(TestCase):
    def test_detect_sentences(self):
        self.skipTest("FIX TEST")
        text = "god is great! i won lottery."
        detector = NLTKSentenceDetection()

        expected = ["god is great", "i won lottery"]
        result = detector.detect_sentences(text)

        self.assertEquals(result, expected)