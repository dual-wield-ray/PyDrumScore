import exporter
from song import RemoveEach, Song, Measure, Range

# TODO: Make some more basic grooves and put them somewhere
BASIC_GROOVE = Measure()
BASIC_GROOVE.sd = [2, 2.5, 4]
BASIC_GROOVE.bd = [1, 1.25]
BASIC_GROOVE.hh = Range(1, Measure.END, 0.5)

FILL = Measure()
FILL.sd = Range(1,Measure.END, 0.25)
FILL.sd = RemoveEach(FILL.sd, 0.75)  # remove each third

class TestSong(Song):

    def generate(self):
        assert self.metadata.workTitle != ""
        assert self.metadata.fileName != ""

        # Append the basic groove 7 times
        for _ in range(7):
            self.add_measure(BASIC_GROOVE)

        # On the eighth, add a fill
        self.add_measure(FILL)

        for m in self.measures:
            m._sanitize()

        exporter.exportSong(self)

if __name__ == "__main__":
    my_song = TestSong()
    my_song.metadata.workTitle = "Test song"
    my_song.metadata.fileName = "DrumScore.mscx"

    my_song.generate()
