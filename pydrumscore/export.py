"""
Exporter entry points for the pydrumscore package.
"""

# Built-in modules
import os
import sys
import importlib
import importlib.util
import logging
from pathlib import Path
from types import ModuleType
from typing import Optional, Union
from copy import deepcopy
from enum import Enum

# External modules

# Local modules
import pydrumscore
from pydrumscore import Measure
from config_handling import read_config


class ExportFormat(Enum):
    MUSICXML = 0
    MSCX = 1
    MSCZ = 2

def export_from_module(mod: ModuleType, export_in: ExportFormat = ExportFormat.MUSICXML, exp_folder_override: Optional[str] = None):
    """
    Exports the song module given as argument.
    This module must have its global "metadata" and "measures"
    objects already filled at call time.

    Args:
        mod (ModuleType): The song module with generation completed
    """

    logging.getLogger(__name__).info(
        "Exporting song '%s' to '%s'.", mod.__name__.split(".")[-1], read_config().export_folder
    )

    # Important: all user-filled objects are *copied* here
    #            Otherwise they could be modified by the exporter
    if not hasattr(mod, "metadata"):
        logging.getLogger(__name__).error(
            "Song module does not have metadata associated. Make sure to fill the 'metadata' object."
        )
        return -1
    metadata = deepcopy(mod.metadata)

    if not hasattr(mod, "measures"):
        logging.getLogger(__name__).error(
            "Song module does not have measures associated. Make sure to fill the 'measures' list."
        )
        return -1

    # Uses the refcounts after the import to determine if a measure had more references that the others
    # This is to try to warn the user to not use direct assignements for creating measures, because they work by reference in Python
    # Instead, only copies should be used.
    # TODO: This doesn't really work... to avoid this problem entirely, one would need to wrap all measures in a Song class
    #       But this would break simplicity a good deal.
    common_ref_count = 0
    for i, m in enumerate(mod.measures):
        ref_count = sys.getrefcount(m)
        if common_ref_count and ref_count != common_ref_count:
            logging.getLogger(__name__).warning(
                "Measure %s might have been modified incorrectly. Make sure to always create Measures using the 'Measure()' constructor.",
                i,
            )
        else:
            common_ref_count = ref_count

    # Copy all measures to not modify user data
    measures = [Measure(m) for m in mod.measures]

    if export_in == ExportFormat.MUSICXML:
        from export_musicxml import export_song
        export_song(metadata, measures, exp_folder_override)
    elif export_in == ExportFormat.MSCX:
        from export_musescore import export_song
    elif export_in == ExportFormat.MSCZ:
        logging.getLogger(__name__).info("Mscz coming soon!")
        return 0

    export_song(metadata, measures, exp_folder_override)

    logging.getLogger(__name__).info("Export completed successfully.")

    return 0


def import_song_module_from_filename(filename: str) -> Union[ModuleType, None]:
    """
    Imports a song module provided as argument, and returns it.
    Can either be a full file path, or only the file name

    Example for a song file "my_song.py":
        import_song_module_from_filename("my_song")
    """

    # Info needed to build the module import str
    found_rel_path = ""
    found_filename = ""
    root_dir = Path(".")

    # Case user gave full path arg
    if os.path.exists(filename):
        found_rel_path = os.path.split(os.path.relpath(filename, root_dir))[0]
        found_filename = os.path.basename(filename).rsplit(".", 1)[0]

    # Case user gave file name only, need to search for relpath
    else:

        def strip_extension(filename):
            return filename.rsplit(".", 1)[0]

        found_filename = strip_extension(filename)

        def find_relpath_by_walk():
            for folder, dirnames, files in os.walk(root_dir, topdown=True):

                # Prune all dirs with invalid names
                dirnames = [d for d in dirnames if not d.startswith((".", "_"))]

                for f in files:
                    if found_filename == strip_extension(f):
                        return os.path.relpath(folder, root_dir)

            return None

        if found_filename:
            found_rel_path = find_relpath_by_walk()
            if found_rel_path:
                assert found_filename
                logging.getLogger(__name__).info(
                    "Found file to export in location: %s", found_rel_path
                )

    if not found_rel_path or not found_filename:
        logging.getLogger(__name__).error(
            "Could not find file '%s' given as argument.", filename
        )
        return None

    # Trim the relpath in case the module is used in a virtual environment (thus contains venv/site-packages...)
    if "site-packages" in found_rel_path:
        found_rel_path = "pydrumscore" + found_rel_path.split("pydrumscore")[-1]

    # Use result to craft module str and begin export
    def build_module_str(filename, relpath):
        if relpath == ".":
            return filename
        import_str = ".".join(relpath.split(os.sep))
        import_str = ".".join([import_str, filename])
        return import_str

    # Result string to import song module
    # Ex. "pydrumscore.test.songs.my_song"
    assert found_filename and found_rel_path
    module_import_str = build_module_str(found_filename, found_rel_path)

    pydrumscore.set_time_signature("4/4")

    assert importlib.util.find_spec(module_import_str), "Could not import module."
    song_module = importlib.import_module(module_import_str)

    return song_module


def export_from_filename(filename: str, export_in: ExportFormat = ExportFormat.MUSICXML, exp_folder_override: Optional[str] = None) -> int:
    """
    Exports a song file provided as argument.
    Can either be a full file path, or only the file name

    Example for a song file "my_song.py":
        export_from_filename("my_song")
    """
    song_module = import_song_module_from_filename(filename)
    if not song_module:
        return -1

    return export_from_module(song_module, export_in, exp_folder_override)


def main():
    """
    Exports a song file provided by command line argument.
    Can either be a full file path, or only the file name

    Example for a song file "my_song.py":
        pydrumscore my_song
    """

    # Allows importing local, user-created modules with the "name only" format (without python -m)
    sys.path.append(os.getcwd())

    if len(sys.argv) < 2:
        print("Must give file name as argument.")
        return -1

    return export_from_filename(sys.argv[1])
