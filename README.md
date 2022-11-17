## What is it?

PyDrumScore is a Python library for generating drum sheet music through code. It aims to provide a lean interface, relying on core Python features and data types. This allows the user to programatically bypass the relative complexity of modern scoring softwares, whose features often go beyond the scope of what is needed to create drum sheet music.

## How does it work?

Two things are needed for the score generator:

- The score **metadata**, such as its title, its author, or the year it was created.
- A list of **measures** that represent the music being played.

The user's sole responsability is to modify these objects inside a python file. They are free to use all the power of Python to do so.
See here a complete example for a classic drum beat.

```python
   """ basic_beat.py """

    # Import pydrumscore
   import pydrumscore.core.song as pds

   # Enter relevant metadata
   metadata = pds.Metadata(
         workTitle = "BasicBeat"
      )

   # Measures of the song; fill this!
   measures = []

   # Add a measure
   measures += pds.Measure(
      bd = [1, 3],  # Bass drum on 1 and 3
      sd = [2, 4],  # Snare on 2 and 4
      hh = pds.note_range(1, END, 1/2)  # Hi-hat from 1 to measure end,
                                        # each lasting half a beat
      )
```

Afterwards, simply call the exporter with:
```
python pydrumscore basic_beat
```

The song module will be imported, and the contents of the ```metadata``` and ```measures``` objects will be converted to an uncompressed MuseScore file under the title *BasicBeat.mscx*. That's it! You can now open this file in MuseScore, from which you can review the results and export to a PDF file.

## Installation

### Using pip

PyDrumScore is distributed as a pure Python package, in the form of a wheel distribution hosted on [PyPI](https://pypi.org/project/pydrumscore/).
It can thus be downloaded with ``pip``, by simply executing in your Python environment:

```
pip install pydrumscore
```

This will install PyDrumScore and all its dependencies in your active Python environment.
Note that it is good practice to use virtual environments when installing packages; see [this guide](https://dev.to/bowmanjd/python-tools-for-managing-virtual-environments-3bko#howto) for a good primer on the concept.

### Manual install
It is possible to download the package content by hand through the [project page](https://pypi.org/project/pydrumscore/#files). The .whl distribution, which is a zip file, can then be uncompressed and added to the environment. Note, however, that this does not handle the package dependencies like ``pip`` would; you will need to install them individually in your environment as well.

## MuseScore plugin
The PyDrumScore package also contains a plugin for MuseScore to refresh modified files with a single button. This allows for a proper workflow for using MuseScore as a viewer to PyDrumScore. To set it up, see [the tutorial](https://musescore.org/en/handbook/3/plugins#enable-disable-plugins) on MuseScore's page. Make sure the plugin is added to your MuseScore plugins folder, and that it is enabled and has a shortcut.

## Tutorials and examples
See the test folder for examples of fully transcribed songs. Stay tuned for upcoming video tutorials as well.