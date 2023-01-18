"""
Exporting functionalities for the pydrumscore package.
Currently only supports exporting in the uncompressed Musescore format,
.mscx. Export in MusicXML and .mscz (zipped musescore) is upcoming.
"""

# Built-in modules
import os
import sys
import importlib
import importlib.util
import logging
from dataclasses import dataclass
from pathlib import Path
from xml.dom import minidom
from collections import namedtuple
from types import ModuleType
from typing import List, Tuple, Optional, Union
from copy import deepcopy
from configparser import ConfigParser
from fractions import Fraction

# External modules
from from_root import from_root
import setuptools_scm

# Local modules
import pydrumscore
from pydrumscore import Metadata, Measure

# Exporter uses api with access to all private members (like a C++ "friend" class)
# pylint: disable=protected-access

# Get version from setuptools' source control
VERSION_MODULE_NAME = "pydrumscore.__version__"
pydrumscore_version = ""  # pylint: disable=invalid-name
if importlib.util.find_spec(VERSION_MODULE_NAME):
    # If using source distribution (or if package was locally built) get version from it
    version_mod = importlib.import_module(VERSION_MODULE_NAME)
    pydrumscore_version = version_mod.version
else:
    pydrumscore_version = setuptools_scm.get_version(root="../", relative_to=__file__)

# Read config file
# Note: Due to a bug, it's not possible to get MuseScore version info from CLI on Windows
#       Perhaps revisit sometime if it has been done, or do it ourselves...
user_configur = ConfigParser()
default_configur = ConfigParser()

config_root = from_root()
if config_root.stem != "pydrumscore":
    # Work around apparent issue in "from_root" where cloned and pip installed setup differ by one level
    config_root = config_root / "pydrumscore"

default_configur.read(config_root / "default_config.ini")

config_path = Path("config.ini")
if Path.exists(config_path):
    user_configur.read(config_path)


def _get_config_option(section: str, option: str):
    assert default_configur.has_option(section, option)

    configur = user_configur if user_configur.has_option(section, option) else default_configur
    return configur.get(section, option)


MS_VERSION = _get_config_option("msversion", "msversion")
PROGRAM_VERSION = _get_config_option("msversion", "program_version")
PROGRAM_REVISION = _get_config_option("msversion", "program_revision")
EXPORT_FOLDER = _get_config_option("export", "export_folder")


@dataclass
class NoteDef:
    # pylint: disable=too-few-public-methods

    """Defines how instruments on the drumset are represented in the XML."""
    display_step: str
    display_octave: str
    instrument_id: str
    stem: str = "up"
    notehead: str = ""

    articulation: str = ""
    flam = False
    ghost = False


NOTEDEFS = {
    "snare": NoteDef("C", "5", "P1-I39"),

    #"snare_ghost": NoteDef("38", "16", ghost=True),

    "hi_hat": NoteDef("G", "5", "P1-I43", notehead="x", articulation="brassMuteClosed"),
    "bass_drum": NoteDef("F", "4", "P1-I37"),


    #"floor_tom": NoteDef("41", "13"),
    #"mid_tom": NoteDef("45", "17"),
    #"high_tom": NoteDef("47", "19"),
    #"cross_stick": NoteDef("37", "21", head="cross"),
    #"crash1": NoteDef("49", "21", head="cross"),
    #"hi_hat_open": NoteDef("46", "12", head="cross", articulation="stringsHarmonic"),
    #"ride": NoteDef("51", "11", head="cross"),
    #"ride_bell": NoteDef("53", "13", head="diamond"),
    #"flam_snare": NoteDef("38", "16", flam=True),
    #"hi_hat_foot": NoteDef("44", "22", head="cross", stem_direction="down"),
}


