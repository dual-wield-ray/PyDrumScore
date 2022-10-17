# Built-in modules
import os
import sys
import importlib
import math
from xml.dom import minidom
from collections import namedtuple
from types import ModuleType
from typing import List, Tuple

# Local modules
from song import Song, Measure

# TODO: Put in a proper config file, and/or generate from installed MS version
MS_VERSION = "3.02"
PROGRAM_VERSION = "3.6.2"
PROGRAM_REVISION = "3224f34"

# Defines how instruments on the drumset are represented
NoteDef = namedtuple("NoteDef", ["pitch", "tpc", "head", "articulation"])
NOTEDEF_BD = NoteDef("36", "14", None, "")
NOTEDEF_SD = NoteDef("38", "16", None, "")
NOTEDEF_HH = NoteDef("42", "20", "cross", "brassMuteClosed")
NOTEDEF_FT = NoteDef("41", "13", None, "")
NOTEDEF_MT = NoteDef("45", "17", None, "")
NOTEDEF_HT = NoteDef("47", "19", None, "")
NOTEDEF_CS = NoteDef("37", "21", "cross", "")
NOTEDEF_C1 = NoteDef("49", "21", "cross", "")
NOTEDEF_HO = NoteDef("46", "12", "cross", "stringsHarmonic")
NOTEDEF_RD = NoteDef("51", "11", "cross", "")
NOTEDEF_RB = NoteDef("53", "13", "diamond", "")

# TODO: Temp, make more flexible
EXPORT_FOLDER = os.path.join("test", "_generated")


