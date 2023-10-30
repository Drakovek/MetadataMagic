#!/usr/bin/env python3

import os
import tqdm
import shutil
import argparse
import html_string_tools
import python_print_tools.printer
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.meta_finder as mm_meta_finder
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.comic_xml as mm_comic_xml
import metadata_magic.archive.comic_archive as mm_comic_archive
import metadata_magic.rename.rename_tools as mm_rename_tools
from os.path import abspath, basename, exists, join



def archive_all(directory:str):
    """
    Attempts to turn every json-media pair into its own cbz archive.
    Only converts media pairs if they are image files.
    
    :param directory: Directory in which to archive files
    :type directory: str, required
    """
    # Get all JSON-Media pairs in the given directory
    full_directory = abspath(directory)
    pairs = mm_meta_finder.get_pairs(full_directory)
    # Delete all media pairs that don't contain images
    for i in range(len(pairs)-1, -1, -1):
        ext = html_string_tools.html.get_extension(pairs[i]["media"]).lower()
        if not ext == ".jpg" and not ext == ".jpeg" and not ext == ".png":
            del pairs[i]
    # Run through each JSON-Media pair
    for pair in tqdm.tqdm(pairs):
        # Copy JSON and media into temp directory
        temp_dir = mm_file_tools.get_temp_dir("dvk_cbz_builder")
        shutil.copy(pair["json"], abspath(join(temp_dir, basename(pair["json"]))))
        shutil.copy(pair["media"], abspath(join(temp_dir, basename(pair["media"]))))
        # Get metadata from the JSON
        metadata = mm_archive.get_info_from_jsons(temp_dir)
        # Create cbz file
        cbz_file = mm_comic_archive.create_cbz(temp_dir, metadata=metadata)
        assert exists(cbz_file)
        # Copy cbz to the original directory
        filename = basename(pair["json"])
        filename = filename[:len(filename) - 5]
        filename = mm_rename_tools.get_available_filename(cbz_file, filename, full_directory)
        new_cbz = abspath(join(full_directory, filename))
        shutil.copy(cbz_file, new_cbz)
        assert exists(new_cbz)
        # Delete the original files
        os.remove(pair["json"])
        os.remove(pair["media"])

def main():
    """
    Sets up the parser for archiving all JSON-image pairs.
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
        archive_all(directory)
