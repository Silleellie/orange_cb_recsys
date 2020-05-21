from unittest import TestCase
from src.content_analyzer.information_processor.nlp import NLTK
from src.content_analyzer.embedding_learner.fasttext import GensimFastText
from src.content_analyzer.raw_information_source import JSONFile


class TestGensimFastText(TestCase):
    def test_start_learning(self):
        list = [[[0.02949842, 0.04819039, 0.02683405, 0.13783221]],
                [[-0.24603415, -0.1258604, 0.24925545, -0.23021373]],
                [[-0.24713391, 0.13750966, 0.00877043, -0.21628569]],
                [[-0.11638978, 0.17369802, -0.18660733, 0.17513901]],
                [[0.15258612, 0.22899817, -0.15156834, -0.21254702]],
                [[-0.10677111, -0.0237601, -0.0353453, -0.23621973]],
                [[0.22311535, 0.09145123, 0.03119936, -0.1178216]],
                [[-0.15863626, -0.16506611, -0.12962262, 0.1801771]],
                [[0.04536469, -0.18906215, -0.17747177, -0.09783045]],
                [[0.11989173, 0.24327743, 0.14084858, 0.23288251]],
                [[0.00249855, -0.12464175, 0.06799347, 0.06086745]],
                [[0.04052542, 0.06269088, -0.14204247, 0.03114885]],
                [[0.02085659, 0.15494178, 0.02734849, 0.01428937]],
                [[-0.01387836, -0.1938315, -0.07655563, -0.02608451]],
                [[-0.09567448, -0.02621552, -0.01877257, -0.13423938]],
                [[0.07947826, -0.12941308, 0.06206714, -0.04967041]],
                [[0.01616536, 0.06537089, 0.00899961, -0.10340416]],
                [[0.03440408, -0.04329452, 0.02909167, -0.03866178]],
                [[0.00475122, 0.10786695, -0.02737187, 0.00830807]],
                [[-0.00274554, -0.0653871, -0.02701236, 0.04182423]]]
        result = GensimFastText(source=JSONFile("dataset/movies_info_reduced.json"),
                                preprocessor=NLTK(),
                                field_name="Genre").start_learning()
        for i, res in enumerate(result):
            self.assertEqual(list[i], res, "Fail in Doc {} - Vector = {}".format(str(i), res))
