"""
Exporting logic for MuseScore file formats (.mscx and .mscz).
"""

# Built-in modules
from pathlib import Path
from xml.dom import minidom
from collections import namedtuple
from typing import List, Optional, Union
from fractions import Fraction
from functools import partial
from dataclasses import dataclass

# External modules
from from_root import from_root

# Local modules
import pydrumscore
from pydrumscore import Measure, Metadata
from config_handling import read_config
import xml_handling

@dataclass
class NoteDefMuseScore:
    """Defines how instruments on the drumset are represented in the mscx."""

    pitch: str
    tpc: str
    head:str = ""
    articulation:str = ""
    flam:bool=False
    stem_direction:str="up"
    ghost:bool=False


NOTEDEFS = {
    "snare": NoteDefMuseScore("38", "16"),
    "snare_ghost": NoteDefMuseScore("38", "16", ghost=True),
    "hi_hat": NoteDefMuseScore("42", "20", head="cross", articulation="brassMuteClosed"),
    "bass_drum": NoteDefMuseScore("36", "14"),
    "floor_tom": NoteDefMuseScore("41", "13"),
    "mid_tom": NoteDefMuseScore("45", "17"),
    "high_tom": NoteDefMuseScore("47", "19"),
    "cross_stick": NoteDefMuseScore("37", "21", head="cross"),
    "crash1": NoteDefMuseScore("49", "21", head="cross"),
    "hi_hat_open": NoteDefMuseScore("46", "12", head="cross", articulation="stringsHarmonic"),
    "ride": NoteDefMuseScore("51", "11", head="cross"),
    "ride_bell": NoteDefMuseScore("53", "13", head="diamond"),
    "flam_snare": NoteDefMuseScore("38", "16", flam=True),
    "hi_hat_foot": NoteDefMuseScore("44", "22", head="cross", stem_direction="down"),
}

@dataclass
class ExportContext():
    is_hh_open = False
    curr_time_sig_str = ""
    time_sig_has_changed = False
    split_time_sig: list[str] = None

    prev_m: Measure = None
    next_m: Measure = None

    tuplet_counter = 0

    def update_time_sig(self, new_time_sig:str):
        self.time_sig_has_changed = new_time_sig != self.curr_time_sig_str
        if self.time_sig_has_changed:
            self.curr_time_sig_str = new_time_sig
            self.split_time_sig = new_time_sig.split("/")
            assert len(self.split_time_sig) == 2


