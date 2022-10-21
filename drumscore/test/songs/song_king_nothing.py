from drumscore.core.song import *
from drumscore.core.song import Metadata
from drumscore.core.beats import SILENCE
from copy import deepcopy

metadata = Metadata(
    workTitle = "King Nothing",
    composer = "Metallica",
)

measures = []

# TODO: Confirm number
for i in range(12):
    measures += SILENCE

# TODO: Accents would be nice!
for i in range(10):
    measures += Measure(
        ho = note_range(1, END, 0.25),
        bd = [2,4] if i > 3 else []
    )

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

INTRO_GROOVE = [
    Measure(
        ho = note_range(1, END, 0.5),
        bd = [1,3],
        sd = [2,4],
    ),
    Measure(
        ho = note_range(1, END, 0.5),
        bd = [1,3,4.5],
        sd = [2,4],
    )
]

# Main groove with a crash on 2
INTRO_GROOVE_C = deepcopy(INTRO_GROOVE)
INTRO_GROOVE_C[0].ho.remove(2)
INTRO_GROOVE_C[0].c1 = [2]

for i in range(2):
    measures += deepcopy(INTRO_GROOVE)
    if i == 0:
        measures[-2].ho.remove(1)
        measures[-2].c1 = [1]

measures += INTRO_GROOVE_C

measures += [Measure(
        ho = note_range(1, END, 0.5, [2,4]),
        bd = [1,3],
        sd = [2,4],
        c1 = [2,4],
    ),
    Measure(
        c1 = [  1.5                      ],
        ho = [1,    2, 2.5, 3,      4    ],
        sd = [  1.5,        3,      4    ],
        bd = [1,               3.5,   4.5],
    )]
        #       1   &   2   &   3   &   4   &
        # c1 =      X                             ]
        # ho =  x       x   x   x       x         ]
        # sd =      s           s       s         ]
        # bd =  b                   b       b     ]

############ Verse 1 ############

# TODO: Offer the option to have repeat of a section
for _ in range(2):
    for i in range(4):
        m = Measure(
            ho = note_range(1, END, 0.5),
            bd = [1,3,4.5],
            sd = [2,4]
        )
        if i == 3:
            m.sd = [2,3,4]
            m.bd = [1, 2.5, 3.5, 4.5]
            m.c1 = [3,4]
            m.ho = note_range(1,3,0.5)

        measures += m


# "All the ones you..."
for i in range(2):
    measures += Measure(
        ho = note_range(1, END, 0.5),
        bd = [1, 2, 3.5, 4.5],
        sd = [3]
    )
    if i == 0:
        measures += Measure(
            ho = note_range(1, END, 0.5, [2.5, 4.5]),
            bd = [1.5, 2],
            sd = [2.5, 4, 4.5, 4.75],
            c1 = [2.5]
        )
    else:
        measures += Measure(
            ho = note_range(1, END, 0.5, [2.5, 4.5, 4]),
            bd = [1.5, 2, 3.5],
            sd = [2.5, 4, 4.25],
            ft = [4.5, 4.75],
            c1 = [2.5]
        )

# "And it comes crashing down..."


# TODO: Should be at top...
# TODO: Catch if user starts index at 0 (allow the option in config?)
measures[0].tempo = 110