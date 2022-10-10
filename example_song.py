import exporter

#TODO: Think about this. It's a little language so it might be ok
from song import *

# TODO: Make some more basic grooves and put them somewhere
BASIC_GROOVE = Measure(
    sd = [2, 2.5, 4],
    bd = [1, 1.25],
    hh = Range(1, Measure.END, 0.5)
    )

FILL = Measure(
    sd = Range(1,Measure.END, 0.25)
    )
FILL.sd = RemoveEach(FILL.sd, 0.5)  # remove each third

class TestSong(Song):

    def generate(self):
        assert self.metadata.workTitle != ""
        assert self.metadata.fileName != ""

        # Append the basic groove 7 times
        for _ in range(7):
            self.add_measure(BASIC_GROOVE)

        # On the eighth, add a fill
        self.add_measure(FILL)

        exporter.exportSong(self)

if __name__ == "__main__":
    my_song = TestSong()
    my_song.metadata.workTitle = "Test song"
    my_song.metadata.fileName = "DrumScore.mscx"

    my_song.generate()
