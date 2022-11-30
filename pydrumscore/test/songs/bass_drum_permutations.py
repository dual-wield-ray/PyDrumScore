# pylint: disable = missing-module-docstring

import pydrumscore as pds
from pydrumscore.beats import MONEY_BEAT

metadata = pds.Metadata(
    workTitle="Bass drum permutations",
)

measures = []

bd_perms = pds.note_range(1, pds.end(), 0.5)

for p in bd_perms:
    m = pds.Measure(MONEY_BEAT)
    if p not in m.bd:
        m.bd += [p]
        measures += m
        measures += MONEY_BEAT

        if p is not bd_perms[-1]:
            measures[-1].has_line_break = True
