# pylint: disable = missing-module-docstring

import pydrumscore.core.song as api

metadata = api.Metadata(
    workTitle = "Eighth Note Denominator",
    )

measures = []

for n in range(1, 13):
    api.set_time_sig(f"{str(n)}/8")
    measures += api.Measure(
        sd = api.note_range(1, api.end, 0.5)
    )
