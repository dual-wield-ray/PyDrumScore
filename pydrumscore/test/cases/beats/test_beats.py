"""
Tests case for basic beats in the basic beats module.
"""

import unittest
from pydrumscore.test.test_base import TestBase

# pylint: disable = missing-function-docstring, missing-class-docstring


class TestBeats(TestBase):
    def test_silence_1b(self):
        self.base_test_song("song_silence")
        self.base_test_song("song_silence", use_musicxml=True)

    def test_bd_1_and_3(self):
        self.base_test_song("bd_1_and_3")
        self.base_test_song("bd_1_and_3", use_musicxml=True)

    def test_money_beat_1b(self):
        self.base_test_song("song_money_beat")
        self.base_test_song("song_money_beat", use_musicxml=True)

    def test_rock_beat_1b(self):
        self.base_test_song("song_rock_beat")
        self.base_test_song("song_rock_beat", use_musicxml=True)

    def test_rock_beat_wopen_1b(self):
        self.base_test_song("song_rock_beat_wopen")
        self.base_test_song("song_rock_beat_wopen", use_musicxml=True)

    def test_shuffle_beat_1b(self):
        self.base_test_song("song_shuffle_beat")
        self.base_test_song("song_shuffle_beat", use_musicxml=True)

    def test_flam_1b(self):
        self.base_test_song("flam_1b")

    def test_ghost_1b(self):
        self.base_test_song("ghost_1b")

    def test_sextuplets_1b(self):
        self.base_test_song("sextuplets")

    def test_money_beat_1b_accents(self):
        self.base_test_song("song_money_beat_accents")


if __name__ == "__main__":
    unittest.main()
