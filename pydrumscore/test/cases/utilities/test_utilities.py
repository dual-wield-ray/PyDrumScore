"""
Test features such as overhead text and tempo changes
"""
import unittest
from pydrumscore.test.test_base import TestBase

# pylint: disable = missing-function-docstring, missing-class-docstring


class TestUtilities(TestBase):
    def test_text_feature(self):
        self.base_test_song("song_text")
        self.base_test_song("song_text", use_musicxml=True)

    def test_tempo_feature(self):
        self.base_test_song("song_tempo_change")
        self.base_test_song("song_tempo_change", use_musicxml=True)


if __name__ == "__main__":
    unittest.main()
