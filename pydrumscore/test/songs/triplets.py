# pylint: disable = missing-module-docstring

from typing import List
from pydrumscore import Measure, note_range, Metadata, end

metadata = Metadata(
    workTitle = "Triplets",
    )

measures:List[Measure] = []

for i in range(12):
    measures += Measure(
        sd = note_range(1, end(), 1/3, excl=[1 + i/3])
    )

measures[-1].has_line_break = True

for i in range(12):
    measures += Measure(
        sd = note_range(1, end(), 1/3, excl=[1 + i/3, 1 + (i+1)/3])
    )
