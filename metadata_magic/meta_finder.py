#!/usr/bin/env python3

import os
import tqdm
import html_string_tools.html
from typing import List
from os.path import abspath, basename, exists, isdir, join
from .rename import rename_tools as mm_rename_tools

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
    jsons = mm_rename_tools.sort_alphanum(jsons)
    media = mm_rename_tools.sort_alphanum(media)
    return (jsons, media)

def get_pairs(path:str) -> List[dict]:
    """
    Returns a list of media files paired with their corresponding JSON metadata file.
    Returned in dicts with "json" and "media" fields.

    :param path: Directory in which to search for media files
    :type path: str, required
    :return: List of media files paired with JSONs
    :rtype: List[dict]
    """
    print("Searching directory...")
    jsons, media = separate_files(path)
    return get_pairs_from_lists(media)

def get_pairs_from_lists(media:List[str]) -> List[dict]:
    """
    Returns a list of media files paired with their corresponding JSON metadata file.
    Returned in dicts with "json" and "media" fields.

    :param media: List of non-JSON media files
    :type media: List[str], required
    :return: List of media files paired with JSONs
    :rtype: List[dict]
    """
    # Get pairs
    pairs = []
    print("Finding JSON metadata:")
    for file in tqdm.tqdm(media):
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
