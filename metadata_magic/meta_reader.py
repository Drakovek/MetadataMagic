#!/usr/bin/env python3

import re
from os.path import abspath
from typing import List
from . import file_tools as mm_file_tools

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
        except (KeyError, TypeError):
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
    # Gets the value of the ID as read from the JSON
    keylist = [["id"], ["display_id"], ["index"], ["submission_id"], ["submitid"]]
    value = get_value_from_keylist(json, keylist, int)
    if value is None:
        value = get_value_from_keylist(json, keylist, str)
    # Return None if no ID value is found
    if value is None:
        return None
    # Strip out leading three letter ID tag if ID is from a DVK file
    try:
        leader = re.findall("^[A-Z]{3}[^0-9A-Z]*(?=[0-9])", value)
        new_value = value[len(leader[0]):]
        value = new_value
    except (IndexError, TypeError): pass
    # Add file ID, if applicable
    file_id = get_value_from_keylist(json, [["file_id"]], str)
    if file_id is not None:
        value = f"{value}-{file_id}"
    # Return Value
    return str(value)

def get_title(json:dict) -> str:
    """
    Attempts to find the title from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :return: Extracted value of the title
    :rtype: str
    """
    keylist = [["title"], ["info", "title"]]
    return get_value_from_keylist(json, keylist, str)

def get_artist(json:dict) -> str:
    """
    Attempts to find the artist from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :return: Extracted value of the artist
    :rtype: str
    """
    keylist = [["artist"], ["uploader"], ["user"], ["username"], ["artists"], ["author", "username"],
               ["creator", "full_name"], ["user", "name"], ["info", "artists"], ["owner"], ["author"]]
    # Try getting artist from string value
    value = get_value_from_keylist(json, keylist, str)
    # Try getting artist from list
    if value is None:
        artists = get_value_from_keylist(json, keylist, list)
        if artists is not None and len(artists) > 0:
            value = artists[0]
    # Return artist value
    return value

def get_date(json:dict) -> str:
    """
    Attempts to find the publication date from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :return: Extracted value of the publication date
    :rtype: str
    """
    # Get the date string
    keylist = [["date"], ["upload_date"], ["published_at"], ["info", "time"]]
    value = get_value_from_keylist(json, keylist, str)
    # Return None if no value can be found
    if value is None:
        return None
    # Format date into standard format
    regex = "(19[7-9][0-9]|2[0-1][0-9]{2})[\\-/](0[1-9]|1[0-2])[\\-/](0[1-9]|[1-2][0-9]|3[0-1])"
    date = re.findall(regex, value)
    if len(date) > 0:
        year, month, day = date[0]
        return f"{year}-{month}-{day}"
    regex = "(19[7-9][0-9]|2[0-1][0-9]{2})(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])"
    date = re.findall(regex, value)
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
    keylist = [["description"], ["caption"], ["content"], ["info", "description"]]
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
    keylist = [["link"], ["post_url"], ["webpage_url"], ["url"], ["web", "page_url"], ["category"]]
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
    keylist = [["link"], ["post_url"], ["webpage_url"], ["url"], ["web", "page_url"]]
    return get_value_from_keylist(json, keylist, str)

def get_tags(json:dict) -> List[str]:
    """
    Attempts to find the tags from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :return: Extracted value for the tags
    :rtype: str
    """
    tags = []
    # Append listed tags to the tag list
    keys = [["info", "web_tags"], ["tags"], ["categories"]]
    for key in keys:
        new_tags = get_value_from_keylist(json, [key], list)
        if new_tags is not None:
            tags.extend(new_tags)
    # Append tags that exist as a single string
    keys = ["da_category", "theme", "species", "gender"]
    for key in keys:
        tag = get_value_from_keylist(json, [[key]], str)
        if tag is not None:
            tags.append(tag)
    # Replace tag with a simple string if applicable
    keylist = [["translated_name"], ["name"]]
    for i in range(0, len(tags)):
        if not isinstance(tags[i], str):
            tags[i] = get_value_from_keylist(tags[i], keylist, str)
    # Delete tags that got replaced as None
    for i in range(len(tags)-1, -1, -1):
        if tags[i] is None:
            del tags[i]
    # Return None if there were no tags
    if tags == []:
        return None
    # Return tags
    return tags

def get_age_rating(json:dict, publisher:str) -> str:
    """
    Attempts to get a standardized age rating based on ratings values in a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :param publisher: Publisher as returned by get_publisher to determine how the rating is stored in the JSON
    :type publisher: str, required
    :return: Extracted value for the age rating
    :rtype: str
    """
    try:
        rating = ""
        # Check the publisher
        if publisher == "DeviantArt":
            # Get age rating from DeviantArt JSON
            mature = json["is_mature"]
            # Return Everyone if not Mature
            if not mature:
                return "Everyone"
            # Check how strict the mature rating should be
            level = json["mature_level"]
            if level == "moderate":
                return "Mature 17+"
            if level == "strict":
                return "X18+"
        if (publisher == "Fur Affinity"
                    or publisher == "Inkbunny"
                    or publisher == "Newgrounds"
                    or publisher == "pixiv"
                    or publisher == "Weasyl"):
            # Get standard age rating keys
            keys = [["rating"], ["rating_name"]]
            rating = get_value_from_keylist(json, keys , str).lower()
    except (AttributeError, KeyError):
        return "Unknown"
    # Return rating from rating string
    if rating == "general" or rating == "e":
        return "Everyone"
    if rating == "t":
        return "Teen"
    if rating == "mature" or rating == "m":
        return "Mature 17+"
    if rating == "adult" or rating == "a" or rating == "r-18" or rating == "explicit":
        return "X18+"
    # Return "Unknown" by default
    return "Unknown"

def load_metadata(json_file:str) -> dict:
    """
    Loads metadata from a given JSON file.
    
    :param json_file: Path of the JSON file to read
    :type json_file: str, required
    :return: Dictionary containing the JSON's metadata using standardized keys
    :rtype: dict
    """
    # Load JSON into dictionary
    json = mm_file_tools.read_json_file(json_file)
    # Set the path of the JSON in the metadata
    meta_dict = {"json_path":abspath(json_file)}
    # Add internal metadata in standardized forms
    meta_dict["id"] = get_id(json)
    meta_dict["title"] = get_title(json)
    meta_dict["artist"] = get_artist(json)
    meta_dict["writer"] = meta_dict["artist"]
    meta_dict["date"] = get_date(json)
    meta_dict["description"] = get_description(json)
    meta_dict["publisher"] = get_publisher(json)
    meta_dict["tags"] = get_tags(json)
    meta_dict["url"] = get_url(json, meta_dict["publisher"], meta_dict["id"])
    meta_dict["age_rating"] = get_age_rating(json, meta_dict["publisher"])
    # Return the dict with all metadata
    return meta_dict
