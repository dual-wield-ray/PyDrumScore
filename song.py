import math
from copy import deepcopy

END = 5

class Metadata():

    # TODO: It's possible to give an arg that doesn't exist from the user side
    def __init__(self, **kwargs) -> None:

        if kwargs is None:
            kwargs = {}

        self.arranger = kwargs["arranger"]             if "arranger" in kwargs else ""
        self.composer = kwargs["composer"]             if "composer" in kwargs else ""
        self.copyright = kwargs["copyright"]           if "copyright" in kwargs else ""
        self.creationDate = kwargs["creationDate"]     if "creationDate" in kwargs else ""
        self.lyricist = kwargs["lyricist"]             if "lyricist" in kwargs else ""
        self.movementNumber = kwargs["movementNumber"] if "movementNumber" in kwargs else ""
        self.movementTitle = kwargs["movementTitle"]   if "movementTitle" in kwargs else ""
        self.movementTitle = kwargs["mscVersion"]      if "mscVersion" in kwargs else ""
        self.platform = kwargs["platform"]             if "platform" in kwargs else ""
        self.poet = kwargs["poet"]                     if "poet" in kwargs else ""
        self.source = kwargs["source"]                 if "source" in kwargs else ""
        self.translator = kwargs["translator"]         if "translator" in kwargs else ""
        self.workNumber = kwargs["workNumber"]         if "workNumber" in kwargs else ""
        self.workTitle = kwargs["workTitle"]           if "workTitle" in kwargs else ""
        self.fileName = kwargs["fileName"]             if "fileName" in kwargs else ""  # Note: Added by self


# TODO: Think of a better way to store times instead of separate lists
class Measure():

    def __init__(self, *args, **kwargs) -> None:

        if len(args):
            assert isinstance(args[0], Measure)
            self.__dict__ = deepcopy(args[0].__dict__)
            return

        if kwargs is None:
            kwargs = {}
        self.bd = kwargs["bd"] if "bd" in kwargs else []
        self.sd = kwargs["sd"] if "sd" in kwargs else []
        self.hh = kwargs["hh"] if "hh" in kwargs else []
        self.ft = kwargs["ft"] if "ft" in kwargs else []
        self.mt = kwargs["mt"] if "mt" in kwargs else []
        self.ht = kwargs["ht"] if "ht" in kwargs else []
        self.cs = kwargs["cs"] if "cs" in kwargs else []
        self.c1 = kwargs["c1"] if "c1" in kwargs else []
        self.ho = kwargs["ho"] if "ho" in kwargs else []
        self.rd = kwargs["rd"] if "rd" in kwargs else []
        self.rb = kwargs["rb"] if "rb" in kwargs else []

        # These limit note durations to insert rests instead
        self.separators = [0, 1, 2, 3]

        # Whether or not to add a line break at the end
        self.has_line_break = False

    def __iter__(self):
        return iter([deepcopy(self)])

    def get_combined_times(self):
        return \
        self.bd + \
        self.sd + \
        self.hh + \
        self.ft + \
        self.mt + \
        self.ht + \
        self.cs + \
        self.c1 + \
        self.ho + \
        self.rd + \
        self.rb

    def __eq__(self, obj):
        if isinstance(obj,Measure):
            if set(self.bd) == set(obj.bd) and \
            set(self.sd) == set(obj.sd) and \
            set(self.hh) == set(obj.hh) and \
            set(self.ft) == set(obj.ft) and \
            set(self.mt) == set(obj.mt) and \
            set(self.ht) == set(obj.ht) and \
            set(self.cs) == set(obj.cs) and \
            set(self.c1) == set(obj.c1) and \
            set(self.ho) == set(obj.ho) and \
            set(self.rd) == set(obj.rd) and \
            set(self.rb) == set(obj.rb):
            
                return True

        return False

    # Remove 1 from all user input values
    def _pre_export(self):
        def _pre_export_list(l):

            # Sanitizes the arrays to start at 0 internally
            for i in range(len(l)):
                l[i] -= 1
                assert(l[i]) >= 0

            l.sort()

            # Insert separators for tuplets that have a gap
            # TODO: Not just triplets
            for i in range(len(l)):
                if i+1 < len(l):
                    if math.isclose((l[i+1] - l[i]), 0.66) \
                    or math.isclose((l[i+1] - l[i]), 0.67):
                        self.separators.append(l[i] + 0.33)

        _pre_export_list(self.bd)
        _pre_export_list(self.sd)
        _pre_export_list(self.hh)
        _pre_export_list(self.ft)
        _pre_export_list(self.mt)
        _pre_export_list(self.ht)
        _pre_export_list(self.cs)
        _pre_export_list(self.c1)
        _pre_export_list(self.ho)
        _pre_export_list(self.rd)
        _pre_export_list(self.rb)

    # TODO: Debug print function

# TODO: What is a song if not a list of measures with metadata?
#       Is this class really needed?
class Song():

    def __init__(self) -> None:
        self.measures = []
        self.metadata = Metadata()

# Wrap for usability
def Range(start, stop, step) -> list:
    import numpy as np
    return np.arange(start,stop,step).tolist()

# TODO: Choose between list comp and inplace edit (perf also)
def RemoveEach(l: list, each: float):
    return [v for v in l if v % 1 != each]
