"""
Contains the API for the pydrumscore exporter.
All the objects and functions here are meant to be called
by the user in their scoring code.
"""

import math
import logging
from copy import deepcopy
from typing import List, Optional
from fractions import Fraction


# Utilities
def note_range(
    start: float, stop: float, step: float, excl: Optional[List[float]] = None
) -> list:
    """Creates a list based on a range and step provided as argument.
    Functions the same way as python's built-in range function, but
    using floats instead of ints. As such, start bound is inclusive and stop
    bound is exclusive.

    Example for eighth notes filling a measure:

    note_range(1, end(), 0.5) -> [1, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]

    :param start: (float): First number in the range
    :param stop: (float): Last number in the range (exclusive bound)
    :param step: (float): Step between entries
    :param excl(opt): list(float): List of values to exclude from range

    :returns:
        list: Range of notes from 'start' to 'stop', separated by 'step'
    """
    # Note: Homemade equivalent of numpy's 'arange'
    res = []
    v = start
    while v < stop and not math.isclose(v, stop):

        exclude = [e for e in excl if math.isclose(v, e)] != [] if excl else False
        if not exclude:
            res.append(v)

        v += step

    return res


# pylint: disable = invalid-name
_end: float = 5.0
""" Represents the numerical value of the end of a measure. Dynamically reassigned based on current time signature."""

_context_time_sig = "4/4"  # pylint: disable = invalid-name


def set_time_sig(time_sig: str) -> None:
    """Sets the time signature for all upcoming measures. By default songs have a time signature of "4/4".

    :param time_sig: (str): New time signature. Must be in the format "int/int".
    """
    split_val = time_sig.split("/")
    is_valid = len(split_val) == 2 and split_val[0].isdigit() and split_val[1].isdigit()
    if not is_valid:
        logging.getLogger(__name__).error(
            "Invalid time signature given: '%s'. Time signature must be in the format 'int/int'.",
            time_sig,
        )
        return

    # pylint: disable = global-statement
    global _context_time_sig
    _context_time_sig = time_sig

    global _end
    subdiv = 4.0 / int(split_val[1])
    _end = 1 + int(split_val[0]) * subdiv


# pylint: enable = invalid-name


def end():
    """Get the current numerical value of the end of a measure. Dynamically reassigned based on current time signature."""
    return _end


# API Classes


class Metadata:
    """
    Contains all the metadata necessary for exporting a song.
    In a song generation file, the global 'metadata' instance of
    this class must be filled with all the relevant information.

    :raises:
        RuntimeError: If data in constructor is not part of valid tags
    """

    # Disable invalid name warning to match the ones in XML
    # For public methods, constructor validation justifies class
    # pylint: disable=invalid-name, too-few-public-methods, too-many-instance-attributes

    def __init__(self, **kwargs) -> None:
        has_error = False
        if kwargs is None:
            kwargs = {}

        self.arranger = ""
        self.composer = ""
        self.copyright = ""
        self.creationDate = ""
        self.lyricist = ""
        self.movementNumber = ""
        self.movementTitle = ""
        self.mscVersion = ""
        self.pydrumscoreVersion = ""
        self.platform = ""
        self.poet = ""
        self.source = ""
        self.translator = ""
        self.workNumber = ""
        self.subtitle = ""
        self.workTitle = ""

        self._ALL_TAGS = dict(vars(self))
        """All tags allowed to be edited in the metadata."""

        # Fill from keyword args
        for k, v in kwargs.items():
            if k not in self._ALL_TAGS:
                logging.getLogger(__name__).error(
                    "Error: metadata value '%s' is not a valid tags.\
                                                   Check for spelling.",
                    k,
                )
                has_error = True
                continue

            if not has_error:
                setattr(self, k, v)

        if has_error:
            print("See supported tags: ")
            print(*self._ALL_TAGS, sep=", ")
            raise RuntimeError("Metadata creation failed.")

    # pylint: enable=invalid-name


