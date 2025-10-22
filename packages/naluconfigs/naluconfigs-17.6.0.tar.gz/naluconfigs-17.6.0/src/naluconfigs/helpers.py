import sys
from pathlib import Path

import yaml

# Determine bundle directory in case this package exists in a pyinstaller app
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    _BUNDLE_DIR = Path(sys._MEIPASS) / "naluconfigs"
else:
    _BUNDLE_DIR = Path(__file__).parent


CONFIGS_DIR = Path.cwd() / _BUNDLE_DIR / "data"
REGISTERS_DIR = CONFIGS_DIR / "registers"
CLOCKS_DIR = CONFIGS_DIR / "clocks"
CHIPS_DIR = CONFIGS_DIR / "chips"

_default_chip_config_cache = {}

def default_chip_config(chip_name: str) -> dict:
    """Retrieve the default chip config for a chip.

    Args:
        chip_name (str): The chip name

    Returns:
        dict: the default chip configuration

    Raises:
        FileNotFoundError: if the config file cannot be found
        OSError: if the config file cannot be read
        yaml.YAMLError: if the config file is invalid YAML
    """
    if chip_name in _default_chip_config_cache:
        return _default_chip_config_cache[chip_name]
    yml_file = CHIPS_DIR / (chip_name + ".yml")
    try:
        with open(yml_file, "r") as f:
            out = yaml.safe_load(f)
            _default_chip_config_cache[chip_name] = out
            return out
    except (FileNotFoundError, OSError):
        raise
    except yaml.YAMLError:
        raise
