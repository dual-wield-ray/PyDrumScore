import unittest
from test.test_base import Test_Base

class Test_Full_Songs(Test_Base):

    def test_highway_to_hell(self):
        self.base_test_song("song_highway_to_hell")

if __name__ == '__main__':
    unittest.main()