class Measure:
    """
    Contains the time values of all the notes in a given measure,
    as well as any accompanying data such as time signature, text,
    or tempo marking.

    :raises:
        RuntimeError: If assigning to a drumset piece that does not exist
    """

    # pylint: disable=too-many-instance-attributes

    _ALL_PIECES: dict = {}
    """Dict of all the drumset pieces that can be put in a measure (shorthand ids only)."""

    _ALL_PIECES_AND_ALIASES: dict = {}
    """Dict of all the drumset pieces that can be put in a measure, including their full name aliases."""

    _ALL_OPTIONS: dict = {}
    """Dict of all the options (tempo, text, repeats) that can be added to a measure."""

    _ALIASES = {
        "ac": ("accent",),
        "bd": ("bass_drum",),
        "ft": ("floor_tom",),
        "sd": ("snare",),
        "sg": ("snare_ghost",),
        "c1": ("crash1",),
        "hh": (
            "hi_hat",
            "hi_hat_closed",
        ),
        "ho": ("hi_hat_open",),
        "rd": ("ride",),
        "rb": ("ride_bell",),
        "ht": ("high_tom",),
        "hf": ("hi_hat_foot",),
        "fm": ("flam_snare",),
        "mt": ("mid_tom",),
        "cs": ("cross_stick",),
    }

    def __init__(self, *args, **kwargs) -> None:
        """Creates a Measure based on the given time values for each
        drumset piece.

        Example for a measure of snare, drum, and hi-hat:
        Measure(
            hh = note_range(1, end, 0.5),
            sd = [2,4],
            bd = [1,3],
        )
        (see :func: '~note_range')

        :param kwargs: Times for each instrument in named lists.

        :raises:
            RuntimeError: If data in constructor is not part of valid tags
        """
        # pylint: disable=invalid-name, multiple-statements

        if args:
            assert isinstance(args[0], Measure)
            self.__dict__ = deepcopy(args[0].__dict__)
            assert self._ALL_PIECES
            assert self._ALL_OPTIONS
            assert hasattr(self, "_USED_PIECES")

        else:
            self.ac: List[int] = []
            self.bd: List[int] = []
            self.ft: List[int] = []
            self.sd: List[int] = []
            self.sg: List[int] = []
            self.c1: List[int] = []
            self.hh: List[int] = []
            self.ho: List[int] = []
            self.rd: List[int] = []
            self.rb: List[int] = []
            self.ht: List[int] = []
            self.hf: List[int] = []
            self.fm: List[int] = []
            self.mt: List[int] = []
            self.cs: List[int] = []

            if not self._ALL_PIECES:
                self._ALL_PIECES = dict(vars(self))

            # Create alias lists
            # If creating new one, don't forget to add mapping in the _ALIAS dict
            self.accent: List[int] = []
            self.bass_drum: List[int] = []
            self.floor_tom: List[int] = []
            self.snare: List[int] = []
            self.snare_ghost: List[int] = []
            self.crash1: List[int] = []
            self.hi_hat_closed: List[int] = []
            self.hi_hat: List[int] = []
            self.hi_hat_open: List[int] = []
            self.ride: List[int] = []
            self.ride_bell: List[int] = []
            self.high_tom: List[int] = []
            self.hi_hat_foot: List[int] = []
            self.flam_snare: List[int] = []
            self.mid_tom: List[int] = []
            self.cross_stick: List[int] = []

            if not self._ALL_PIECES_AND_ALIASES:
                self._ALL_PIECES_AND_ALIASES = dict(vars(self))

            self._USED_PIECES: List[str] = []  # filled at pre-export

            self.has_line_break = False
            """Whether or not to add a line break at the end"""

            self.tempo: Optional[float] = None
            """Tempo starting from this measure"""

            self.no_repeat = False
            """Do not use repeat symbol for this measure"""

            self.start_repeat = False
            self.end_repeat = False

            self.text = None
            """Text at the beginning of the measure. Useful for lyrics."""

            self.dynamic = None
            """Dynamic of the measure (f, ff, p, mf)..."""

            self.time_sig = (
                _context_time_sig  # Gets globally defined value in current context
            )
            """Time sig to be added at measure start"""

            if not self._ALL_OPTIONS:
                self._ALL_OPTIONS: dict = {
                    k: v for k, v in vars(self).items() if k not in self._ALL_PIECES
                }

        has_error = False

        if kwargs is None:
            kwargs = {}

        # Init from user args
        for k, v in kwargs.items():
            if k not in self._ALL_PIECES_AND_ALIASES and k not in self._ALL_OPTIONS:
                logging.getLogger(__name__).error(
                    "Measure argument + '%s' is not supported.", k
                )
                has_error = True
                continue
            setattr(self, k, v)

        if has_error:
            print("Valid drumset pieces:")
            print(*self._ALL_PIECES_AND_ALIASES, sep=", ")
            print("Valid measure options:")
            print(*self._ALL_OPTIONS, sep=", ")
            raise RuntimeError("Measure contained invalid drumset pieces or options.")

        # These limit note durations to insert rests instead
        self._separators: List[Fraction] = []

        self._end = Fraction(_end)

    def replace(self, from_notes: List[float], to_notes: List[float], times: List[int]):
        """Replaces a set of notes from one list to another.
        Useful for introducing slight variations in a measure, such as replacing
        a single hi-hat note with an open hi-hat.

        :param from_notes: List from which to remove the times
        :type from_notes: List[float]
        :param to_notes: List from which to insert the times
        :type to_notes: List[float]
        :param times: Times that should be replaced
        :type times: List[int]
        """
        # TODO: Assert that they are both owned by self?
        for time in times:
            if time in from_notes:
                from_notes.remove(time)
                to_notes.append(time)

    def __iter__(self):
        return iter([deepcopy(self)])

    def _get_combined_times(self) -> List[Fraction]:
        """
        Creates a list of all the times in the measure,
        regardless of the instrument. Used in exporting
        logic.

        :returns:
            List[Fraction]: All the times in the measure, for all instruments
        """
        res = []
        for p in self._USED_PIECES:
            if p == "ac":
                continue  # accents don't count

            assert hasattr(self, p)
            res += getattr(self, p)

        res.sort()

        return res

    def __eq__(self, obj):
        if isinstance(obj, Measure):
            for p in self._USED_PIECES:
                assert hasattr(self, p)
                assert hasattr(obj, p)
                if set(getattr(self, p)) != set(getattr(obj, p)):
                    return False

            for p in self._ALL_OPTIONS:
                assert hasattr(self, p)
                assert hasattr(obj, p)
                if getattr(self, p) != getattr(obj, p):
                    return False

        return True

    def _pre_export(self):
        """
        Pre-formats the measure content in preparation
        for use by the exporter. In particular, indices
        are shifted to start at 0.
        """

        def pre_export_list(lst):

            # Sanitizes the arrays to start at 0 internally
            # Then, convert all into a Fraction object to perform safe operations on it
            for i, _ in enumerate(lst):
                lst[i] -= 1
                assert (lst[i]) >= 0

                lst[i] = Fraction(lst[i]).limit_denominator(
                    20
                )  # TODO: This changes the type, not good with type hints

            lst.sort()

            # Insert separators for tuplets that have a gap
            # TODO: Support for all tuplet types
            # TODO: Won't work for tuplets of different pieces
            gaps = [0.66]
            for i, v in enumerate(lst):
                if i + 1 < len(lst):
                    for g in gaps:
                        until_next = lst[i + 1] - v
                        if math.isclose(until_next, g, rel_tol=0.1):
                            self._separators.append(
                                Fraction(v + g / 2.0).limit_denominator(20)
                            )

        # Combine all the alias lists into the main list used for export (the shorthand)
        for k, v in self._ALIASES.items():
            main_list = getattr(self, k)
            for alias in v:
                main_list += getattr(self, alias)

        # Only do export for pieces that are actually used (broken)
        self._USED_PIECES = [k for k, v in self._ALL_PIECES.items() if v is not None]
        for p in self._USED_PIECES:
            assert hasattr(self, p)
            pre_export_list(getattr(self, p))

        combined_times = self._get_combined_times()
        self._separators.append(0.0)
        for _, t in enumerate(combined_times):
            sep = float(int(t))
            if sep not in self._separators:
                self._separators.append(sep)

    def debug_print(self):
        """
        Prints the contents of the measure to the console, in a visual "ASCII" format.

        :warning Does not yet support subdivisions of more than 16th... Still experimental.
        """
        first_line = "    "
        for i in note_range(1, _end, 1):
            first_line += str(i) + "   &   "
        print(first_line)

        for p in self._USED_PIECES:
            vals = getattr(self, p)
            if not vals:
                continue

            res_str = p + "  "
            sym = "o" if p not in ["hh", "ho", "c1"] else "x"  # TODO: Use notedef

            sep = "-"
            if p == "ac":
                sym = ">"
                sep = " "

            step = 0.125

            for _ in note_range(1, vals[0], step):
                res_str += sep

            for i, v in enumerate(vals):
                res_str += sym
                next_v = vals[i + 1] if i != len(vals) - 1 else _end
                until_next = next_v - v

                assert until_next > step or math.isclose(
                    until_next, step
                ), "Debug not yet supported for 32 notes or more"

                for _ in note_range(v, next_v - step, step):
                    res_str += sep

            print(res_str)
