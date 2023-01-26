"""
Contains the base class test class.
"""

# Built-in modules
import unittest
import os
import inspect

# External modules
import xmldiff
from xmldiff import main

# Local modules
from pydrumscore import export


class TestBase(unittest.TestCase):
    """
    Base class for test cases that use a specific song file,
    export it, and compare the result to a reference data file.
    """

    def base_test_song(self, song_name: str, use_musicxml=False) -> None:
        """Exports the song of the given name and does a diff to compare it to the
        reference data. Certain divergence are allowed (such as style) while any
        change in core content fails the test.

        :param song_name: Name of the song for this test case
        """

        export_in = export.ExportFormat.MSCX if not use_musicxml else export.ExportFormat.MUSICXML

        caller_dirname = os.path.dirname(inspect.stack()[1].filename)
        test_export_folder = os.path.join(caller_dirname, "_generated")

        # Generate from the song script
        ext = ".mscx" if not use_musicxml else ".musicxml"
        song_module = export.import_song_module_from_filename(song_name)
        exported_filename = song_module.metadata.workTitle + ext
        export.export_from_module(song_module, export_in, test_export_folder)

        # Get the generated xml, and the test data to compare
        test_data_path = os.path.join(
            caller_dirname,
            "data",
            exported_filename,
        )
        self.assertTrue(os.path.isfile(test_data_path), "Test data must exist")

        generated_data_path = os.path.join(test_export_folder, exported_filename)

        self.assertTrue(
            os.path.isfile(generated_data_path), "Generated data must exist"
        )

        diff_ok = self.diff_mscx(test_data_path, generated_data_path) if not use_musicxml else self.diff_musicxml(test_data_path, generated_data_path)

        self.assertTrue(diff_ok, "Exported must be the same as generated.")

    def diff_mscx(self, test_data_path, generated_data_path):

        diff_res = main.diff_files(
            test_data_path,
            generated_data_path,
            diff_options={"F": 0.5, "ratio_mode": "accurate"},
        )

        non_negligible_diff = []
        for d in diff_res:
            # Allow attribute diffs for now
            if isinstance(
                d,
                (
                    xmldiff.actions.InsertAttrib,
                    xmldiff.actions.DeleteAttrib,
                    xmldiff.actions.RenameAttrib,
                ),
            ):
                continue

            # Allow text content diffs for now
            if isinstance(
                d,
                (
                    xmldiff.actions.UpdateTextIn,
                    xmldiff.actions.UpdateTextAfter,
                    xmldiff.actions.InsertComment,
                ),
            ):
                continue

            # Allow node move only within same parent
            if isinstance(d, xmldiff.actions.MoveNode):
                node_str = d.node.rsplit("/", 1)[0].split("[")[0]
                target_str = d.target.split("[")[0]
                if node_str == target_str:
                    continue

            def check_ignorable_in_str(s):
                # Ignore style diffs
                ignorable = [
                    "Style",
                    "Instrument",
                    "Part",
                    "VBox",
                    "show",
                    "programRevision",
                    "programVersion",
                ]
                for ign in ignorable:
                    if ign in s:
                        return True
                return False

            # Node insertion, rename, or deletion => Need to check
            if isinstance(d, xmldiff.actions.InsertNode):
                if check_ignorable_in_str(d.target) or check_ignorable_in_str(d.tag):
                    continue

            if isinstance(
                d,
                (
                    xmldiff.actions.DeleteNode,
                    xmldiff.actions.RenameNode,
                    xmldiff.actions.MoveNode,
                ),
            ):
                if check_ignorable_in_str(d.node):
                    continue

            # Reach here => Test fail, we have bad diff
            non_negligible_diff.append(d)

        return len(non_negligible_diff) == 0


    def diff_musicxml(self, test_data_path, generated_data_path):

        diff_res = main.diff_files(
            test_data_path,
            generated_data_path,
            diff_options={"F": 0.05}
        )

        non_negligible_diff = []
        for d in diff_res:
            # Allow attribute diffs for now
            if isinstance(
                d,
                (
                    xmldiff.actions.InsertAttrib,
                    xmldiff.actions.DeleteAttrib,
                    xmldiff.actions.RenameAttrib,
                ),
            ):
                continue

            # Allow text content diffs for now
            if isinstance(
                d,
                (
                    xmldiff.actions.UpdateTextIn,
                    xmldiff.actions.UpdateTextAfter,
                    xmldiff.actions.InsertComment,
                ),
            ):
                continue

            # Allow node move only within same parent
            if isinstance(d, xmldiff.actions.MoveNode):
                node_str = d.node.rsplit("/", 1)[0].split("[")[0]
                target_str = d.target.split("[")[0]
                if node_str == target_str:
                    continue

            def check_ignorable_in_str(s):
                print(s)
                # Ignore style diffs
                ignorable = [
                    "divisions",
                    "line"
                ]
                for ign in ignorable:
                    if ign in s:
                        return True
                return False

            # Node insertion, rename, or deletion => Need to check
            if isinstance(d, xmldiff.actions.InsertNode):
                if check_ignorable_in_str(d.target) or check_ignorable_in_str(d.tag):
                    continue

            if isinstance(
                d,
                (
                    xmldiff.actions.DeleteNode,
                    xmldiff.actions.RenameNode,
                    xmldiff.actions.MoveNode,
                ),
            ):
                if check_ignorable_in_str(d.node):
                    continue

            # Reach here => Test fail, we have bad diff
            non_negligible_diff.append(d)

        return len(non_negligible_diff) == 0
