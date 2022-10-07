import exporter
from bitstring import BitString

class Measure():
    bd = []
    sn = []
    hh = []

BASIC_GROOVE = Measure()
BASIC_GROOVE.hh = [8, 8, 8, 8, 8, 8, 8, 8]
BASIC_GROOVE.sn = [0,    4,    0,    4]
BASIC_GROOVE.bd = [4,    0,    4,    0]

BASIC_GROOVE.hh = BitString('0b11111111')

def main():

    song_metadata = exporter.Metadata()
    song_measures = []

    song_measures.append(BASIC_GROOVE)

    exporter.exportSong(song_metadata, song_measures)

if __name__ == "__main__":
    main()
