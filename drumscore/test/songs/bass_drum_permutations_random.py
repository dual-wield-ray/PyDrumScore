import random

import drumscore.core.song as api
from drumscore.core.beats import MONEY_BEAT

metadata = api.Metadata(
    workTitle = "Bass drum permutations, shuffled",
    )

measures = []

num_measures = 13
bd_perms = api.note_range(1, api.END, 0.5)

for n in range(num_measures):
    m = api.Measure(MONEY_BEAT)
    r = random.randrange(0,len(bd_perms))
    p = bd_perms[r]
    if not p in m.bd:
        m.bd += [p]
        measures += m
        measures += MONEY_BEAT

        # if n != num_measures-1:
        measures[-1].has_line_break = True


num_measures_full_shuffle = 10
for n in range(num_measures_full_shuffle):
    for _ in range(2):
        m = api.Measure(MONEY_BEAT)
        m.no_repeat = True
        r = random.randrange(0,len(bd_perms))
        while(bd_perms[r] in m.bd):
            r = random.randrange(0,len(bd_perms))
            continue
        m.bd += [bd_perms[r]]
        measures += m

    if n != num_measures_full_shuffle-1:
        measures[-1].has_line_break = True
