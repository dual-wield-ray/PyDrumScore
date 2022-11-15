"""
Test the command line interface features
"""

import unittest
from pydrumscore.core.export import export_from_filename

from pydrumscore.test.songs import song_silence

# pylint: disable = missing-function-docstring, missing-class-docstring
class TestCli(unittest.TestCase):

    # TODO: Can fail if songs are also contained in a local package build
    #       File discovery could be more robust

    ####### Should pass #######
    def test_name_without_extension(self):
        self.assertEqual(export_from_filename("song_silence"), 0)

    def test_name_with_extension(self):
        self.assertEqual(export_from_filename("song_silence.py"), 0)

    def test_name_with_path(self):
        full_path = song_silence.__file__
        self.assertEqual(export_from_filename(full_path), 0)

    def test_with_non_ascii(self):
        self.assertEqual(export_from_filename("song_accented_metadata"), 0)

    ####### Should fail #######
    def test_with_nothing(self):
        self.assertEqual(export_from_filename(""), -1)

    def test_with_garbage(self):
        self.assertEqual(export_from_filename("GarbageName!é3^`45"), -1)

    def test_with_capitalized_name(self):
        self.assertEqual(export_from_filename("song_silence".capitalize()), -1)

if __name__ == '__main__':
    unittest.main()
