"""
Test the command line interface features
"""

import unittest
from pydrumscore.test.test_base import TestBase

# pylint: disable = missing-function-docstring, missing-class-docstring


class TestTimeSignatures(TestBase):
    def test_simple_change(self):
        self.base_test_song("time_sig_simple_change")

    def test_eight_note_denominator(self):
        self.base_test_song("time_eighth_note_denominator")


if __name__ == "__main__":
    unittest.main()
