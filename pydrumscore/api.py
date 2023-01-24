"""
Contains the API for the pydrumscore exporter.
All the objects and functions here are meant to be called
by the user in their scoring code.
"""

# Built-in modules
from copy import deepcopy
from fractions import Fraction
from inspect import signature
import logging
import math
from typing import List, Optional


def note_range(
    start: float, stop: float, step: float, excl: Optional[List[float]] = None
) -> list:
    """Creates a list based on a range (start, stop) and step provided as argument.
    Functions the same way as python's built-in range function, but
    using floats instead of ints. As such, start bound is inclusive and stop
    bound is exclusive.

    Example for eighth notes filling a measure:

    note_range(1, 5, 0.5) -> [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]

    :param start: (float): First number in the range
    :param stop: (float): Last number in the range (exclusive bound)
    :param step: (float): Step between entries
    :param excl(opt): list(float): List of specific values to exclude from range.

    :returns:
        list: Range of notes from 'start' to 'stop', separated by 'step'
    """

    # Note: Homemade implementation of numpy's 'arange', to avoid having dependency on numpy
    #       for a single function.

    # Input validation
    has_error = False
    if has_error := (start < 0):
        logging.getLogger(__name__).error("Range start must be positive.")
    if has_error := (stop < 0):
        logging.getLogger(__name__).error("Range stop must be positive.")
    if has_error := (start < 0):
        logging.getLogger(__name__).error("Range start must be less or equal to stop.")
    if has_error:
        logging.getLogger(__name__).error("Note range generation failed.")
        return []

    result_range = []

    curr = start
    while curr < stop and not math.isclose(curr, stop):

        is_excluded = (
            [e for e in excl if math.isclose(curr, e)] != [] if excl else False
        )
        if not is_excluded:
            result_range.append(curr)

        curr += step

    return result_range


def set_time_signature(time_sig: str) -> None:
    """Sets the time signature for all upcoming measures. By default, songs have a time signature of "4/4".

    :param time_sig: (str): New time signature. Must be in the format "int/int".
    """

    # Validate argument
    split_val = time_sig.split("/")
    is_valid = len(split_val) == 2 and split_val[0].isdigit() and split_val[1].isdigit()
    if not is_valid:
        logging.getLogger(__name__).error(
            "Invalid time signature given: '%s'. Time signature must be in the format 'int/int'.",
            time_sig,
        )
        return

    # pylint: disable = protected-access
    Measure._current_time_sig = time_sig

    # Update the measure end time to stay in sync
    subdiv = 4.0 / int(split_val[1])
    Measure._current_end = int(split_val[0]) * subdiv + 1


def end():
    """Get the current numerical value of the end of a measure. Dynamically reassigned based on current time signature.
    Typically used in a `note_range()`, such as ::

    note_range(1, end(), 0.5) -> [1, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
    """

    return Measure._current_end  # pylint: disable=protected-access


# These getters/setters are a bit of wizardry that allows for a shared list, and more importantly,
# for protecting the attributes from any readdressing on assignation. When assigning a value to a property with them, the value will
# be copied instead reassigning the memory address.
def _shared_list_getter(attr):
    def get_list(self):
        return getattr(self, attr)

    return get_list


def _shared_list_setter(attr):
    def replace_list(self, value):
        lst: list = getattr(self, attr)
        if not value or value is lst:
            return  # Note: Assign to self happens with +=

        lst.clear()
        lst.extend(value)

    return replace_list


