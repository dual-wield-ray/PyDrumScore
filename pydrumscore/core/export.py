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
import math
from pathlib import Path
from xml.dom import minidom
from collections import namedtuple
from types import ModuleType
from typing import List, Tuple, Optional
from copy import deepcopy
from configparser import ConfigParser

# External modules
from from_root import from_root
import setuptools_scm

# Local modules
import pydrumscore.core.song
from pydrumscore.core.song import Metadata, Measure

# Get version from setuptools' source control
VERSION_MODULE_NAME = "pydrumscore.__version__"
pydrumscore_version = "" #pylint: disable=invalid-name
if importlib.util.find_spec(VERSION_MODULE_NAME):
    # If using source distribution (or if package was locally built) get version from it
    version_mod = importlib.import_module(VERSION_MODULE_NAME)
    pydrumscore_version = version_mod.version
else:
    pydrumscore_version = setuptools_scm.get_version(
            root='../../', relative_to=__file__)

# Read config file
# Note: Due to a bug, it's not possible to get MuseScore version info from CLI on Windows
#       Perhaps revisit sometime if it has been done, or do it ourselves...
configur = ConfigParser()
configur.read("config.ini")

MS_VERSION = configur.get('msversion','msversion')
PROGRAM_VERSION = configur.get('msversion','program_version')
PROGRAM_REVISION = configur.get('msversion','program_revision')
EXPORT_FOLDER = configur.get('export','export_folder')

class NoteDef:
    # pylint: disable=too-few-public-methods

    """ Defines how instruments on the drumset are represented in the XML. """
    def __init__(self, pitch: str, tpc: str, head="", articulation="", flam=False, stem_direction = "up") -> None:
        # pylint: disable=too-many-arguments
        self.pitch = pitch
        self.tpc = tpc
        self.head = head
        self.articulation = articulation
        self.flam = flam
        self.stem_direction = stem_direction

NOTEDEFS = {
        "sd" : NoteDef("38", "16"),
        "hh" : NoteDef("42", "20", head = "cross", articulation = "brassMuteClosed"),
        "bd" : NoteDef("36", "14"),
        "ft" : NoteDef("41", "13"),
        "mt" : NoteDef("45", "17"),
        "ht" : NoteDef("47", "19"),
        "cs" : NoteDef("37", "21", head = "cross"),
        "c1" : NoteDef("49", "21", head = "cross"),
        "ho" : NoteDef("46", "12", head = "cross", articulation = "stringsHarmonic"),
        "rd" : NoteDef("51", "11", head = "cross"),
        "rb" : NoteDef("53", "13", head = "diamond"),
        "fm" : NoteDef("38", "16", flam = True),
        "hf" : NoteDef("44", "22", head="cross", stem_direction="down"),
    }


