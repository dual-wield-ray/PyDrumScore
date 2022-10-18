import drumscore.core.song as api

SILENCE = api.Measure(
    )

MONEY_BEAT = api.Measure(
    sd = [2, 4],
    bd = [1, 3],
    hh = api.note_range(1, api.END, 0.5)
    )

ROCK_BEAT = api.Measure(
    sd = [2,4],
    bd = [1,3,3.5],
    hh = api.note_range(1, api.END, 0.5)
    )

ROCK_BEAT_WOPEN = api.Measure(
    sd = [2,4],
    bd = [1,3,3.5],
    hh = api.note_range(1, api.END-0.5, 0.5),
    ho = [4.5]
    )

SHUFFLE_BEAT = api.Measure(
    sd = [2,4],
    bd = [1,3],
    hh = api.note_range(1, api.END, 1) + [1.66, 2.66, 3.66, 4.66]
    )

HIGHWAY_GROOVE = api.Measure(
    sd = [2,4],
    bd = [1,3,4.5],
    hh = api.note_range(1, api.END, 0.5)
    )

# Includes crash on 1
HIGHWAY_GROOVE_O = api.Measure(
    sd = [2,4],
    bd = [1,3,4.5],
    ho = api.note_range(1.5, api.END, 0.5),
    c1 = [1]
    )