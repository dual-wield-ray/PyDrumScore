# pylint: disable = missing-module-docstring, missing-function-docstring, redefined-outer-name, global-statement, invalid-name

import pydrumscore.core.song as api
from pydrumscore.core.song import Measure, note_range, end

from pydrumscore.core.beats import SILENCE

########### Metadata ###########
metadata = api.Metadata(
        workTitle = "Uptown Funk (feat. Bruno Mars)",
        composer = "Mark Ronson, Bruno Mars",
    )
########### End Metadata ###########


########### Song creation ###########

# Wishlist:
# It's easy to forget to add a Measure that you constructed yourself
#


measures = []

for i in range(8):
    m = Measure(SILENCE)
    if i == 7:
        m.bd = [4.25]
        m.fm = [4]

    measures += m

# Verses
def verse(skip_first_m=False):
    for i in range(16):
        if i == 0 and skip_first_m:
            continue

        m = Measure(
            hh = note_range(1, end, 0.5),
            sd = [2,4],
            bd = [1,2,3,4],
            # ac = [1,2,3,4]
        )
        if i == 0:
            m.replace(m.hh,m.c1,[1])
        if i % 2:
            m.replace(m.hh,m.ho,[4.5])

        global measures
        measures += m


# Girls, hit your hallelujah
def girls_hit_hallelujah():
    for i in range(8):
        m = Measure(
            bd = [1,2,3,4],
            # ac = [1,2,3,4]
        )

        # Cause uptown funk gonne give it to ya (buildup)
        if i >= 4 and i != 7:
            m.sd = note_range(1, end, 0.5)

        if i == 7:
            # Don't believe me just watch!
            m = Measure(
                sd = [1],
                fm = [4],
                bd = [4.25],
            )

        global measures
        measures += m


# Chorus
def chorus():
    for i in range(8):
        m = Measure(
            hh = note_range(1, end, 0.5),
            sd = [2,4],
            bd = [1,2,3,4],
            # ac = [1,2,3,4]
        )
        if i % 4 == 3:
            m.sd += note_range(3.5,end,0.25)
            m.hh = [hh for hh in m.hh if hh not in note_range(3.5,end,0.5)]
        elif i % 4 == 0:
            m.replace(m.hh,m.c1,[1])
        elif i % 2:
            m.replace(m.hh,m.ho,[4.5])

        global measures
        measures += m


verse()
girls_hit_hallelujah()

chorus()
for i in range(4):
    m = Measure(
        hh = note_range(1, 3.5, 0.5),
        sd = [2,4] + note_range(3.5,end,0.25),
        bd = [1,2,3,4],
    )
    if i == 3:
        m = Measure(
            fm = [1,2,3,4],
            bd = [1.5, 2.5, 3.5,4.25]
        )

    measures += m

# Stop! Wait a minute
measures += Measure(
    sd = [1],
    hh = [1],
    fm = [4],
    bd = [4.25]
)

verse(skip_first_m=True)
girls_hit_hallelujah()

chorus()
for i in range(4):
    m = Measure(
        hh = note_range(1, 3.5, 0.5),
        sd = [2,4] + note_range(3.5,end,0.25),
        bd = [1,2,3,4],
    )
    if i == 3:
        m = Measure(
            fm = [1,2,3,4],
            bd = [1.5, 2.5, 3.5,4.25]
        )

    measures += m

# Before we leave
for i in range(20):
    m = Measure(
        bd = [1,2,3,4],
        sd = [2,4],
    )
    if i == 3:
        m.ho = [4.5]

    elif i > 3:
        m.hh = note_range(1,end,0.5)
        if i % 2:
            if i == 11:
                m.hh.remove(4)
                m.hh.remove(4.5)
                m.fm = [4]
                m.sd.remove(4)
                m.bd += [4.25]
                m.bd.remove(4)
            elif i == 19:
                m = Measure(
                    fm = [1,2,3,4],
                    bd = [1.5, 2.5, 3.5,4.25]
                )
            else:
                m.replace(m.hh, m.ho, [4.5])

    measures += m

# Final chorus
chorus()
for i in range(4):
    m = Measure(
        hh = note_range(1, 3.5, 0.5),
        sd = [2,4] + note_range(3.5,end,0.25),
        bd = [1,2,3,4],
    )
    if i == 3:
        m = Measure(
            sd = [1,2,3,4],
            ho = [1,2,3,4],
            bd = [1.5, 2.5, 3.5,4.25]
        )

    measures += m

# Reprise of chorus with ride bell!
for i in range(16):
    m = Measure(
        rd = note_range(1, end, 1),
        rb = note_range(1.5, end, 1),
        sd = [2,4],
        bd = [1,2,3,4],
    )

    if i in [0,8,12]:
        m.replace(m.rd, m.c1,[1])

    if i == 7:
        m = Measure(
            ho = [1],
            sd = [1.5],
            fm = [2,3,4],
            bd = [1,2.5,3.5,4.25]
        )
    elif i == 11:
        m = Measure(
            sd = note_range(1,3,0.5) + note_range(3,end,0.25),
            bd = [1,2,3,4],
        )

    elif i == 15:
        m = Measure(
            sd = note_range(1,4.25,0.25,excl=[2,2.5,3.5,3.75])
        )

    measures += m

measures[0].tempo = 115
