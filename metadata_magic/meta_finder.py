#!/usr/bin/env python3

import os
import tqdm
import html_string_tools.html
import metadata_magic.sort as mm_sort
from os.path import abspath, basename, exists, isdir, join
from typing import List

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
        extension = html_string_tools.html.get_extension(full_file)
        if extension.lower() == ".json":
            jsons.append(full_file)
        elif not isdir(full_file):
            media.append(full_file)
        else:
            directories.append(full_file)
    # Append files in subdirectories
    for directory in directories:
        new_jsons, new_media = separate_files(directory)
        jsons.extend(new_jsons)
        media.extend(new_media)
    # Return JSON and media files separated
    jsons = mm_sort.sort_alphanum(jsons)
    media = mm_sort.sort_alphanum(media)
    return (jsons, media)

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
    return get_pairs_from_lists(media, print_info)

def get_pairs_from_lists(media:List[str], print_info:bool=True) -> List[dict]:
    """
    Returns a list of media files paired with their corresponding JSON metadata file.
    Returned in dicts with "json" and "media" fields.

    :param media: List of non-JSON media files
    :type media: List[str], required
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
    # Get JSON-media pairs
    for file in iterator:
        # Check if JSON with extension exists
        base = basename(file)
        parent = abspath(join(file, os.pardir))
        json = abspath(join(parent, base + ".json"))
        if exists(json):
            pair = {"json": json, "media": file}
            pairs.append(pair)
            continue
        # Check if JSON without extension exists
        extension = html_string_tools.html.get_extension(file)
        base = base[:len(base)-len(extension)]
        json = abspath(join(parent, base + ".json"))
        if exists(json):
            pair = {"json": json, "media": file}
            pairs.append(pair)
            continue
    # Return pairs
    return pairs
