#!/usr/bin/env python3

import os
import tqdm
import argparse
import python_print_tools.printer
import metadata_magic.meta_finder as mm_meta_finder
from os.path import abspath, exists, join
from typing import List

def find_missing_metadata(path:str) -> List[str]:
    """
    Returns a list of media files without corresponding JSON metadata.

    :param path: Directory in which to search
    :type path: str, required
    :return: List of media files with missing metadata
    :rtype: list[str]
    """
    # Separate JSON and media files and get proper metadata pairs
    jsons, media = mm_meta_finder.separate_files(path)
    pairs = mm_meta_finder.get_pairs_from_lists(media)
    # Remove paired JSON files
    print("Finding media with missing metadata:")
    for pair in tqdm.tqdm(pairs):
        try:
            index = media.index(pair["media"])
            del media[index]
        except ValueError: pass
    # Return list of media without metadata
    return media

def main():
    """
    Sets up the parser for the user to find media with missing metadata files.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory to search for media within.",
            nargs="?",
            type=str,
            default=str(os.getcwd()))
    args = parser.parse_args()
    # Check that directory is valid
    directory = abspath(args.directory)
    if not exists(directory):
        python_print_tools.printer.color_print("Invalid directory.", "red")
    else:
        # Get list of media with missing metadata
        missing = find_missing_metadata(directory)
        length = len(missing)
        # Print list of missing metadata
        if length > 0:
            python_print_tools.printer.print_files(directory, missing)
            python_print_tools.printer.color_print(f"{length} media files with missing metadata.", "red")
        else:
            python_print_tools.printer.color_print("No missing metadata found.", "green")
