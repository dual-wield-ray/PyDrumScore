"""
Test the command line interface features
"""

import unittest
from pydrumscore.test.test_base import TestBase
from pydrumscore.core.export import export_from_filename

# pylint: disable = missing-function-docstring, missing-class-docstring
class TestCli(TestBase):

    ####### Should pass #######
    def test_simple_change(self):
        self.base_test_song("time_sig_simple_change")

    ####### Should fail #######
    # def test_with_nothing(self):
    #     self.assertEqual(export_from_filename(""), -1)

    # def test_with_garbage(self):
    #     self.assertEqual(export_from_filename("GarbageName!é3^`45"), -1)

    # def test_with_capitalized_name(self):
    #     self.assertEqual(export_from_filename("song_silence".capitalize()), -1)

if __name__ == '__main__':
    unittest.main()
