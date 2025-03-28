#!/usr/bin/env python3

import re
import html_string_tools
import metadata_magic.file_tools as mm_file_tools
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
        except (KeyError, TypeError):
            # Check next key in list if key is invalid
            continue
    return None

def get_string_from_metadata(metadata:dict, template:str) -> str:
    """
    Returns a text string based on given metadata and a string template.
    Keys in the template marked as {key} will be replaced with the key values in metadata.

    :param metadata: Dictionary with metadata key-value pairs
    :type metadata: dict, required
    :param template: Metadata string template
    :type template: str, required
    :return: String containing metadata as defined by the template
    :rtype: str
    """
    # Find all keys in the template string
    filename = template
    keys = re.findall(r"(?<={)[^}]+(?=})", template)
    # Replace all the keys in the string with their values
    for key in keys:
        # Attempt to get the key
        base_key = re.sub(r"!.*", "", key)
        try:
            value = metadata[base_key]
        except KeyError:
            try:
                value = metadata["original"][base_key]
            except KeyError: return None
        # Pad value, if appropriate
        try:
            pad_value = int(re.findall(r"(?<=!p)[0-9]+$", key)[0])
            value = str(value).zfill(pad_value)
        except IndexError: pass
        # Return none if the key is empty
        if value is None:
            return None
        # Convert the value to a string, if necessary
        if isinstance(value, list):
            value = ",".join(value)
        filename = filename.replace(f"{{{key}}}", str(value))
    # Remove all key references that weren't found in the metadata
    filename = re.sub(r"{[^}]*}", "", filename).strip()
    # Return the filename
    return filename

def get_id(json:dict, config:dict) -> str:
    """
    Attempts to find the ID from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :param config: Dictionary of a metadata-magic config file
    :type config: dict, required
    :return: Extracted value for the ID
    :rtype: str
    """
    # Gets the value of the ID as read from the JSON
    keylist = config["json_reader"]["id"]["keys"]
    value = get_value_from_keylist(json, keylist, int)
    if value is None:
        value = get_value_from_keylist(json, keylist, str)
    # Return None if no ID value is found
    if value is None:
        return None
    # Strip out leading three letter ID tag if ID is from an old DVK file
    value = re.sub(r"^[A-Z]{3}[^0-9A-Z]?(?=[0-9]+$)", "", str(value))
    # Return Value
    return value

def get_title(json:dict, config:dict) -> str:
    """
    Attempts to find the title from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :param config: Dictionary of a metadata-magic config file
    :type config: dict, required
    :return: Extracted value of the title
    :rtype: str
    """
    keylist = config["json_reader"]["title"]["keys"]
    return get_value_from_keylist(json, keylist, str)

def get_num(json:dict, config:dict) -> str:
    """
    Attempts to find the image/index num from a given JSON dictionary.
    Index refers to a number indicating the image/part number in a collection.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :param config: Dictionary of a metadata-magic config file
    :type config: dict, required
    :return: Extracted value of the index
    :rtype: str
    """
    keylist = config["json_reader"]["num"]["keys"]
    value = get_value_from_keylist(json, keylist, int)
    if value is None:
        return get_value_from_keylist(json, keylist, str)
    return str(value)

def get_artists_and_writers(json:dict, config:dict, extension:str) -> (List[str], List[str]):
    """
    Attempts to find the artists and writers from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :param config: Dictionary of a metadata-magic config file
    :type config: dict, required
    :param extension: Extension of the JSON file's associated media
    :type extension: str, required
    :return: Extracted value of the authors, structured (artists, writers)
    :rtype: List[str], List[str]
    """
    # Get multiple artists and writers
    artist_keys = config["json_reader"]["artists"]["keys"]
    writer_keys = config["json_reader"]["writers"]["keys"]
    artists = get_value_from_keylist(json, artist_keys, list)
    writers = get_value_from_keylist(json, writer_keys, list)
    # Get single artist and writers
    single_artist = get_value_from_keylist(json, artist_keys, str)
    single_writer = get_value_from_keylist(json, writer_keys, str)
    if artists is None and single_artist is not None:
        artists = [single_artist]
    if writers is None and single_writer is not None:
        writers = [single_writer]
    # Update fields if only writers or artists are present
    if artists is None:
        artists = writers
    if writers is None:
        writers = artists
    # Check if the file is a written work
    text_extensions = [".txt", ".rtf", ".htm", ".html", ".doc", ".docx", ".odt"]
    if writers == artists and extension.lower() in text_extensions:
        artists = None
    # Return artists and writers
    return (artists, writers)

def get_date(json:dict, config:dict) -> str:
    """
    Attempts to find the publication date from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :param config: Dictionary of a metadata-magic config file
    :type config: dict, required
    :return: Extracted value of the publication date
    :rtype: str
    """
    # Get the base date string
    keylist = config["json_reader"]["date"]["keys"]
    value = get_value_from_keylist(json, keylist, str)
    # Return None if no value can be found
    if value is None:
        return None
    # Format date into standard format
    regex = "(19[0-9]{2}|2[0-1][0-9]{2})[\\-/](0[1-9]|1[0-2])[\\-/](0[1-9]|[1-2][0-9]|3[0-1])"
    date = re.findall(regex, value)
    if len(date) > 0:
        year, month, day = date[0]
        return f"{year}-{month}-{day}"
    regex = "(19[0-9]{2}|2[0-1][0-9]{2})(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])"
    date = re.findall(regex, value)
    if len(date) > 0:
        year, month, day = date[0]
        return f"{year}-{month}-{day}"
    return None

