Welcome to PyDrumScore!
=======================

.. include:: ../README.md
   :parser: myst_parser.sphinx_

.. toctree::
   :maxdepth: 2
   :caption: Navigation:

   source/modules

What does it do?
================



How it works
============

Two things are needed for the score generator:

- The score **metadata**, such as its title, its author, or the year it was created.
- A list of **measures** that represent the music being played.

The user's sole responsability is to modify these objects inside a python file. They are free to use all the power of Python to do so.
See here an example for a classic drum beat.

.. code-block:: python

   """ basic_beat.py """
   import pydrumscore.core.song as pds  # Import pydrumscore

   # Enter all relevant metadata
   metadata = pds.Metadata(
         workTitle = "BasicBeat"
      )

   # Measures of the entire song; fill this!
   measures = []

   # Add a measure
   measures += pds.Measure(
      bd = [1, 3],  # Bass drum on 1 and 3
      sd = [2, 4],  # Snare on 2 and 4
      hh = note_range(1, END, 1/2)  # Hi-hat from 1 to measure end, each lasting half a beat
      )



Installation
============

Using pip
---------
PyDrumScore is distributed as a pure Python package, in the form of a wheel distribution hosted on `PyPI <https://pypi.org/project/pydrumscore/>`_.
It can thus be downloaded with ``pip``, by simply executing in your Python environment::

   pip install pydrumscore

This will install PyDrumScore and all its dependencies in your active Python environment.
Note that it is good practice to use virtual environments when installing packages; see `this guide <https://dev.to/bowmanjd/python-tools-for-managing-virtual-environments-3bko#howto>`_ for a good primer on the concept.

Manual install
--------------
It is possible to download the package content by hand through the `project page <https://pypi.org/project/pydrumscore/#files>`_. The file contents of the .whl distribution, which is a zip file, can then be added to the environment. Note, however, that this does not handle the package dependencies like `pip`` would; you will need to install them individually in your environment as well.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`license`
