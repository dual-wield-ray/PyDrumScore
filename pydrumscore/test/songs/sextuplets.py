# pylint: disable = missing-module-docstring

from pydrumscore import Measure, note_range, Metadata, end
from typing import List

metadata = Metadata(
    workTitle = "Sextuplets",
    )

measures:List[Measure] = []

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

# measures += Measure(
#     sd = note_range(1, end(), 1.0/3.0, excl=[1 + 2/3])
# )

# measures += Measure(
#     sd = note_range(1, end(), 1.0/3.0, excl=[4 + 1/3])
# )

# measures += Measure(
#     sd = note_range(1, end(), 1.0/3.0, excl=[4 + 2/3])
# )

for i in range(12):
    measures += Measure(
        sd = note_range(1, end(), 1/3, excl=[1 + i/3])
    )

measures[-1].has_line_break = True

# for i in range(12):
#     measures += Measure(
#         sd = note_range(1, end(), 1/3, excl=[1 + i/3, 1 + (i+1)/3])
#     )

# for i in range(12):
#     measures += Measure(
#         sd = note_range(1, end(), 1/6, excl=[1 + i/6])
#     )

