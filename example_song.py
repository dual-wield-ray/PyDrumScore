#TODO: Think about this. It's like a little language so it might be ok
from song import *

from beats import MONEY_BEAT

def generate_metadata(song: Song):
    song.metadata = Metadata(
        workingTitle = "MoneyBeat_1b"
    )

def generate_song(song: Song):
    for _ in range(1):
        song.add_measure(MONEY_BEAT)
