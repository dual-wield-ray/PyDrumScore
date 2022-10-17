from beats import MONEY_BEAT
from song import *
from copy import deepcopy

def generate_metadata(song: Song):
    song.metadata = Metadata(
        workTitle = "Hi-hat open permutations",
        )

def generate_song(song: Song):

    hho_perms = Range(1, END, 0.5)
    
    for p in hho_perms:
        m = deepcopy(MONEY_BEAT)

        m.hh.remove(p)
        m.ho += [p]

        song.add_measure(m)
        song.add_measure(MONEY_BEAT)

        if p is not hho_perms[-1]:
            song.add_line_break()
