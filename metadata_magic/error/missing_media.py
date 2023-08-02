#!/usr/bin/env python3

import os
import tqdm
import argparse
import python_print_tools.printer
import metadata_magic.meta_finder as mm_meta_finder
from os.path import abspath, exists, join
from typing import List

def find_missing_media(path:str) -> List[str]:
    """
    Returns a list of JSON metadata files without corresponding media.

    :param path: Directory in which to search
    :type path: str, required
    :return: List of JSON files with missing media
    :rtype: list[str]
    """
    # Separate JSON and media files and get proper metadata pairs
    jsons, media = mm_meta_finder.separate_files(path)
    pairs = mm_meta_finder.get_pairs_from_lists(media)
    # Remove paired JSON files
    print("Finding JSONs with missing media:")
    for pair in tqdm.tqdm(pairs):
        try:
            index = jsons.index(pair["json"])
            del jsons[index]
        except ValueError: pass
    # Return list of JSON files without media
    return jsons

def main():
    """
    Sets up the parser for the user to find JSONs with missing media files.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory to search for JSONs within.",
            nargs="?",
            type=str,
            default=str(os.getcwd()))
    args = parser.parse_args()
    # Check that directory is valid
    directory = abspath(args.directory)
    if not exists(directory):
        python_print_tools.printer.color_print("Invalid directory.", "red")
    else:
        # Get list of JSONs with missing media
        missing = find_missing_media(directory)
        length = len(missing)
        # Print list of missing media
        if length > 0:
            python_print_tools.printer.print_files(directory, missing)
            python_print_tools.printer.color_print(f"{length} JSONs with missing media.", "red")
        else:
            python_print_tools.printer.color_print("No JSONs with missing media found.", "green")
