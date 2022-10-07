from xml.dom import minidom

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

def cleanXMLWhiteSpace(xml_doc):
    xml_str = xml_doc.toxml()
    xml_str = xml_str.replace('\n', '')
    xml_str = xml_str.replace('\t', '')
    xml_str = xml_str.replace('>    <', '><')
    return minidom.parseString(xml_str)

# Create root
root = minidom.Document()
xml = root.createElement('museScore')
xml.setAttribute("version", "3.02")
root.appendChild(xml)

# Program metadata
programVersion = root.createElement("programVersion")
programVersionTxt = root.createTextNode("3.6.2")
programVersion.appendChild(programVersionTxt)
xml.appendChild(programVersion)

programRevision = root.createElement("programRevision")
programRevisionTxt = root.createTextNode("3224f34")
programRevision.appendChild(programRevisionTxt)
xml.appendChild(programRevision)

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

# TODO: remove dummy metadata
title = "Drum Scoring!"
addElement("metaTag", score, [("name", "arranger")], text="")
addElement("metaTag", score, [("name", "composer")], text="")
addElement("metaTag", score, [("name", "copyright")], text="")
addElement("metaTag", score, [("name", "creationDate")], text="2022-10-07")
addElement("metaTag", score, [("name", "lyricist")], text="")
addElement("metaTag", score, [("name", "movementNumber")], text="")
addElement("metaTag", score, [("name", "movementTitle")], text="")
addElement("metaTag", score, [("name", "platform")], text="Microsoft Windows")
addElement("metaTag", score, [("name", "poet")], text="")
addElement("metaTag", score, [("name", "source")], text="")
addElement("metaTag", score, [("name", "translator")], text="")
addElement("metaTag", score, [("name", "workNumber")], text="")
addElement("metaTag", score, [("name", "workTitle")], text=title)

# Boilerplate for drums
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
addElement("text", text, text=title)

# Measures start here!
measure = addElement("Measure", staff)
voice = addElement("voice", measure)
timesig = addElement("TimeSig", voice) # Only for first measure
addElement("sigN", timesig, text="4")
addElement("sigD", timesig, text="4")
rest = addElement("Rest", voice)
addElement("durationType", rest, text="whole")

voice = addElement("voice", measure)
rest = addElement("Rest", voice)
addElement("durationType", rest, text="whole")

# Save
xml_str = root.toprettyxml(indent = "\t", encoding="UTF-8")
save_path_file = "test.mscx"
with open(save_path_file, "wb") as f:
    f.write(xml_str)