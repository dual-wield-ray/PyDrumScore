from xml.dom import minidom
from typing import List, Tuple, Optional
from pathlib import Path
import os

def add_xml_elem_to_doc(
    root: minidom.Document,
    name: str,
    parent: minidom.Element,
    attr: Optional[List[Tuple[str, str]]] = None,
    inner_txt: Optional[str] = None,
    insert_before: Optional[minidom.Element] = None,
) -> minidom.Element:

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

def save_doc_to_file(doc, dir, filename):
    xml_str = doc.toprettyxml(indent="    ", encoding="UTF-8")

    if not os.path.exists(dir):
        os.makedirs(dir)

    save_path = Path(dir) / filename
    with open(save_path, "wb") as f:
        f.write(xml_str)