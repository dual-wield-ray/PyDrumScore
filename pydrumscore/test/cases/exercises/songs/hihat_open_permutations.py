# pylint: disable = missing-module-docstring

import pydrumscore as pds
from pydrumscore.beats import MONEY_BEAT

metadata = pds.Metadata(
    workTitle="Hi-hat open permutations",
)

measures = []

hho_perms = pds.note_range(1, pds.end(), 0.5)
for p in hho_perms:
    m = pds.Measure(MONEY_BEAT)

    m.hh.remove(p)
    m.ho += [p]

    measures += m
    measures += MONEY_BEAT

    if p is not hho_perms[-1]:
        measures[-1].has_line_break = True
