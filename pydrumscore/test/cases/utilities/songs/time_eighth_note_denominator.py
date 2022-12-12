# pylint: disable = missing-module-docstring

import pydrumscore as pds

metadata = pds.Metadata(
    workTitle="Eighth Note Denominator",
)

measures = []

for n in range(1, 13):
    pds.set_time_signature(f"{str(n)}/8")
    measures += pds.Measure(snare=pds.note_range(1, pds.end(), 0.5))
