#!/usr/bin/env python3

import metadata_magic.config as mm_config

def test_get_default_config_paths():
    """
    Tests the get_default_config_paths function.
    """
    config_paths = mm_config.get_default_config_paths()
    assert len(config_paths) == 5

def test_get_config():
    """
    Tests the get_config file.
    """
    # Test getting the default config file
    paths = ["/non/existant/file.json"]
    config = mm_config.get_config(paths)
    assert config["json_reader"]["title"]["keys"] == [["title"], ["info", "title"]]
