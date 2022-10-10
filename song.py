import exporter
import numpy as np

class Measure():
    bd = []
    sd = []
    hh = []

BASIC_GROOVE = Measure()
BASIC_GROOVE.hh = np.arange(0,4,0.5).tolist()
BASIC_GROOVE.sd = [1,1.5,3]
BASIC_GROOVE.bd = [0,0.25]

FILL = Measure()
FILL.sd = np.arange(0,2,0.25).tolist()
FILL.sd = [s for s in FILL.sd if s % 1 != 0.75] # remove each third

def main():

    song_metadata = exporter.Metadata()
    song_measures = []

    for i in range(7):
        song_measures.append(BASIC_GROOVE)
    song_measures.append(FILL)

    exporter.exportSong(song_metadata, song_measures)

if __name__ == "__main__":
    main()