def export_song(metadata: Metadata, measures: List[Measure]):
    """
    Exports the song given as argument as an mscx file (xml).

    :param metadata: Copy of the 'metadata' object filled by the user. Must exist.
    :param measures: Copy of the 'measures' object filled by the user. Must contain at least one measure.

    """

    assert metadata, "Metadata cannot be 'None'."
    assert measures, "Measures cannot be empty."

    # Create DOCTYPE
    imp = minidom.getDOMImplementation('')
    doctype = imp.createDocumentType('score-partwise', '-//Recordare//DTD MusicXML 4.0 Partwise//EN', 'http://www.musicxml.org/dtds/partwise.dtd')

    # Create root document
    root = minidom.Document()
    root.insertBefore(doctype, root.documentElement)
    xml = root.createElement("score-partwise")
    xml.setAttribute("version", "4.0")  # TODO: Check what version is needed
    root.appendChild(xml)

    def add_xml_elem(
        name: str,
        parent: minidom.Element,
        attr: Optional[List[Tuple[str, str]]] = None,
        inner_txt: Optional[str] = None,
        insert_before: Optional[minidom.Element] = None,
    ) -> Union[minidom.Element, None]:

        e = root.createElement(name)

        if attr is None:
            attr = []

        for attr_pair in attr:
            e.setAttribute(attr_pair[0], attr_pair[1])

        # Note: Setting "" for inner_txt sets the empty str as text
        #       Helps to reduce diffs in xml output (<tag></tag> vs. <tag/>)
        if inner_txt is not None:
            e.appendChild(root.createTextNode(inner_txt))

        # Give the option to insert at specific place
        # For Musescore, *order matters*, so check tests if changing it
        if insert_before is not None:
            for c in parent.childNodes:
                if c is insert_before:
                    parent.insertBefore(e, c)
                    return e
            assert False, (
                "Could not prepend element "
                + e.nodeName
                + " to "
                + insert_before.nodeName
                + ", because the later is missing in children. Check that parent node really owns both."
            )
        else:
            # Order not important, just append to end
            parent.appendChild(e)

        return e

    work = add_xml_elem("work", xml)
    add_xml_elem("work-title", work, inner_txt=metadata.workTitle)

    identification = add_xml_elem("identification", xml)
    encoding = add_xml_elem("encoding", identification)
    add_xml_elem("software", encoding, inner_txt="PyDrumScore")  # TODO: Add version?
    #add_xml_elem("encoding-data", encoding, "")  # TODO?
    add_xml_elem("supports", encoding, attr=[("element","accidental"), ("type", "yes")])
    add_xml_elem("supports", encoding, attr=[("element","beam"), ("type", "yes")])
    add_xml_elem("supports", encoding, attr=[("element","print"), ("attribute", "new-page"), ("type", "no")])
    add_xml_elem("supports", encoding, attr=[("element","print"), ("attribute", "new-system"), ("type", "no")])
    add_xml_elem("supports", encoding, attr=[("element","stem"), ("type", "yes")])

    xml_part_filepath = str(Path(from_root(__file__).parent, "refxml", "PartXML_MusicXML.xml"))
    xml.appendChild(minidom.parse(xml_part_filepath).firstChild)




    # TODO: Make sure all Metadata is used and supported
    #metadata.mscVersion = MS_VERSION
    #metadata.pydrumscoreVersion = pydrumscore_version
    #for tag in Metadata._ALL_METADATA_TAGS:
    #    add_xml_elem("metaTag", score, [("name", tag)], inner_txt=getattr(metadata, tag))


    # Song content export starts here

    staff = add_xml_elem("part", xml, attr=[("id", "P1")])

    # All measures are pre-formatted for export
    # Any modifications is forbidden past this point
    for m in measures:
        m._pre_export()

    # Export context; all the stuff that is not
    # related to a single measure, but instead persists
    # over time and is needed for logic
    is_hh_open = False
    curr_time_sig_str = ""
    is_beam_started = False


    for m_idx, m in enumerate(measures):

        measure = add_xml_elem("measure", staff, attr=[("number", str(m_idx+1))])
        attributes = add_xml_elem("attributes", measure)
        # add_xml_elem("divisions", attributes, inner_txt="2")
        key = add_xml_elem("key", attributes)
        add_xml_elem("fifths", key, inner_txt="0")


        #if m.dynamic:
        #    dynamic = add_xml_elem("Dynamic", voice)
        #    add_xml_elem("subtype", dynamic, inner_txt=m.dynamic)

        #if m.text:
        #    sys_text = add_xml_elem("SystemText", voice)
        #    add_xml_elem("text", sys_text, inner_txt=m.text)

        #if m.has_line_break:
        #    lyt_break = add_xml_elem("LayoutBreak", measure)
        #    add_xml_elem("subtype", lyt_break, inner_txt="line")

        assert m._time_sig
        if m._time_sig != curr_time_sig_str:
            curr_time_sig_str = m._time_sig
            split_sig = m._time_sig.split("/")
            assert len(split_sig) == 2

            timesig = add_xml_elem("time", attributes)
            add_xml_elem("beats", timesig, inner_txt=split_sig[0])
            add_xml_elem("beat-type", timesig, inner_txt=split_sig[1])

        clef = add_xml_elem("clef", attributes)
        add_xml_elem("sign", clef, inner_txt="percussion")
        add_xml_elem("line", clef, inner_txt="2")

        # Note: Displaying the note symbol is tricky because the ref
        #       xml is malformed, and blocked by xml minidom.
        #       We might need to convert to ElementTree to make it work...
        #
        #       The reference xml does <text><sym>metNoteQuarterUp</sym> = 10</text>
        #       But, pasting that string results in the <> symbols being interpreted
        #       as regular chars. Meanwhile, parsing that string from code throws.
        #       So at the moment, we just add 'bpm' instead...
        #if m.tempo:
        #    tempo = add_xml_elem("Tempo", voice)
        #    add_xml_elem("tempo", tempo, inner_txt=str(m.tempo / 60.0))
        #    add_xml_elem("followText", tempo, inner_txt="1")
        #    add_xml_elem("text", tempo, inner_txt=str(m.tempo) + " bpm")

        all_times = m._get_combined_times()

        # Handle repeat symbol
        #if len(all_times) and not m.no_repeat and m_idx != 0 and m == measures[m_idx - 1]:  # Don't use for empty measures
        #    repeat = add_xml_elem("RepeatMeasure", voice)
        #    add_xml_elem("durationType", repeat, inner_txt="measure")
        #    add_xml_elem("duration", repeat, inner_txt=curr_time_sig_str)
        #    continue

        all_times += m._separators  # Add separators
        all_times = list(set(all_times))  # Remove duplicates
        all_times.sort()  # Read from left to right in time

        # Counts how many chords/rests are left to complete tuplet
        # Set at first note, decreased after each and closed at 0
        tuplet_counter = 0

        for i, _ in enumerate(all_times):

            def calc_note_dur(notes: List[Fraction]):

                # Check if note on this time
                if curr_time not in notes:
                    return 0  # No note right now

                # Use gap between curr time and next time
                # We don't want longer than a quarter note dur for non-rests
                return min(until_next, 1)

            curr_time = all_times[i]
            next_time = m._get_next_time(all_times, i)
            until_next = next_time - curr_time

            all_durs = {}
            for p in m._used_pieces:
                dur = calc_note_dur(getattr(m, p))
                if dur:
                    all_durs[p] = dur

            assert 0 not in all_durs.values()

            # If note, stems are connected => shortest becomes value of all
            # Rests fill the value of the gap
            is_rest = not all_durs
            chord_dur = min(all_durs.values()) if not is_rest else until_next

            DurationXML = namedtuple("DurationXML", ["durationType", "isTuplet", "isDotted"])

            def get_duration_xml(dur):

                dotted = False  # TODO: Find way to not dot *everything* in the chord...
                tuplet = False
                dur_str = ""
                if dur == (m._end - 1) and is_rest:
                    dur_str = "measure"
                elif dur == 4 and is_rest:
                    dur_str = "whole"
                elif dur == 3 and is_rest:
                    dur_str = "half"
                    dotted = True
                elif dur == 2 and is_rest:
                    dur_str = "half"
                elif dur == 1:
                    dur_str = "quarter"
                elif dur == Fraction(3, 4):
                    dur_str = "eighth"
                    dotted = True
                elif dur == Fraction(1, 2):
                    dur_str = "eighth"
                elif dur == Fraction(1, 4):
                    dur_str = "16th"
                elif dur == Fraction(1, 3):
                    tuplet = True
                    dur_str = "eighth"
                elif dur == Fraction(2, 3):
                    tuplet = True
                    dur_str = "quarter"
                elif dur == Fraction(1, 6):
                    tuplet = True
                    dur_str = "16th"

                assert dur_str != "", "Invalid note duration '" + str(dur) + "'."

                return DurationXML(dur_str, tuplet, dotted)

            dur_xml = get_duration_xml(chord_dur)

            # Handle tuplet header
            # if dur_xml.isTuplet and tuplet_counter == 0:
            #     tuplet = add_xml_elem("Tuplet", voice)

            #     tuplet_dur = round(1.0 / chord_dur)  # ex. 3 for triplet
            #     normal_dur_str = "2" if tuplet_dur == 3 else "4" if tuplet_dur == 6 else "8"

            #     add_xml_elem("normalNotes", tuplet, inner_txt=normal_dur_str)
            #     add_xml_elem("actualNotes", tuplet, inner_txt=str(tuplet_dur))
            #     add_xml_elem("baseNote", tuplet, inner_txt=dur_xml.durationType)
            #     number = add_xml_elem("Number", tuplet)
            #     add_xml_elem("style", number, inner_txt="Tuplet")
            #     add_xml_elem("text", number, inner_txt=str(tuplet_dur))

            #     # Init tuplet counter
            #     tuplet_counter = tuplet_dur

            # Handle rest (not part of "Chord" xml block)
            # if is_rest:
            #     rest = add_xml_elem("Rest", voice)
            #     if dur_xml.isTuplet:
            #         add_xml_elem("BeamMode", rest, inner_txt="mid")
            #     if dur_xml.isDotted:
            #         add_xml_elem("dots", rest, inner_txt="1")  # Must be before durationType!
            #     add_xml_elem("durationType", rest, inner_txt=dur_xml.durationType)
            #     if dur_xml.durationType == "measure":
            #         add_xml_elem("duration", rest, inner_txt=curr_time_sig_str)

            # Write chord (non-rest group of notes)
            if True:

                #if dur_xml.isDotted:
                #    add_xml_elem("dots", chord, inner_txt="1")

                #add_xml_elem("durationType", chord, inner_txt=dur_xml.durationType)

                #accent_chord = all_durs.get("accent") is not None
                #if accent_chord:
                #    art = add_xml_elem("Articulation", chord)
                #    add_xml_elem("subtype", art, inner_txt="articAccentAbove")
                #    add_xml_elem("anchor", art, inner_txt="3")

                #stem_dir = add_xml_elem("StemDirection", chord, inner_txt="up")

                def add_note(measure, notedef: NoteDef, is_first_note: bool, beam_started: bool):

                    # If flam, add little note before main note
                    # if notedef.flam:
                    #     acc_chord = add_xml_elem("Chord", voice, insert_before=chord)
                    #     acc_note = add_xml_elem("Note", acc_chord)
                    #     add_xml_elem(
                    #         "durationType",
                    #         acc_chord,
                    #         inner_txt="eighth",
                    #         insert_before=acc_note,
                    #     )
                    #     add_xml_elem("acciaccatura", acc_chord, insert_before=acc_note)
                    #     spanner = add_xml_elem("Spanner", acc_note, attr=[("type", "Tie")])
                    #     add_xml_elem("Tie", spanner, inner_txt="\n")
                    #     next_e = add_xml_elem("next", spanner)
                    #     add_xml_elem("location", next_e, inner_txt="\n")
                    #     add_xml_elem("pitch", acc_note, inner_txt=notedef.pitch)
                    #     add_xml_elem("tpc", acc_note, inner_txt=notedef.tpc)

                    # if notedef.articulation:
                    #     if notedef is NOTEDEFS["hi_hat"] and is_hh_open \
                    #         or notedef is NOTEDEFS["hi_hat_open"] and not is_hh_open:
                    #         art = add_xml_elem("Articulation", chord, insert_before=stem_dir)
                    #         add_xml_elem("subtype", art, inner_txt=notedef.articulation)
                    #         add_xml_elem("anchor", art, inner_txt="3")

                    # Main note
                    note = add_xml_elem("note", measure)

                    # Connect flam's little note with main
                    # if notedef.flam:
                    #     spanner = add_xml_elem("Spanner", note, attr=[("type", "Tie")])
                    #     prev_e = add_xml_elem("prev", spanner)
                    #     location = add_xml_elem("location", prev_e)
                    #     add_xml_elem("grace", location, inner_txt="0")

                    #if notedef.ghost:
                    #    symbol_l = add_xml_elem("Symbol", note)
                    #    add_xml_elem("name", symbol_l, inner_txt="noteheadParenthesisLeft")
                    #    symbol_r = add_xml_elem("Symbol", note)
                    #    add_xml_elem("name", symbol_r, inner_txt="noteheadParenthesisRight")

                    if not is_first_note:
                        add_xml_elem("chord", note)

                    unpitched = add_xml_elem("unpitched", note)
                    add_xml_elem("display-step", unpitched, inner_txt=notedef.display_step)
                    add_xml_elem("display-octave", unpitched, inner_txt=notedef.display_octave)

                    add_xml_elem("duration", note, inner_txt="1")
                    add_xml_elem("instrument", note, attr=[("id", notedef.instrument_id)])
                    add_xml_elem("voice", note, inner_txt="1")
                    add_xml_elem("type", note, inner_txt=dur_xml.durationType)
                    add_xml_elem("stem", note, inner_txt=notedef.stem)

                    if notedef.ghost:
                        add_xml_elem("velocity", note, inner_txt="-50")  # Lower volume playback

                    if notedef.notehead:
                        add_xml_elem("notehead", note, inner_txt=notedef.notehead)

                    end_beam_times = [3, m._end]
                    if is_first_note:
                        nonlocal is_beam_started
                        print(beam_started)
                        if not beam_started and next_time not in end_beam_times:
                            add_xml_elem("beam", note, attr=[("number", "1")], inner_txt="begin")

                            is_beam_started = True
                        elif next_time in end_beam_times:
                            add_xml_elem("beam", note, attr=[("number", "1")], inner_txt="end")

                            is_beam_started = False
                        else:
                            add_xml_elem("beam", note, attr=[("number", "1")], inner_txt="continue")

                # Add all notes at time
                is_first_note = True
                for k, v in all_durs.items():
                    if v and k != "accent":
                        add_note(measure, NOTEDEFS[k], is_first_note, is_beam_started)
                        is_first_note = False

                # Handle hi-hat open/close
                # TODO: Result is valid, but might be ugly in certain cases. To improve
                if all_durs.get("hi_hat") and all_durs.get("hi_hat_open"):
                    raise RuntimeError(f"Error on measure {m_idx}: Hi-hat open and closed cannot overlap.")

                is_hh_open = False if all_durs.get("hi_hat") else True if all_durs.get("hi_hat_open") else is_hh_open

            # Close tuplet if needed
            # if tuplet_counter > 0:
            #     tuplet_counter -= 1
            #     if tuplet_counter == 0:
            #         add_xml_elem("endTuplet", voice)

        barline = add_xml_elem("barline", measure, attr=[("location", "right")])
        add_xml_elem("bar-style", barline, inner_txt="light-heavy")

    # Save
    xml_str = root.toprettyxml(indent="\t", encoding="UTF-8")
    if not os.path.exists(EXPORT_FOLDER):
        os.makedirs(EXPORT_FOLDER)

    assert metadata.workTitle
    filename = metadata.workTitle + ".musicxml"

    save_path = Path(EXPORT_FOLDER) / filename
    with open(save_path, "wb") as f:
        f.write(xml_str)


