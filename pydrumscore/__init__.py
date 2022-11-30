"""
Contains pydrumscore's song creation API. Use the classes and functions in this package to create song modules.
"""
import logging

# Imports the entire API into the "pydrumscore" namespace
# Note: This wildcard approach means the API needs to be maintained to not leak symbols
#       The approach is similar to what is done in numpy, for example
from pydrumscore.api import *

# Init logger for all modules
logging.basicConfig(level=logging.INFO)
