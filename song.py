from copy import deepcopy
import numpy as np

class Metadata():
    arranger = ""
    composer = ""
    copyright = ""
    creationDate = ""
    lyricist = ""
    movementNumber = ""
    movementTitle = ""
    platform = ""
    poet = ""
    source = ""
    translator = ""
    workNumber = ""
    workTitle = ""
    fileName = ""  # Note: Added by self


class Measure():

    END = 5

    def __init__(self, **kwargs) -> None:
        self.bd = []
        self.sd = []
        self.hh = []
        if kwargs is not None:
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

    # Clear all measures
    def clear(self) -> None:
        self.measures = []

    def add_measure(self, m):
        self.measures.append(deepcopy(m))  # TODO: Remove deepcopy?

# Wrap for usability
def Range(start, stop, step) -> list:
    return np.arange(start,stop,step).tolist()

# TODO: Choose between list comp and inplace edit (perf also)
def RemoveEach(l: list, each: float):
    return [v for v in l if v % 1 != each]
