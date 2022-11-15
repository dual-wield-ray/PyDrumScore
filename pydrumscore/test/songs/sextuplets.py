# pylint: disable = missing-module-docstring

from pydrumscore.core.song import Measure, note_range, Metadata

metadata = Metadata(
    workTitle = "Sextuplets",
    )

measures = []

measures += Measure(
    sd = note_range(1, 2, 1.0/6.0)
)