class Measure:
    """
    Contains the time values of all the notes in a given measure,
    as well as any accompanying data such as time signature, text,
    or tempo marking.

    This class is intended to be instantiated by the user. Fill in the ``measures`` object
    in a score file to define the measures that must be exported.

    :raises:
        RuntimeError: If assigning to a drumset piece that does not exist
    """

    # pylint: disable=too-many-instance-attributes

    # Measure "creation context", representing persistent state between measures such as time signature
    # TODO: If this context grows, create an internal class for it
    _current_end = 5.0
    """ Represents the numerical value of the end of a measure. Dynamically reassigned based on current time signature."""

    _current_time_sig = "4/4"
    """ Represents the time signature. Is set by the user through `set_time_signature()`"""

    # Defines all the properties for a Measure object. Writing it out allows for parser (intellisense) support
    # The multiple assigns define the aliases: all members that point to the same list in memory
    # That list is stored in the private attribute that starts with an underscore
    # Ex. property "snare" and property "sd" both point to "_snare"
    accent = ac = property(
        fget=_shared_list_getter("_accent"), fset=_shared_list_setter("_accent")
    )
    bass_drum = bd = property(
        fget=_shared_list_getter("_bass_drum"), fset=_shared_list_setter("_bass_drum")
    )
    floor_tom = ft = property(
        fget=_shared_list_getter("_floor_tom"), fset=_shared_list_setter("_floor_tom")
    )
    snare = sd = property(
        fget=_shared_list_getter("_snare"), fset=_shared_list_setter("_snare")
    )
    snare_ghost = sg = property(
        fget=_shared_list_getter("_snare_ghost"),
        fset=_shared_list_setter("_snare_ghost"),
    )
    crash1 = c1 = property(
        fget=_shared_list_getter("_crash1"), fset=_shared_list_setter("_crash1")
    )
    hi_hat = hh = hi_hat_closed = property(
        fget=_shared_list_getter("_hi_hat"), fset=_shared_list_setter("_hi_hat")
    )
    hi_hat_open = ho = property(
        fget=_shared_list_getter("_hi_hat_open"),
        fset=_shared_list_setter("_hi_hat_open"),
    )
    ride = rd = property(
        fget=_shared_list_getter("_ride"), fset=_shared_list_setter("_ride")
    )
    ride_bell = rb = property(
        fget=_shared_list_getter("_ride_bell"), fset=_shared_list_setter("_ride_bell")
    )
    high_tom = ht = property(
        fget=_shared_list_getter("_high_tom"), fset=_shared_list_setter("_high_tom")
    )
    hi_hat_foot = hf = property(
        fget=_shared_list_getter("_hi_hat_foot"),
        fset=_shared_list_setter("_hi_hat_foot"),
    )
    flam_snare = fm = property(
        fget=_shared_list_getter("_flam_snare"), fset=_shared_list_setter("_flam_snare")
    )
    mid_tom = mt = property(
        fget=_shared_list_getter("_mid_tom"), fset=_shared_list_setter("_mid_tom")
    )
    cross_stick = cs = property(
        fget=_shared_list_getter("_cross_stick"),
        fset=_shared_list_setter("_cross_stick"),
    )
    _ALL_PIECES = (
        "accent",
        "bass_drum",
        "floor_tom",
        "snare",
        "snare_ghost",
        "crash1",
        "hi_hat",
        "hi_hat_open",
        "ride",
        "ride_bell",
        "high_tom",
        "hi_hat_foot",
        "flam_snare",
        "mid_tom",
        "cross_stick",
    )
    """All the drumset pieces that can be put in a measure (full names only)."""

    _ALL_OPTIONS = (
        "has_line_break",
        "tempo",
        "no_repeat",
        "text",
        "dynamic",
    )
    """All the option names (tempo, text, repeats...) that can be added to a measure."""

    def __init__(
        self,
        *args,
        accent: Optional[list] = None,
        bass_drum: Optional[list] = None,
        floor_tom: Optional[list] = None,
        snare: Optional[list] = None,
        snare_ghost: Optional[list] = None,
        crash1: Optional[list] = None,
        hi_hat: Optional[list] = None,
        hi_hat_open: Optional[list] = None,
        ride: Optional[list] = None,
        ride_bell: Optional[list] = None,
        high_tom: Optional[list] = None,
        hi_hat_foot: Optional[list] = None,
        flam_snare: Optional[list] = None,
        mid_tom: Optional[list] = None,
        cross_stick: Optional[list] = None,
        ac: Optional[list] = None,
        hi_hat_closed: Optional[list] = None,
        bd: Optional[list] = None,
        ft: Optional[list] = None,
        sd: Optional[list] = None,
        sg: Optional[list] = None,
        c1: Optional[list] = None,
        hh: Optional[list] = None,
        ho: Optional[list] = None,
        rd: Optional[list] = None,
        rb: Optional[list] = None,
        ht: Optional[list] = None,
        hf: Optional[list] = None,
        fm: Optional[list] = None,
        mt: Optional[list] = None,
        cs: Optional[list] = None,
        has_line_break=False,
        tempo: Optional[float] = None,
        no_repeat=False,
        text: Optional[str] = None,
        dynamic: Optional[str] = None,
    ) -> None:
        """Creates a Measure based on the given time values for each
        drumset piece.

        Example for a measure of snare, drum, and hi-hat:
        Measure(
            hh = note_range(1, end, 0.5),
            sd = [2,4],
            bd = [1,3],
        )
        (see :func: '~note_range')
        """
        # pylint: disable=invalid-name, multiple-statements

        # If copied from another Measure

        if args:
            assert isinstance(args[0], Measure)
            self.__dict__ = deepcopy(args[0].__dict__)
            return

        # If created from scratch

        # Add the underlying container for all note lists
        # For example "_snare" contains the data for the "snare" and "sd" properties
        for p in self._ALL_PIECES:
            setattr(self, "_" + p, [])

        self.accent = accent if accent else []
        self.bass_drum = bass_drum if bass_drum else []
        self.floor_tom = floor_tom if floor_tom else []
        self.snare = snare if snare else []
        self.snare_ghost = snare_ghost if snare_ghost else []
        self.crash1 = crash1 if crash1 else []
        self.hi_hat = hi_hat if hi_hat else []
        self.hi_hat_open = hi_hat_open if hi_hat_open else []
        self.ride = ride if ride else []
        self.ride_bell = ride_bell if ride_bell else []
        self.high_tom = high_tom if high_tom else []
        self.hi_hat_foot = hi_hat_foot if hi_hat_foot else []
        self.flam_snare = flam_snare if flam_snare else []
        self.mid_tom = mid_tom if mid_tom else []
        self.cross_stick = cross_stick if cross_stick else []

        # Also set values for all the aliases
        self.hi_hat_closed = hi_hat_closed if hi_hat_closed else []
        self.ac = ac if ac else []
        self.bd = bd if bd else []
        self.ft = ft if ft else []
        self.sd = sd if sd else []
        self.sg = sg if sg else []
        self.c1 = c1 if c1 else []
        self.hh = hh if hh else []
        self.ho = ho if ho else []
        self.rd = rd if rd else []
        self.rb = rb if rb else []
        self.ht = ht if ht else []
        self.hf = hf if hf else []
        self.fm = fm if fm else []
        self.mt = mt if mt else []
        self.cs = cs if cs else []

        # Set up "options", basically everything that is not a note
        # IMPORTANT: If adding an option, make sure to add it to _ALL_OPTIONS

        self.has_line_break = has_line_break
        """Whether or not to add a line break at the end of this measure. Useful for drum exercises that have multiple sections."""

        self.tempo: Optional[float] = tempo
        """Tempo starting from this measure."""

        self.no_repeat = no_repeat
        """Tells the exporter to not replace this measure with a repeat, and to instead write it out fully even if it is identical to the previous measure."""

        self.text: Optional[str] = text
        """Text displayed at the beginning of the measure. Useful for lyrics or other indications."""

        self.dynamic: Optional[str] = dynamic
        """Dynamics (volume) of the measure, such as forte(f), piano (p), fortissimo (ff), mezzo forte(mf), etc."""

        self._time_sig = (
            Measure._current_time_sig
        )  # Remembers value in context at time of creation
        """Time signature to be added at measure start. """

        self._separators: List[Fraction] = []
        """These time values for rests limit note durations and "slice up" the measure in a way that makes sense. """

        self._end = Fraction(Measure._current_end)
        """Measure time end based on time signature at moment of creation."""

        self._used_pieces: List[str] = []
        """All pieces (names) used by this measure. Filled at pre-export because can be affected after constructor."""

    def __iter__(self):
        return iter([deepcopy(self)])

    def __eq__(self, obj):
        if isinstance(obj, Measure):
            for p in Measure._ALL_PIECES:
                assert hasattr(self, p)
                assert hasattr(obj, p)
                if set(getattr(self, p)) != set(getattr(obj, p)):
                    return False

            for p in Measure._ALL_OPTIONS:
                assert hasattr(self, p)
                assert hasattr(obj, p)
                if getattr(self, p) != getattr(obj, p):
                    return False

        return True

    def _get_combined_times(self) -> List[Fraction]:
        """
        Creates a list of all the times in the measure,
        regardless of the instrument. Used in exporting
        logic.

        :returns:
            List[Fraction]: All the times in the measure, for all instruments
        """
        res = []
        for p in self._used_pieces:
            if p in ["ac", "accent"]:
                continue  # accents don't count

            assert hasattr(self, p)
            res += getattr(self, p)

        res.sort()

        return res

    def _get_next_time(self, combined_times, curr_idx):
        """Get next time based on current time index. If at last, return end value based on time signature."""
        return (
            combined_times[curr_idx + 1]
            if curr_idx + 1 < len(combined_times)
            else self._end
        )

    def _pre_export(self):
        """
        Pre-formats the measure content in preparation
        for use by the exporter.
        """

        def _pre_export_piece(lst: list):

            assert lst

            # Sanitizes the arrays to start at 0 internally
            # Then, convert all into a Fraction object to perform safe operations on it
            for i, _ in enumerate(lst):
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

        # Only do export for pieces that are actually used
        self._used_pieces = [p for p in Measure._ALL_PIECES if getattr(self, p)]
        for p in self._used_pieces:
            _pre_export_piece(getattr(self, p))

        # Add separators based on measure content
        # A separator "cuts up" the measure to prevent valid, but ugly
        # results like quarter notes going over a beat when on the "and",
        # or dotted rests.
        self._separators.append(Fraction(1))  # Always add on first time of measure

        all_times = self._get_combined_times()

        # Add a separator at the last time of the bar.
        # TODO: This logic only affects tuplet and it's broken, fix in tuplet support
        max_sep = self._end - 1
        if all_times and math.ceil(all_times[-1]) < max_sep:
            self._separators.append(Fraction(math.ceil(all_times[-1])))
        # END

        for i, t in enumerate(all_times):
            self._separators.append(Fraction(math.floor(t)))

            # Avoids dotted rests, and instead splits them into
            # only 1s, 2s, or 4s
            until_next = self._get_next_time(all_times, i) - t
            if until_next >= 2 and until_next != 4:
                self._separators.append(Fraction(math.ceil(t) + 1.0))

    def replace(
        self, from_notes: List[float], to_notes: List[float], times: List[float]
    ):
        """Replaces a set of notes from one list to another.
        Useful for introducing slight variations in a measure, such as replacing
        a single hi-hat note with an open hi-hat.

        :param from_notes: List from which to remove the times
        :type from_notes: List[float]
        :param to_notes: List from which to insert the times
        :type to_notes: List[float]
        :param times: Times that should be replaced
        :type times: List[float]
        """
        # TODO: Assert that they are both owned by self?
        # TODO: This function is inefficient, to work around issues of assignation and float comparisons

        def float_in(n, lst):
            for t in lst:
                if math.isclose(n, t):
                    return True
            return False

        res = [n for n in from_notes if not float_in(n, times)]
        from_notes.clear()
        from_notes.extend(res)
        to_notes.extend(times)

    def debug_print(self):
        """
        Prints the contents of the measure to the console, in a visual "ASCII" format.

        :warning: Does not yet support subdivisions of more than 16th... This function is still experimental.
        """
        first_line = "    "
        for i in note_range(1, self._end, 1):
            first_line += str(i) + "   &   "
        print(first_line)

        for p in self._used_pieces:
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
                next_v = vals[i + 1] if i != len(vals) - 1 else self._end
                until_next = next_v - v

                assert until_next > step or math.isclose(
                    until_next, step
                ), "Debug not yet supported for 32 notes or more"

                for _ in note_range(v, next_v - step, step):
                    res_str += sep

            print(res_str)


