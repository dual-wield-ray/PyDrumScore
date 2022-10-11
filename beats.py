from song import *

MONEY_BEAT = Measure(
    sd = [2, 4],
    bd = [1, 3],
    hh = Range(1, END, 0.5)
    )

ROCK_BEAT = Measure(
    sd = [2,4],
    bd = [1,3,3.5],
    hh = Range(1, END, 0.5)
    )

SHUFFLE_BEAT = Measure(
    sd = [2,4],
    bd = [1,3],
    hh = Range(1, END, 1) + [1.66, 2.66, 3.66, 4.66]
    )

