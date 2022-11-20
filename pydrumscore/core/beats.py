"""
Library of some basic, commonly used drum beats. To be used in song creation by user.
"""

from pydrumscore.core.song import Measure, end, note_range

SILENCE = Measure(
    )

MONEY_BEAT = Measure(
    sd = [2, 4],
    bd = [1, 3],
    hh = note_range(1, end, 0.5)
    )

ROCK_BEAT = Measure(
    sd = [2,4],
    bd = [1,3,3.5],
    hh = note_range(1, end, 0.5)
    )

ROCK_BEAT_WOPEN = Measure(
    sd = [2,4],
    bd = [1,3,3.5],
    hh = note_range(1, end-0.5, 0.5),
    ho = [4.5]
    )

SHUFFLE_BEAT = Measure(
    sd = [2,4],
    bd = [1,3],
    hh = note_range(1, end, 1) + [1.66, 2.66, 3.66, 4.66]
    )

HIGHWAY_GROOVE = Measure(
    sd = [2,4],
    bd = [1,3,4.5],
    hh = note_range(1, end, 0.5)
    )

# Includes crash on 1
HIGHWAY_GROOVE_O = Measure(
    sd = [2,4],
    bd = [1,3,4.5],
    ho = note_range(1.5, end, 0.5),
    c1 = [1]
    )
