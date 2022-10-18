import unittest
from drumscore.test.test_base import TestBase

class TestBeats(TestBase):

    # TODO: For now this is generates four quarter silences
    #       This is due to the measure "separators", revisit
    def test_silence_1b(self):
        self.base_test_song("song_silence")

    def test_money_beat_1b(self):
        self.base_test_song("song_money_beat")

    def test_rock_beat_1b(self):
        self.base_test_song("song_rock_beat")

    def test_rock_beat_wopen_1b(self):
        self.base_test_song("song_rock_beat_wopen")

    def test_shuffle_beat_1b(self):
        self.base_test_song("song_shuffle_beat")

    def test_flam_1b(self):
        self.base_test_song("flam_1b")

if __name__ == '__main__':
    unittest.main()
