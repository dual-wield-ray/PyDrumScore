# pylint: disable = missing-module-docstring, missing-function-docstring

from copy import deepcopy
from pydrumscore.core.song import Measure, Metadata, note_range, end
from pydrumscore.core.beats import SILENCE

metadata = Metadata(
    workTitle = "King Nothing",
    composer = "Metallica",
    subtitle = "Drum transcription"
)

measures = []

for i in range(4):
    measures += SILENCE

# TODO: Catch if user starts index at 0 (allow the option in config?)
measures[0].tempo = 115

for i in range(4):
    measures += Measure(
        hh = note_range(1,end,1)
    )

INTRO_HH_BD = Measure(
        ho = note_range(1, end, 0.25),
        bd = [2,4] if i > 3 else [],
        ac = [2,4]
    )
for i in range(10):
    measures += INTRO_HH_BD

# End of intro
measures += Measure(
    ho = [2, 2.5, 4, 4.5],
    sd = [1, 3],
    c1 = [1, 3],
    bd = [2.5, 4.5],
)
measures += Measure(
    ho = [2, 2.5],
    sd = [1],
    c1 = [1],
    bd = [2.5, 3.5,  4.5],
    fm =     [3,   4]
)

MAIN_GROOVE = [
    Measure(
        ho = note_range(1, end, 0.5),
        bd = [1,3],
        sd = [2,4],
    ),
    Measure(
        ho = note_range(1, end, 0.5),
        bd = [1,3,4.5],
        sd = [2,4],
    )
]

# Main groove crash variants
MAIN_GROOVE_C1 = deepcopy(MAIN_GROOVE)
MAIN_GROOVE_C1[0].replace(MAIN_GROOVE_C1[0].ho, MAIN_GROOVE_C1[0].c1, [1])
MAIN_GROOVE_C2 = deepcopy(MAIN_GROOVE)
MAIN_GROOVE_C2[0].replace(MAIN_GROOVE_C2[0].ho, MAIN_GROOVE_C2[0].c1, [2])


measures += MAIN_GROOVE_C1
measures += MAIN_GROOVE

measures += MAIN_GROOVE_C2
measures += [Measure(
        ho = note_range(1, end, 0.5, [2,4]),
        c1 = [2,4],
        bd = [1,3],
        sd = [2,4],
    ),
    Measure(
        c1 = [1.5],
        ho = [1,2, 2.5, 3,4],
        sd = [1.5,3,4],
        bd = [1,3.5,4.5],
    )]

############ Verse 1 ############

# TODO: Offer the option to have repeat of a section
for _ in range(2):
    for i in [1,2,3,4]:
        m = Measure(
            ho = note_range(1, end, 0.5),
            bd = [1,3,4.5],
            sd = [2,4]
        )
        if i == 4:
            m.sd = [2,3,4]
            m.bd = [1, 2.5, 3.5, 4.5]
            m.c1 = [3,4]
            m.ho = note_range(1,3,0.5)

        measures += m


# "All the wants you waste"
def all_the_wants(version:int):
    res = []
    for idx in [1,2]:
        res += Measure(
            ho = note_range(1.5, end, 0.5),
            bd = [1, 2, 4.5],
            sd = [3],
            c1 = [1],
        )
        if idx == 1:
            res += Measure(
                ho = note_range(1, end, 0.5, [2.5, 4.5]),
                bd = [1.5, 2, 4],
                sd = [2.5, 4.5, 4.75],
                c1 = [2.5]
            )
        else:
            if version == 1:
                res += Measure(
                    ho = note_range(1, end, 0.5, [2.5, 4.5, 4]),
                    bd = [1.5, 2, 3.5],
                    sd = [2.5, 4, 4.25],
                    ft = [4.5, 4.75],
                    c1 = [2.5]
                )
            elif version == 2:
                res += Measure(
                    ho = [1],
                    bd = [1.5, 2],
                    sd = [2.5],
                    c1 = [2.5],
                    hh = [3,4],
                )

    return res

measures += all_the_wants(1)


# "Then it all crashes down"
def then_it_all_crashes_down(verse:int):
    for _ in range(2):
        res = []
        for j in [1,2,3,4]:
            if j != 4:
                res += Measure(
                    ho = note_range(1, end, 0.5, excl=[1]),
                    bd = [1,3,4.5],
                    sd = [2,4],
                    c1 = [1],
                )
            else:
                # Snare/floor crescendo
                if verse == 1:
                    res += Measure(
                        sd = note_range(1, end, 0.5),
                        ft = note_range(1, end, 0.5)
                    )
                elif verse == 2:
                    res += Measure(
                        sd = note_range(1, 4, 0.5) + note_range(4,end,0.25),
                        ft = note_range(1, 4, 0.5)
                    )
        return res

measures += then_it_all_crashes_down(1)

# (crash choke) "Where's your crown king nothing?"
wheres_your_crown = Measure(
    c1 = [1],
    ho = [2, 3, 4],
    bd = [1, 4.5],
    ac = [2,3,4]
)
measures += wheres_your_crown


measures += MAIN_GROOVE_C1
measures += MAIN_GROOVE

