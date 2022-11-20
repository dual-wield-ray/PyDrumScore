# pylint: disable = missing-module-docstring

import random

import pydrumscore.core.song as api
from pydrumscore.core.beats import MONEY_BEAT

metadata = api.Metadata(
    workTitle = "Bass drum permutations, shuffled",
    )

measures = []

NUM_MEASURES = 13
bd_perms = api.note_range(1, api.end, 0.5)

for n in range(NUM_MEASURES):
    m = api.Measure(MONEY_BEAT)
    r = random.randrange(0,len(bd_perms))
    p = bd_perms[r]
    if not p in m.bd:
        m.bd += [p]
        measures += m
        measures += MONEY_BEAT

        # if n != num_measures-1:
        measures[-1].has_line_break = True


NUM_MEASURES_FULL_SHUFFLE = 10
for n in range(NUM_MEASURES_FULL_SHUFFLE):
    for _ in range(2):
        m = api.Measure(MONEY_BEAT)
        m.no_repeat = True
        r = random.randrange(0,len(bd_perms))
        while bd_perms[r] in m.bd:
            r = random.randrange(0,len(bd_perms))
            continue
        m.bd += [bd_perms[r]]
        measures += m

    if n != NUM_MEASURES_FULL_SHUFFLE-1:
        measures[-1].has_line_break = True
