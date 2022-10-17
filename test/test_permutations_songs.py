import unittest
from test.test_base import Test_Base

class Test_Permutations(Test_Base):

    def test_bass_drum_permutations(self):
        self.base_test_song("bass_drum_permutations")

    def test_hihat_open_permutations(self):
        self.base_test_song("hihat_open_permutations")

if __name__ == '__main__':
    unittest.main()
