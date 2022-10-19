from drumscore.core.song import Measure, END, note_range, Metadata

metadata = Metadata(
    workTitle = "Sextuplets",
    )

measures = []

measures += Measure(
    sd = note_range(1, END, 1.0/6.0)
)
