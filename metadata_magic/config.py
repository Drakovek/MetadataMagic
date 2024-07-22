#!/usr/bin/env python3

import os
import json
import metadata_magic
import metadata_magic.file_tools as mm_file_tools
from os.path import abspath, expandvars
from typing import List

config_json = '{'
config_json = f'{config_json}\n    "json_reader": {{'
config_json = f'{config_json}\n        "id": {{'
config_json = f'{config_json}\n            "keys": [["id"],'
config_json = f'{config_json}\n                ["display_id"],'
config_json = f'{config_json}\n                ["index"],'
config_json = f'{config_json}\n                ["submission_id"],'
config_json = f'{config_json}\n                ["submitid"]]'
config_json = f'{config_json}\n        }},\n'
config_json = f'{config_json}\n        "title": {{'
config_json = f'{config_json}\n            "keys": [["title"],'
config_json = f'{config_json}\n                ["info", "title"]]'
config_json = f'{config_json}\n        }},\n'
config_json = f'{config_json}\n        "artists": {{'
config_json = f'{config_json}\n            "keys": [["artists"],'
config_json = f'{config_json}\n                ["info", "artists"],'
config_json = f'{config_json}\n                ["artist"],'
config_json = f'{config_json}\n                ["username"],'
config_json = f'{config_json}\n                ["user"],'
config_json = f'{config_json}\n                ["owner"],'
config_json = f'{config_json}\n                ["author", "username"],'
config_json = f'{config_json}\n                ["user", "name"]]'
config_json = f'{config_json}\n        }},\n'
config_json = f'{config_json}\n        "writers": {{'
config_json = f'{config_json}\n            "keys": [["writers"],'
config_json = f'{config_json}\n                ["authors"],'
config_json = f'{config_json}\n                ["writer"],'
config_json = f'{config_json}\n                ["author"],'
config_json = f'{config_json}\n                ["creator", "full_name"]]'
config_json = f'{config_json}\n        }},\n'
config_json = f'{config_json}\n        "date": {{'
config_json = f'{config_json}\n            "keys": [["date"],'
config_json = f'{config_json}\n                ["upload_date"],'
config_json = f'{config_json}\n                ["published_at"],'
config_json = f'{config_json}\n                ["info", "time"]]'
config_json = f'{config_json}\n        }},\n'
config_json = f'{config_json}\n        "description": {{'
config_json = f'{config_json}\n            "keys": [["description"],'
config_json = f'{config_json}\n                ["caption"],'
config_json = f'{config_json}\n                ["content"],'
config_json = f'{config_json}\n                ["info", "description"],'
config_json = f'{config_json}\n                ["chapter_description"],'
config_json = f'{config_json}\n                ["post_content"],'
config_json = f'{config_json}\n                ["webtoon_summary"]]'
config_json = f'{config_json}\n        }},\n'
config_json = f'{config_json}\n        "tags": {{'
config_json = f'{config_json}\n            "keys": [["info", "web_tags"],'
config_json = f'{config_json}\n                ["tags"],'
config_json = f'{config_json}\n                ["categories"],'
config_json = f'{config_json}\n                ["genres"],'
config_json = f'{config_json}\n                ["da_category"],'
config_json = f'{config_json}\n                ["theme"],'
config_json = f'{config_json}\n                ["species"],'
config_json = f'{config_json}\n                ["gender"]],'
config_json = f'{config_json}\n            "internal_keys": [["translated_name"],'
config_json = f'{config_json}\n                ["name"]]'
config_json = f'{config_json}\n        }},\n'
config_json = f'{config_json}\n        "publisher": {{'
config_json = f'{config_json}\n            "keys": [["link"],'
config_json = f'{config_json}\n                ["post_url"],'
config_json = f'{config_json}\n                ["webpage_url"],'
config_json = f'{config_json}\n                ["page_url"],'
config_json = f'{config_json}\n                ["url"],'
config_json = f'{config_json}\n                ["web", "page_url"],'
config_json = f'{config_json}\n                ["category"]],'
config_json = f'{config_json}\n            "match": [{{"match":"deviantart", "publisher":"DeviantArt"}},'
config_json = f'{config_json}\n                {{"match":"furaffinity", "publisher":"Fur Affinity"}},'
config_json = f'{config_json}\n                {{"match":"newgrounds", "publisher":"Newgrounds"}},'
config_json = f'{config_json}\n                {{"match":"pixiv", "publisher":"pixiv"}},'
config_json = f'{config_json}\n                {{"match":"weasyl", "publisher":"Weasyl"}},'
config_json = f'{config_json}\n                {{"match":"inkbunny", "publisher":"Inkbunny"}},'
config_json = f'{config_json}\n                {{"match":"patreon", "publisher":"Patreon"}},'
config_json = f'{config_json}\n                {{"match":"twitter", "publisher":"Twitter"}},'
config_json = f'{config_json}\n                {{"match":"tumblr", "publisher":"Tumblr"}},'
config_json = f'{config_json}\n                {{"match":"youtube", "publisher":"YouTube"}},'
config_json = f'{config_json}\n                {{"match":"non-existant-website.ca", "publisher":"DVK Test"}}]'
config_json = f'{config_json}\n        }},\n'
config_json = f'{config_json}\n        "url": {{'
config_json = f'{config_json}\n            "keys": [["link"],'
config_json = f'{config_json}\n                ["post_url"],'
config_json = f'{config_json}\n                ["webpage_url"],'
config_json = f'{config_json}\n                ["url"],'
config_json = f'{config_json}\n                ["web", "page_url"]],'
config_json = f'{config_json}\n            "patterns": {{'
config_json = f'{config_json}\n                "Fur Affinity": "https://www.furaffinity.net/view/*",'
config_json = f'{config_json}\n                "pixiv": "https://www.pixiv.net/en/artworks/*",'
config_json = f'{config_json}\n                "Inkbunny": "https://inkbunny.net/s/*"'
config_json = f'{config_json}\n            }}'
config_json = f'{config_json}\n        }},\n'
config_json = f'{config_json}\n        "age_rating": {{'
config_json = f'{config_json}\n            "keys": [["age_rating"],'
config_json = f'{config_json}\n                ["rating"],'
config_json = f'{config_json}\n                ["rating_name"]],'
config_json = f'{config_json}\n            "allowed": ["DeviantArt",'
config_json = f'{config_json}\n                "Fur Affinity",'
config_json = f'{config_json}\n                "Newgrounds",'
config_json = f'{config_json}\n                "pixiv",'
config_json = f'{config_json}\n                "Weasyl",'
config_json = f'{config_json}\n                "Inkbunny",'
config_json = f'{config_json}\n                "DVK Test"],'
config_json = f'{config_json}\n            "match": {{'
config_json = f'{config_json}\n                "e": "Everyone",'
config_json = f'{config_json}\n                "general": "Everyone",'
config_json = f'{config_json}\n                "t": "Teen",'
config_json = f'{config_json}\n                "pg": "Teen",'
config_json = f'{config_json}\n                "m": "Mature 17+",'
config_json = f'{config_json}\n                "r": "Mature 17+",'
config_json = f'{config_json}\n                "mature": "Mature 17+",'
config_json = f'{config_json}\n                "x": "X18+",'
config_json = f'{config_json}\n                "a": "X18+",'
config_json = f'{config_json}\n                "r-18": "X18+",'
config_json = f'{config_json}\n                "adult": "X18+",'
config_json = f'{config_json}\n                "explicit": "X18+"'
config_json = f'{config_json}\n            }},'
config_json = f'{config_json}\n            "specialized": {{'
config_json = f'{config_json}\n                "DeviantArt": {{'
config_json = f'{config_json}\n                    "keys": [["mature_level"],'
config_json = f'{config_json}\n                        ["is_mature"]],'
config_json = f'{config_json}\n                    "match": {{'
config_json = f'{config_json}\n                        "false": "Everyone",'
config_json = f'{config_json}\n                        "moderate": "Mature 17+",'
config_json = f'{config_json}\n                        "strict": "X18+"'
config_json = f'{config_json}\n                    }}'
config_json = f'{config_json}\n                }}'
config_json = f'{config_json}\n            }}'
config_json = f'{config_json}\n        }},\n'
config_json = f'{config_json}\n        "index": {{'
config_json = f'{config_json}\n            "keys": [["image_num"],'
config_json = f'{config_json}\n                ["image_number"],'
config_json = f'{config_json}\n                ["part"],'
config_json = f'{config_json}\n                ["num"]]'
config_json = f'{config_json}\n        }}'
config_json = f'{config_json}\n    }}'
config_json = f'{config_json}\n}}'

DEFAULT_CONFIG = json.loads(config_json)

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
    return DEFAULT_CONFIG
