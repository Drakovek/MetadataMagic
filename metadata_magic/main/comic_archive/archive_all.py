#!/usr/bin/env python3

from metadata_magic.main.meta_finder import get_pairs
from metadata_magic.main.comic_archive.comic_archive import create_cbz
from metadata_magic.main.comic_archive.comic_xml import generate_info_from_jsons
from metadata_magic.main.rename.rename_tools import get_available_filename
from metadata_magic.main.file_tools.file_tools import get_temp_dir
from html_string_tools.main.html_string_tools import get_extension
from argparse import ArgumentParser
from os import getcwd, remove
from os.path import abspath, basename, exists, join
from python_print_tools.main.python_print_tools import color_print
from shutil import copy
from tqdm import tqdm

def archive_all(directory:str):
    """
    Attempts to turn every json-media pair into its own cbz archive.
    Only converts media pairs if they are image files.
    
    :param directory: Directory in which to archive files
    :type directory: str, required
    """
    # Get all JSON-Media pairs in the given directory
    full_directory = abspath(directory)
    pairs = get_pairs(full_directory)
    # Delete all media pairs that don't contain images
    for i in range(len(pairs)-1, -1, -1):
        ext = get_extension(pairs[i]["media"]).lower()
        if not ext == ".jpg" and not ext == ".jpeg" and not ext == ".png":
            del pairs[i]
    # Run through each JSON-Media pair
    for pair in tqdm(pairs):
        # Copy JSON and media into temp directory
        temp_dir = get_temp_dir("dvk_cbz_builder")
        copy(pair["json"], abspath(join(temp_dir, basename(pair["json"]))))
        copy(pair["media"], abspath(join(temp_dir, basename(pair["media"]))))
        # Get metadata from the JSON
        metadata = generate_info_from_jsons(temp_dir)
        # Create cbz file
        cbz_file = create_cbz(temp_dir, metadata=metadata)
        assert exists(cbz_file)
        # Copy cbz to the original directory
        filename = basename(pair["json"])
        filename = filename[:len(filename) - 5]
        filename = get_available_filename(cbz_file, filename, full_directory)
        new_cbz = abspath(join(full_directory, filename))
        copy(cbz_file, new_cbz)
        assert exists(new_cbz)
        # Delete the original files
        remove(pair["json"])
        remove(pair["media"])

def main():
    """
    Sets up the parser for archiving all JSON-image pairs.
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
        archive_all(directory)