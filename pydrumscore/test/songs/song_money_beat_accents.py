# pylint: disable = missing-module-docstring

import pydrumscore as api
from pydrumscore.core.beats import MONEY_BEAT

measures = []

metadata = api.Metadata(
        workTitle = "MoneyBeat_Accents_1b"
    )

measures += api.Measure(MONEY_BEAT)
measures[0].ac = [2,4]
