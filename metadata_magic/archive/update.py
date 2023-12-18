#!/usr/bin/env python3

import os
import tqdm
import argparse
import html_string_tools.html
import python_print_tools.printer
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive as mm_archive
from os.path import abspath, isdir, exists

def update_fields(existing_metadata:dict, updating_metadata:dict) -> dict:
    """
    Updates a dictionary of existing metadata with a new set of metadata fields.
    Metadata fields marked as None in updating_metadata will not be altered.
    Existing_metadata will be updated to the existing fields in updating_metadata.

    :param existing_metadata: Metadata to update
    :type existing_metadata: dict, required
    :param updating_metadata: Values used to update the existing metadata
    :type updating_metadata: dict, required
    :return: Updated metadata
    :rtype: dict
    """
    return_metadata = dict()
    for item in existing_metadata.items():
        return_metadata[item[0]] = item[1]
        try:
            if updating_metadata[item[0]] is not None:
                return_metadata[item[0]] = updating_metadata[item[0]]
        except KeyError:
            return_metadata[item[0]] = item[1]
    return return_metadata

def mass_update_archives(directory:str, metadata:dict, update_covers:bool=False):
    """
    Updates all the media archive files in a given directory to use new metadata.
    Any metadata fields with a value of None will be unaltered from the orignal archive file.
    Currently supports CBZ and EPUB files.
    
    :param directory: Directory in which to look for archivefiles, including subdirectories
    :type directory: str, required
    :param metadata: Metadata to update the archive files with
    :type metadata: dict, required
    :param update_covers: Whether to regenerate cover images, defaults to False
    :type update_covers: bool, optional
    """
    # Get list of archive files in the directory
    archive_files = mm_file_tools.find_files_of_type(directory, ".cbz")
    archive_files.extend(mm_file_tools.find_files_of_type(directory, ".epub"))
    # Run through archive files
    for archive_file in tqdm.tqdm(archive_files):
        # Update the archive file with the metadata
        new_metadata = update_fields(mm_archive.get_info_from_archive(archive_file), metadata)
        mm_archive.update_archive_info(archive_file, new_metadata, update_cover=update_covers)

def user_update_file(file:str, update_cover:bool):
    """
    Update one specific CBZ or EPUB file with user provided metadata.
    
    :param file: Archive file to update
    :type file: str, required
    :param update_cover: Whether to regenerate cover images
    :type update_cover: bool, required
    """
    # Read info from the given file
    full_file = abspath(file)
    existing_metadata = mm_archive.get_info_from_archive(full_file)
    # Get metadata from the user
    updating_metadata = mm_archive.get_metadata_from_user(mm_archive.get_empty_metadata(), True)
    # Update the archive metadata
    updating_metadata = update_fields(existing_metadata, updating_metadata)
    mm_archive.update_archive_info(full_file, updating_metadata, update_cover=update_cover)

def user_mass_update(directory:str, update_covers:bool):
    """
    Mass update all the CBZ and EPUB files in a given directory with user provided metadata.
    
    :param directory: Directory containing archive files to update
    :type directory: str, required
    :param update_covers: Whether to regenerate cover images
    :type update_covers: bool, required
    """
    # Get metadata to update
    updating_metadata = mm_archive.get_metadata_from_user(mm_archive.get_empty_metadata(), True)
    # Mass update cbz and epub files
    mass_update_archives(abspath(directory), updating_metadata, update_covers=update_covers)

def main():
    """
    Sets up the parser for updating media archives.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "path",
            help="Directory or archive file to update with metadata.",
            nargs="?",
            type=str,
            default=str(os.getcwd()))
    parser.add_argument(
            "-c",
            "--cover",
            help="Regenerate cover image(s).",
            action="store_true")
    args = parser.parse_args()
    # Check that directory is valid
    path = abspath(args.path)
    if not exists(path):
        python_print_tools.printer.color_print("Invalid path.", "red")
    elif isdir(path):
        user_mass_update(path, args.cover)
    else:
        user_update_file(path, args.cover)
