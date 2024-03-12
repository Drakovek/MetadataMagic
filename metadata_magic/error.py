#!/usr/bin/env python3

import os
import tqdm
import argparse
import python_print_tools.printer
import metadata_magic.sort as mm_sort
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.meta_finder as mm_meta_finder
import metadata_magic.meta_reader as mm_meta_reader
import metadata_magic.archive.archive as mm_archive
from os.path import abspath, exists
from typing import List

LONG_DESCRIPTION = 1000

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

def find_long_descriptions(path:str, length:int=LONG_DESCRIPTION) -> List[str]:
    """
    Returns a list of archives and metadata files with overly long descriptions.
    
    :param path: Directory in which to search for metadata
    :type path: str, required
    :param length: Number of characters for a description to be considered long, defaults to LONG_DESCRIPTION value
    :type length: int, optional
    :return: List of archives and metadata files with overly long titles
    :rtype: List[str]
    """
    # Get a list of all archive files
    print("Searching archives with long descriptions...")
    full_path = abspath(path)
    archive_files = mm_file_tools.find_files_of_type(full_path, [".cbz", ".epub"])
    # Run through all archive files
    long = []
    for archive_file in tqdm.tqdm(archive_files):
        metadata = mm_archive.get_info_from_archive(archive_file)
        if metadata["description"] is not None and len(metadata["description"]) > length:
            long.append(archive_file)
    # Get a list of all json media pairs
    print("Searching JSONs with long descriptions...")
    pairs = mm_meta_finder.get_pairs(full_path)
    # Run throug all json files
    for pair in pairs:
        metadata = mm_meta_reader.load_metadata(pair["json"], pair["media"])
        if metadata["description"] is not None and len(metadata["description"]) > length:
            long.append(pair["json"])
    # Return list of files with long descriptions
    return mm_sort.sort_alphanum(long)

    

def find_missing_fields(path:str, fields:List[str]) -> List[str]:
    """
    Finds archive files with certain missing fields in their metadata.
    Will include a file if all the fields given equal None.
    
    :param path: Directory in which to search for media
    :type path: str, required
    :param fields: List of metadata fields to check for
    :type fields: list[str], required
    :return: List of archive files missing the given fields
    :rtype: list[str]
    """
    # Get a list of all archive files
    full_path = abspath(path)
    archive_files = mm_file_tools.find_files_of_type(full_path, [".cbz", ".epub"])
    # Run through all files
    missing = []
    for archive_file in tqdm.tqdm(archive_files):
        # Get metadata from the archive file
        metadata = mm_archive.get_info_from_archive(archive_file)
        # Run through each field
        missing.insert(0, archive_file)
        for field in fields:
            try:
                # Add to list if the field is missing
                if metadata[field] is not None and (not field == "age_rating" or not metadata[field] == "Unknown"):
                    del missing[0]
                    break
            except KeyError: pass
    # Return the list of missing files
    return mm_sort.sort_alphanum(missing)

def print_errors(error_files:List[str], root_directory:str, print_text:str):
    """
    Prints the files gotten from one of the error-finding functions.
    
    :param error_files: List of paths to files to print, as returned by the error-finding functions.
    :type error_files: List[str], required
    :param root_directory: Root directory of the given error files
    :type root_directory: str, required
    :param print_text: String to describe the type of error files being printed
    :type print_text: str, required
    """
    length = len(error_files)
    if length > 0:
        python_print_tools.printer.color_print(f"{length} {print_text}:", "red")
        python_print_tools.printer.print_files(root_directory, error_files)
        print("")
    else:
        python_print_tools.printer.color_print(f"No {print_text}.\n", "green")
    
def main():
    """
    Sets up the parser for the user to find errors in metadata.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory to search for files within",
            nargs="?",
            type=str,
            default=str(os.getcwd()))
    parser.add_argument(
            "-l",
            "--long-description",
            nargs="?",
            const=LONG_DESCRIPTION,
            default=None,
            type=int,
            help="Find metadata with an overly long description")
    parser.add_argument(
            "-m",
            "--missing-media",
            help="Find JSON files with no associated media",
            action="store_true")
    parser.add_argument(
            "-j",
            "--missing-json",
            help="Find media files with no associated JSON metadata",
            action="store_true")
    parser.add_argument(
            "-f",
            "--missing-fields",
            help="Find media archives with missing metadata fields",
            action="store_true")
    args = parser.parse_args()
    # Check that directory is valid
    directory = abspath(args.directory)
    if not exists(directory):
        python_print_tools.printer.color_print("Invalid directory.", "red")
    else:
        # Find missing media
        if args.missing_media:
            missing = find_missing_media(directory)
            print_errors(missing, directory, "JSONs With Missing Media")
        # Find long descriptions
        if args.long_description is not None:
            long = find_long_descriptions(directory, args.long_description)
            print_errors(long, directory, "Media With Long Descriptions")
        # Find missing metadata
        if args.missing_json:
            missing = find_missing_media(directory)
            print_errors(missing, directory, "Media With Missing JSON Metadata")
        # Find missing fields
        if args.missing_fields:
            # Ask the user for what type of missing field to search for
            print("[T] Missing title")
            print("[A] Missing artist")
            print("[D] Missing date")
            print("[S] Missing summary")
            print("[P] Missing publisher")
            print("[U] Missing URL")
            print("[R] Missing Age Rating")
            print("[G] Missing Grade/Score")
            print("[L] Missing Labels/Tags")
            print("[C] Missing Chain/Series")
            response = str(input("Which Missing Metadata Field?: ")).lower()
            # Check media based on user response
            responses = {"t":{"key":["title"], "label":"title"}, "a":{"key":["artists", "writers"], "label":"artist/writer"},
                        "d":{"key":["date"], "label":"date"}, "s":{"key":["description"], "label":"summary"},
                        "p":{"key":["publisher"], "label":"publisher"}, "u":{"key":["url"], "label":"URL"},
                        "r":{"key":["age_rating"], "label":"age rating"}, "g":{"key":["score"], "label":"grade/score"},
                        "l":{"key":["tags"], "label":"labels/tags"}, "c":{"key":["series"], "label":"series"}}
            try:
                label = responses[response]["label"]
                missing = find_missing_fields(directory, responses[response]["key"])
                print_errors(missing, directory, f"archives with missing {label} field")
            except KeyError:
                python_print_tools.printer.color_print("Invalid response.", "red")
