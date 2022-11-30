# pylint: disable = missing-module-docstring

import pydrumscore as pds
from pydrumscore.beats import SILENCE

metadata = pds.Metadata(workTitle="Text on first measure")

measures = [SILENCE]

measures[0].text = "This is some text"
