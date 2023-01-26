from configparser import ConfigParser
from from_root import from_root
from pathlib import Path
import setuptools_scm
import importlib
from collections import namedtuple

# PyDrumScoreConfig = namedtuple('PyDrumScoreConfig', ['export_folder', 'pydrumscore_version', 'msversion', 'program_revision', 'program_version'])

# def ReadConfig() ->PyDrumScoreConfig:

class PDSConfig:

    def __init__(self) -> None:

        # Get pydrumscore version from setuptools' source control
        self.pydrumscore_version = ""
        version_module_name = "pydrumscore.__version__"
        if importlib.util.find_spec(version_module_name):
            # If using source distribution (or if package was locally built) get version from it
            version_mod = importlib.import_module(version_module_name)
            self.pydrumscore_version = version_mod.version
        else:
            self.pydrumscore_version = setuptools_scm.get_version(root="../", relative_to=__file__)

        # Read config file
        config_root = from_root()
        if config_root.stem != "pydrumscore":
            # Work around apparent issue in "from_root" where cloned and pip installed setup differ by one level
            config_root = config_root / "pydrumscore"

        # Note: Due to a bug, it's not possible to get MuseScore version info from CLI on Windows
        #       Perhaps revisit sometime if it has been done, or do it ourselves...
        self.user_configur = ConfigParser()
        config_path = Path("config.ini")
        if Path.exists(config_path):
            self.user_configur.read(config_path)

        self.default_configur = ConfigParser()
        self.default_configur.read(config_root / "default_config.ini")

    def get_config_option(self, section: str, option: str):
        assert self.default_configur.has_option(section, option)

        configur = self.user_configur if self.user_configur.has_option(section, option) else self.default_configur
        return configur.get(section, option)