def exportSong(song: Song):
    """
    Exports the song given as argument as an mscx file (xml).
    :param song: The song to export
    """

    # Utilities
    def addElement(name: str, parent, attr: List[Tuple[str,str]] = [], inner_txt = None):

        e = root.createElement(name)
        for attr_pair in attr:
            e.setAttribute(attr_pair[0], attr_pair[1])

        # Note: Adding empty strings in xml better follows MS format
        if inner_txt != None:
            e.appendChild(root.createTextNode(inner_txt))

        parent.appendChild(e)

        return e

    # Create root document
    root = minidom.Document()
    xml = root.createElement('museScore')
    xml.setAttribute("version", MS_VERSION)
    root.appendChild(xml)

    # Program metadata
    addElement("programVersion", xml, inner_txt=PROGRAM_VERSION)
    addElement("programRevision", xml, inner_txt=PROGRAM_REVISION)

    # Score
    score = addElement("Score", xml)
    addElement("LayerTag", score, [("id", "0"), ("tag", "default")], "")
    addElement("currentLayer", score, inner_txt="0")
    addElement("Division", score, [], "480")

    # Style
    style = addElement("Style", score, [])
    addElement("pageWidth", style, [], "8.5")
    addElement("pageHeight", style, [], "11")
    addElement("Spatium", style, [], "1.74978")

    addElement("showInvisible", score, inner_txt="1")
    addElement("showUnprintable", score, inner_txt="1")
    addElement("showFrames", score, inner_txt="1")
    addElement("showMargins", score, inner_txt="0")

    addElement("metaTag", score, [("name", "arranger")], inner_txt=song.metadata.arranger)
    addElement("metaTag", score, [("name", "composer")], inner_txt=song.metadata.composer)
    addElement("metaTag", score, [("name", "copyright")], inner_txt=song.metadata.copyright)
    addElement("metaTag", score, [("name", "creationDate")], inner_txt=song.metadata.creationDate)
    addElement("metaTag", score, [("name", "lyricist")], inner_txt=song.metadata.lyricist)
    addElement("metaTag", score, [("name", "movementNumber")], inner_txt=song.metadata.movementNumber)
    addElement("metaTag", score, [("name", "movementTitle")], inner_txt=song.metadata.movementTitle)
    addElement("metaTag", score, [("name", "mscVersion")], inner_txt=MS_VERSION)
    addElement("metaTag", score, [("name", "platform")], inner_txt=song.metadata.platform)
    addElement("metaTag", score, [("name", "poet")], inner_txt=song.metadata.poet)
    addElement("metaTag", score, [("name", "source")], inner_txt=song.metadata.source)
    addElement("metaTag", score, [("name", "translator")], inner_txt=song.metadata.translator)
    addElement("metaTag", score, [("name", "workNumber")], inner_txt=song.metadata.workNumber)
    addElement("metaTag", score, [("name", "workTitle")], inner_txt=song.metadata.workTitle)

    # Boilerplate for defining the drumset instrument
    # Copied from a valid exported score
    def addXMLSnippet(path):
        """
        Inserts an XML file into the 'score' xml variable.
        Also cleans the file of whitespace before doing so.
        """
        def cleanXMLWhiteSpace(xml_doc):
            xml_str = xml_doc.toxml()
            xml_str = xml_str.replace('\n', '')
            xml_str = xml_str.replace('\t', '')
            xml_str = xml_str.replace('>    <', '><')
            return minidom.parseString(xml_str)

        xml_doc = minidom.parse(path)
        xml_doc = cleanXMLWhiteSpace(xml_doc)
        xml_doc = xml_doc.firstChild
        score.appendChild(xml_doc)

    addXMLSnippet("ReferenceXML/PartXML.xml")

    # Boilerplate for Staff
    staff = addElement("Staff", score, [("id", "1")])
    vbox = addElement("VBox", staff)
    addElement("height", vbox, inner_txt="10")
    addElement("boxAutoSize", vbox, inner_txt="0")
    text = addElement("Text", vbox)
    addElement("style", text, inner_txt="Title")
    addElement("text", text, inner_txt=song.metadata.workTitle)

    # Song data export starts

    # TODO: Rethink this
    if not song.measures[0].time_sig:
        song.measures[0].time_sig = "4/4"

    if not song.measures[0].tempo:
        song.measures[0].tempo = 100

    for m in song.measures:
        m._pre_export()  # Shift indices to start at 0
    
    # Keep track of hh state so we don't spam with O and +
    is_hh_open = False
    curr_time_sig = ""
    curr_time_sigN = -1

    for m_idx, m in enumerate(song.measures):
        
        measure = addElement("Measure", staff)
        voice = addElement("voice", measure)

        if m.has_line_break:
            lyt_break = addElement("LayoutBreak", measure)
            addElement("subtype", lyt_break, inner_txt="line")

        if m.time_sig:
            curr_time_sig = m.time_sig
            split_sig = m.time_sig.split("/")
            assert len(split_sig) == 2
            curr_time_sigN = float(split_sig[0])

            timesig = addElement("TimeSig", voice)
            addElement("sigN", timesig, inner_txt=split_sig[0])
            addElement("sigD", timesig, inner_txt=split_sig[1])

        # TODO: Fix the text and note icon not appearing
        #if m.tempo:
        #    tempo = addElement("Tempo", measure)
        #    addElement("tempo", tempo, inner_txt=str(m.tempo/60.0))
        #    addElement("followText", tempo, inner_txt="1")
            #text_e = addElement("text", tempo, inner_txt=str('<b></b><font face="ScoreText"/>O<b><font face="Edwin"/> = 200</b>'))
            #addElement("b", text_e, inner_txt="")
            #font = addElement("font", text_e, attr=[("face", "ScoreText")])


        all_times = m.get_combined_times()  # Combine all times in the measure that contain a note

        if not m_idx == 0:
            if m == song.measures[m_idx-1] and len(all_times):
                repeat = addElement("RepeatMeasure", voice)
                addElement("durationType", repeat, inner_txt="measure")
                addElement("duration", repeat, inner_txt="4/4")
                continue
        
        # Add these as extra separators for each beat
        # Prevents ex. quarter notes going over a beat when on the "and"
        all_times += m.separators

        all_times = list(set(all_times))  # Remove duplicates
        all_times.sort()  # Read from left to right in time

        # Counts how many chords/rests are left to complete tuplet
        # Set at first note, decreased after each and closed at 0
        tuplet_counter = 0

        for i in range(len(all_times)):

            def calc_note_dur(notes):

                # Check if note on this time
                try:
                    notes.index(curr_time)
                except ValueError:
                    return 0    # No note right now

                # Use gap between curr time and next time
                duration = until_next
                
                # For notes, we don't want longer than a quarter
                if duration > 1:
                    duration = 1

                return duration

            curr_time = all_times[i]
            next_time = all_times[i+1] if i < len(all_times)-1 else curr_time_sigN
            until_next = next_time - curr_time

            # TODO: Cleanup
            hh_dur = calc_note_dur(m.hh)
            sd_dur = calc_note_dur(m.sd)
            bd_dur = calc_note_dur(m.bd)
            ft_dur = calc_note_dur(m.ft)
            mt_dur = calc_note_dur(m.mt)
            ht_dur = calc_note_dur(m.ht)
            cs_dur = calc_note_dur(m.cs)
            c1_dur = calc_note_dur(m.c1)
            ho_dur = calc_note_dur(m.ho)
            rd_dur = calc_note_dur(m.rd)
            rb_dur = calc_note_dur(m.rb)

            all_durs = [
                hh_dur,
                sd_dur,
                bd_dur,
                ft_dur,
                mt_dur,
                ht_dur,
                cs_dur,
                c1_dur,
                ho_dur,
                rd_dur,
                rb_dur]
            # End TODO

            # Remove zero before getting min value of voice
            all_durs = [i for i in all_durs if i != 0]

            # If note, stems are connected => shortest becomes value of all
            # Rests fill the value of the gap
            is_rest = len(all_durs) == 0
            chord_dur = min(all_durs) if not is_rest else until_next

            DurationXML = namedtuple("DurationXML", ["durationType", "isTuplet", "isDotted"])
            def get_duration_xml(dur):

                dotted = False  # TODO: Find way to not dot *everything* in the chord...
                triplet = False
                dur_str = ""
                if dur == curr_time_sigN:
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
                elif math.isclose(dur, 0.33) \
                    or math.isclose(dur, 0.34):
                    triplet = True
                    dur_str = "eighth"
                elif math.isclose(dur, 0.66) or math.isclose(dur, 0.67):
                    assert False, "Invalid note duration in tuplet"
                elif dur ==  0.25:
                    dur_str = "16th"

                assert dur_str != "", "Generating chord duration failed."

                return DurationXML(dur_str, triplet, dotted)

            dur_xml = get_duration_xml(chord_dur)

            # Handle tuplet header
            # TODO: More than just triplets!
            if dur_xml.isTuplet and tuplet_counter == 0:
                tuplet = addElement("Tuplet", voice)
                addElement("normalNotes", tuplet, inner_txt="2")
                addElement("actualNotes", tuplet, inner_txt="3")
                addElement("baseNote", tuplet, inner_txt="eighth")
                number = addElement("Number", tuplet)
                addElement("style", number, inner_txt="Tuplet")
                addElement("text", number, inner_txt="3")
                
                tuplet_counter = 3

            # Write rest
            if is_rest:
                rest = addElement("Rest", voice)
                if dur_xml.isTuplet:
                    addElement("BeamMode", rest, inner_txt="mid")
                addElement("durationType", rest, inner_txt=dur_xml.durationType)
                if (dur_xml.durationType == "measure"):
                    addElement("duration", rest, inner_txt=curr_time_sig)

                if dur_xml.isDotted:
                    addElement("dots", chord, inner_txt="1")

            # Write chord (non-rest group of notes)
            else:
                chord = addElement("Chord", voice)

                if dur_xml.isDotted:
                    addElement("dots", chord, inner_txt="1")

                addElement("durationType", chord, inner_txt=dur_xml.durationType)
                addElement("StemDirection", chord, inner_txt="up")

                def addNote(chord, noteDef, is_hh_open=False):

                    note = addElement("Note", chord)
                    addElement("pitch", note, inner_txt=noteDef.pitch)
                    addElement("tpc", note, inner_txt=noteDef.tpc)
                    
                    if noteDef.head:
                        addElement("head", note, inner_txt=noteDef.head)

                    if noteDef.articulation:
                        if noteDef is NOTEDEF_HH and is_hh_open \
                        or noteDef is NOTEDEF_HO and not is_hh_open:
                            art = addElement("Articulation", chord)
                            addElement("subtype", art, inner_txt=noteDef.articulation)
                            addElement("anchor", art, inner_txt="3")

                # TODO: Cleanup
                assert not (hh_dur and ho_dur)
                if bd_dur: addNote(chord, NOTEDEF_BD)
                if sd_dur: addNote(chord, NOTEDEF_SD)
                if hh_dur: addNote(chord, NOTEDEF_HH, is_hh_open)
                if ft_dur: addNote(chord, NOTEDEF_FT)
                if mt_dur: addNote(chord, NOTEDEF_MT)
                if ht_dur: addNote(chord, NOTEDEF_HT)
                if cs_dur: addNote(chord, NOTEDEF_CS)
                if c1_dur: addNote(chord, NOTEDEF_C1)
                if ho_dur: addNote(chord, NOTEDEF_HO, is_hh_open)
                if rd_dur: addNote(chord, NOTEDEF_RD)
                if rb_dur: addNote(chord, NOTEDEF_RB)

                # TODO: This behaviour might not be always pretty
                if hh_dur: is_hh_open = False
                elif ho_dur: is_hh_open = True
                

            # Close triplet if needed
            if tuplet_counter > 0:
                tuplet_counter -= 1
                if tuplet_counter == 0:
                    addElement("endTuplet", voice)

    # Save
    xml_str = root.toprettyxml(indent = "\t", encoding="UTF-8")
    if not os.path.exists(EXPORT_FOLDER):
        os.mkdir(EXPORT_FOLDER)

    assert song.metadata.fileName or song.metadata.workTitle

    filename = song.metadata.fileName if song.metadata.fileName \
               else song.metadata.workTitle + ".mscx"

    save_path = os.path.join(EXPORT_FOLDER, filename)
    with open(save_path, "wb") as f:
        f.write(xml_str)


