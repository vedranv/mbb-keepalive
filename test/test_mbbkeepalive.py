from unittest.case import TestCase
import os
from mbbkeepalive.mbb import NMCliConList

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