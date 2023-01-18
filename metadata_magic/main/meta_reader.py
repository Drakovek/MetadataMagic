#!/usr/bin/env python3

from json import load as load_json
from os.path import abspath
from typing import List

def get_value_from_keylist(dictionary:dict, keylist:List[List[str]], type_obj):
    """
    Returns the value for the first valid given key in a dictionary.
    
    :param dictionary: Dictionary to search for values within
    :type dictionary: dict, required
    :param keylist: List of potential keys to search for, in order for nested dicts
    :type keylist: list[list[str], required
    :param type_obj: The type of data expected to be returned
    :return type_obj: object, required
    :return: Value of the given key
    :rtype: any
    """
    for keys in keylist:
        try:
            # Get the value from the given nested key list
            result = None
            internal = dictionary
            for key in keys:
                result = internal[key]
                internal = result
            # Return result if not None
            if result is not None and isinstance(result, type_obj):
                return result
        except KeyError:
            # Check next key in list if key is invalid
            continue
    return None

def get_title(json:dict) -> str:
    """
    Attempts to find the title from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :return: Extracted value of the title
    :rtype: str
    """
    keylist = [["title"]]
    return get_value_from_keylist(json, keylist, str)

def get_artist(json:dict) -> str:
    """
    Attempts to find the artist from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :return: Extracted value of the artist
    :rtype: str
    """
    keylist = [["artist"], ["uploader"], ["user"], ["username"], ["author", "username"], ["user", "name"]]
    return get_value_from_keylist(json, keylist, str)

def load_metadata(json_file:str) -> dict:
    """
    Loads metadata from a given JSON file.
    
    :param json_file: Path of the JSON file to read
    :type json_file: str, required
    :return: Dictionary containing the JSON's metadata using standardized keys
    :rtype: dict
    """
    # Load JSON into dictionary
    path = abspath(json_file)
    try:
        with open(path) as in_file:
            json = load_json(in_file)
    except FileNotFoundError:
        json = dict()
    # Set the path of the JSON in the metadata
    meta_dict = {"json_path":path}
    # Get the title from the given JSON file
    meta_dict["title"] = get_title(json)
    # Get the artist from the given JSON file
    meta_dict["artist"] = get_artist(json)
    # Return the dict with all metadata
    return meta_dict