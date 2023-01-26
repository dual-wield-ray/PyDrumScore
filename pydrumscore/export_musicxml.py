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
from typing import List, Optional, Union
from copy import deepcopy
from fractions import Fraction
from functools import partial

# External modules
from from_root import from_root

# Local modules
import pydrumscore
from pydrumscore import Metadata, Measure
from config_handling import read_config
import xml_handling

# Exporter uses api with access to all private members (like a C++ "friend" class)
# pylint: disable=protected-access

@dataclass
class NoteDefMusicXML:
    """Defines how instruments on the drumset are represented in the MusicXML."""
    display_step: str
    display_octave: str
    instrument_id: str
    stem: str = "up"
    notehead: str = ""
    articulation: str = ""
    flam: bool = False
    ghost: bool = False


NOTEDEFS = {
    "snare": NoteDefMusicXML("C", "5", "P1-I39"),
    "snare_ghost": NoteDefMusicXML("C", "5", "P1-I39", ghost=True),
    "hi_hat": NoteDefMusicXML("G", "5", "P1-I43", notehead="x", articulation="brassMuteClosed"),
    "bass_drum": NoteDefMusicXML("F", "4", "P1-I37"),

    "floor_tom": NoteDefMusicXML("A", "4", "P1-I42"),
    "mid_tom": NoteDefMusicXML("D", "5", "P1-I46"),
    "high_tom": NoteDefMusicXML("E", "5", "P1-I48"),
    #"cross_stick": NoteDef("37", "21", head="cross"),
    "crash1": NoteDefMusicXML("A", "5", "P1-I50", notehead="x"),
    "hi_hat_open": NoteDefMusicXML("G", "5", "P1-I47", notehead="x", articulation="natural"),
    "ride": NoteDefMusicXML("F", "5", "P1-I52", notehead="x"),
    "ride_bell": NoteDefMusicXML("F", "5", "P1-I54", notehead="diamond"),
    "flam_snare": NoteDefMusicXML("C", "5", "P1-I39", flam=True),
    #"hi_hat_foot": NoteDef("44", "22", head="cross", stem_direction="down"),
}


