# pylint: disable = missing-module-docstring

import pydrumscore as api
from pydrumscore.core.beats import SILENCE

metadata = api.Metadata(workTitle="Text on first measure")

measures = [SILENCE]

measures[0].text = "This is some text"