def export_song(metadata: Metadata, measures: List[Measure], exp_folder_override: Optional[str] = None):
    """
    Exports the song given as argument as an mscx file (xml).

    :param metadata: Copy of the 'metadata' object filled by the user. Must exist.
    :param measures: Copy of the 'measures' object filled by the user. Must contain at least one measure.

    """

    assert metadata, "Metadata cannot be 'None'."
    assert measures, "Measures cannot be empty."
    assert metadata.workTitle

    # Read export config
    config = read_config()
    export_folder = config.export_folder if not exp_folder_override else exp_folder_override

    # Create root document
    root = minidom.Document()
    add_xml_elem = partial(xml_handling.add_xml_elem_to_doc, root)

    xml = root.createElement("museScore")
    xml.setAttribute("version", config.msversion)
    root.appendChild(xml)

    # Program metadata
    add_xml_elem("programVersion", xml, inner_txt=config.program_version)
    add_xml_elem("programRevision", xml, inner_txt=config.program_revision)

    # Score
    score = add_xml_elem("Score", xml)
    add_xml_elem("LayerTag", score, [("id", "0"), ("tag", "default")], "")
    add_xml_elem("currentLayer", score, inner_txt="0")
    add_xml_elem("Division", score, [], "480")

    # Style (default)
    style = add_xml_elem("Style", score, [])
    add_xml_elem("pageWidth", style, [], "8.5")
    add_xml_elem("pageHeight", style, [], "11")
    add_xml_elem("Spatium", style, [], "1.74978")
    add_xml_elem("showInvisible", score, inner_txt="1")
    add_xml_elem("showUnprintable", score, inner_txt="1")
    add_xml_elem("showFrames", score, inner_txt="1")
    add_xml_elem("showMargins", score, inner_txt="0")

    metadata.mscVersion = config.msversion
    metadata.pydrumscoreVersion = pydrumscore.get_version()
    for tag in Metadata._ALL_METADATA_TAGS:
        add_xml_elem(
            "metaTag", score, [("name", tag)], inner_txt=getattr(metadata, tag)
        )

    # Inserts a pre-exported boilerplate XML file into the 'score' xml variable
    xml_part_filepath = str(Path(from_root(__file__).parent, "refxml", "PartXML.xml"))
    score.appendChild(minidom.parse(xml_part_filepath).firstChild)

    # Boilerplate for Staff
    staff = add_xml_elem("Staff", score, [("id", "1")])
    vbox = add_xml_elem("VBox", staff)
    add_xml_elem("height", vbox, inner_txt="10")
    add_xml_elem("boxAutoSize", vbox, inner_txt="0")
    text = add_xml_elem("Text", vbox)
    add_xml_elem("style", text, inner_txt="Title")
    add_xml_elem("text", text, inner_txt=metadata.workTitle)
    if metadata.subtitle:
        text = add_xml_elem("Text", vbox)
        add_xml_elem("style", text, inner_txt="Subtitle")
        add_xml_elem("text", text, inner_txt=metadata.subtitle)
    if metadata.composer:
        text = add_xml_elem("Text", vbox)
        add_xml_elem("style", text, inner_txt="Composer")
        add_xml_elem("text", text, inner_txt=metadata.composer)
    if metadata.lyricist:
        text = add_xml_elem("Text", vbox)
        add_xml_elem("style", text, inner_txt="Lyricist")
        add_xml_elem("text", text, inner_txt=metadata.lyricist)

    # Song content export starts here

    # All measures are pre-formatted for export
    # Any modifications is forbidden past this point
    for m in measures:
        m._pre_export()

    # Export context; all the stuff that is not
    # related to a single measure, but instead persists
    # over time and is needed for logic
    export_context = ExportContext()

    for m_idx, m in enumerate(measures):

        measure = add_xml_elem("Measure", staff)
        voice = add_xml_elem("voice", measure)

        all_times = m._get_combined_times()
        all_times += m._separators  # Add separators
        all_times = list(set(all_times))  # Remove duplicates
        all_times.sort()  # Read from left to right in time

        if m.dynamic:
            dynamic = add_xml_elem("Dynamic", voice)
            add_xml_elem("subtype", dynamic, inner_txt=m.dynamic)

        if m.text:
            sys_text = add_xml_elem("SystemText", voice)
            add_xml_elem("text", sys_text, inner_txt=m.text)

        if m.has_line_break:
            lyt_break = add_xml_elem("LayoutBreak", measure)
            add_xml_elem("subtype", lyt_break, inner_txt="line")

        export_context.update_time_sig(m._time_sig)
        if export_context.time_sig_has_changed:
            timesig = add_xml_elem("TimeSig", voice)
            add_xml_elem("sigN", timesig, inner_txt=export_context.split_time_sig[0])
            add_xml_elem("sigD", timesig, inner_txt=export_context.split_time_sig[1])

        # Note: Displaying the note symbol is tricky because the ref
        #       xml is malformed, and blocked by xml minidom.
        #       We might need to convert to ElementTree to make it work...
        #
        #       The reference xml does <text><sym>metNoteQuarterUp</sym> = 10</text>
        #       But, pasting that string results in the <> symbols being interpreted
        #       as regular chars. Meanwhile, parsing that string from code throws.
        #       So at the moment, we just add 'bpm' instead...
        if m.tempo:
            tempo = add_xml_elem("Tempo", voice)
            add_xml_elem("tempo", tempo, inner_txt=str(m.tempo / 60.0))
            add_xml_elem("followText", tempo, inner_txt="1")
            add_xml_elem("text", tempo, inner_txt=str(m.tempo) + " bpm")


        # Handle repeats
        is_repeat = (len(m._get_combined_times())
            and not m.no_repeat
            and m_idx != 0
            and m == export_context.prev_m)

        if (is_repeat):  # Don't use for empty measures
            repeat = add_xml_elem("RepeatMeasure", voice)
            add_xml_elem("durationType", repeat, inner_txt="measure")
            add_xml_elem("duration", repeat, inner_txt=export_context.curr_time_sig_str)
            continue

        # Counts how many chords/rests are left to complete tuplet
        # Set at first note, decreased after each and closed at 0
        export_context.tuplet_counter = 0

        for i, _ in enumerate(all_times):

            def calc_note_dur(notes: List[Fraction]):

                # Check if note on this time
                if curr_time not in notes:
                    return 0  # No note right now

                # Use gap between curr time and next time
                # We don't want longer than a quarter note dur for non-rests
                return min(until_next, 1)

            curr_time = all_times[i]
            until_next = m._get_next_time(all_times, i) - curr_time

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

            DurationXML = namedtuple(
                "DurationXML", ["durationType", "isTuplet", "isDotted"]
            )

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
            if dur_xml.isTuplet and export_context.tuplet_counter == 0:
                tuplet = add_xml_elem("Tuplet", voice)

                tuplet_dur = round(1.0 / chord_dur)  # ex. 3 for triplet
                normal_dur_str = (
                    "2" if tuplet_dur == 3 else "4" if tuplet_dur == 6 else "8"
                )

                add_xml_elem("normalNotes", tuplet, inner_txt=normal_dur_str)
                add_xml_elem("actualNotes", tuplet, inner_txt=str(tuplet_dur))
                add_xml_elem("baseNote", tuplet, inner_txt=dur_xml.durationType)
                number = add_xml_elem("Number", tuplet)
                add_xml_elem("style", number, inner_txt="Tuplet")
                add_xml_elem("text", number, inner_txt=str(tuplet_dur))

                # Init tuplet counter
                export_context.tuplet_counter = tuplet_dur

            # Handle rest (not part of "Chord" xml block)
            if is_rest:
                rest = add_xml_elem("Rest", voice)
                if dur_xml.isTuplet:
                    add_xml_elem("BeamMode", rest, inner_txt="mid")
                if dur_xml.isDotted:
                    add_xml_elem(
                        "dots", rest, inner_txt="1"
                    )  # Must be before durationType!
                add_xml_elem("durationType", rest, inner_txt=dur_xml.durationType)
                if dur_xml.durationType == "measure":
                    add_xml_elem("duration", rest, inner_txt=export_context.curr_time_sig_str)

            # Write chord (non-rest group of notes)
            else:
                chord = add_xml_elem("Chord", voice)

                if dur_xml.isDotted:
                    add_xml_elem("dots", chord, inner_txt="1")

                add_xml_elem("durationType", chord, inner_txt=dur_xml.durationType)

                accent_chord = all_durs.get("accent") is not None
                if accent_chord:
                    art = add_xml_elem("Articulation", chord)
                    add_xml_elem("subtype", art, inner_txt="articAccentAbove")
                    add_xml_elem("anchor", art, inner_txt="3")

                stem_dir = add_xml_elem("StemDirection", chord, inner_txt="up")

                def add_note(chord, notedef):

                    # If flam, add little note before main note
                    if notedef.flam:
                        acc_chord = add_xml_elem("Chord", voice, insert_before=chord)
                        acc_note = add_xml_elem("Note", acc_chord)
                        add_xml_elem(
                            "durationType",
                            acc_chord,
                            inner_txt="eighth",
                            insert_before=acc_note,
                        )
                        add_xml_elem("acciaccatura", acc_chord, insert_before=acc_note)
                        spanner = add_xml_elem(
                            "Spanner", acc_note, attr=[("type", "Tie")]
                        )
                        add_xml_elem("Tie", spanner, inner_txt="\n")
                        next_e = add_xml_elem("next", spanner)
                        add_xml_elem("location", next_e, inner_txt="\n")
                        add_xml_elem("pitch", acc_note, inner_txt=notedef.pitch)
                        add_xml_elem("tpc", acc_note, inner_txt=notedef.tpc)

                    if notedef.articulation:
                        if (
                            notedef is NOTEDEFS["hi_hat"]
                            and export_context.is_hh_open
                            or notedef is NOTEDEFS["hi_hat_open"]
                            and not export_context.is_hh_open
                        ):
                            art = add_xml_elem(
                                "Articulation", chord, insert_before=stem_dir
                            )
                            add_xml_elem("subtype", art, inner_txt=notedef.articulation)
                            add_xml_elem("anchor", art, inner_txt="3")

                    # Main note
                    note = add_xml_elem("Note", chord)

                    # Connect flam's little note with main
                    if notedef.flam:
                        spanner = add_xml_elem("Spanner", note, attr=[("type", "Tie")])
                        prev_e = add_xml_elem("prev", spanner)
                        location = add_xml_elem("location", prev_e)
                        add_xml_elem("grace", location, inner_txt="0")

                    if notedef.ghost:
                        symbol_l = add_xml_elem("Symbol", note)
                        add_xml_elem(
                            "name", symbol_l, inner_txt="noteheadParenthesisLeft"
                        )
                        symbol_r = add_xml_elem("Symbol", note)
                        add_xml_elem(
                            "name", symbol_r, inner_txt="noteheadParenthesisRight"
                        )

                    add_xml_elem("pitch", note, inner_txt=notedef.pitch)
                    add_xml_elem("tpc", note, inner_txt=notedef.tpc)

                    if notedef.ghost:
                        add_xml_elem(
                            "velocity", note, inner_txt="-50"
                        )  # Lower volume playback

                    if notedef.head:
                        add_xml_elem("head", note, inner_txt=notedef.head)

                # Add all notes at time
                for k, v in all_durs.items():
                    if v and k != "accent":
                        add_note(chord, NOTEDEFS[k])

                # Handle hi-hat open/close
                # TODO: Result is valid, but might be ugly in certain cases. To improve
                if all_durs.get("hi_hat") and all_durs.get("hi_hat_open"):
                    raise RuntimeError(
                        f"Error on measure {m_idx}: Hi-hat open and closed cannot overlap."
                    )

                export_context.is_hh_open = (
                    False
                    if all_durs.get("hi_hat")
                    else True
                    if all_durs.get("hi_hat_open")
                    else export_context.is_hh_open
                )

            # Close tuplet if needed
            if export_context.tuplet_counter > 0:
                export_context.tuplet_counter -= 1
                if export_context.tuplet_counter == 0:
                    add_xml_elem("endTuplet", voice)

        export_context.prev_m = m

    # Save
    xml_handling.save_doc_to_file(root, export_folder, metadata.workTitle + ".mscx")