def export_from_module(mod: ModuleType):

    # TODO: Proper logging
    print("Exporting song '" + mod.__name__.split('.')[-1] + "'")

    out_song = Song()
    out_song.metadata = mod.metadata
    out_song.measures = [Measure(m) for m in mod.measures]

    exportSong(out_song)

    print("Export completed successfully.")

    return out_song


def main():
    """
    Exports a song file provided by command line argument.

    Example for a song file "my_song.py":
        python export.py my_song

    The song file can be in any folder of the configured song directory (TODO!).
    """

    if not len(sys.argv):
        print("Error: Must give file name as argument")
        print("Type 'help()' for more info.")
        return

    filename = sys.argv[1]

    # Find file in subdirectories
    rootDir = os.path.abspath(os.path.dirname(__file__))

    module_import_str = ""
    foundRelPath = ""
    for folder, _, files in os.walk(rootDir):

        # TODO: Terribly ugly section
        relpath = os.path.relpath(folder, rootDir)
        if relpath == ".":
            relpath = ""
        split_path = relpath.split("\\")

        ignore = False
        for p in split_path:
            if p.startswith(".") or p.startswith("_"):
                ignore = True
                break
        if ignore:
            continue
        # End ugly section

        for f in files:
            f = f.rsplit('.', 1)[0]  # Strip extension
            if filename == f:
                # Build module import string
                # TODO: Not sure if slashes are consistent across platforms...
                foundRelPath = os.path.join(relpath, f)
                module_import_str = ".".join(foundRelPath.split("\\"))  # Convert to module syntax
                break
    
    if not module_import_str:
        print("Error: Could not find file '" + filename + "' given as argument.")
        return -1

    print("Found file to export in location: " + foundRelPath)

    # Import module and export result
    # TODO: Might fail?
    song_module = importlib.import_module(module_import_str)
    export_from_module(song_module)

    return 0

if __name__ == "__main__":
    main()

