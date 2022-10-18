import unittest
from drumscore.test.test_base import TestBase

class TestFullSongs(TestBase):

    def test_highway_to_hell(self):
        self.base_test_song("song_highway_to_hell")

if __name__ == '__main__':
    unittest.main()
