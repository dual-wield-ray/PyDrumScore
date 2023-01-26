from configparser import ConfigParser
from from_root import from_root
from pathlib import Path
from collections import namedtuple

PyDrumScoreConfig = namedtuple('PyDrumScoreConfig', ['export_folder', 'msversion', 'program_revision', 'program_version'])

def read_config() ->PyDrumScoreConfig:

        # Read config file
        config_root = from_root()
        if config_root.stem != "pydrumscore":
            # Work around apparent issue in "from_root" where cloned and pip installed setup differ by one level
            config_root = config_root / "pydrumscore"

        # Note: Due to a bug, it's not possible to get MuseScore version info from CLI on Windows
        #       Perhaps revisit sometime if it has been done, or do it ourselves...
        user_configur = ConfigParser()
        config_path = Path("config.ini")
        if Path.exists(config_path):
            user_configur.read(config_path)

        default_configur = ConfigParser()
        default_configur.read(config_root / "default_config.ini")

        def get_config_option(section: str, option: str):
            assert default_configur.has_option(section, option)

            configur = user_configur if user_configur.has_option(section, option) else default_configur
            return configur.get(section, option)

        return PyDrumScoreConfig(
                get_config_option("export", "export_folder"),
                get_config_option("msversion", "msversion"),
                get_config_option("msversion", "program_version"),
                get_config_option("msversion", "program_revision"),
        )