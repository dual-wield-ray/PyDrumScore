# pylint: disable = missing-module-docstring

import pydrumscore.core.song as api
from pydrumscore.core.beats import MONEY_BEAT

measures = []

metadata = api.Metadata(
        workTitle = "MoneyBeat_1b"
    )

measures += MONEY_BEAT
