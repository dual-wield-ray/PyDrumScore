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
from song import Song

# TODO: Put in a proper config file, and/or generate from installed MS version
MS_VERSION = "3.02"
PROGRAM_VERSION = "3.6.2"
PROGRAM_REVISION = "3224f34"

# Defines how instruments on the drumset are represented
NoteDef = namedtuple("NoteDef", ["pitch", "tpc", "head"])
NOTEDEF_BD = NoteDef("36", "14", None)
NOTEDEF_SD = NoteDef("38", "16", None)
NOTEDEF_HH = NoteDef("42", "20", "cross")

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
    for m in song.measures:
        m._pre_export()  # Shift indices to start at 0

    needs_time_sig = True
    for m in song.measures:
        measure = addElement("Measure", staff)
        voice = addElement("voice", measure)

        # Needs time signature to the first measure only
        # TODO: Support for other than 4/4
        if needs_time_sig:
            timesig = addElement("TimeSig", voice)
            addElement("sigN", timesig, inner_txt="4")
            addElement("sigD", timesig, inner_txt="4")
            needs_time_sig = False

        all_times = m.hh + m.sd + m.bd  # Combine all times in the measure that contain a note
        
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
            next_time = all_times[i+1] if i < len(all_times)-1 else 4
            until_next = next_time - curr_time

            hh_dur = calc_note_dur(m.hh)
            sd_dur = calc_note_dur(m.sd)
            bd_dur = calc_note_dur(m.bd)
            all_durs = [hh_dur, sd_dur, bd_dur]

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

                if dur == 1.0:
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
                if dur_xml.isDotted:
                    addElement("dots", chord, inner_txt="1")

            # Write chord (non-rest group of notes)
            else:
                chord = addElement("Chord", voice)

                if dur_xml.isDotted:
                    addElement("dots", chord, inner_txt="1")

                addElement("durationType", chord, inner_txt=dur_xml.durationType)
                addElement("StemDirection", chord, inner_txt="up")

                def addNote(chord, noteDef):
                    note = addElement("Note", chord)
                    addElement("pitch", note, inner_txt=noteDef.pitch)
                    addElement("tpc", note, inner_txt=noteDef.tpc)
                    if noteDef.head:
                        addElement("head", note, inner_txt=noteDef.head)

                if bd_dur:
                    addNote(chord, NOTEDEF_BD)
                if sd_dur:
                    addNote(chord, NOTEDEF_SD)
                if hh_dur:
                    addNote(chord, NOTEDEF_HH)

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
    mod.generate_metadata(out_song)
    mod.generate_song(out_song)

    exportSong(out_song)

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
                module_import_str = foundRelPath.split('.')[0]  # Combine path and strip extension
                module_import_str = ".".join(module_import_str.split("\\"))  # Convert to module syntax
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

