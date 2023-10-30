#!/usr/bin/env python3

import os
import re
import argparse
import html_string_tools.html
import python_print_tools.printer
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.meta_finder as mm_meta_finder
import metadata_magic.meta_reader as mm_meta_reader
import metadata_magic.archive.epub as mm_epub
import metadata_magic.archive.comic_archive as mm_comic_archive
from os.path import abspath, isdir, exists

def get_directory_archive_type(directory:str) -> str:
    """
    Returns what kind of media archive the files in a given directory can be converted into.
    Returns "epub" if the directory contains text media.
    Returns "cbz" if the directory contains image media.
    Returns None if the directory contains no compatable media.

    :param directory: Directory to search for media within
    :type directory: str, required
    :return: Type of archive the directory's contents are suitable for
    :rtype: str
    """
    # Return "epub" if the directory contains text files
    if mm_file_tools.directory_contains(directory, [".txt"], False):
        return "epub"
    # Return "cbz" if the directory contains image files
    if mm_file_tools.directory_contains(directory, [".png", ".jpeg", ".jpg"], True):
        return "cbz"
    # Return None if no appropriate archive format could be found
    return None

def get_empty_metadata() -> dict:
    """
    Returns a dictionary with keys for multiple metadata fields, populated as None.
    This dict structure is used as a framework for metadata in media archive formats.
    """
    meta_dict = dict()
    meta_dict["title"] = None
    meta_dict["series"] = None
    meta_dict["series_number"] = None
    meta_dict["series_total"] = None
    meta_dict["description"] = None
    meta_dict["date"] = None
    meta_dict["writer"] = None
    meta_dict["artist"] = None
    meta_dict["cover_artist"] = None
    meta_dict["publisher"] = None
    meta_dict["tags"] = None
    meta_dict["url"] = None
    meta_dict["age_rating"] = None
    meta_dict["score"] = None
    return meta_dict

def get_info_from_jsons(path:str) -> dict:
    """
    Extracts the data to be put into archive metadata from a JSON file in a given directory.
    Extracts data from the first JSON file found in directory when alphanumerically sorted.
    Searches sub-directories as well.
    
    :param path: Directory in which to search for JSON files
    :type path: str, required
    :return: Dictionary containing the metadata info
    :rtype: dict
    """
    # Get all the JSON pairs
    pairs = mm_meta_finder.get_pairs(path)
    # Read all JSON metadata
    json_metas = []
    for pair in pairs:
        json_metas.append(mm_meta_reader.load_metadata(pair["json"]))
    # Get first instance of JSON metadata
    try:
        main_meta = json_metas[0]
    except IndexError: return get_empty_metadata()
    # Get most metadata from first JSON
    metadata = get_empty_metadata()
    metadata["title"] = main_meta["title"]
    metadata["date"] = main_meta["date"]
    metadata["writer"] = main_meta["writer"]
    metadata["artist"] = main_meta["artist"]
    metadata["cover_artist"] = main_meta["artist"]
    metadata["publisher"] = main_meta["publisher"]
    metadata["url"] = main_meta["url"]
    # Get description metadata
    description = main_meta["description"]
    if description is not None:
        description = html_string_tools.html.replace_entities(description)
        description = re.sub("<a [^<>]*>|<\\/a[^<>]*>|<b>|<i>|</b>|</i>", "", description)
        description = re.sub("<[^<>]*>", " ", description)
        description = re.sub("\\s+", " ", description)
        description = html_string_tools.regex.remove_whitespace(description)
    metadata["description"] = description
    # Get tag metadata
    tags = main_meta["tags"]
    if tags is not None and tags is not []:
        tag_string = tags[0]
        for i in range(1, len(tags)):
            tag_string = f"{tag_string},{tags[i]}"
        metadata["tags"] = tag_string
    # Get highest age rating in list of JSON metadata
    highest_age = "Unknown"
    for json_meta in json_metas:
        if json_meta["age_rating"] == "X18+":
            highest_age = "X18+"
            continue
        elif json_meta["age_rating"] == "Mature 17+" and not highest_age == "X18+":
            highest_age = "Mature 17+"
            continue
        elif json_meta["age_rating"] == "Teen" and (highest_age == "Everyone" or highest_age == "Unknown"):
            highest_age = "Teen"
            continue
        elif json_meta["age_rating"] == "Everyone" and highest_age == "Unknown":
            highest_age = "Everyone"
    metadata["age_rating"] = highest_age
    # Return metadata
    return metadata

