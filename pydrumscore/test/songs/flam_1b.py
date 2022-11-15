# pylint: disable = missing-module-docstring

import pydrumscore.core.song as api

########### Metadata ###########
metadata = api.Metadata(
        workTitle = 'Flam_1b'
    )
########### End Metadata ###########


########### Song creation ###########

# Fill up this array with api.Measure objects
measures = []

measures += api.Measure(
    fm = [1]
    )

########### End song creation ###########
