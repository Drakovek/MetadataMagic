#!/usr/bin/env python3

import os
import re
import copy
import tqdm
import html_string_tools
import metadata_magic.archive as mm_archive
import python_file_tools as pft
from os.path import abspath, basename, isdir, join
from typing import List

def separate_files(path:str, include_subdirectories:bool=True) -> tuple:
    """
    Returns a list of all files in a directory and sub_directories.
    Separated by JSON files and non-JSON files.

    :param path: Directory in which to search
    :type path: str, required
    :param include_subdirectories: Whether to include files in subdirectories, defaults to True
    :type include_subdirectories: bool, optional
    :return: List of JSON files and non-JSONs, organized (jsons, media)
    :rtype: tuple
    """
    # Get all files in the given directory
    absolute_path = abspath(path)
    all_files = pft.find_all_files(path, include_subdirectories=include_subdirectories)
    # Seperate JSON and non-JSON files
    media = []
    jsons = []
    directories = []
    for file in all_files:
        full_file = abspath(join(absolute_path, file))
        extension = html_string_tools.get_extension(full_file).lower()
        if extension == ".json":
            jsons.append(full_file)
        else:
            media.append(full_file)
    # Return JSON and media files separated
    jsons = pft.sort.sort_alphanum(jsons)
    media = pft.sort.sort_alphanum(media)
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
    # Create a dictionary mapping JSON files to the file name sans .json extension
    base_json_map = {}
    for json in jsons:
        parent = abspath(join(json, os.pardir))
        no_json_extension = abspath(join(parent, basename(json).lower()[:-5]))
        base_json_map[no_json_extension] = json
    # Run through the list of media, finding matching JSON files
    for media_file in iterator:
        # Get media file altered so base name is non-case sensitive
        parent = abspath(join(media_file, os.pardir))
        base_media_file = abspath(join(parent, basename(media_file).lower()))
        # Check if JSON exists with the same basename plus .json (test.png.json)
        json_path = base_json_map.pop(base_media_file, None)
        # Check minus the main media extension if json path not found
        if json_path is None:
            base_media_file = re.sub(r"\.[0-9A-Za-z]{1,5}$", "", base_media_file)
            json_path = base_json_map.pop(base_media_file, None)
        # If a pair was found, add to the list of pairs
        if json_path is not None:
            pair = {"json":json_path, "media":media_file}
            pairs.append(pair)
    # Return the JSON-media pairs
    return pairs

def get_pairs(path:str, print_info:bool=True, include_subdirectories:bool=True) -> List[dict]:
    """
    Returns a list of media files paired with their corresponding JSON metadata file.
    Returned in dicts with "json" and "media" fields.

    :param path: Directory in which to search for media files
    :type path: str, required
    :param print_info: Whether to print search updates to the user, defaults to true
    :type print_info: bool, optional
    :param include_subdirectories: Whether to include files in subdirectories, defaults to True
    :type include_subdirectories: bool, optional
    :return: List of media files paired with JSONs
    :rtype: List[dict]
    """
    # Print info if appropriate
    if print_info:
        print("Searching directory...")
    # Get the list of json and media files and pair when appropriate
    jsons, media = separate_files(path, include_subdirectories=include_subdirectories)
    return get_pairs_from_lists(jsons, media, print_info)
