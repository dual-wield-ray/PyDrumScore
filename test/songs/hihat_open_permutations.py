from song import *
from beats import MONEY_BEAT

metadata = Metadata(
    workTitle = "Hi-hat open permutations",
    )

measures = []

hho_perms = Range(1, END, 0.5)
for p in hho_perms:
    m = Measure(MONEY_BEAT)

    m.hh.remove(p)
    m.ho += [p]

    measures += m
    measures += MONEY_BEAT

    if p is not hho_perms[-1]:
        measures[-1].has_line_break = True
