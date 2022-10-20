"""
Exporting functionalities for the drumscore package.
Currently only supports exporting in the uncompressed Musescore format,
.mscx. Export in MusicXML and .mscz (zipped musescore) is needed.
"""

# Built-in modules
import os
import sys
import importlib
import logging
import math
from xml.dom import minidom
from collections import namedtuple
from types import ModuleType
from typing import List, Tuple

# Local modules
import drumscore.core.song as api

# TODO: Put in a proper config file, and/or generate from installed MS version
MS_VERSION = "3.02"
PROGRAM_VERSION = "3.6.2"
PROGRAM_REVISION = "3224f34"

EXPORT_FOLDER = os.path.join("drumscore", "test", "_generated", "other")

# Defines how instruments on the drumset are represented
NoteDef = namedtuple("NoteDef", ["pitch", "tpc", "head", "articulation", "flam"])
NOTEDEFS = {
        "bd" : NoteDef("36", "14", None, "", False),
        "sd" : NoteDef("38", "16", None, "", False),
        "hh" : NoteDef("42", "20", "cross", "brassMuteClosed", False),
        "ft" : NoteDef("41", "13", None, "", False),
        "mt" : NoteDef("45", "17", None, "", False),
        "ht" : NoteDef("47", "19", None, "", False),
        "cs" : NoteDef("37", "21", "cross", "", False),
        "c1" : NoteDef("49", "21", "cross", "", False),
        "ho" : NoteDef("46", "12", "cross", "stringsHarmonic", False),
        "rd" : NoteDef("51", "11", "cross", "", False),
        "rb" : NoteDef("53", "13", "diamond", "", False),
        "fm" : NoteDef("38", "16", None, "", True),
    }


