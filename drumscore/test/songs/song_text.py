import drumscore.core.song as api
from drumscore.core.beats import SILENCE

metadata = api.Metadata(
        workTitle = "Text on first measure"
    )

measures = [SILENCE]

measures[0].text = "This is some text"
