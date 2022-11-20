"""
Test the command line interface features
"""

import unittest
from pydrumscore.test.test_base import TestBase

# pylint: disable = missing-function-docstring, missing-class-docstring
class TestCli(TestBase):

    def test_simple_change(self):
        self.base_test_song("time_sig_simple_change")

if __name__ == '__main__':
    unittest.main()
