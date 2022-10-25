"""
Contains the API for the drumscore exporter.
All the objects and functions here are meant to be exploited
by the user in their scoring code.
"""

import math
import logging
from copy import deepcopy
from typing import List
import numpy as np  # TODO: Remove dependency on numpy

############ Utilities ############
def note_range(start:float, stop:float, step:float, excl: List[float] = None) -> list:
    """Creates a list based on a range and step provided as argument.
    Functions the same way as python's built-in range function, but
    using floats instead of ints. As such, start bound is inclusive and stop
    bound is exclusive.

    Example for eighth notes filling a measure:

    note_range(1, END, 0.5) -> [1, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]

    :param start: (float): First number in the range
    :param stop: (float): Last number in the range (exclusive bound)
    :param step: (float): Step between entries
    :param excl(opt): list(float): List of values to exclude from range

    :returns:
        list: Range of notes from 'start' to 'stop', separated by 'step'
    """
    if not excl:
        excl = []
    return [v for v in np.arange(start,stop,step) if v not in excl]

END = 5
""" Represents the numerical value of the end of a measure."""
# TODO: Dynamic reassign based on current time sig

############ API Classes ############

class Metadata():
    """
    Contains all the metadata necessary for exporting a song.
    In a song generation file, the global 'metadata' instance of
    this class must be filled with all the relevant information.

    :raises:
        RuntimeError: If data in constructor is not part of valid tags
    """
    # Disable invalid name warning to match the ones in XML
    # For public methods, constructor validation justifies class
    # pylint: disable=invalid-name, too-few-public-methods

    ALL_TAGS = ["arranger" ,
                "composer",
                "copyright",
                "creationDate",
                "lyricist",
                "movementNumber",
                "movementTitle",
                "mscVersion",
                "platform",
                "poet",
                "source",
                "translator",
                "workNumber",
                "workTitle"]
    """All tags allowed to be edited in the metadata."""

    def __init__(self, **kwargs) -> None:
        has_error = False
        if kwargs is None:
            kwargs = {}

        # Init all tags to default
        for t in self.ALL_TAGS:
            setattr(self, t, "")

        # Fill from keyword args
        for k,v in kwargs.items():
            if k not in self.ALL_TAGS:
                logging.getLogger(__name__).error("Error: metadata value '%s' is not a valid tags.\
                                                   Check for spelling.", k)
                has_error = True
                continue

            if not has_error:
                setattr(self, k, v)

        if has_error:
            print("See supported tags: ")
            print(*self.ALL_TAGS, sep=", ")
            raise RuntimeError("Metadata creation failed.")

    # pylint: enable=invalid-name

class Measure():
    """
    Contains the time values of all the notes in a given measure,
    as well as any accompanying data such as time signature, text,
    or tempo marking.

    :raises:
        RuntimeError: If assigning to a drumset piece that does not exist
    """
    ALL_PIECES = ["bd",
                "sd",
                "hh",
                "ft",
                "mt",
                "ht",
                "cs",
                "c1",
                "ho",
                "rd",
                "rb",
                "ac",
                "fm"]

    def __init__(self, *args, **kwargs) -> None:
        """Creates a Measure based on the given time values for each
        drumset piece.

        Example for a measure of snare, drum, and hi-hat:
        Measure(
            sd = [2,4],
            bd = [1,3],
            hh = note_range(1, END, 0.5)
        )
        (see :func: '~note_range')

        :param kwargs: Times for each instrument in named lists.

        :raises:
            RuntimeError: If data in constructor is not part of valid tags
        """

        if args:
            assert isinstance(args[0], Measure)
            self.__dict__ = deepcopy(args[0].__dict__)
            return

        has_error = False

        if kwargs is None:
            kwargs = {}

        # Init all to empty
        for p in self.ALL_PIECES:
            setattr(self, p, [])

        # Init from user args
        for k,v in kwargs.items():
            if k not in self.ALL_PIECES:
                logging.getLogger(__name__).error("Drumset piece + '%s' is not supported.", k)
                has_error = True
                continue

            setattr(self, k, v)

        if has_error:
            print("Valid drumset pieces:")
            print(*self.ALL_PIECES, sep=", ")
            raise RuntimeError("Measure contained invalid drumset pieces.")

        # These limit note durations to insert rests instead
        self.separators = []

        # Whether or not to add a line break at the end
        self.has_line_break = False

        # Time sig to be added at measure start
        self.time_sig = None

        # Tempo starting from this measure
        self.tempo = None

        self.no_repeat = False


    def __iter__(self):
        return iter([deepcopy(self)])


    def get_combined_times(self) -> List[int]:
        """
        Creates a list of all the times in the measure,
        regardless of the instrument. Used in exporting
        logic.

        :returns:
            List[int]: All the times in the measure, for all instruments
        """
        res = []
        for p in self.ALL_PIECES:
            if p == "ac":
                continue  # accents don't count

            assert hasattr(self,p)
            res += getattr(self,p)

        res.sort()

        return res


    def __eq__(self, obj):
        if isinstance(obj, Measure):
            for p in self.ALL_PIECES:
                assert hasattr(self,p)
                assert hasattr(obj,p)
                if set(getattr(self,p)) != set(getattr(obj,p)):
                    return False

        return True


    def pre_export(self):
        """
        Pre-formats the measure content in preparation
        for use by the exporter. In particular, indices
        are shifted to start at 0.
        """
        def pre_export_list(l):

            # Sanitizes the arrays to start at 0 internally
            for i, _ in enumerate(l):
                l[i] -= 1
                l[i] = round(l[i],3)
                assert(l[i]) >= 0

            l.sort()

            # Insert separators for tuplets that have a gap
            # TODO: Support for all tuplet types
            # TODO: Won't work for tuplets of different pieces
            gaps = [0.66]
            for i, _ in enumerate(l):
                if i+1 < len(l):
                    for g in gaps:
                        until_next = l[i+1] - l[i]
                        if math.isclose(until_next, g, rel_tol=0.1):
                            self.separators.append(l[i] + g/2.0)


        for p in self.ALL_PIECES:
            assert hasattr(self,p)
            pre_export_list(getattr(self,p))

        combined_times = self.get_combined_times()
        self.separators.append(0.0)
        for _, t in enumerate(combined_times):
            sep = float(int(t))
            if sep not in self.separators:
                self.separators.append(sep)

    # TODO: Debug print function