def export_song(metadata, measures):
    """
    Exports the song given as argument as an mscx file (xml).
    :param song: The song to export
    """

    # Utilities
    def add_elem(name: str,
                   parent,
                   attr: List[Tuple[str,str]] = None,
                   inner_txt = None,
                   insert_before=None):

        if attr is None:
            attr = []

        e = root.createElement(name)
        for attr_pair in attr:
            e.setAttribute(attr_pair[0], attr_pair[1])

        # Note: Adding empty strings in xml better follows MS format
        if inner_txt is not None:
            e.appendChild(root.createTextNode(inner_txt))

        if insert_before is not None:
            for c in parent.childNodes:
                if c is insert_before:
                    parent.insertBefore(e, c)
                    return e
            assert False, "Could not prepend element " + e.nodeName + " to " + \
                           insert_before.nodeName + " because the later is missing."
        else:
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

    for tag in metadata.ALL_TAGS:
        if tag == "mscVersion":
            add_elem("metaTag", score, [("name", tag)], inner_txt=MS_VERSION)
            continue

        assert hasattr(metadata, tag)
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

    add_xml_snippet("drumscore/refxml/PartXML.xml")

    # Boilerplate for Staff
    staff = add_elem("Staff", score, [("id", "1")])
    vbox = add_elem("VBox", staff)
    add_elem("height", vbox, inner_txt="10")
    add_elem("boxAutoSize", vbox, inner_txt="0")
    text = add_elem("Text", vbox)
    add_elem("style", text, inner_txt="Title")
    add_elem("text", text, inner_txt=metadata.workTitle)

    # Song data export starts

    # TODO: Rethink this
    if not measures[0].time_sig:
        measures[0].time_sig = "4/4"

    if not measures[0].tempo:
        measures[0].tempo = 100

    for m in measures:
        m.pre_export()  # Shift indices to start at 0

    # Keep track of hh state so we don't spam with O and +
    is_hh_open = False
    curr_time_sig = ""
    curr_time_sig_n = -1

    for m_idx, m in enumerate(measures):

        measure = add_elem("Measure", staff)
        voice = add_elem("voice", measure)

        if m.has_line_break:
            lyt_break = add_elem("LayoutBreak", measure)
            add_elem("subtype", lyt_break, inner_txt="line")

        if m.time_sig:
            curr_time_sig = m.time_sig
            split_sig = m.time_sig.split("/")
            assert len(split_sig) == 2
            curr_time_sig_n = float(split_sig[0])

            timesig = add_elem("TimeSig", voice)
            add_elem("sigN", timesig, inner_txt=split_sig[0])
            add_elem("sigD", timesig, inner_txt=split_sig[1])

        # TODO: Displaying the note symbol is tricky because the ref
        #       xml is malformed, and blocked by xml minidom.
        #       We might need to convert to ElementTree to make it work...
        #
        #       The reference xml does <text><sym>metNoteQuarterUp</sym> = 10</text>
        #       But, pasting that string results in the <> symbols being interpreted
        #       as regular chars. Meanwhile, parsing that string from code throws.
        if m.tempo:
            tempo = add_elem("Tempo", voice)
            add_elem("tempo", tempo, inner_txt=str(m.tempo/60.0))
            add_elem("followText", tempo, inner_txt="1")
            add_elem("text", tempo, inner_txt=str(m.tempo) + " bpm")


        all_times = m.get_combined_times()  # Combine all times in the measure that contain a note

        if not m_idx == 0:
            if m == measures[m_idx-1] and len(all_times):
                repeat = add_elem("RepeatMeasure", voice)
                add_elem("durationType", repeat, inner_txt="measure")
                add_elem("duration", repeat, inner_txt="4/4")
                continue

        # Add these as extra separators for each beat
        # Prevents ex. quarter notes going over a beat when on the "and"
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

                # For notes, we don't want longer than a quarter
                duration = min(duration, 1)

                return duration

            curr_time = all_times[i]
            next_time = all_times[i+1] if i < len(all_times)-1 else curr_time_sig_n
            until_next = next_time - curr_time

            all_durs = {}
            for p in m.ALL_PIECES:
                assert hasattr(m,p)
                all_durs[p] = calc_note_dur(getattr(m,p))

            # Remove zero before getting min value of voice
            zero_keys = [k for (k,v) in all_durs.items() if v==0]
            all_nonzero_durs = dict(all_durs)
            for k in zero_keys:
                all_nonzero_durs.pop(k)

            # If note, stems are connected => shortest becomes value of all
            # Rests fill the value of the gap
            is_rest = len(all_nonzero_durs) == 0
            chord_dur = min(all_nonzero_durs.values()) if not is_rest else until_next

            DurationXML = namedtuple("DurationXML", ["durationType", "isTuplet", "isDotted"])
            def get_duration_xml(dur):

                dotted = False  # TODO: Find way to not dot *everything* in the chord...
                tuplet = False
                dur_str = ""
                if dur == curr_time_sig_n:
                    dur_str = "measure"
                elif dur == 4.0:
                    dur_str = "whole"
                elif dur == 2.0:
                    dur_str = "half"
                elif dur == 1.0:
                    dur_str = "quarter"
                elif dur == 0.75:
                    dur_str = "eighth"
                    dotted = True
                elif dur ==  0.5:
                    dur_str = "eighth"
                elif math.isclose(dur, 0.16, rel_tol=0.1):
                    tuplet = True
                    dur_str = "16th"
                elif math.isclose(dur, 0.33, rel_tol=0.1):
                    tuplet = True
                    dur_str = "eighth"
                elif dur ==  0.25:
                    dur_str = "16th"

                assert dur_str != "", "Invalid note duration in tuplet"

                return DurationXML(dur_str, tuplet, dotted)

            dur_xml = get_duration_xml(chord_dur)

            # Handle tuplet header
            if dur_xml.isTuplet and tuplet_counter == 0:
                tuplet = add_elem("Tuplet", voice)

                tuplet_dur = round(1.0/chord_dur)  # 3 for triplet...
                normal_dur_str = "2" if tuplet_dur == 3 \
                                else "4" if tuplet_dur == 6 \
                                else "8"

                add_elem("normalNotes", tuplet, inner_txt=normal_dur_str)
                add_elem("actualNotes", tuplet, inner_txt=str(tuplet_dur))
                add_elem("baseNote", tuplet, inner_txt=dur_xml.durationType)
                number = add_elem("Number", tuplet)
                add_elem("style", number, inner_txt="Tuplet")
                add_elem("text", number, inner_txt=str(tuplet_dur))

                tuplet_counter = tuplet_dur

            # Write rest
            if is_rest:
                rest = add_elem("Rest", voice)
                if dur_xml.isTuplet:
                    add_elem("BeamMode", rest, inner_txt="mid")
                add_elem("durationType", rest, inner_txt=dur_xml.durationType)
                if dur_xml.durationType == "measure":
                    add_elem("duration", rest, inner_txt=curr_time_sig)

                if dur_xml.isDotted:
                    add_elem("dots", chord, inner_txt="1")

            # Write chord (non-rest group of notes)
            else:
                chord = add_elem("Chord", voice)

                if dur_xml.isDotted:
                    add_elem("dots", chord, inner_txt="1")

                add_elem("durationType", chord, inner_txt=dur_xml.durationType)
                add_elem("StemDirection", chord, inner_txt="up")

                def add_note(chord, notedef, is_hh_open=False):

                    # If note is a flam, add the note before first
                    if notedef.flam:
                        acc_chord = add_elem("Chord", voice, insert_before=chord)
                        acc_note = add_elem("Note", acc_chord)
                        add_elem("durationType", acc_chord, inner_txt="eighth", \
                            insert_before=acc_note)
                        add_elem("acciaccatura", acc_chord, insert_before=acc_note)
                        spanner = add_elem("Spanner", acc_note, attr=[("type", "Tie")])
                        add_elem("Tie", spanner, inner_txt="")
                        next_e = add_elem("next", spanner)
                        add_elem("location", next_e, inner_txt="")
                        add_elem("pitch", acc_note, inner_txt=notedef.pitch)
                        add_elem("tpc", acc_note, inner_txt=notedef.tpc)

                    # Main note
                    note = add_elem("Note", chord)

                    if notedef.flam:
                        spanner = add_elem("Spanner", note, attr=[("type", "Tie")])
                        prev_e = add_elem("prev", spanner)
                        location = add_elem("location", prev_e)
                        add_elem("grace", location, inner_txt="0")

                    add_elem("pitch", note, inner_txt=notedef.pitch)
                    add_elem("tpc", note, inner_txt=notedef.tpc)

                    if notedef.head:
                        add_elem("head", note, inner_txt=notedef.head)

                    if notedef.articulation:
                        if notedef is NOTEDEFS["hh"] and is_hh_open \
                        or notedef is NOTEDEFS["ho"] and not is_hh_open:
                            art = add_elem("Articulation", chord)
                            add_elem("subtype", art, inner_txt=notedef.articulation)
                            add_elem("anchor", art, inner_txt="3")


                if all_durs["hh"] and all_durs["ho"]:
                    raise RuntimeError("Error on measure " + m_idx + \
                          ": Hi-hat open and closed cannot overlap. ")

                for k,v in all_durs.items():
                    if v:
                        if k in ["hh", "ho"]:
                            add_note(chord, NOTEDEFS[k], is_hh_open)  # TODO: Remove hack
                        else:
                            add_note(chord, NOTEDEFS[k])

                # TODO: Result might not always be desired
                if all_durs["hh"]:
                    is_hh_open = False
                elif all_durs["ho"]:
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

    save_path = os.path.join(EXPORT_FOLDER, filename)
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

    logging.getLogger(__name__).info("Exporting song '%s'", mod.__name__.split('.')[-1])

    metadata = mod.metadata
    measures = [api.Measure(m) for m in mod.measures]

    export_song(metadata, measures)

    logging.getLogger(__name__).info("Export completed successfully.")


