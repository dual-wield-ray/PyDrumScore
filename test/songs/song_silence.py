#TODO: Think about this. It's like a little language so it might be ok
from song import *

from beats import SILENCE

def generate_metadata(song: Song):
    song.metadata = Metadata(
        workTitle = "Silence_1b"
    )

def generate_song(song: Song):
    song.add_measure(SILENCE)
