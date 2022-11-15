# PyDrumScore

PyDrumScore is a Python library for generating drum sheet music through code. It aims to provide a lean interface, relying on core Python features and data types. This allows the user to programatically bypass the relative complexity of modern scoring softwares, whose features often go beyond the scope of what is needed to create drum sheet music.

## Known limitations of prerelease versions
These important are planned for future releases
- MusicXML format not supported yet
- Tuplets still experimental

In accordance with the aim of PyDrumScore to remain a tool that does one thing well, and not a swiss army knife of features, the following are not on the roadmap for the tool:
- Support for non-percussion (pitched) instruments
- Support for live playback
- Dedicated GUI for editing

## MuseScore plugin
The PyDrumScore package also contains a plugin for MuseScore to refresh modified files using "F5". To set it up, see [the tutorial](https://musescore.org/en/handbook/3/plugins#enable-disable-plugins) on MuseScore's page. Make sure the plugin is added to your MuseScore plugins folder, and that it is enabled and has a shortcut.

## Examples
See the test folder for examples of fully transcribed songs.