section = deepcopy(MAIN_GROOVE)
for i in range(2):
    section[i].replace(section[i].ho, section[i].c1, [2,4])
section[-1].bd.remove(4.5)
measures += section

# Fill before verse 2
measures += Measure(
    ho = note_range(1,end,0.5, excl=[1.5,3]),
    c1 = [1.5,3],
    sd = [1.5,3],
    bd = [1,2,2.5,4.5],
)
measures += Measure(
    sd = [1,1.75,2,2.5,3,3.25,3.5],
    fm = [4],
    bd = [4.5],
    c1 = [1],
    ho = [1.5],
)

# Verse 2
for i in [1,2,3,4]:
    m = Measure(
        ho = note_range(1, end, 0.5),
        bd = [1,3,4.5],
        sd = [2,4]
    )
    if i == 1:
        m.replace(m.ho, m.c1, [1])
    if i == 4:
        m.sd = [2,3,4]
        m.bd = [1, 2.5, 3.5, 4.5]
        m.c1 = [3,4]
        m.ho = note_range(1,3,0.5)

    measures += m

for i in [1,2,3,4]:
    m = Measure(
        ho = note_range(1, end, 0.5),
        bd = [1,3,4.5],
        sd = [2,4]
    )
    m.replace(m.ho, m.c1, [2])
    if i == 4:
        m.sd = [2,3,4]
        m.bd = [1, 2.5, 3.5, 4.5]
        m.c1 = [2]
        m.ho = note_range(1,3,0.5, excl=[2]) + [3,4]

    measures += m

# "All the wants" reprise
measures += all_the_wants(1)

# Then it all crashes down 2nd time
measures += then_it_all_crashes_down(2)
measures += then_it_all_crashes_down(1)

# Where's your crown 2nd time
measures += wheres_your_crown

for i in [1,2,3,4]:
    m = Measure(
        ho = note_range(1, end, 0.5),
        bd = [1,3,4.5],
        sd = [2,4]
    )
    if i == 1:
        m.replace(m.ho, m.c1, [1])
    if i == 4:
        m.sd = [2,3,4]
        m.bd = [1, 2.5, 3.5, 4.5]
        m.c1 = [3,4]
        m.ho = note_range(1,3,0.5)

    measures += m

section = deepcopy(MAIN_GROOVE)
for i in range(2):
    section[i].replace(section[i].ho, section[i].c1, [2,4])
section[-1].bd.remove(4.5)
measures += section

# Fill before end of guitar solo
measures += Measure(
    ho = note_range(1,end,0.5, excl=[1.5,3]),
    c1 = [1.5,3],
    sd = [1.5,3],
    bd = [1,2,2.5,4.5],
)
measures += Measure(
    sd = [1] + note_range(1.75,3.5,0.25),
    mt = note_range(3.5,4,0.25),
    ft = note_range(4,end,0.25),
    c1 = [1],
    ho = [1.5],
)

measures += all_the_wants(2)


# Lead up to bridge
m = Measure(MAIN_GROOVE[1])
m.replace(m.ho, m.c1, [1])
measures+=m
measures += Measure(
    bd = [1,3],
    sd = [2,4,4.75],
    ho = note_range(1, end, 0.5),
)

# Fil before bridge
measures += Measure(
    sd = [1,2,3],
    bd = [1.5,2.5],
    mt = [3.5],
    ht = [4],
    ft = note_range(1,3.5,0.5) + [4.5],
)
measures += Measure(
    sd = note_range(1, end, 0.5),
    ft = note_range(1, end, 0.5),
)
measures += Measure(
    bd = [1],
    c1 = [1],
    ho = [2,3,4]
)

# Bridge starts
for i in range(16):
    measures += INTRO_HH_BD

for i in range(8):
    m = Measure(
        ho = note_range(1,end,0.25),
        bd = [1,3],
    )
    if i < 4:
        m.replace(m.ho, m.sd, [2,2.25,4])
    elif i < 6:
        m.replace(m.ho, m.sd, [2,2.25,4,4.25])
    elif i == 6:
        m.bd.remove(3)
        m.replace(m.ho, m.sd, [2,2.25,3,3.25,4,4.25])
    elif i == 7:
        m = Measure(
            sd = note_range(1,end, 0.25)
        )
    measures += m

# Then it all crashes down, where's your crown
measures += then_it_all_crashes_down(2)
measures += then_it_all_crashes_down(1)
measures += wheres_your_crown

# Drum pause
measures += Measure(
    bd = [1],
    c1 = [1],
)
for i in range(3):
    measures += SILENCE

measures += MAIN_GROOVE_C1
measures += MAIN_GROOVE
measures += MAIN_GROOVE_C2
measures += Measure(
    ho = note_range(1,end,0.5, excl=[1.5,3]),
    c1 = [1.5,3],
    sd = [1.5,3],
    bd = [1,2,2.5,4.5],
)
measures += Measure(
    sd = [1],
    fm = [3,4],
    bd = [2.5,3.5,4.5],
    c1 = [1],
    ho = [1.5,2],
)

measures += Measure(
    bd = [1],
    c1 = [1],
)