def get_string_from_user(value_type:str, default_value:str=None) -> str:
    """
    Gets a string from the user with prompt generated from given value type.

    :param value_type: Name of the value user is inputting, used for the prompt
    :type value_type: str, required
    :param default_value: Default value to return, defaults to None
    :type default_value: str, optional
    :return: User value or default if the value is invalid
    :rtype: str
    """
    # Set the prompt
    prompt = value_type
    if default_value is not None:
        prompt = f"{prompt} (Defalut is \"{default_value}\")"
    # Get value from the user
    value = str(input(f"{prompt}: "))
    value = re.sub(r"^\s+|\s+$", "", value)
    # Return user value if the value is valid
    if not value == "":
        return value
    # Return default value if user value is not valid
    return default_value

def get_list_from_user(value_type:str, default_value:str=None) -> str:
    """
    Gets a list from the user with prompt generated from given value type.

    :param value_type: Name of the value user is inputting, used for the prompt
    :type value_type: str, required
    :param default_value: Default value to return, defaults to None
    :type default_value: str, optional
    :return: User value or default if the value is invalid
    :rtype: str
    """
    # Get the string value
    value = get_string_from_user(value_type, default_value)
    if value is None: return None
    # Split value by comma
    value_list = value.split(",")
    # Remove whitespace from each value
    value = ""
    for item in value_list:
        value = f"{value}{item},"
    value = re.sub(r"\s*,+$", "", value)
    value = re.sub(r"\s*,\s*", ",", value)
    # Return the value
    return value

def user_string_default(value_type:str, default_value:str) -> str:
    """
    Gets a string from the user with prompt generated from given value type.
    Will simply return the default value without prompting the user if not None.

    :param value_type: Name of the value user is inputting, used for the prompt
    :type value_type: str, required
    :param default_value: Default value to return, defaults to None
    :type default_value: str, optional
    :return: User value or default if the value is invalid
    :rtype: str
    """
    if default_value is not None:
        return default_value
    return get_string_from_user(value_type, None)

def user_list_default(value_type:str, default_value:str) -> str:
    """
    Gets a list from the user with prompt generated from given value type.
    Will simply return the default value without prompting the user if not None.

    :param value_type: Name of the value user is inputting, used for the prompt
    :type value_type: str, required
    :param default_value: Default value to return, defaults to None
    :type default_value: str, optional
    :return: User value or default if the value is invalid
    :rtype: str
    """
    if default_value is not None:
        return default_value
    return get_list_from_user(value_type, None)