def export_song(metadata: Metadata, measures: List[Measure]):
    """
    Exports the song given as argument as an mscx file (xml).

    :param metadata: Copy of the 'metadata' object filled by the user. Must exist.
    :param measures: Copy of the 'measures' object filled by the user. Must contain at least one measure.
    """

    assert metadata, "Metadata cannot be 'None'."
    assert measures, "Measures cannot be empty."

    def add_elem(name: str,
                   parent:minidom.Element,
                   attr: Optional[List[Tuple[str,str]]] = None,
                   inner_txt: Optional[str] = None,
                   insert_before: Optional[minidom.Element] = None):

        if attr is None:
            attr = []

        e = root.createElement(name)

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
            assert False, "Could not prepend element " + e.nodeName + " to " + insert_before.nodeName + ", because the later is missing in children. Check that parent node really owns both."
        else:
            # Order not important, just append to end
            parent.appendChild(e)

        return e

    # Create root document
    root = minidom.Document()
    xml = root.createElement('museScore')
    xml.setAttribute("version", MS_VERSION)
    root.appendChild(xml)

    # Program metadata
    add_elem("programVersion", xml, inner_txt=PROGRAM_VERSION)
    add_elem("programRevision", xml, inner_txt=PROGRAM_REVISION)

    # Score
    score = add_elem("Score", xml)
    add_elem("LayerTag", score, [("id", "0"), ("tag", "default")], "")
    add_elem("currentLayer", score, inner_txt="0")
    add_elem("Division", score, [], "480")

    # Style
    style = add_elem("Style", score, [])
    add_elem("pageWidth", style, [], "8.5")
    add_elem("pageHeight", style, [], "11")
    add_elem("Spatium", style, [], "1.74978")
    add_elem("showInvisible", score, inner_txt="1")
    add_elem("showUnprintable", score, inner_txt="1")
    add_elem("showFrames", score, inner_txt="1")
    add_elem("showMargins", score, inner_txt="0")

    metadata.mscVersion = MS_VERSION
    metadata.pydrumscoreVersion = pydrumscore_version
    for tag in metadata.ALL_TAGS:
        assert hasattr(metadata, tag), "Invalid tag give to export."
        add_elem("metaTag", score, [("name", tag)], inner_txt=getattr(metadata, tag))

    # Boilerplate for defining the drumset instrument
    # Copied from a valid exported score
    def add_xml_snippet(path):
        """
        Inserts an XML file into the 'score' xml variable.
        Also cleans the file of whitespace before doing so.
        """
        def clean_xml_whitespace(xml_doc):
            xml_str = xml_doc.toxml()
            xml_str = xml_str.replace('\n', '')
            xml_str = xml_str.replace('\t', '')
            xml_str = xml_str.replace('>    <', '><')
            return minidom.parseString(xml_str)

        xml_doc = minidom.parse(path)
        xml_doc = clean_xml_whitespace(xml_doc)
        xml_doc = xml_doc.firstChild
        score.appendChild(xml_doc)

    add_xml_snippet("pydrumscore/refxml/PartXML.xml")

    # Boilerplate for Staff
    staff = add_elem("Staff", score, [("id", "1")])
    vbox = add_elem("VBox", staff)
    add_elem("height", vbox, inner_txt="10")
    add_elem("boxAutoSize", vbox, inner_txt="0")
    text = add_elem("Text", vbox)
    add_elem("style", text, inner_txt="Title")
    add_elem("text", text, inner_txt=metadata.workTitle)
    if metadata.subtitle:
        text = add_elem("Text", vbox)
        add_elem("style", text, inner_txt="Subtitle")
        add_elem("text", text, inner_txt=metadata.subtitle)
    if metadata.composer:
        text = add_elem("Text", vbox)
        add_elem("style", text, inner_txt="Composer")
        add_elem("text", text, inner_txt=metadata.composer)
    if metadata.lyricist:
        text = add_elem("Text", vbox)
        add_elem("style", text, inner_txt="Lyricist")
        add_elem("text", text, inner_txt=metadata.lyricist)


    ########### Song content export starts ###########

    # First measure needs some default info if user didn't provide it
    first_m = measures[0]
    if not first_m.time_sig:
        first_m.time_sig = "4/4"
    if not first_m.tempo:
        first_m.tempo = 100

    # TODO: Sketchy pattern is still there
    for m in measures:
        m.pre_export()


    # Export context; all the stuff that is not
    # related to a single measure, but instead persists
    # over time and is needed for logic
    is_hh_open = False
    curr_time_sig_str = ""
    curr_time_sig_num = -1

    for m_idx, m in enumerate(measures):

        measure = add_elem("Measure", staff)

        if m.start_repeat:
            add_elem("startRepeat", measure)
        if m.end_repeat:
            add_elem("endRepeat", measure, inner_txt="2")

        voice = add_elem("voice", measure)

        if m.dynamic:
            dynamic = add_elem("Dynamic", voice)
            add_elem("subtype", dynamic, inner_txt=m.dynamic)

        if m.text:
            sys_text = add_elem("SystemText", voice)
            add_elem("text", sys_text, inner_txt=m.text)

        if m.has_line_break:
            lyt_break = add_elem("LayoutBreak", measure)
            add_elem("subtype", lyt_break, inner_txt="line")

        if m.time_sig and m.time_sig != curr_time_sig_str:
            curr_time_sig_str = m.time_sig
            split_sig = m.time_sig.split("/")
            assert len(split_sig) == 2
            curr_time_sig_num = int(split_sig[0])

            timesig = add_elem("TimeSig", voice)
            add_elem("sigN", timesig, inner_txt=split_sig[0])
            add_elem("sigD", timesig, inner_txt=split_sig[1])

        # Note: Displaying the note symbol is tricky because the ref
        #       xml is malformed, and blocked by xml minidom.
        #       We might need to convert to ElementTree to make it work...
        #
        #       The reference xml does <text><sym>metNoteQuarterUp</sym> = 10</text>
        #       But, pasting that string results in the <> symbols being interpreted
        #       as regular chars. Meanwhile, parsing that string from code throws.
        #       So at the moment, we just add 'bpm' instead...
        if m.tempo:
            tempo = add_elem("Tempo", voice)
            add_elem("tempo", tempo, inner_txt=str(m.tempo/60.0))
            add_elem("followText", tempo, inner_txt="1")
            add_elem("text", tempo, inner_txt=str(m.tempo) + " bpm")


        all_times = m.get_combined_times()

        # Handle repeat symbol
        if not m.no_repeat \
        and m_idx != 0 \
        and m == measures[m_idx-1] \
        and len(all_times):  # Don't use for empty measures
            repeat = add_elem("RepeatMeasure", voice)
            add_elem("durationType", repeat, inner_txt="measure")
            add_elem("duration", repeat, inner_txt=curr_time_sig_str)
            continue

        # Add measure separators
        # A separator "cuts up" the measure to prevent valid, but ugly
        # results like quarter notes going over a beat when on the "and",
        # or dotted rests.

        # Add a separator at the last time of the bar.
        max_sep = curr_time_sig_num - 1
        if all_times and math.ceil(all_times[-1]) < max_sep:
            m.separators.append(math.ceil(all_times[-1]))

        # Avoids dotted rests, and instead splits them into
        # only 1s, 2s, or 4s
        for i,t in enumerate(all_times):
            next_time = all_times[i+1] if i+1 < len(all_times) else curr_time_sig_num
            until_next = next_time - t
            if until_next > 2 and until_next != 4.0:
                m.separators.append(math.ceil(t) + 1.0)

        all_times += m.separators

        all_times = list(set(all_times))  # Remove duplicates
        all_times.sort()  # Read from left to right in time

        # Counts how many chords/rests are left to complete tuplet
        # Set at first note, decreased after each and closed at 0
        tuplet_counter = 0

        for i, _ in enumerate(all_times):

            def calc_note_dur(notes):
                # Check if note on this time
                try:
                    notes.index(curr_time)
                except ValueError:
                    return 0    # No note right now

                # Use gap between curr time and next time
                duration = until_next

                # For drum notes, we don't want longer than a quarter
                duration = min(duration, 1)

                return duration

            curr_time = all_times[i]
            next_time = all_times[i+1] if i < len(all_times)-1 else curr_time_sig_num
            until_next = next_time - curr_time

            all_durs = {}
            for p in m.USED_PIECES:
                assert hasattr(m, p)
                dur = calc_note_dur(getattr(m,p))
                if dur:
                    all_durs[p] = dur

            assert 0 not in all_durs.values()
            assert 0.0 not in all_durs.values()

            # If note, stems are connected => shortest becomes value of all
            # Rests fill the value of the gap
            is_rest = len(all_durs) == 0
            chord_dur = min(all_durs.values()) if not is_rest else until_next

            DurationXML = namedtuple("DurationXML", ["durationType", "isTuplet", "isDotted"])
            def get_duration_xml(dur):

                dotted = False  # TODO: Find way to not dot *everything* in the chord...
                tuplet = False
                dur_str = ""
                if dur == curr_time_sig_num:
                    dur_str = "measure"
                elif dur == 4.0:
                    dur_str = "whole"
                elif dur == 3.0:
                    dur_str = "half"
                    dotted = True
                elif dur == 2.0:
                    dur_str = "half"
                elif dur == 1.0:
                    dur_str = "quarter"
                elif dur == 0.75:
                    dur_str = "eighth"
                    dotted = True
                elif dur ==  0.5:
                    dur_str = "eighth"
                elif dur ==  0.25:
                    dur_str = "16th"
                elif math.isclose(dur, 0.33, rel_tol=0.1):
                    tuplet = True
                    dur_str = "eighth"
                elif math.isclose(dur, 0.16, rel_tol=0.1):
                    tuplet = True
                    dur_str = "16th"

                assert dur_str != "", "Invalid note duration '" + str(dur) + "'."

                return DurationXML(dur_str, tuplet, dotted)

            dur_xml = get_duration_xml(chord_dur)

            # Handle tuplet header
            if dur_xml.isTuplet and tuplet_counter == 0:
                tuplet = add_elem("Tuplet", voice)

                tuplet_dur = round(1.0/chord_dur)  # ex. 3 for triplet
                normal_dur_str = "2" if tuplet_dur == 3 \
                                else "4" if tuplet_dur == 6 \
                                else "8"

                add_elem("normalNotes", tuplet, inner_txt=normal_dur_str)
                add_elem("actualNotes", tuplet, inner_txt=str(tuplet_dur))
                add_elem("baseNote", tuplet, inner_txt=dur_xml.durationType)
                number = add_elem("Number", tuplet)
                add_elem("style", number, inner_txt="Tuplet")
                add_elem("text", number, inner_txt=str(tuplet_dur))

                # Init tuplet counter
                tuplet_counter = tuplet_dur

            # Handle rest (not part of "Chord" xml block)
            if is_rest:
                rest = add_elem("Rest", voice)
                if dur_xml.isTuplet:
                    add_elem("BeamMode", rest, inner_txt="mid")
                if dur_xml.isDotted:
                    add_elem("dots", rest, inner_txt="1")  # Must be before durationType!
                add_elem("durationType", rest, inner_txt=dur_xml.durationType)
                if dur_xml.durationType == "measure":
                    add_elem("duration", rest, inner_txt=curr_time_sig_str)

            # Write chord (non-rest group of notes)
            else:
                chord = add_elem("Chord", voice)

                if dur_xml.isDotted:
                    add_elem("dots", chord, inner_txt="1")

                add_elem("durationType", chord, inner_txt=dur_xml.durationType)

                accent_chord = all_durs.get("ac") is not None
                if accent_chord:
                    art = add_elem("Articulation", chord)
                    add_elem("subtype", art, inner_txt="articAccentAbove")
                    add_elem("anchor", art, inner_txt="3")

                stem_dir = add_elem("StemDirection", chord, inner_txt="up")

                def add_note(chord, notedef):

                    # If flam, add little note before main note
                    if notedef.flam:
                        acc_chord = add_elem("Chord", voice, insert_before=chord)
                        acc_note = add_elem("Note", acc_chord)
                        add_elem("durationType", acc_chord, inner_txt="eighth", \
                            insert_before=acc_note)
                        add_elem("acciaccatura", acc_chord, insert_before=acc_note)
                        spanner = add_elem("Spanner", acc_note, attr=[("type", "Tie")])
                        add_elem("Tie", spanner, inner_txt="\n")
                        next_e = add_elem("next", spanner)
                        add_elem("location", next_e, inner_txt="\n")
                        add_elem("pitch", acc_note, inner_txt=notedef.pitch)
                        add_elem("tpc", acc_note, inner_txt=notedef.tpc)

                    if notedef.articulation:
                        if notedef is NOTEDEFS["hh"] and is_hh_open \
                        or notedef is NOTEDEFS["ho"] and not is_hh_open:
                            art = add_elem("Articulation", chord, insert_before=stem_dir)
                            add_elem("subtype", art, inner_txt=notedef.articulation)
                            add_elem("anchor", art, inner_txt="3")

                    # Main note
                    note = add_elem("Note", chord)

                    # Connect flam little note with main
                    if notedef.flam:
                        spanner = add_elem("Spanner", note, attr=[("type", "Tie")])
                        prev_e = add_elem("prev", spanner)
                        location = add_elem("location", prev_e)
                        add_elem("grace", location, inner_txt="0")

                    add_elem("pitch", note, inner_txt=notedef.pitch)
                    add_elem("tpc", note, inner_txt=notedef.tpc)

                    if notedef.head:
                        add_elem("head", note, inner_txt=notedef.head)

                # Add all notes at time
                for k,v in all_durs.items():
                    if v and k != "ac":
                        add_note(chord, NOTEDEFS[k])

                # Handle hi-hat open/close
                # TODO: Result might not always be desired
                if all_durs.get("hh") and all_durs.get("ho"):
                    raise RuntimeError("Error on measure " + str(m_idx) + ": Hi-hat open and closed cannot overlap.")
                if all_durs.get("hh"):
                    is_hh_open = False
                elif all_durs.get("ho"):
                    is_hh_open = True

            # Close tuplet if needed
            if tuplet_counter > 0:
                tuplet_counter -= 1
                if tuplet_counter == 0:
                    add_elem("endTuplet", voice)

    # Save
    xml_str = root.toprettyxml(indent = "\t", encoding="UTF-8")
    if not os.path.exists(EXPORT_FOLDER):
        os.makedirs(EXPORT_FOLDER)

    assert metadata.workTitle
    filename = metadata.workTitle + ".mscx"

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

    logging.getLogger(__name__).info("Exporting song '%s' to '%s'.", mod.__name__.split('.')[-1], EXPORT_FOLDER)

    # Important: all user-filled objects are *copied* here
    #            Otherwise they could be modified by the exporter
    if not hasattr(mod, "metadata"):
        logging.getLogger(__name__).error("Song module does not have metadata associated. Make sure to fill the 'metadata' object.")
        return -1
    metadata = deepcopy(mod.metadata)

    if not hasattr(mod, "measures"):
        logging.getLogger(__name__).error("Song module does not have measures associated. Make sure to fill the 'measures' list.")
        return -1
    measures = [Measure(m) for m in mod.measures]

    export_song(metadata, measures)

    logging.getLogger(__name__).info("Export completed successfully.")

    return 0


