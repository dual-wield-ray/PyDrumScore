import unittest
import os

from xmldiff import main

import export

# Songs to test
import test.songs.song_money_beat as song_money_beat
import test.songs.song_rock_beat as song_rock_beat
import test.songs.song_rock_beat as song_shuffle_beat

CURRPATH = os.path.abspath(os.path.dirname(__file__))

class Test_1_bar(unittest.TestCase):

    def base_test_song(self, song_mod):
        
        # Generate from the song script
        song = export.export_from_module(song_mod)
        exported_name = song.metadata.workTitle

        # Get the generated xml, and the test data to compare
        test_data_path = os.path.join(CURRPATH, "data", exported_name + ".mscx")
        generated_data_path = os.path.join(CURRPATH, "_generated", exported_name + ".mscx")

        # Compare. For now we do a hard test; zero differences allowed!
        diff_res = main.diff_files(test_data_path, generated_data_path)
        self.assertFalse(diff_res, "Exported must be the same as generated.")

    def test_money_beat_1b(self):
        self.base_test_song(song_money_beat)

    def test_rock_beat_1b(self):
        self.base_test_song(song_rock_beat)

    def test_rock_beat_1b(self):
        self.base_test_song(song_shuffle_beat)

if __name__ == '__main__':
    unittest.main()
