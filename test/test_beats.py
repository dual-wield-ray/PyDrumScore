import unittest
import os
import importlib

from xmldiff import main

import export

CURRPATH = os.path.abspath(os.path.dirname(__file__))

class Test_1_bar(unittest.TestCase):

    def base_test_song(self, song_name):
        
        # Generate from the song script
        module_import_str = "test.songs." + song_name
        song_module = importlib.import_module(module_import_str)
        song = export.export_from_module(song_module)
        exported_name = song.metadata.workTitle

        # Get the generated xml, and the test data to compare
        test_data_path = os.path.join(CURRPATH, "data", exported_name + ".mscx")
        self.assertTrue(os.path.isfile(test_data_path), "Test data must exist")

        generated_data_path = os.path.join(CURRPATH, "_generated", exported_name + ".mscx")
        self.assertTrue(os.path.isfile(generated_data_path), "Generated data must exist")

        # Compare. For now we do a hard test; zero differences allowed!
        diff_res = main.diff_files(test_data_path, generated_data_path)

        # TODO, IMPORTANT: Super sketchy
        non_negligible_diff = []
        for d in diff_res:
            if hasattr(d, "node"):
                if "Style" in d.node \
                or "Part" in d.node \
                or "VBox" in d.node:
                    continue
            if hasattr(d, "target"):
                if "Style" in d.target \
                or "Part" in d.target \
                or "VBox" in d.target:
                    continue
            if hasattr(d, "tag"):
                if "show" in d.tag:
                    continue

            non_negligible_diff.append(d)

        self.assertFalse(non_negligible_diff, "Exported must be the same as generated.")

    # TODO: For now this is generates four quarter silences
    #       This is due to the measure "separators", revisit
    def test_silence_1b(self):
        self.base_test_song("song_silence")

    def test_money_beat_1b(self):
        self.base_test_song("song_money_beat")

    def test_rock_beat_1b(self):
        self.base_test_song("song_rock_beat")

    def test_shuffle_beat_1b(self):
        self.base_test_song("song_shuffle_beat")

if __name__ == '__main__':
    unittest.main()
