"""
Contains pydrumscore's song creation API. Use the classes and functions in this package to create song modules.
"""
import logging

# Imports the entire API into the "pydrumscore" namespace
# TODO: Rethink this wildcard import (might be ok in the end)
from pydrumscore.core.api import *

# Init logger for all modules
logging.basicConfig(level=logging.INFO)