def main():
    """
    Exports a song file provided by command line argument.
    Can either be a full file path, or only the file name

    Example for a song file "my_song.py":
        python drumscore my_song

    The song file can be in any folder of the configured song directory (TODO!).
    """

    if len(sys.argv) < 2:
        logging.getLogger(__name__).error("Must give file name as argument.\
                                           Type 'help()' for more info.")
        return -1

    file_arg = sys.argv[1]
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)

    # Info needed to build the module import str
    found_rel_path = ""
    filename = ""

    # Case user gave full path arg
    if os.path.exists(file_arg):
        found_rel_path = os.path.relpath(os.path.split(file_arg)[1], root_dir)
        filename = os.path.basename(file_arg)

    # Case user gave file name only, need to search for relpath
    else:
        filename = file_arg.rsplit('.', 1)[0]

        def find_relpath_by_walk():
            for folder, dirnames, files in os.walk(root_dir, topdown=True):

                # Prune all dirs with invalid names
                for d in dirnames:
                    if d.startswith(".") or d.startswith("_"):
                        dirnames.remove(d)

                for f in files:
                    f = f.rsplit('.', 1)[0]  # Strip extension
                    if filename == f:
                        return os.path.relpath(folder, root_dir)

            return None


        found_rel_path = find_relpath_by_walk()
        if found_rel_path:
            logging.getLogger(__name__).info("Found file to export in location: %s", found_rel_path)

    if not found_rel_path:
        logging.getLogger(__name__).error("Could not find file '%s' given as argument.", file_arg)
        return -1

    # Use result to craft module str and begin export
    def build_module_str(filename, relpath):
        if relpath == ".":
            relpath = ""
        import_str = ".".join(relpath.split(os.sep))
        import_str = ".".join(["drumscore", import_str, filename])
        return import_str

    # Result string to import song module
    # Ex. "drumscore.test.songs.my_song"
    assert filename and found_rel_path
    module_import_str = build_module_str(filename, found_rel_path)

    assert importlib.util.find_spec(module_import_str)
    song_module = importlib.import_module(module_import_str)
    export_from_module(song_module)

    return 0
