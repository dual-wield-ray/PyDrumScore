from beats import MONEY_BEAT
from song import *
from copy import deepcopy

def generate_metadata(song: Song):
    song.metadata = Metadata(
        workTitle = "Bass drum permutations",
        )

def generate_song(song: Song):

    bd_perms = Range(1, END, 0.5)
    
    for p in bd_perms:
        m = deepcopy(MONEY_BEAT)
        if not p in m.bd:
            m.bd += [p]
            song.add_measure(m)
            song.add_measure(MONEY_BEAT)

            if p is not bd_perms[-1]:
                song.add_line_break()
