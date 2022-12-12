# pylint: disable = missing-module-docstring

import pydrumscore as pds

metadata = pds.Metadata(
    workTitle="Time Signature Simple Change",
)

measures = []

for n in range(1, 13):
    pds.set_time_signature(f"{str(n)}/4")
    measures += pds.Measure(sd=pds.note_range(1, pds.end(), 1))
