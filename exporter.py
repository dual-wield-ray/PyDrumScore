from bitstring import BitString
from xml.dom import minidom

# TODO: Put in a proper config file
MU_VERSION = "3.02"
PROGRAM_VERSION = "3.6.2"
PROGRAM_REVISION = "3224f34"

class Metadata():
    arranger = ""
    composer = ""
    copyright = ""
    creationDate = ""
    lyricist = ""
    movementNumber = ""
    movementTitle = ""
    platform = ""
    poet = ""
    source = ""
    translator = ""
    workNumber = ""
    workTitle = "Drum Score"

    fileName = "DrumScore.mscx"

def exportSong(metadata, measures):

    # Utilities
    def addElement(name, parent, attributes = [], text = None):
        elem = root.createElement(name)
        for attr_pair in attributes:
            elem.setAttribute(attr_pair[0], attr_pair[1])

        if text is not None:
            text_node = root.createTextNode(text)
            elem.appendChild(text_node)

        parent.appendChild(elem)

        return elem

    def addHiHatNote(chord, durationType):
        note = addElement("Note", chord)
        addElement("pitch", note, text="42")
        addElement("tpc", note, text="20")
        addElement("head", note, text="cross")

    def addSnareNote(chord, durationType):
        note = addElement("Note", chord)
        addElement("pitch", note, text="38")
        addElement("tpc", note, text="16")

    def addBassNote(chord, durationType):
        note = addElement("Note", chord)
        addElement("pitch", note, text="36")
        addElement("tpc", note, text="14")

    def cleanXMLWhiteSpace(xml_doc):
        xml_str = xml_doc.toxml()
        xml_str = xml_str.replace('\n', '')
        xml_str = xml_str.replace('\t', '')
        xml_str = xml_str.replace('>    <', '><')
        return minidom.parseString(xml_str)

    # Create root
    root = minidom.Document()
    xml = root.createElement('museScore')
    xml.setAttribute("version", MU_VERSION)
    root.appendChild(xml)

    # Program metadata
    addElement("programVersion", xml, text=PROGRAM_VERSION)
    addElement("programRevision", xml, text=PROGRAM_REVISION)

    # Score
    score = addElement("Score", xml)
    addElement("LayerTag", score, [("id", "0"), ("tag", "default")], "")
    addElement("currentLayer", score, text="0")
    addElement("Division", score, [], "480")

    # Style
    style = addElement("Style", score, [])
    addElement("pageWidth", style, [], "8.5")
    addElement("pageHeight", style, [], "11")
    addElement("enableVerticalSpread", style, [], "1")
    addElement("Spatium", style, [], "1.74978")

    addElement("showInvisible", score, text="1")
    addElement("showUnprintable", score, text="1")
    addElement("showFrames", score, text="1")
    addElement("showMargins", score, text="0")

    # TODO: All of them really needed in meta config? Poet??
    addElement("metaTag", score, [("name", "arranger")], text=metadata.arranger)
    addElement("metaTag", score, [("name", "composer")], text=metadata.composer)
    addElement("metaTag", score, [("name", "copyright")], text=metadata.copyright)
    addElement("metaTag", score, [("name", "creationDate")], text=metadata.creationDate)
    addElement("metaTag", score, [("name", "lyricist")], text=metadata.lyricist)
    addElement("metaTag", score, [("name", "movementNumber")], text=metadata.movementNumber)
    addElement("metaTag", score, [("name", "movementTitle")], text=metadata.movementTitle)
    addElement("metaTag", score, [("name", "platform")], text=metadata.platform)
    addElement("metaTag", score, [("name", "poet")], text=metadata.poet)
    addElement("metaTag", score, [("name", "source")], text=metadata.source)
    addElement("metaTag", score, [("name", "translator")], text=metadata.translator)
    addElement("metaTag", score, [("name", "workNumber")], text=metadata.workNumber)
    addElement("metaTag", score, [("name", "workTitle")], text=metadata.workTitle)

    # Boilerplate for drumset part
    order = minidom.parse("ReferenceXML/OrderXML.xml")
    order = cleanXMLWhiteSpace(order)
    order = order.firstChild
    score.appendChild(order)

    part = minidom.parse("ReferenceXML/PartXML.xml")
    part = cleanXMLWhiteSpace(part)
    part = part.firstChild
    score.appendChild(part)

    # Staff
    staff = addElement("Staff", score, [("id", "1")])
    vbox = addElement("VBox", staff)
    addElement("height", vbox, text="10")
    text = addElement("Text", vbox)
    addElement("style", text, text="Title")
    addElement("text", text, text=metadata.workTitle)

    # Measures start here!

    for (i, m) in enumerate(measures):
        measure = addElement("Measure", staff)
        voice = addElement("voice", measure)

        #TODO: Support for other than 4/4
        if i == 0:
            timesig = addElement("TimeSig", voice) # Only for first measure
            addElement("sigN", timesig, text="4")
            addElement("sigD", timesig, text="4")

        all_chords = m.hh + m.sd + m.bd
        all_chords = list(set(all_chords))
        all_chords.sort()

        for i, chord_time in enumerate(all_chords):

            def calculate_note_duration(notes, note_time):

                # TODO: Float precision?
                note_idx = -1
                try:
                    note_idx = notes.index(note_time)
                except ValueError:
                    note_idx = -1

                if note_idx != -1:
                    duration = next_chord_val - note_time
                
                    if duration > 1:
                        duration = 1

                    return duration
                
                return 0

            next_chord_val = all_chords[i+1] if i < len(all_chords)-1 else 4

            chord = addElement("Chord", voice)

            hh_duration = calculate_note_duration(m.hh, chord_time)
            sd_duration = calculate_note_duration(m.sd, chord_time)
            bd_duration = calculate_note_duration(m.bd, chord_time)
            all_durations = [hh_duration, sd_duration, bd_duration]
            all_durations = [i for i in all_durations if i != 0]
            chord_duration = min(all_durations)

            chord_duration_str = ""
            match chord_duration:
                case 1.0:
                    chord_duration_str = "quarter"
                case 0.5:
                    chord_duration_str = "eighth"
                case 0.25:
                    chord_duration_str = "16th"

            assert(chord_duration_str)
            addElement("durationType", chord, text=chord_duration_str)
            addElement("StemDirection", chord, text="up")

            if hh_duration:
                addHiHatNote(chord, chord_duration_str)
            if sd_duration:
                addSnareNote(chord, chord_duration_str)
            if bd_duration:
                addBassNote(chord, chord_duration_str)

    # Save
    xml_str = root.toprettyxml(indent = "\t", encoding="UTF-8")
    save_path_file = metadata.fileName
    with open(save_path_file, "wb") as f:
        f.write(xml_str)
