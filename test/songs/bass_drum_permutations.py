from song import *
from beats import MONEY_BEAT

metadata = Metadata(
    workTitle = "Bass drum permutations",
    )

measures = []

bd_perms = Range(1, END, 0.5)
    
for p in bd_perms:
    m = Measure(MONEY_BEAT)
    if not p in m.bd:
        m.bd += [p]
        measures += m
        measures += MONEY_BEAT

        if p is not bd_perms[-1]:
            measures[-1].has_line_break = True
