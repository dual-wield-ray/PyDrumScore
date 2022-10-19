import math
from copy import deepcopy
import numpy as np
#from types import FunctionType, MethodType

############ Utilities ############
def note_range(start, stop, step) -> list:
    return np.arange(start,stop,step).tolist()

END = 5

############ API Classes ############

class Metadata():

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
                print("Error: metadata value " + k + " is not in accepted tags. Check for spelling.")
                has_error = True
                continue

            if not has_error:
                setattr(self, k, v)

        if has_error:
            print("See supported tags: ")
            print(*self.ALL_TAGS, sep=", ")
            raise RuntimeError("Metadata creation failed.")


    # pylint: enable=invalid-name


#code_str = "def " + t + "(self): print('" + v + "')"
#f_code = compile(code_str, "_", "exec")
#environment = {}
#exec(f_code, environment)
#setattr(self, "print_" + t, MethodType(environment[t],Metadata))

class Measure():

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
                "fm"]

    def __init__(self, *args, **kwargs) -> None:

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
                print("Drumset piece + '" + k + "' is not supported.")
                has_error = True
                continue

            setattr(self, k, v)

        # These limit note durations to insert rests instead
        self.separators = []

        # Whether or not to add a line break at the end
        self.has_line_break = False

        # Time sig to be added at measure start
        self.time_sig = None

        # Tempo starting from this measure
        self.tempo = None


    def __iter__(self):
        return iter([deepcopy(self)])


    def get_combined_times(self):

        res = []
        for p in self.ALL_PIECES:
            assert hasattr(self,p)
            res += getattr(self,p)

        return res


    def __eq__(self, obj):
        if isinstance(obj, Measure):
            for p in self.ALL_PIECES:
                assert hasattr(self,p)
                assert hasattr(obj,p)
                if set(getattr(self,p)) != set(getattr(obj,p)):
                    return False

        return True


    # Remove 1 from all user input values
    def _pre_export(self):
        def _pre_export_list(l):

            # Sanitizes the arrays to start at 0 internally
            for i, _ in enumerate(l):
                l[i] -= 1
                assert(l[i]) >= 0

            l.sort()

            # Insert separators for tuplets that have a gap
            # TODO: Not just triplets
            for i, _ in enumerate(l):
                if i+1 < len(l):
                    if math.isclose((l[i+1] - l[i]), 0.66) \
                    or math.isclose((l[i+1] - l[i]), 0.67):
                        self.separators.append(l[i] + 0.33)

        for p in self.ALL_PIECES:
            assert(hasattr(self,p))
            _pre_export_list(getattr(self,p))

        combined_times = self.get_combined_times()
        self.separators.append(0)
        for t in combined_times:
            self.separators.append(int(t))

    # TODO: Debug print function

# TODO: What is a song if not a list of measures with metadata?
#       Is this class really needed?
class Song():

    def __init__(self) -> None:
        self.measures = []
        self.metadata = Metadata()

