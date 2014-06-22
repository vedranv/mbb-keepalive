from unittest.case import TestCase
import os
from mbbkeepalive.mbb import NMCliConList, Tele2TpoParser

__author__ = 'vedran'

test_files_dir = os.path.join(os.path.dirname(__file__), 'files')


class NmcliConListParseTest(TestCase):

    def test_con_list_parse(self):
        with open(os.path.join(test_files_dir, 'nmcli_con_list')) as f:
            input_ = f.read()

        nmcli = NMCliConList(input_)
        self.assertEqual(2, len(nmcli.interfaces))
        self.assertEqual(1, len(nmcli.gsm_interfaces))
        self.assertTrue(nmcli.has_gsm_interface())


class Tele2TpoParserTest(TestCase):

    def test_tpo_parse(self):
        with open(os.path.join(test_files_dir, 'tpo')) as f:
            output_ = f.read()
        parser = Tele2TpoParser(output_)
        self.assertEqual(18.69, parser.tpo['prepaid_remaining'])
        self.assertEqual(0, parser.tpo['promo_remaining'])
        self.assertEqual(1235, parser.tpo['option_remaining'])
