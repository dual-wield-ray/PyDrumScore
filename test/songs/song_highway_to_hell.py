from song import *
from beats import SILENCE, MONEY_BEAT, HIGHWAY_GROOVE, HIGHWAY_GROOVE_O

########### Metadata ###########
metadata = Metadata(
        workTitle = "Highway to Hell"
    )
########### End Metadata ###########


########### Song creation ###########
measures = []

first_two = Measure()
first_two.time_sig = "2/4"
first_two.tempo = 10
measures += Measure(first_two)

# Intro
for i in range(4):
    measures += SILENCE
measures[-4].time_sig = "4/4"

# Drums start
for i in range(2):
    measures += MONEY_BEAT
for i in range(2):
    measures += HIGHWAY_GROOVE

# Verse 1 (Livin' easy)
for i in range(15):
    measures += HIGHWAY_GROOVE

# My friends are gonna be there too
# TODO: Flam support
buildup_section = [
    Measure(
        sd = [1] + Range(2, END, 0.5),
        c1 = [1],
        ft = Range(2, END, 0.5)
        ),
    Measure(
        sd = Range(1, 4, 0.5) + [4],
        ft = Range(1, 4, 0.5)
        )]

measures += buildup_section

# Chorus
chorus_2b = []
chorus_2b += HIGHWAY_GROOVE_O
chorus_2b += Measure(
    sd = [2, 4],
    bd = [1, 3],
    ho = Range(1, 3, 0.5),
    c1 = [3,4]
    )

chorus_section = []
for i in range(3):
    chorus_section += chorus_2b

measures += chorus_section

# Section before next verse 2
# TODO: Support for hh foot
measures += Measure(
    sd = [2, 4, 4.5],
    bd = [1, 3],
    ho = Range(1, 4, 0.5),
    c1 = [4, 4.5]
    )

measures += Measure( hh = Range(1, END, 1) )

measures += Measure(
    hh = Range(1, END, 1),
    sd = [3.5],
    mt = [4],
    c1 = [4.5],
    bd = [4.5],
    )


# Verse 2 (No stop sign)
for i in range(15):
    m = Measure(HIGHWAY_GROOVE)

    if i == 0:
        m.bd = m.bd[1:]
    if i >= 8 and i not in [10,13]:
        m.ho.append(2)
        m.hh.remove(2)
        m.hh.remove(2.5)

    measures += m

# Same buildup again
measures += buildup_section

# Chorus
measures += chorus_section

# Section before guitar solo
measures += Measure(
    ho = Range(1, 4, 0.5),
    c1 = [4] +    [4.5],
    sd = [2, 4] + [4.5],
    bd = [1, 3],
)

measures += Measure( hh = Range(1, END, 1))
measures += Measure(
    sd = [1, 2.5, 4],
    c1 = [1, 2.5, 4],
    bd = [1.5, 2, 3, 3.5]
)

measures += Measure( hh = Range(1, END, 1))
measures += Measure(
    sd = [1, 2.5, 4],
    c1 = [1, 2.5, 4],
    bd = [1.5, 2, 3, 3.5, 4.5]
)
measures += Measure(
    sd = [1.5, 3, 4],
    c1 = [1.5],
    bd = [1, 2, 2.5]
)

# Guitar solo
for i in range(7):
    measures += chorus_2b

measures += Measure(
    sd = [2, 4, 4.5],
    bd = [1, 3],
    ho = Range(1, 4, 0.5),
    c1 = [4, 4.5]
    )
measures += Measure(
    hh = [1,2],
    sd = [4],
    bd = [3],
    c1 = [3,4]
    )

# Last round of chorus groove
measures += chorus_section

# Ending fill
measures += Measure(
    ho = Range(1, 3, 0.5),
    sd = [2, 3],
    bd = [1, 4, 4.5],
    ft = [3.5],
    c1 = [4.5]
    )

# And I'm going down....
for i in range(4):
    measures += SILENCE

# TODO: Garbage can ending

########### End song creation ###########
