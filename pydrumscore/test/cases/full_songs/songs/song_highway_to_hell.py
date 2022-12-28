# pylint: disable = missing-module-docstring

import pydrumscore as pds
from pydrumscore.beats import SILENCE, MONEY_BEAT, HIGHWAY_GROOVE, HIGHWAY_GROOVE_O

metadata = pds.Metadata(
    workTitle="Highway to Hell",
)

measures = []

pds.set_time_signature("2/4")
first_two = pds.Measure()
first_two.tempo = 10
measures += pds.Measure(first_two)

# Intro
pds.set_time_signature("4/4")
for i in range(4):
    measures += SILENCE

# Drums start
for i in range(2):
    measures += MONEY_BEAT
for i in range(2):
    measures += HIGHWAY_GROOVE

# Verse 1 (Livin' easy)
for i in range(15):
    measures += HIGHWAY_GROOVE

# My friends are gonna be there too
buildup_section = [
    pds.Measure(
        sd=[1] + pds.note_range(2, pds.end(), 0.5),
        c1=[1],
        ft=pds.note_range(2, pds.end(), 0.5),
    ),
    pds.Measure(sd=pds.note_range(1, 4, 0.5) + [4], ft=pds.note_range(1, 4, 0.5)),
]

measures += buildup_section

# Chorus
chorus_2b = []
chorus_2b += HIGHWAY_GROOVE_O
chorus_2b += pds.Measure(sd=[2, 4], bd=[1, 3], ho=pds.note_range(1, 3, 0.5), c1=[3, 4])

chorus_section = []
for i in range(3):
    chorus_section += chorus_2b

measures += chorus_section

# Section before next verse 2
measures += pds.Measure(
    sd=[2, 4, 4.5], bd=[1, 3], ho=pds.note_range(1, 4, 0.5), c1=[4, 4.5]
)

measures += pds.Measure(hh=pds.note_range(1, pds.end(), 1))

measures += pds.Measure(
    hh=pds.note_range(1, pds.end(), 1),
    sd=[3.5],
    mt=[4],
    c1=[4.5],
    bd=[4.5],
)


# Verse 2 (No stop sign)
for i in range(15):
    m = pds.Measure(HIGHWAY_GROOVE)

    if i == 0:
        m.bd = m.bd[1:]
    if i >= 8 and i not in [10, 13]:
        m.ho.append(2)
        m.hh.remove(2)
        m.hh.remove(2.5)

    measures += m

# Same buildup again
measures += buildup_section

# Chorus
measures += chorus_section

# Section before guitar solo
measures += pds.Measure(
    ho=pds.note_range(1, 4, 0.5),
    c1=[4] + [4.5],
    sd=[2, 4] + [4.5],
    bd=[1, 3],
)

measures += pds.Measure(hh=pds.note_range(1, pds.end(), 1))
measures += pds.Measure(sd=[1, 2.5, 4], c1=[1, 2.5, 4], bd=[1.5, 2, 3, 3.5])

measures += pds.Measure(hh=pds.note_range(1, pds.end(), 1))
measures += pds.Measure(sd=[1, 2.5, 4], c1=[1, 2.5, 4], bd=[1.5, 2, 3, 3.5, 4.5])
measures += pds.Measure(sd=[1.5], fm=[3, 4], c1=[1.5], bd=[1, 2, 2.5])

# Guitar solo
for i in range(7):
    measures += chorus_2b

measures += pds.Measure(
    sd=[2, 4, 4.5], bd=[1, 3], ho=pds.note_range(1, 4, 0.5), c1=[4, 4.5]
)
measures += pds.Measure(hh=[1, 2], sd=[4], bd=[3], c1=[3, 4])

# Last round of chorus groove
measures += chorus_section

# Ending fill
measures += pds.Measure(
    ho=pds.note_range(1, 3, 0.5), sd=[2], fm=[3], bd=[1, 4, 4.5], ft=[3.5], c1=[4.5]
)

# And I'm going down....
for i in range(4):
    measures += SILENCE

# TODO: Garbage can ending
