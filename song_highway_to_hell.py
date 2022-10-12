from song import *
from beats import *
from copy import deepcopy

def generate_metadata(song: Song):
    song.metadata = Metadata(
        workTitle = "Highway to Hell"
    )

def generate_song(song: Song):
    
    # TODO: Missing first two beats

    # Intro
    for i in range(4):
        song.add_measure(SILENCE)

    # Drums start
    for i in range(2):
        song.add_measure(MONEY_BEAT)
    for i in range(2):
        song.add_measure(HIGHWAY_GROOVE)

    # Verse 1 (Livin' easy)
    for i in range(15):
        song.add_measure(HIGHWAY_GROOVE)

    # My friends are gonna be there too
    # TODO: Flam support
    def buildup_section():
        song.add_measure(
            Measure(
            sd = [1] + Range(2, END, 0.5),
            c1 = [1],
            ft = Range(2, END, 0.5)
            ))

        song.add_measure(
            Measure(
            sd = Range(1, 4, 0.5) + [4],
            ft = Range(1, 4, 0.5)
            ))
    buildup_section()

    # Chorus
    def chorus():
        for i in range(3):
            song.add_measure(HIGHWAY_GROOVE_O)
            song.add_measure(Measure(
                sd = [2, 4],
                bd = [1, 3],
                ho = Range(1, 3, 0.5),
                c1 = [3,4]
                ))
    chorus()

    # Section before next verse 2
    # TODO: Support for hh foot
    song.add_measure(Measure(
        sd = [2, 4, 4.5],
        bd = [1, 3],
        ho = Range(1, 4, 0.5),
        c1 = [4]
        ))

    for i in range(2):
        m = Measure(
            hh = Range(1, END, 1),
            )
        if i == 1:
            m.sd = [3.5]
            m.mt = [4]
            m.c1 = [4.5]
            m.bd = [4.5]

        song.add_measure(m)

    # Verse 2 (No stop sign)
    for i in range(15):
        m = deepcopy(HIGHWAY_GROOVE)

        if i == 0:
            m.bd = m.bd[1:]
        if i >= 8 and i not in [10,13]:
            m.ho += [2]
            m.hh.remove(2)

        song.add_measure(m)

    # Reuses buildup section to chorus 2
    buildup_section()

    # Reuse chorus
    chorus()
