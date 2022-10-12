#TODO: Think about this. It's like a little language so it might be ok
from song import *

from beats import ROCK_BEAT_WOPEN

def generate_metadata(song: Song):
    song.metadata = Metadata(
        workTitle = "RockBeatWOpen_1b"
    )

def generate_song(song: Song):
    song.add_measure(ROCK_BEAT_WOPEN)