def export_from_filename(filename: str) -> int:
    """
    Exports a song file provided as argument.
    Can either be a full file path, or only the file name

    Example for a song file "my_song.py":
        export_from_filename("my_song")

    The song file can be in any folder of the configured song directory (TODO).
    """

    # Info needed to build the module import str
    found_rel_path = ""
    found_filename = ""
    root_dir = from_root("__main__.py").parent

    # Case user gave full path arg
    if os.path.exists(filename):
        found_rel_path = os.path.split(os.path.relpath(filename, root_dir))[0]
        found_filename = os.path.basename(filename).rsplit('.', 1)[0]

    # Case user gave file name only, need to search for relpath
    else:
        def strip_extension(filename):
            return filename.rsplit('.', 1)[0]

        found_filename = strip_extension(filename)

        def find_relpath_by_walk():
            for folder, dirnames, files in os.walk(root_dir, topdown=True):

                # Prune all dirs with invalid names
                dirnames = [d for d in dirnames \
                            if not d.startswith(".") and not d.startswith("_")]

                for f in files:
                    if found_filename == strip_extension(f):
                        return os.path.relpath(folder, root_dir)

            return None

        if found_filename:
            found_rel_path = find_relpath_by_walk()
            if found_rel_path:
                assert found_filename
                logging.getLogger(__name__).info("Found file to export in location: %s", found_rel_path)

    if not found_rel_path or not found_filename:
        logging.getLogger(__name__).error("Could not find file '%s' given as argument.", filename)
        return -1

    # Use result to craft module str and begin export
    def build_module_str(filename, relpath):
        if relpath == ".":
            relpath = ""
        import_str = ".".join(relpath.split(os.sep))
        import_str = ".".join([import_str, filename])
        return import_str

    # Result string to import song module
    # Ex. "pydrumscore.test.songs.my_song"
    assert found_filename and found_rel_path
    module_import_str = build_module_str(found_filename, found_rel_path)

    pydrumscore.core.song._preexport_reset()  # pylint: disable = protected-access

    assert importlib.util.find_spec(module_import_str), "Could not import module."
    song_module = importlib.import_module(module_import_str)

    return export_from_module(song_module)

def main():
    """
    Exports a song file provided by command line argument.
    Can either be a full file path, or only the file name

    Example for a song file "my_song.py":
        python pydrumscore -m my_song

    The song file can be in any folder of the configured song directory (TODO).
    """

    if len(sys.argv) < 2:
        print("Must give file name as argument. Type 'help()' for more info.")
        return -1

    return export_from_filename(sys.argv[1])
