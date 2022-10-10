import unittest
import os

from xmldiff import main

import exporter

import example_song

class Test_1_bar(unittest.TestCase):

    def test_money_beat(self):

        exporter.export_from_module(example_song)

        currPath = os.path.abspath(os.path.dirname(__file__))

        test_data_path = os.path.join(currPath, "data", "MoneyBeat_1b.mscx")
        generated_data_path = os.path.join(currPath, "..", "_output", "MoneyBeat_1b.mscx")

        diff_res = main.diff_files(test_data_path, generated_data_path)
        self.assertFalse(diff_res)

if __name__ == '__main__':
    unittest.main()