def export_from_module(mod: ModuleType):
    """
    Exports the song module given as argument.
    This module must have its global "metadata" and "measures"
    objects already filled at call time.

    Args:
        mod (ModuleType): The song module with generation completed
    """

    logging.getLogger(__name__).info("Exporting song '%s' to '%s'.", mod.__name__.split(".")[-1], EXPORT_FOLDER)

    # Important: all user-filled objects are *copied* here
    #            Otherwise they could be modified by the exporter
    if not hasattr(mod, "metadata"):
        logging.getLogger(__name__).error("Song module does not have metadata associated. Make sure to fill the 'metadata' object.")
        return -1
    metadata = deepcopy(mod.metadata)

    if not hasattr(mod, "measures"):
        logging.getLogger(__name__).error("Song module does not have measures associated. Make sure to fill the 'measures' list.")
        return -1

    # Uses the refcounts after the import to determine if a measure had more references that the others
    # This is to try to warn the user to not use direct assignements for creating measures, because they work by reference in Python
    # Instead, only copies should be used.
    # TODO: This doesn't always work... to avoid this problem entirely, one would need to wrap all measures in a Song class
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

    measures = [Measure(m) for m in mod.measures]

    export_song(metadata, measures)

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
                    if found_filename == strip_extension(f) and f.endswith(".py"):
                        return os.path.relpath(folder, root_dir)

            return None

        if found_filename:
            found_rel_path = find_relpath_by_walk()
            if found_rel_path:
                assert found_filename
                logging.getLogger(__name__).info("Found file to export in location: %s", found_rel_path)

    if not found_rel_path or not found_filename:
        logging.getLogger(__name__).error("Could not find file '%s' given as argument.", filename)
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


def export_from_filename(filename: str) -> int:
    """
    Exports a song file provided as argument.
    Can either be a full file path, or only the file name

    Example for a song file "my_song.py":
        export_from_filename("my_song")
    """
    song_module = import_song_module_from_filename(filename)
    if not song_module:
        return -1

    return export_from_module(song_module)


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
