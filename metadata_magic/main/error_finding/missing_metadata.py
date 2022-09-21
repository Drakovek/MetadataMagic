#!/usr/bin/env python3

from argparse import ArgumentParser
from metadata_magic.main.meta_finder import get_pairs_from_lists
from metadata_magic.main.meta_finder import separate_files
from os import getcwd
from os.path import abspath, exists
from python_print_tools.main.python_print_tools import color_print
from python_print_tools.main.python_print_tools import print_files
from tqdm import tqdm
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
    jsons, media = separate_files(path)
    pairs = get_pairs_from_lists(media)
    # Remove paired JSON files
    print("Finding media with missing metadata:")
    for pair in tqdm(pairs):
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
    parser = ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory to search for media within.",
            nargs="?",
            type=str,
            default=str(getcwd()))
    args = parser.parse_args()
    # Check that directory is valid
    directory = abspath(args.directory)
    if not exists(directory):
        color_print("Invalid directory.", "red")
    else:
        # Get list of media with missing metadata
        missing = find_missing_metadata(directory)
        length = len(missing)
        # Print list of missing metadata
        if length > 0:
            print_files(directory, missing)
            color_print(f"{length} media files with missing metadata.", "red")
        else:
            color_print("No missing metadata found.", "green")

if __name__ == "__main__":
    main()
