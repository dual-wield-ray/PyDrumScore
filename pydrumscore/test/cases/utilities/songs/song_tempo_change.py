# pylint: disable = missing-module-docstring

from typing import List
import pydrumscore as pds
from pydrumscore import Measure

metadata = pds.Metadata(workTitle="Test tempo change")

measures: List[Measure] = []

# Test default value of tempo when there is nothing
measures += Measure()

measures += Measure(tempo=110)

measures += Measure(tempo=120)

measures += Measure()
measures[-1].tempo = 60

measures += Measure()
measures[-1].tempo = 10
