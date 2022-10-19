import unittest
import os
import importlib

import xmldiff
from xmldiff import main

from drumscore.core import export

CURRPATH = os.path.abspath(os.path.dirname(__file__))

class TestBase(unittest.TestCase):

    def base_test_song(self, song_name):

        # Generate from the song script
        module_import_str = "drumscore.test.songs." + song_name
        song_module = importlib.import_module(module_import_str)
        export.export_from_module(song_module)
        exported_name = song_module.metadata.workTitle

        # Get the generated xml, and the test data to compare
        test_data_path = os.path.join(CURRPATH, "data", exported_name + ".mscx")
        self.assertTrue(os.path.isfile(test_data_path), "Test data must exist")

        generated_data_path = os.path.join(CURRPATH, "_generated", exported_name + ".mscx")
        self.assertTrue(os.path.isfile(generated_data_path), "Generated data must exist")

        diff_res = main.diff_files(
            generated_data_path, test_data_path,
            diff_options={'F': 0.5, 'ratio_mode': 'accurate'})

        # TODO: Still better, but far from perfect
        non_negligible_diff = []
        for d in diff_res:

            # Allow attrib diffs for now
            # TODO: Revisit
            if isinstance(d, (xmldiff.actions.InsertAttrib, \
                             xmldiff.actions.DeleteAttrib, \
                             xmldiff.actions.RenameAttrib)):
                continue

            # Allow text content diffs for now
            # TODO: Revisit
            if isinstance(d, (xmldiff.actions.UpdateTextIn, \
                             xmldiff.actions.UpdateTextAfter, \
                             xmldiff.actions.InsertComment)):
                continue

            # Allow node move only within same parent
            if isinstance(d, xmldiff.actions.MoveNode):
                node_str = d.node.rsplit("/",1)[0].split('[')[0]
                target_str = d.target.split('[')[0]
                if node_str == target_str:
                    continue

            def check_ignorable_in_str(s):
                # Ignore style diffs
                ignorable = ["Style", "Instrument", "Part", "VBox", "show"]
                for ign in ignorable:
                    if ign in s:
                        return True
                return False

            # Need to check
            if isinstance(d, xmldiff.actions.InsertNode):
                if check_ignorable_in_str(d.target) \
                or "show" in d.tag:
                    continue

            if isinstance(d, (xmldiff.actions.DeleteNode, \
                             xmldiff.actions.RenameNode, \
                             xmldiff.actions.MoveNode)):
                if check_ignorable_in_str(d.node):
                    continue

            # Test fail, we have bad diffs
            non_negligible_diff.append(d)

        self.assertFalse(non_negligible_diff, "Exported must be the same as generated.")