def get_description(json:dict, config:dict) -> str:
    """
    Attempts to find the description from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :param config: Dictionary of a metadata-magic config file
    :type config: dict, required
    :return: Extracted value for the description
    :rtype: str
    """
    keylist = [["description"], ["caption"], ["content"], ["info", "description"],
            ["chapter_description"], ["post_content"], ["webtoon_summary"]]
    return get_value_from_keylist(json, keylist, str)

def get_publisher(json:dict, config:dict) -> str:
    """
    Attempts to find the publisher from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :param config: Dictionary of a metadata-magic config file
    :type config: dict, required
    :return: Extracted value for the publisher
    :rtype: str
    """
    # Find the page URL/category of the media to base publisher on
    keylist = config["json_reader"]["publisher"]["keys"]
    url = get_value_from_keylist(json, keylist, str)
    # Return None if there was no returned value
    if url is None:
        return None
    # Find a publisher by matching to a value in the config file
    url = url.lower()
    for comparison in config["json_reader"]["publisher"]["match"]:
        if re.fullmatch(comparison["match"], url, flags=re.IGNORECASE):
            return comparison["publisher"]
    # Return None of no appropriate publisher can be found
    return None

def get_url(json:dict, config:dict, publisher:str=None) -> str:
    """
    Gets the page URL for the media described by the JSON.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :param config: Dictionary of a metadata-magic config file
    :type config: dict, required
    :param publisher: Publisher as returned by get_publisher, defaults to None
    :type publisher: str, optional
    :return: URL that the media originated from
    :rtype: str
    """
    # Attempt to get the publisher via the publisher and id
    try:
        pattern = config["json_reader"]["url"]["patterns"][publisher]
        return get_string_from_metadata(json, pattern)
    except (KeyError, TypeError): pass
    # Return default URL if it couldn't be determined by ID and publisher
    keylist = config["json_reader"]["url"]["keys"]
    url = get_value_from_keylist(json, keylist, str)
    if url is None:
        try:
            url = get_value_from_keylist(json["original"], keylist, str)
        except KeyError: return None
    return url

def get_tags(json:dict, config:dict) -> List[str]:
    """
    Attempts to find the tags from a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :param config: Dictionary of a metadata-magic config file
    :type config: dict, required
    :return: Extracted value for the tags
    :rtype: str
    """
    # Create a list of all the tags in the metadata
    tags = []
    keylist = config["json_reader"]["tags"]["keys"]
    for key in keylist:
        multi_tags = get_value_from_keylist(json, [key], list)
        if multi_tags is None:
            tags.append(get_value_from_keylist(json, [key], str))
            continue
        tags.extend(multi_tags)
    # Replace tags that are not strings
    keylist = config["json_reader"]["tags"]["internal_keys"]
    for i in range(0, len(tags)):
        if not isinstance(tags[i], str):
            tags[i] = get_value_from_keylist(tags[i], keylist, str) 
    # Delete tags that have no value
    for i in range(len(tags)-1, -1, -1):
        if tags[i] is None or tags[i] == "":
            del tags[i]
    # Return None if there are no tags
    if tags == []:
        return None
    # Return tags
    return tags

def get_age_rating(json:dict, config:dict, publisher:str) -> str:
    """
    Attempts to get a standardized age rating based on ratings values in a given JSON dictionary.
    
    :param json: JSON in dict form to search for metadata within
    :type json: dict, required
    :param config: Dictionary of a metadata-magic config file
    :type config: dict, required
    :param publisher: Publisher as returned by get_publisher to determine how the rating is stored in the JSON
    :type publisher: str, required
    :return: Extracted value for the age rating
    :rtype: str
    """
    # Get the keylist and match list
    try:
        keylist = config["json_reader"]["age_rating"]["specialized"][publisher]["keys"]
        match = config["json_reader"]["age_rating"]["specialized"][publisher]["match"]
    except KeyError:
        keylist = config["json_reader"]["age_rating"]["keys"]
        match = config["json_reader"]["age_rating"]["match"]
    # Get the age rating based on the base metadata value and its match in the config
    try:
        assert publisher in config["json_reader"]["age_rating"]["allowed"]
        base = get_value_from_keylist(json, keylist, str).lower()
        return match[base]
    except (AssertionError, AttributeError, KeyError):
        return "Unknown"

def load_metadata(json_file:str, config:dict, media_file:str) -> dict:
    """
    Loads metadata from a given JSON file.
    
    :param json_file: Path of the JSON file to read
    :type json_file: str, required
    :param config: Dictionary of a metadata-magic config file
    :type config: dict, required
    :param media_file: Path of the associated media file of the JSON
    :type media_file: str, required
    :return: Dictionary containing the JSON's metadata using standardized keys
    :rtype: dict
    """
    # Load JSON into dictionary
    json = mm_file_tools.read_json_file(json_file)
    # Set the path of the JSON in the metadata
    meta_dict = {"json_path":abspath(json_file)}
    # Add internal metadata in standardized forms
    meta_dict["original"] = json
    meta_dict["id"] = get_id(json, config)
    meta_dict["title"] = get_title(json, config)
    meta_dict["num"] = get_num(json, config)
    meta_dict["date"] = get_date(json, config)
    meta_dict["description"] = get_description(json, config)
    meta_dict["publisher"] = get_publisher(json, config)
    meta_dict["tags"] = get_tags(json, config)
    meta_dict["age_rating"] = get_age_rating(json, config, meta_dict["publisher"])
    extension = html_string_tools.get_extension(media_file)
    meta_dict["artists"], meta_dict["writers"] = get_artists_and_writers(json, config, extension)
    meta_dict["url"] = get_url(meta_dict, config, meta_dict["publisher"])
    # Return the dict with all metadata
    return meta_dict
