#!/usr/bin/env python3

from argparse import ArgumentParser
from html_string_tools.main.html_string_tools import get_extension
from json.decoder import JSONDecodeError
from os import getcwd, listdir
from os.path import abspath, basename, exists, isdir, join
from metadata_magic.main.meta_reader import get_empty_metadata
from metadata_magic.main.meta_finder import get_pairs
from metadata_magic.main.comic_archive.comic_archive import get_info_from_cbz
from metadata_magic.main.meta_reader import load_metadata as get_info_from_json
from metadata_magic.main.rename.rename_tools import rename_file
from python_print_tools.main.python_print_tools import color_print
from re import sub as resub
from tqdm import tqdm

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
    cbz_files = []
    directories = [abspath(path)]
    while len(directories) > 0:
        # Get list of files in the path
        cur_path = directories[0]
        files = listdir(cur_path)
        # Run through files in directory
        for file in files:
            cur_file = abspath(join(cur_path, file))
            if isdir(cur_file):
                directories.append(cur_file)
            elif get_extension(cur_file) == ".cbz":
                cbz_files.append(cur_file)
        # Delete directory from list
        del directories[0]
    # Rename all CBZ files
    for cbz_file in tqdm(cbz_files):
        filename = get_filename_from_metadata(
            cbz_file, add_artist=add_artist, add_date=add_date)
        rename_file(cbz_file, filename)

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
    pairs = get_pairs(path)
    # Rename each pair
    print("Renaming JSON and media files:")
    for pair in tqdm(pairs):
        # Get paths from the pair
        json = pair["json"]
        media = pair["media"]
        # Get filename
        filename = get_filename_from_metadata(
                json, add_artist=add_artist, add_date=add_date, add_id=add_id)
        # Rename JSON
        new_file = rename_file(json, filename)
        # Rename media
        try:
            filename = basename(new_file)
            filename = filename[:len(filename) - len(get_extension(filename))]
            rename_file(media, filename)
        except TypeError: pass

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
    try:
        # Load JSON metadata if applicable
        metadata = get_info_from_json(full_file)
    except (JSONDecodeError, UnicodeDecodeError):
        # Load CBZ metadata if applicable
        metadata = get_info_from_cbz(full_file)
    # Return filename if metadata could not be found
    if metadata["title"] is None:
        filename = basename(full_file)
        filename = resub("\\.json$", "", filename)
        return filename[:len(filename) - len(get_extension(filename))]
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
    header = resub("[-_\\s]+$", "", header)
    if not header == "":
        title = f"[{header}] {title}"
    # Return title
    return title

def main():
    """
    Sets up the parser for the user to rename JSON files.
    """
    # Set up argument parser
    parser = ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory in which to rename files.",
            nargs="?",
            type=str,
            default=str(getcwd()))
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
        color_print("Invalid directory.", "red")
    else:
        rename_json_pairs(directory, add_artist=args.artist, add_id=args.id, add_date=args.date)
        print()
        rename_cbz_files(directory, add_artist=args.artist, add_date=args.date)
        color_print("Finished renaming.", "green")

if __name__ == "__main__":
    main()
