# pylint: disable = missing-module-docstring

import pydrumscore.core.song as api

metadata = api.Metadata(
    workTitle = "Eighth Note Denominator",
    )

measures = []

api.set_time_sig("3/8")
measures += api.Measure(
    sd = api.note_range(1, api.end, 0.5)
)

api.set_time_sig("6/8")
measures += api.Measure(
    sd = api.note_range(1, api.end, 0.5)
)

api.set_time_sig("9/8")
measures += api.Measure(
    sd = api.note_range(1, api.end, 0.5)
)

api.set_time_sig("12/8")
measures += api.Measure(
    sd = api.note_range(1, api.end, 0.5)
)
