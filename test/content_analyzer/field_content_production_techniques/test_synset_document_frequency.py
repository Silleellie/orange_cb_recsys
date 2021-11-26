from unittest import TestCase
import os

from orange_cb_recsys.content_analyzer.content_representation.content import FeaturesBagField
from orange_cb_recsys.content_analyzer.raw_information_source import JSONFile
from orange_cb_recsys.content_analyzer.field_content_production_techniques import PyWSDSynsetDocumentFrequency
from test import dir_test_files

file_path = os.path.join(dir_test_files, "movies_info_reduced.json")


class TestSynsetDocumentFrequency(TestCase):
    def test_produce_content(self):
        technique = PyWSDSynsetDocumentFrequency()

        features_bag_list = technique.produce_content("Plot", [], JSONFile(file_path))

        self.assertEqual(len(features_bag_list), 20)
        self.assertIsInstance(features_bag_list[0], FeaturesBagField)