class Metadata:
    """
    Contains all the metadata necessary for exporting a song.
    In a song generation file, the global `metadata` instance of
    this class must be filled with all the relevant information.
    """

    # Disable invalid name warning to match the ones in XML
    # For "too few public methods", constructor validation justifies class
    # pylint: disable=invalid-name, too-few-public-methods, too-many-instance-attributes, too-many-arguments

    def __init__(
        self,
        arranger="",
        composer="",
        Copyright="",  # Note: capitalized because "copyright" is a Python builtin
        creationDate="",
        lyricist="",
        movementNumber="",
        movementTitle="",
        mscVersion="",
        platform="",
        poet="",
        pydrumscoreVersion="",
        source="",
        subtitle="",
        translator="",
        workNumber="",
        workTitle="",
    ) -> None:

        self.arranger = arranger
        self.composer = composer
        self.copyright = Copyright
        self.creationDate = creationDate
        self.lyricist = lyricist
        self.movementNumber = movementNumber
        self.movementTitle = movementTitle
        self.mscVersion = mscVersion
        self.platform = platform
        self.poet = poet
        self.pydrumscoreVersion = pydrumscoreVersion
        self.source = source
        self.subtitle = subtitle
        self.translator = translator
        self.workNumber = workNumber
        self.workTitle = workTitle

    # We need a list of all the kwargs, but we don't want to put
    # "kwargs" in __init__ signature because parsers
    # like intellisense would not give hints
    _ALL_METADATA_TAGS = [
        kwarg[0].lower() + kwarg[1:]
        for kwarg in signature(__init__).parameters
        if kwarg != "self"
    ]

    # pylint: enable=invalid-name
