# pylint: disable = missing-module-docstring

import random

import pydrumscore as pds
from pydrumscore.beats import MONEY_BEAT

metadata = pds.Metadata(
    workTitle="Bass drum permutations, shuffled",
)

measures = []

NUM_MEASURES = 13
bd_perms = pds.note_range(1, pds.end(), 0.5)

for n in range(NUM_MEASURES):
    m = pds.Measure(MONEY_BEAT)
    r = random.randrange(0, len(bd_perms))
    p = bd_perms[r]
    if p not in m.bd:
        m.bd += [p]
        measures += m
        measures += MONEY_BEAT

        measures[-1].has_line_break = True


NUM_MEASURES_FULL_SHUFFLE = 10
for n in range(NUM_MEASURES_FULL_SHUFFLE):
    for _ in range(2):
        m = pds.Measure(MONEY_BEAT)
        m.no_repeat = True
        r = random.randrange(0, len(bd_perms))
        while bd_perms[r] in m.bd:
            r = random.randrange(0, len(bd_perms))
            continue
        m.bd += [bd_perms[r]]
        measures += m

    if n != NUM_MEASURES_FULL_SHUFFLE - 1:
        measures[-1].has_line_break = True
