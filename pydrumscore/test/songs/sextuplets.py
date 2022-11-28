# pylint: disable = missing-module-docstring

from pydrumscore import Measure, note_range, Metadata, end

metadata = Metadata(
    workTitle = "Sextuplets",
    )

measures = []

# measures += Measure(
#     sd = note_range(1, 2, 1.0/6.0)
# )


# measures += Measure(
#     sd = note_range(1, 2, 1.0/3.0)
# )


# measures += Measure(
#     sd = note_range(2, 3, 1.0/3.0)
# )


# measures += Measure(
#     sd = note_range(1, 3, 1.0/3.0)
# )

# measures += Measure(
#     sd = note_range(1, 4, 1.0/3.0)
# )

# measures += Measure(
#     sd = note_range(1, end(), 1.0/3.0)
# )

# measures += Measure(
#     sd = note_range(1, end(), 1.0/3.0, excl=[1 + 1/3])
# )

measures += Measure(
    sd = note_range(1, end(), 1.0/3.0, excl=[1 + 2/3])
)

# measures += Measure(
#     sd = note_range(1, end(), 1.0/3.0, excl=[4 + 1/3])
# )

# measures += Measure(
#     sd = note_range(1, end(), 1.0/3.0, excl=[4 + 2/3])
# )