def export_song(metadata: Metadata, measures: List[Measure], exp_folder_override: Optional[str] = None):
    """
    Exports the song given as argument as an mscx file (xml).

    :param metadata: Copy of the 'metadata' object filled by the user. Must exist.
    :param measures: Copy of the 'measures' object filled by the user. Must contain at least one measure.

    """

    assert metadata, "Metadata cannot be 'None'."
    assert measures, "Measures cannot be empty."
    assert metadata.workTitle

    config = read_config()
    export_folder = config.export_folder if not exp_folder_override else exp_folder_override

    # Create DOCTYPE
    imp = minidom.getDOMImplementation('')
    doctype = imp.createDocumentType('score-partwise', '-//Recordare//DTD MusicXML 4.0 Partwise//EN', 'http://www.musicxml.org/dtds/partwise.dtd')

    # Create root document
    root = minidom.Document()
    root.insertBefore(doctype, root.documentElement)
    xml = root.createElement("score-partwise")
    xml.setAttribute("version", "4.0")  # TODO: Check what version is needed
    root.appendChild(xml)

    # Init xml writing function with created XML document
    add_xml_elem = partial(xml_handling.add_xml_elem_to_doc, root)

    # Boilerplate
    work = add_xml_elem("work", xml)
    add_xml_elem("work-title", work, inner_txt=metadata.workTitle)

    identification = add_xml_elem("identification", xml)
    encoding = add_xml_elem("encoding", identification)
    add_xml_elem("software", encoding, inner_txt="PyDrumScore")  # TODO: Add version?
    #add_xml_elem("encoding-data", encoding, "")  # TODO?
    add_xml_elem("supports", encoding, attr=[("element", "accidental"), ("type", "yes")])
    add_xml_elem("supports", encoding, attr=[("element", "beam"), ("type", "yes")])
    add_xml_elem("supports", encoding, attr=[("element", "print"), ("attribute", "new-page"), ("type", "no")])
    add_xml_elem("supports", encoding, attr=[("element", "print"), ("attribute", "new-system"), ("type", "no")])
    add_xml_elem("supports", encoding, attr=[("element", "stem"), ("type", "yes")])

    xml_part_filepath = str(Path(from_root(__file__).parent, "refxml", "PartXML_MusicXML.xml"))
    xml.appendChild(minidom.parse(xml_part_filepath).firstChild)

    # Song content export starts here

    part = add_xml_elem("part", xml, attr=[("id", "P1")])

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
    current_divisions = -1
    repeat_started = False


    for m_idx, m in enumerate(measures):
        is_first_measure = (m_idx == 0)

        measure = add_xml_elem("measure", part, attr=[("number", str(m_idx+1))])
        attributes = add_xml_elem("attributes", measure)

        new_divisions = max(m._divisions, current_divisions)
        divisions_changed = new_divisions != current_divisions
        current_divisions = new_divisions

        if m == measures[0] or divisions_changed:
            add_xml_elem("divisions", attributes, inner_txt=str(m._divisions))

        #if m.dynamic:
        #    dynamic = add_xml_elem("Dynamic", voice)
        #    add_xml_elem("subtype", dynamic, inner_txt=m.dynamic)

        if m.text:
            direction = add_xml_elem("direction", measure)
            direction_type = add_xml_elem("direction-type", direction)
            add_xml_elem("words", direction_type, inner_txt=m.text)

        #if m.has_line_break:
        #    lyt_break = add_xml_elem("LayoutBreak", measure)
        #    add_xml_elem("subtype", lyt_break, inner_txt="line")

        if is_first_measure:
            key = add_xml_elem("key", attributes)
            add_xml_elem("fifths", key, inner_txt="0")

        assert m._time_sig
        if m._time_sig != curr_time_sig_str:
            curr_time_sig_str = m._time_sig
            split_sig = m._time_sig.split("/")
            assert len(split_sig) == 2

            timesig = add_xml_elem("time", attributes)
            add_xml_elem("beats", timesig, inner_txt=split_sig[0])
            add_xml_elem("beat-type", timesig, inner_txt=split_sig[1])

        if is_first_measure:
            clef = add_xml_elem("clef", attributes)
            add_xml_elem("sign", clef, inner_txt="percussion")
            add_xml_elem("line", clef, inner_txt="2")

        # TODO: Uniformize with the mscx once issue #25 is completed
        if m.tempo:
            direction = add_xml_elem("direction", measure, attr=[("placement", "above")])
            direction_type = add_xml_elem("direction-type", direction)
            add_xml_elem("words", direction_type, attr=[("font-weight", "bold"), ("font-size", "12")], inner_txt=str(m.tempo) + " bpm")
            add_xml_elem("sound", direction, attr=[("tempo", str(m.tempo))])

        all_times = m._get_combined_times()

        # Handle repeat symbol
        if len(all_times) and not m.no_repeat and m_idx != 0 and m == measures[m_idx - 1]:
            if not repeat_started:  # Don't use for empty measures
                measure_style = add_xml_elem("measure-style", attributes, attr=[("number", "1")])
                add_xml_elem("measure-repeat", measure_style, attr=[("type", "start")], inner_txt="1")
                repeat_started = True
                # Note: unlike in mscx, the measure data itself is copied each repeated measure, so we continue the normal flow

        elif repeat_started:
            measure_style = add_xml_elem("measure-style", attributes, attr=[("number", "1")])
            add_xml_elem("measure-repeat", measure_style, attr=[("type", "stop")], inner_txt="")
            repeat_started = False

        m._separators = list(set(m._separators))
        beam_groups = []
        group_lower_bound = 0

        for s in [3, m._end]:
            group = [t for t in all_times if (t >= group_lower_bound and t < s)]
            if group:
                beam_groups.append(group)
            group_lower_bound = s

        all_times += m._separators  # Add separators
        all_times = list(set(all_times))  # Remove duplicates
        all_times.sort()  # Read from left to right in time

        # Counts how many chords/rests are left to complete tuplet
        # Set at first note, decreased after each and closed at 0
        tuplet_counter = 0

        for i, t in enumerate(all_times):

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
                dur = calc_note_dur(getattr (m, p))
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
                elif dur == 0:
                    dur_str = "rest"

                assert dur_str != "", "Invalid note duration '" + str(dur) + "'."

                return DurationXML(dur_str, tuplet, dotted)

            dur_xml = get_duration_xml(chord_dur)

            # Handle rest (not part of "Chord" xml block)
            if is_rest:
                note = add_xml_elem("note", measure)
                rest = add_xml_elem("rest", note)

                add_xml_elem("duration", note, inner_txt=str(chord_dur * current_divisions))
                add_xml_elem("voice", note, inner_txt="1")
                if dur_xml.durationType == "measure":
                    rest.setAttribute("measure", "yes")
                else:
                    add_xml_elem("type", note, inner_txt=dur_xml.durationType)
                if dur_xml.isDotted:
                    add_xml_elem("dot", note)

            # Write chord (non-rest group of notes)
            else:

                accent_chord = all_durs.get("accent") is not None

                def add_note(measure, notedef: NoteDefMusicXML, is_first_note: bool, beam_started: bool):

                    # If flam, add little note before main note
                    if notedef.flam:
                        acc_note = add_xml_elem("note", measure)
                        add_xml_elem(
                            "grace",
                            acc_note,
                            attr=[("slash", "yes")],
                        )

                        unpitched = add_xml_elem("unpitched", acc_note)
                        add_xml_elem("display-step", unpitched, inner_txt=notedef.display_step)
                        add_xml_elem("display-octave", unpitched, inner_txt=notedef.display_octave)

                        add_xml_elem("tie", acc_note, attr=[("type", "start")])
                        add_xml_elem("instrument", acc_note, attr=[("id", notedef.instrument_id)])
                        add_xml_elem("voice", acc_note, inner_txt="1")
                        add_xml_elem("type", acc_note, inner_txt="eighth")
                        add_xml_elem("stem", acc_note, inner_txt=notedef.stem)
                        notations = add_xml_elem("notations", acc_note)
                        add_xml_elem("tied", notations, attr=[("type", "start")])

                    # Main note
                    note = add_xml_elem("note", measure)

                    if not is_first_note:
                        add_xml_elem("chord", note)

                    unpitched = add_xml_elem("unpitched", note)
                    add_xml_elem("display-step", unpitched, inner_txt=notedef.display_step)
                    add_xml_elem("display-octave", unpitched, inner_txt=notedef.display_octave)

                    add_xml_elem("duration", note, inner_txt=str(chord_dur * current_divisions))
                    instrument = add_xml_elem("instrument", note, attr=[("id", notedef.instrument_id)])
                    add_xml_elem("voice", note, inner_txt="1")
                    add_xml_elem("type", note, inner_txt=dur_xml.durationType)

                    if dur_xml.isDotted and is_first_note:
                        add_xml_elem("dot", note)

                    add_xml_elem("stem", note, inner_txt=notedef.stem)

                    # Connect flam's little note with main
                    if notedef.flam:
                        notations = add_xml_elem("notations", note)
                        add_xml_elem("tied", notations, attr=[("type", "stop")])
                        add_xml_elem("tie", note, attr=[("type", "stop")], insert_before=instrument)

                    if notedef.ghost:
                        note.setAttribute("dynamics", "-55.56")  # Lower volume playback
                        add_xml_elem("notehead", note, attr=[("parentheses", "yes")], inner_txt="normal")

                    # TODO: Default notehead for everything?
                    if notedef.notehead:
                        add_xml_elem("notehead", note, inner_txt=notedef.notehead)

                    if is_first_note and chord_dur < 1:

                        for group in beam_groups:
                            if t not in group or len(group) == 1:
                                continue

                            if t == group[0]:
                                add_xml_elem("beam", note, attr=[("number", "1")], inner_txt="begin")

                            elif t == group[-1]:
                                add_xml_elem("beam", note, attr=[("number", "1")], inner_txt="end")

                            else:
                                add_xml_elem("beam", note, attr=[("number", "1")], inner_txt="continue")

                            break

                    if accent_chord and is_first_note:
                        notations = add_xml_elem("notations", note)
                        articulations = add_xml_elem("articulations", notations)
                        add_xml_elem("accent", articulations)

                    if notedef.articulation:
                        if notedef is NOTEDEFS["hi_hat"] and is_hh_open:
                            notations = add_xml_elem("notations", note)
                            technical = add_xml_elem("technical", notations)
                            add_xml_elem("stopped", technical)
                        elif notedef is NOTEDEFS["hi_hat_open"] and not is_hh_open:
                            notations = add_xml_elem("notations", note)
                            technical = add_xml_elem("technical", notations)
                            harmonic = add_xml_elem("harmonic", technical, attr=[("placement", "above")])
                            add_xml_elem("natural", harmonic)

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

        # Measure might have no attributes, in which case delete the empty xml
        if not attributes.hasChildNodes():
            attributes.parentNode.removeChild(attributes)
            del attributes

        if m_idx == len(measures)-1:
            barline = add_xml_elem("barline", measure, attr=[("location", "right")])
            add_xml_elem("bar-style", barline, inner_txt="light-heavy")

    # Save
    xml_handling.save_doc_to_file(root, export_folder, metadata.workTitle + ".musicxml")


def export_from_module(mod: ModuleType, exp_folder_override: Optional[str] = None):
    """
    Exports the song module given as argument.
    This module must have its global "metadata" and "measures"
    objects already filled at call time.

    Args:
        mod (ModuleType): The song module with generation completed
    """

    logging.getLogger(__name__).info("Exporting song '%s' to '%s'.", mod.__name__.split(".")[-1], read_config().export_folder)

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


def export_from_filename(filename: str, exp_folder_override: Optional[str] = None) -> int:
    """
    Exports a song file provided as argument.
    Can either be a full file path, or only the file name

    Example for a song file "my_song.py":
        export_from_filename("my_song")
    """
    song_module = import_song_module_from_filename(filename)
    if not song_module:
        return -1

    return export_from_module(song_module, exp_folder_override)


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
