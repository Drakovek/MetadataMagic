#!/usr/bin/env python3

import os
import json
import metadata_magic.file_tools as mm_file_tools
from os.path import abspath, expandvars, join
from typing import List

CONFIG_DIRECTORY = abspath(join(abspath(join(abspath(__file__), os.pardir)), "config_files"))
DEFAULT_CONFIG_FILE = abspath(join(CONFIG_DIRECTORY, "config.json"))

def get_default_config_paths() -> List[str]:
    """
    Returns a list of all the default locations for the metadata-magic config file.

    :return: List of default paths to the config file
    :rtype: List[str]
    """
    config_paths = []
    if os.name == "nt":
        # Add Windows Paths
        config_paths.append(r"%APPDATA%\metadata-magic\config.json")
        config_paths.append(r"%APPDATA%\metadata-magic\metadata-magic.json")
        config_paths.append(r"%USERPROFILE%\metadata-magic\config.json")
        config_paths.append(r"%USERPROFILE%\metadata-magic\metadata-magic.json")
        config_paths.append(r"%USERPROFILE%\metadata-magic.json")
    else:
        # Add Linux/MacOS/Unix-based paths
        config_paths.append(r"/etc/metadata-magic.json")
        config_paths.append(r"${HOME}/.config/metadata-magic/config.json")
        config_paths.append(r"${HOME}/.config/metadata-magic/metadata-magic.json")
        config_paths.append(r"${HOME}/.metadata-magic/config.json")
        config_paths.append(r"${HOME}/.metadata-magic/metadata-magic.json")
    # Replace the environment variables in paths
    for i in range(0, len(config_paths)):
        config_paths[i] = abspath(expandvars(config_paths[i]))
    # Return the config paths
    return config_paths

def get_config(paths:List[str]) -> dict:
    """
    Returns a dict for the first valid JSON file in the given path list.

    :param paths: List of potential paths to JSON config files.
    :type paths: List[str], required
    :return: Contents of the configuration file
    :rtype: dict
    """
    # Try to read any of the config files
    for file in paths:
        config = mm_file_tools.read_json_file(abspath(file))
        if config is not None and not config == {}:
            return config
    # Return an empty dictionary if the config file couldn't be read
    return mm_file_tools.read_json_file(DEFAULT_CONFIG_FILE)
