.. include:: contentheader.rst

Getting started
===============

This section assumes that you have PyDrumScore installed in a python environment on your machine. If not, refer to the installation section of the :ref:`main page <readme>`.

To test whether PyDrumScore is correctly installed in your environment, simply run:

::

  pydrumscore


You should get a message prompting you to add a file argument to export.

Lastly, you should also have set up MuseScore already. You can find the steps on the :doc:`MuseScore Setup <musescore>` page.

Writing a simple score
----------------------

The following is a step-by-step example for creating a simple score and exporting it. First off, create a new empty Python file in the editor of your choice. Name it as you wish; here it is called ``example_song.py``.

PyDrumScore needs two components for its export:

- A ``metadata`` object that contains the information about the song to export. For example, the title of the piece, its author, etc.
- A ``measures`` list, which contains all the musical data.

Both of these objects must be defined as at the root level of the song file. First, the metadata:

.. code-block:: python

  import pydrumscore

  metadata = pydrumscore.Metadata(
    workTitle = "Example Song"
  )

Notice the ``import pydrumscore`` line, which is needed to make all of the features of PyDrumScore available in the file. When using classes and functions provided by PyDrumScore, we will need to precede them with ``pydrumscore.``, just like we did for the ``Metadata``.

In the constructor of the metadata, we provide the title of our song in the form of a string. For the full list of arguments that can be provided, see the metadata class reference.

.. TODO: Reference the metadata class api

Afterwards, add some measures to the song. For now, leave a simple empty list, like so:

.. code-block:: python

  import pydrumscore

  metadata = pydrumscore.Metadata(
    workTitle = "Example Song"
  )

  measures = []

This song file can be exported by calling in terminal:

::

  pydrumscore example_song

It's important to note that the argument provided must be the name of the file itself, which may differ from the title given to the song.

.. note:: PyDrumScore currently only exports for **MuseScore 3.x**, which at the time of writing is the latest major release. There is currently a MuseScore 4.x in the works, and support for those further MuseScore versions will be added in time.

.. image:: images/about_musescore_versions.png
  :width: 400
  :alt: Window of with header written "About MuseScore". Label "Version" has number 3.6.2 highlighted, while label "Revision" has number 3224f34 highlighted.
