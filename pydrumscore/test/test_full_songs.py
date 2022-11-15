"""
Test reference real-life, full songs
"""

import unittest
from pydrumscore.test.test_base import TestBase

# pylint: disable = missing-function-docstring, missing-class-docstring
class TestFullSongs(TestBase):

    def test_highway_to_hell(self):
        self.base_test_song("song_highway_to_hell")

    def test_king_nothing(self):
        self.base_test_song("song_king_nothing")

    def test_uptown_funk(self):
        self.base_test_song("song_uptown_funk")

if __name__ == '__main__':
    unittest.main()
