END = 5

class Metadata():

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
        self.platform = kwargs["platform"]             if "platform" in kwargs else ""
        self.poet = kwargs["poet"]                     if "poet" in kwargs else ""
        self.source = kwargs["source"]                 if "source" in kwargs else ""
        self.translator = kwargs["translator"]         if "translator" in kwargs else ""
        self.workNumber = kwargs["workNumber"]         if "workNumber" in kwargs else ""
        self.workTitle = kwargs["workTitle"]           if "workTitle" in kwargs else ""
        self.fileName = kwargs["fileName"]             if "fileName" in kwargs else ""  # Note: Added by self

class Measure():

    def __init__(self, **kwargs) -> None:
        if kwargs is None:
            kwargs = {}
        self.bd = kwargs["bd"] if "bd" in kwargs else []
        self.sd = kwargs["sd"] if "sd" in kwargs else []
        self.hh = kwargs["hh"] if "hh" in kwargs else []

    # Remove 1 from all user input values
    # Sanitizes the arrays to start at 0 internally
    def _sanitize(self):
        def _sanitize_list(l):
            for i in range(len(l)):
                l[i] -= 1
                assert(l[i]) >= 0

        _sanitize_list(self.bd)
        _sanitize_list(self.sd)
        _sanitize_list(self.hh)

    # TODO: Debug print function

class Song():

    def __init__(self) -> None:
        self.measures = []
        self.metadata = Metadata()

    # Song generation goes here
    def generate(self):
        pass

    def add_measure(self, m):
        from copy import deepcopy
        self.measures.append(deepcopy(m))  # TODO: Remove deepcopy?

# Wrap for usability
def Range(start, stop, step) -> list:
    import numpy as np
    return np.arange(start,stop,step).tolist()

# TODO: Choose between list comp and inplace edit (perf also)
def RemoveEach(l: list, each: float):
    return [v for v in l if v % 1 != each]
