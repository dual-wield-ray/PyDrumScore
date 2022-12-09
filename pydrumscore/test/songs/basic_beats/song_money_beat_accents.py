# pylint: disable = missing-module-docstring

import pydrumscore as pds
from pydrumscore.beats import MONEY_BEAT

measures = []

metadata = pds.Metadata(workTitle="MoneyBeat_Accents_1b")

measures += pds.Measure(MONEY_BEAT)
measures[0].ac = [2, 4]
