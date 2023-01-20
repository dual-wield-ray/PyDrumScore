"""
Test reference real-life, full songs
"""

import unittest
from pydrumscore.test.test_base import TestBase

# pylint: disable = missing-function-docstring, missing-class-docstring


class TestFullSongs(TestBase):
    def test_highway_to_hell(self):
        # self.base_test_song("song_highway_to_hell")
        self.base_test_song("song_highway_to_hell", use_musicxml=True)

    def test_king_nothing(self):
        # self.base_test_song("song_king_nothing")
        self.base_test_song("song_king_nothing", use_musicxml=True)

    def test_uptown_funk(self):
        # self.base_test_song("song_uptown_funk")
        self.base_test_song("song_uptown_funk", use_musicxml=True)


if __name__ == "__main__":
    unittest.main()
