#!/usr/bin/env python3

import os
import re
import tqdm
import argparse
import json.decoder
import html_string_tools
import python_print_tools.printer
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.meta_finder as mm_meta_finder
import metadata_magic.meta_reader as mm_meta_reader
import metadata_magic.rename.rename_tools as mm_rename_tools
import metadata_magic.archive.comic_archive as mm_comic_archive
from os.path import abspath, basename, exists, join

def rename_cbz_files(path:str,
            add_artist:bool=False,
            add_date:bool=False):
    """
    Renames all CBZ files based on metadata.

    :param path: Path of directory containing CBZ files
    :type path: str, required
    :param add_artist: Whether to add artist's name, defaults to False
    :type add_artist: bool, optional
    :param add_date: Whether to add publication date, defaults to False
    :type add_date: bool, optional
    :param add_id: Whether to add media ID, defaults to False
    :type add_id: bool, optional
    """
    # Get list of CBZ files
    print("Renaming CBZ files:")
    cbz_files = mm_file_tools.find_files_of_type(abspath(path), ".cbz")
    # Rename all CBZ files
    for cbz_file in tqdm.tqdm(cbz_files):
        filename = get_filename_from_metadata(
            cbz_file, add_artist=add_artist, add_date=add_date)
        mm_rename_tools.rename_file(cbz_file, filename)

def get_filename_from_metadata(file:str,
            add_artist:bool=False,
            add_date:bool=False,
            add_id:bool=False) -> str:
    """
    Returns a filename based on metadata for a given file.
    Mostly based on title, with options for adding artist, ID, and date info.

    :param file: Path of file to get name for
    :type file: str, required
    :param add_artist: Whether to add artist's name, defaults to False
    :type add_artist: bool, optional
    :param add_date: Whether to add publication date, defaults to False
    :type add_date: bool, optional
    :param add_id: Whether to add media ID, defaults to False
    :type add_id: bool, optional
    :return: Filename based on metadata, not including extension
    :rtype: str
    """
    full_file = abspath(file)
    # Load JSON metadata if applicable
    metadata = mm_meta_reader.load_metadata(full_file)
    if metadata["title"] is None:
        # Load CBZ metadata if applicable
        metadata = mm_comic_archive.get_info_from_cbz(full_file)
    # Return filename if metadata could not be found
    if metadata["title"] is None:
        filename = basename(full_file)
        filename = re.sub("\\.json$", "", filename)
        return filename[:len(filename) - len(html_string_tools.html.get_extension(filename))]
    # Get title
    title = metadata["title"]
    # Get ID if applicable
    header = ""
    identifier = None
    if add_id:
        try:
            identifier = metadata["id"]
        except KeyError: identifier = None
    if identifier is not None:
        header = identifier
    # Get date if applicable
    date = None
    if add_date:
        date = metadata["date"]
    if date is not None:
        header = f"{date}_{header}"
    # Get artist if applicable
    artist = None
    if add_artist:
        try:
            artist = metadata["writer"]
            assert artist is not None
        except (AssertionError, KeyError):
            artist = metadata["artist"]
    if artist is not None:
        header = f"{artist}_{header}"
    # Add header to title
    header = re.sub("[-_\\s]+$", "", header)
    if not header == "":
        title = f"[{header}] {title}"
    # Return title
    return title

def rename_json_pairs(path:str,
            add_artist:bool=False,
            add_date:bool=False,
            add_id:bool=False):
    """
    Renames all JSON files and their associated media based on JSON metadata.

    :param path: Path of directory containing JSON files
    :type path: str, required
    :param add_artist: Whether to add artist's name, defaults to False
    :type add_artist: bool, optional
    :param add_date: Whether to add publication date, defaults to False
    :type add_date: bool, optional
    :param add_id: Whether to add media ID, defaults to False
    :type add_id: bool, optional
    """
    # Get JSON pairs
    pairs = mm_meta_finder.get_pairs(path)
    # Rename each pair
    print("Renaming JSON and media files:")
    for pair in tqdm.tqdm(pairs):
        # Get paths from the pair
        json = pair["json"]
        media = pair["media"]
        # Get filename
        filename = get_filename_from_metadata(
                json, add_artist=add_artist, add_date=add_date, add_id=add_id)
        # Rename JSON
        new_file = mm_rename_tools.rename_file(json, filename)
        # Rename media
        try:
            filename = basename(new_file)
            extension = html_string_tools.html.get_extension(filename)
            filename = filename[:len(filename) - len(extension)]
            mm_rename_tools.rename_file(media, filename)
        except TypeError: pass

def main():
    """
    Sets up the parser for the user to rename JSON files.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory in which to rename files.",
            nargs="?",
            type=str,
            default=str(os.getcwd()))
    parser.add_argument(
            "-a",
            "--artist",
            help="Add media artist to the beginning of renamed files.",
            action="store_true")
    parser.add_argument(
            "-d",
            "--date",
            help="Add publication date to the beginning of renamed files.",
            action="store_true")
    parser.add_argument(
            "-i",
            "--id",
            help="Add media ID to the beginning of renamed files.",
            action="store_true")
    args = parser.parse_args()
    # Check that directory is valid
    directory = abspath(args.directory)
    if not exists(directory):
        python_print_tools.printer.color_print("Invalid directory.", "red")
    else:
        rename_json_pairs(directory, add_artist=args.artist, add_id=args.id, add_date=args.date)
        print()
        rename_cbz_files(directory, add_artist=args.artist, add_date=args.date)
        python_print_tools.printer.color_print("Finished renaming.", "green")
