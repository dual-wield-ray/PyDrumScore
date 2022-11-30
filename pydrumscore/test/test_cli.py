"""
Test the command line interface features
"""

import unittest
from pydrumscore.export import export_from_filename

from pydrumscore.test.songs import song_silence

# pylint: disable = missing-function-docstring, missing-class-docstring


class TestCli(unittest.TestCase):

    # Should pass
    def test_name_without_extension(self):
        self.assertEqual(export_from_filename("song_silence"), 0)

    def test_name_with_extension(self):
        self.assertEqual(export_from_filename("song_silence.py"), 0)

    def test_name_with_path(self):
        full_path = song_silence.__file__
        self.assertEqual(export_from_filename(full_path), 0)

    def test_with_non_ascii(self):
        self.assertEqual(export_from_filename("song_accented_metadata"), 0)

    # Should fail
    def test_with_no_filename(self):
        self.assertEqual(export_from_filename(""), -1)

    # TODO: Make these fail if the files don't exist (after test folders rework, #)
    def test_with_no_metadata(self):
        self.assertEqual(export_from_filename("song_no_metadata"), -1)

    def test_with_no_measures(self):
        self.assertEqual(export_from_filename("song_no_measures"), -1)

    def test_with_no_metadata_or_measures(self):
        self.assertEqual(export_from_filename("song_no_metadata_or_measures"), -1)

    def test_with_garbage(self):
        self.assertEqual(export_from_filename("GarbageName!é3^`45"), -1)

    def test_with_capitalized_name(self):
        self.assertEqual(export_from_filename("song_silence".capitalize()), -1)


if __name__ == "__main__":
    unittest.main()
