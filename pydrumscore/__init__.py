"""
Contains pydrumscore's song creation API. Use the classes and functions in this package to create song modules.
"""
import logging
import importlib

# Imports the entire API into the "pydrumscore" namespace
# Note: This wildcard approach means the API needs to be maintained to not leak symbols
#       The approach is similar to what is done in numpy, for example
from pydrumscore.api import *

# Init logger for all modules
logging.basicConfig(level=logging.INFO)

def get_version():
    # Get pydrumscore version from setuptools' source control
    pydrumscore_version = ""
    version_module_name = "pydrumscore.__version__"
    if importlib.util.find_spec(version_module_name):
        # If using source distribution (or if package was locally built) get version from it
        version_mod = importlib.import_module(version_module_name)
        return version_mod.version
    else:
        import setuptools_scm
        return setuptools_scm.get_version(root="../", relative_to=__file__)
