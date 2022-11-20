# pylint: disable = missing-module-docstring

import pydrumscore.core.song as api
from pydrumscore.core.beats import MONEY_BEAT

metadata = api.Metadata(
    workTitle = "Bass drum permutations",
    )

measures = []

bd_perms = api.note_range(1, api.end, 0.5)

for p in bd_perms:
    m = api.Measure(MONEY_BEAT)
    if not p in m.bd:
        m.bd += [p]
        measures += m
        measures += MONEY_BEAT

        if p is not bd_perms[-1]:
            measures[-1].has_line_break = True
