Philosophy
==========

.. include:: contentheader.rst

Why PyDrumScore exists
----------------------

I created PyDrumScore primarily for myself. As a drummer, drum teacher, and programmer, I found myself longing for a simple tool to score drums quickly and efficiently.
Modern scoring software is incredibly powerful, but for drums, it can sometimes be **too powerful**. Driven by the need to allow for complex orchestrations with multiple instruments, these tools have developed extensive interfaces that can have a steep learning curve.
Tackling this learning curve is worth it for composers who need the full extent of those features, but for drums it can feel like overkill. In addition, I have personally felt that drums tend to be "tacked on" to most scoring tools.
With drums relegated to an afterthought, the inherent complexity of the software leaks into the beautiful simplicity of our instrument. 🥲


Core technical philosophies
---------------------------

Beginner friendly
^^^^^^^^^^^^^^^^^
I am keenly aware that the Venn diagram of people who are both avid drummers and interested in Python programming is far from a perfect circle. Having both of these technical backgrounds is rare, so it's likely that many potential users would be new to programming.
Knowing this, many efforts were made to make the user experience as straightforward as possible

The use, as much as possible, of Python's core library
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This helps to preserve simplicity and allows people already familiar with Python syntax to get started with only a minimal API to learn. It also reduces unneeded dependencies.
Basic data types, such as lists and dicts, are preferred to unnecessary classes that act as wrappers to them.

Avoiding software bloat
^^^^^^^^^^^^^^^^^^^^^^^
In order to keep software clean, simple, deterministic, and performant, the number of features must remain relatively low. PyDrumScore is not meant to be a swiss army knife; instead, it aims to fix a very specific problem, and not more.

As such, some features that might seem to be logical continuations of the idea, are not intended to be added to PyDrumScore. These include:

- Support for other instruments (with the exception of other unpitched percussion)
- Support for live playback
- A custom programming language
- Dedicated GUI for editing
- Style editing of the generated scores (such as margins, line break sizes, etc.) [1]_

.. [1] For this purpose, support for providing a template score file in which the style was crafted from a given scoring tool would be ideal.
