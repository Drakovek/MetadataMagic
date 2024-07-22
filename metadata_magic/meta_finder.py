#!/usr/bin/env python3

import os
import re
import copy
import tqdm
import html_string_tools.html
import html_string_tools.regex
import metadata_magic.sort as mm_sort
from os.path import abspath, basename, exists, isdir, join
from typing import List

ARCHIVE_EXTENSIONS = [".cbz", ".epub"]

def separate_files(path:str) -> tuple:
    """
    Returns a list of all files in a directory and sub_directories.
    Separated by JSON files and non-JSON files.

    :param path: Directory in which to search
    :type path: str, required
    :return: List of JSON files and non-JSONs, organized (jsons, media)
    :rtype: tuple
    """
    # Get all files in the given directory
    absolute_path = abspath(path)
    all_files = os.listdir(absolute_path)
    # Seperate JSON and non-JSON files
    media = []
    jsons = []
    directories = []
    for file in all_files:
        full_file = abspath(join(absolute_path, file))
        extension = html_string_tools.html.get_extension(full_file).lower()
        if extension == ".json":
            jsons.append(full_file)
        elif isdir(full_file):
            directories.append(full_file)
        elif not extension in ARCHIVE_EXTENSIONS:
            media.append(full_file)    
    # Append files in subdirectories
    for directory in directories:
        new_jsons, new_media = separate_files(directory)
        jsons.extend(new_jsons)
        media.extend(new_media)
    # Return JSON and media files separated
    jsons = mm_sort.sort_alphanum(jsons)
    media = mm_sort.sort_alphanum(media)
    return (jsons, media)

def get_pairs_from_lists(jsons:List[str], media:List[str], print_info:bool=True) -> List[dict]:
    """
    Returns a list of media files paired with their corresponding JSON metadata file.
    Returned in dicts with "json" and "media" fields.

    :param media: List of non-JSON media files
    :type media: List[str], required
    :param json: List of JSON media files
    :type json: List[str], required
    :param print_info: Whether to print search updates to the user, defaults to true
    :type print_info: bool, optional
    :return: List of media files paired with JSONs
    :rtype: List[dict]
    """
    # Print info if appropriate
    pairs = []
    iterator = media
    if print_info:
        print("Finding JSON metadata:")
        iterator = tqdm.tqdm(media)
    # Create a new list of json basenames with the extension altered
    jsons_modified = []
    lower = lambda a: a.lower()
    for json in jsons:
        base = abspath(json)[:-5]
        base = html_string_tools.regex.regex_replace(lower, r"\.[0-9A-Za-z]{1,5}$", base)
        jsons_modified.append(base)
    # Run through the list of media, finding matching JSON files
    pairs = []
    reference_jsons = copy.deepcopy(jsons)
    for media_file in iterator:
        # Get the file with the altered extension
        base = abspath(media_file)
        base = html_string_tools.regex.regex_replace(lower, r"\.[0-9A-Za-z]{1,5}$", base)
        # Check if the JSON exists with the same basename
        try:
            index = jsons_modified.index(base)
        except ValueError:
            try:
                # Remove the media extension and check again
                base = re.sub(r"\.[0-9A-Za-z]{1,5}$", "", base)
                index = jsons_modified.index(base)
            except ValueError: continue
        # Create a pair, then add to the list of pairs
        pair = {"json":reference_jsons[index], "media":media_file}
        pairs.append(pair)
        # Delete the items from the json list and the basename list
        del jsons_modified[index]
        del reference_jsons[index]
    # Return the JSON-media pairs
    return pairs

def get_pairs(path:str, print_info:bool=True) -> List[dict]:
    """
    Returns a list of media files paired with their corresponding JSON metadata file.
    Returned in dicts with "json" and "media" fields.

    :param path: Directory in which to search for media files
    :type path: str, required
    :param print_info: Whether to print search updates to the user, defaults to true
    :type print_info: bool, optional
    :return: List of media files paired with JSONs
    :rtype: List[dict]
    """
    # Print info if appropriate
    if print_info:
        print("Searching directory...")
    # Get the list of json and media files and pair when appropriate
    jsons, media = separate_files(path)
    return get_pairs_from_lists(jsons, media, print_info)
