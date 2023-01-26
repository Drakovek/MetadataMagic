#!/usr/bin/env python3

from json import load as load_json
from os.path import abspath
from re import findall
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

def get_id(json:dict) -> str:
    """
    Attempts to find the ID from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :return: Extracted value for the ID
    :rtype: str
    """
    keylist = [["id"], ["display_id"], ["index"], ["submission_id"], ["submitid"]]
    value = get_value_from_keylist(json, keylist, int)
    if value is not None:
        return str(value)
    return get_value_from_keylist(json, keylist, str)

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
    keylist = [["artist"], ["uploader"], ["user"], ["username"], ["author", "username"],
               ["creator", "full_name"], ["user", "name"], ["owner"]]
    return get_value_from_keylist(json, keylist, str)

def get_date(json:dict) -> str:
    """
    Attempts to find the publication date from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :return: Extracted value of the publication date
    :rtype: str
    """
    # Get the date string
    keylist = [["date"], ["upload_date"], ["published_at"]]
    value = get_value_from_keylist(json, keylist, str)
    # Return None if no value can be found
    if value is None:
        return None
    # Format date into standard format
    regex = "(19[7-9][0-9]|2[0-1][0-9]{2})\\-(0[1-9]|1[0-2])\\-(0[1-9]|[1-2][0-9]|3[0-1])"
    date = findall(regex, value)
    if len(date) > 0:
        year, month, day = date[0]
        return f"{year}-{month}-{day}"
    regex = "(19[7-9][0-9]|2[0-1][0-9]{2})(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])"
    date = findall(regex, value)
    if len(date) > 0:
        year, month, day = date[0]
        return f"{year}-{month}-{day}"
    return None

def get_description(json:dict) -> str:
    """
    Attempts to find the description from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :return: Extracted value for the description
    :rtype: str
    """
    keylist = [["description"], ["caption"], ["content"]]
    return get_value_from_keylist(json, keylist, str)

def get_publisher(json:dict) -> str:
    """
    Attempts to find the publisher from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :return: Extracted value for the publisher
    :rtype: str
    """
    # Find the page URL/category of the media to base publisher on
    keylist = [["link"], ["url"], ["post_url"], ["webpage_url"], ["category"]]
    value = get_value_from_keylist(json, keylist, str)
    # Return None if there was no returned value
    if value is None:
        return None
    value = value.lower()
    # Find a publisher based on recieved value
    if "deviantart" in value:
        return "DeviantArt"
    if "furaffinity" in value:
        return "Fur Affinity"
    if "inkbunny" in value:
        return "Inkbunny"
    if "newgrounds" in value:
        return "Newgrounds"
    if "patreon" in value:
        return "Patreon"
    if "pixiv" in value:
        return "pixiv"
    if "weasyl" in value:
        return "Weasyl"
    if "youtube" in value:
        return "YouTube"
    # Return None of no appropriate publisher can be found
    return None

def get_url(json:dict, publisher:str=None, media_id:str=None) -> str:
    """
    Gets the page URL for the media described by the JSON.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :param publisher: Publisher as returned by get_publisher, defaults to None
    :type publisher: str, optional
    :param media_id: ID as returned by get_id, defaults to None
    :type media_id: str, optional
    :return: URL that the media originated from
    :rtype: str
    """
    # Return None if publisher or ID are non-existant
    if publisher is not None and media_id is not None:
        # Generate media URL from publisher and ID if necessary
        if publisher == "Fur Affinity":
            return f"https://www.furaffinity.net/view/{media_id}/"
        if publisher == "Inkbunny":
            return f"https://inkbunny.net/s/{media_id}"
        if publisher == "pixiv":
            return f"https://www.pixiv.net/en/artworks/{media_id}"
    # Return default URL if it couldn't be determined by ID and publisher
    keylist = [["link"], ["url"], ["post_url"], ["webpage_url"]]
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
    # Add internal metadata in standardized forms
    meta_dict["id"] = get_id(json)
    meta_dict["title"] = get_title(json)
    meta_dict["artist"] = get_artist(json)
    meta_dict["date"] = get_date(json)
    meta_dict["description"] = get_description(json)
    meta_dict["publisher"] = get_publisher(json)
    meta_dict["url"] = get_url(json, meta_dict["publisher"], meta_dict["id"])
    # Return the dict with all metadata
    return meta_dict