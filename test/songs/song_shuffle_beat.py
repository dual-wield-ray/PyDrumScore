#TODO: Think about this. It's like a little language so it might be ok
from song import *

from beats import SHUFFLE_BEAT

def generate_metadata(song: Song):
    song.metadata = Metadata(
        workTitle = "ShuffleBeat_1b"
    )

def generate_song(song: Song):
    song.add_measure(SHUFFLE_BEAT)
