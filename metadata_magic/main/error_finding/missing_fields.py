#!/usr/bin/env python3

from metadata_magic.main.meta_reader import get_empty_metadata
from metadata_magic.main.comic_archive.comic_archive import get_info_from_cbz
from metadata_magic.main.file_tools.file_tools import find_files_of_type
from argparse import ArgumentParser
from os import getcwd
from os.path import abspath, exists
from python_print_tools.main.python_print_tools import color_print
from python_print_tools.main.python_print_tools import print_files
from typing import List
from tqdm import tqdm

def find_missing_comic_info(path:str) -> List[str]:
    """
    Finds .cbz archives that have no attached metadata.
    Includes .cbz archives where the ComicInfo.xml file is not in the base directory.
    
    :param path: Directory in which to search for files
    :type path: str, required
    :return: List of .cbz archives with no metadata
    :rtype: list[str]
    """
    # Find all the .cbz files in the given path
    empty_metadata = get_empty_metadata()
    empty_metadata["age_rating"] = "Unknown"
    cbz_files = find_files_of_type(abspath(path), ".cbz")
    # Check the metadata of each CBZ file
    missing = []
    for cbz_file in tqdm(cbz_files):
        # Check if metadata is empty
        metadata = get_info_from_cbz(cbz_file, False)
        if metadata == get_empty_metadata() or metadata == empty_metadata:
            missing.append(cbz_file)
    # Return .cbz files with missing comic info
    return missing

def find_missing_fields(path:str, fields:List[str], null_value:str=None) -> List[str]:
    """
    Finds .cbz archives with certain missing fields in their metadata.
    Will include a file if all the fields given equal None.
    
    :param path: Directory in which to search for media
    :type path: str, required
    :param fields: List of metadata fields to check for
    :type fields: list[str], required
    :param null_value: An optional additional value to be considered as None, defaults to None
    :type null_value: str, optional
    :return: List of .cbz archive files missing the given fields
    :rtype: list[str]
    """
    # Find all the .cbz files in the given path
    cbz_files = find_files_of_type(abspath(path), ".cbz", include_subdirectories=True)
    # Check the metadata of each CBZ file
    missing = []
    for cbz_file in tqdm(cbz_files):
        include = True
        metadata = get_info_from_cbz(cbz_file)
        # Check if the given metadata is None
        for field in fields:
            if metadata[field] is not None and not metadata[field] == null_value:
                include = False
                break
        # Add to the list of cbzs with a missing field if applicable
        if include:
            missing.append(cbz_file)
    # Return the list of .cbz files with missing fields
    return missing

def main():
    """
    Sets up the parser for finding files with missing metadata fields.
    """
    # Set up argument parser
    parser = ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory in which to search for media with missing metadata.",
            nargs="?",
            type=str,
            default=str(getcwd()))
    args = parser.parse_args()
    # Check that directory is valid
    path = abspath(args.directory)
    if not exists(path):
        color_print("Invalid path.", "red")
    else:
        # Ask the user for what type of missing field to search for
        print("[M] Missing metadata")
        print("[T] Missing title")
        print("[A] Missing artist")
        print("[D] Missing date")
        print("[S] Missing summary")
        print("[P] Missing publisher")
        print("[U] Missing URL")
        print("[R] Missing Age Rating")
        print("[G] Missing Grade/Score")
        print("[L] Missing Label/Tag")
        print("[C] Missing Chain/Series")
        response = str(input("Which Missing Metadata Field?: ")).lower()
        # Check media based on user response
        label = None
        if response == "m":
            # Missing metadata content
            label = "metadata"
            missing = find_missing_comic_info(path)
        elif response == "t":
            # Missing title
            label = "title"
            missing = find_missing_fields(path, ["title"])
        elif response == "a":
            # Missing artist
            label = "artist/writer"
            missing = find_missing_fields(path, ["artist", "writer"])
        elif response == "d":
            # Missing date
            label = "date"
            missing = find_missing_fields(path, ["date"])
        elif response == "s":
            # Missing summary
            label = "summary"
            missing = find_missing_fields(path, ["description"])
        elif response == "p":
            # Missing publisher
            label = "publisher"
            missing = find_missing_fields(path, ["publisher"])
        elif response == "u":
            # Missing URL
            label = "URL"
            missing = find_missing_fields(path, ["url"])
        elif response == "r":
            # Missing age rating
            label = "age rating"
            missing = find_missing_fields(path, ["age_rating"], null_value="Unknown")
        elif response == "g":
            # Missing grade
            label = "grade/score"
            missing = find_missing_fields(path, ["score"])
        elif response == "l":
            # Missing tags
            label = "tags"
            missing = find_missing_fields(path, ["tags"])
        elif response == "c":
            # Missing summary
            label = "series"
            missing = find_missing_fields(path, ["series"])
        # Print results
        if label is not None:
            length = len(missing)
            if length > 0:
                print_files(path, missing)
                color_print(f"{length} files with missing {label}.", "red")
            else:
                color_print(f"No files with missing {label}.", "green")
        else:
            color_print("Invalid response.", "red")