def get_metadata_from_user(metadata:dict, get_score:bool) -> dict:
    """
    Gets a list of metadata from the user.
    Will not ask the user for certain fields that already contain default metadata.
    Metadata is formatted in a dictionary as returned by get_empty_metadata.

    :param metadata: Existing metadata to not ask the user for
    :type metadata: dict, required
    :param get_score: Whether to ask the user for the score
    :type get_score: bool, required
    :return: Dictonary of metadata input by the user
    :rtype: dict
    """
    user_metadata = metadata
    # Get the title
    user_metadata["title"] = get_string_from_user("Title", user_metadata["title"])
    # Get the date
    regex = "(19[7-9][0-9]|2[0-1][0-9]{2})\\-(0[1-9]|1[0-2])\\-(0[1-9]|[1-2][0-9]|3[0-1])"
    while user_metadata["date"] is None or len(re.findall(regex, user_metadata["date"])) == 0:
        user_metadata["date"] = get_string_from_user("Date (YYYY-MM-DD)", None)
    # Get the artists
    user_metadata["artist"] = user_list_default("Illustrator", user_metadata["artist"])
    if user_metadata["cover_artist"] is None:
        user_metadata["cover_artist"] = get_list_from_user("Cover Artist", user_metadata["artist"])
    if user_metadata["writer"] is None:
        user_metadata["writer"] = get_list_from_user("Writer", user_metadata["artist"])
    # Get the publisher
    user_metadata["publisher"] = user_string_default("Publisher", user_metadata["publisher"])
    # Get the URL
    user_metadata["url"] = user_string_default("URL", user_metadata["url"])
    # Get the description
    user_metadata["description"] = user_string_default("Description", user_metadata["description"])
    # Get the tags
    user_metadata["tags"] = user_list_default("Tags", user_metadata["tags"])
    # Get the age rating
    age_ratings = {"0":"Unknown", "1":"Everyone", "2":"Teen", "3":"Mature 17+", "4":"X18+"}
    if user_metadata["age_rating"] is None:
        try:
            print("0) Unknown\n1) Everyone\n2) Teen\n3) Mature 17+\n4) X18+")
            value = user_string_default("Age Rating", None)
            user_metadata["age_rating"] = age_ratings[value]
        except KeyError: user_metadata["age_rating"] = None
    # Get the score
    if get_score:
        user_metadata["score"] = user_string_default("Score (Range 0-5)", None)
    # Return the user metadata
    return user_metadata

def main():
    """
    Sets up the parser for creating a media archive.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "path",
            help="Directory to encapsulate in a media archive.",
            nargs="?",
            type=str,
            default=str(os.getcwd()))
    parser.add_argument(
            "-s",
            "--summary",
            help="Use user summary instead of summary in metadata.",
            action="store_true")
    parser.add_argument(
            "-d",
            "--date",
            help="Use user date instead of date in metadata.",
            action="store_true")
    parser.add_argument(
            "-a",
            "--artists",
            help="Use user artists instead of artists in metadata.",
            action="store_true")
    parser.add_argument(
            "-p",
            "--publisher",
            help="Use user publisher instead of publisher in metadata.",
            action="store_true")
    parser.add_argument(
            "-u",
            "--url",
            help="Use user URL instead of URL in metadata.",
            action="store_true")
    parser.add_argument(
            "-t",
            "--tags",
            help="Use user tags instead of tags in metadata.",
            action="store_true")
    parser.add_argument(
            "-r",
            "--rating",
            help="Use user age rating instead of rating in metadata.",
            action="store_true")
    parser.add_argument(
            "-g",
            "--grade",
            help="Use user grade/score instead of score in metadata.",
            action="store_true")
    args = parser.parse_args()
    # Check that directory is valid
    path = abspath(args.path)
    if not exists(path) or not isdir(path):
        python_print_tools.printer.color_print("Invalid path.", "red")
    else:
        # Discover the type of archive to create
        archive_type = get_directory_archive_type(path)
        if archive_type is None:
            python_print_tools.printer.color_print("Unsupported media.", "red")
        else:
            # Get existing info from a directory
            metadata = get_info_from_jsons(path)
            if metadata["title"] is None:
                metadata["title"] = ""
            # Remove default values that the user wishes to change
            if args.summary:
                metadata["description"] = None
            if args.date:
                metadata["date"] = None
            if args.artists:
                metadata["artist"] = None
                metadata["cover_artist"] = None
                metadata["writer"] = None
            if args.publisher:
                metadata["publisher"] = None
            if args.url:
                metadata["url"] = None
            if args.tags:
                metadata["tags"] = None
            if args.rating:
                metadata["age_rating"] = None
            if args.grade:
                metadata["score"] = None
            # Get  metadata values from the user
            metadata = get_metadata_from_user(metadata, args.grade)
            # Create the archive        
            if archive_type == "cbz":
                mm_comic_archive.create_cbz(path, metadata["title"], metadata)
            if archive_type == "epub":
                chapters = mm_epub.get_default_chapters(path, metadata["title"])
                mm_epub.create_epub(chapters, metadata, path)
