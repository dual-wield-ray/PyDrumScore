"""
Contains the base class test class.
"""

# Built-in modules
import unittest
import os
import importlib

# External modules
import xmldiff
from xmldiff import main

# Local modules
from pydrumscore.core import export

CURRPATH = os.path.abspath(os.path.dirname(__file__))

class TestBase(unittest.TestCase):
    """
    Base class for test cases that use a specific song file,
    export it, and compare the result to a reference data file.
    """

    def base_test_song(self, song_name: str) -> None:
        """Exports the song of the given name and does a diff to compare it to the
        reference data. Certain divergence are allowed (such as style) while any
        change in core content fails the test.

        :param song_name: Name of the song for this test case
        """

        export.EXPORT_FOLDER = "pydrumscore/test/_generated"

        # Generate from the song script
        export.export_from_filename(song_name)

        # TODO: Remove. Get exported name from module itself
        module_import_str = "pydrumscore.test.songs." + song_name
        song_module = importlib.import_module(module_import_str)
        exported_name = song_module.metadata.workTitle
        # END TODO

        # Get the generated xml, and the test data to compare
        test_data_path = os.path.join(CURRPATH, "data", exported_name + ".mscx")
        self.assertTrue(os.path.isfile(test_data_path), "Test data must exist")

        generated_data_path = os.path.join(CURRPATH, "_generated", exported_name + ".mscx")

        self.assertTrue(os.path.isfile(generated_data_path), "Generated data must exist")

        diff_res = main.diff_files(
            test_data_path, generated_data_path,
            diff_options={'F': 0.5, 'ratio_mode': 'accurate'})

        non_negligible_diff = []
        for d in diff_res:

            # Allow attrib diffs for now
            if isinstance(d, (xmldiff.actions.InsertAttrib, \
                             xmldiff.actions.DeleteAttrib, \
                             xmldiff.actions.RenameAttrib)):
                continue

            # Allow text content diffs for now
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
                ignorable = ["Style", "Instrument", "Part", "VBox", "show", "programRevision", "programVersion"]
                for ign in ignorable:
                    if ign in s:
                        return True
                return False

            # Need to check
            if isinstance(d, xmldiff.actions.InsertNode):
                if check_ignorable_in_str(d.target) \
                or check_ignorable_in_str(d.tag):
                    continue

            if isinstance(d, (xmldiff.actions.DeleteNode, \
                             xmldiff.actions.RenameNode, \
                             xmldiff.actions.MoveNode)):
                if check_ignorable_in_str(d.node):
                    continue

            # Test fail, we have bad diffs
            non_negligible_diff.append(d)

        self.assertFalse(non_negligible_diff, "Exported must be the same as generated.")
