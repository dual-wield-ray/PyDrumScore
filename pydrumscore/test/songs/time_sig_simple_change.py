# pylint: disable = missing-module-docstring

import pydrumscore.core.song as api

metadata = api.Metadata(
    workTitle = "Time Signature Simple Change",
    )

measures = []

api.set_time_sig("3/4")
measures += api.Measure(
    sd = api.note_range(1, api.end, 0.5)
)

api.set_time_sig("4/4")
measures += api.Measure(
    sd = api.note_range(1, api.end, 0.5)
)

api.set_time_sig("2/4")
measures += api.Measure(
    sd = api.note_range(1, api.end, 0.5)
)
