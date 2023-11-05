#!/usr/bin/env python3

import os
import tqdm
import argparse
import html_string_tools.html
import python_print_tools.printer
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.epub as mm_epub
import metadata_magic.archive.comic_archive as mm_comic_archive
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
        if updating_metadata[item[0]] is not None:
            return_metadata[item[0]] = updating_metadata[item[0]]
    return return_metadata

def mass_update_cbzs(directory:str, metadata:dict):
    """
    Updates all the cbz files in a given directory to use new metadata.
    Any metadata fields with a value of None will be unaltered from the orignal cbz file.
    
    :param directory: Directory in which to look for cbz files, including subdirectories
    :type directory: str, required
    :param metadata: Metadata to update the cbz files with
    :type metadata: dict, required
    """
    # Get list of cbz files in the directory
    cbz_files = mm_file_tools.find_files_of_type(directory, ".cbz")
    for cbz_file in tqdm.tqdm(cbz_files):
        # Update the cbz file with the metadata
        new_metadata = update_fields(mm_comic_archive.get_info_from_cbz(cbz_file), metadata)
        mm_comic_archive.update_cbz_info(cbz_file, new_metadata)

def mass_update_epubs(directory:str, metadata:dict):
    """
    Updates all the epub files in a given directory to use new metadata.
    Any metadata fields with a value of None will be unaltered from the orignal epub file.
    
    :param directory: Directory in which to look for epub files, including subdirectories
    :type directory: str, required
    :param metadata: Metadata to update the epub files with
    :type metadata: dict, required
    """
    # Get list of epub files in the directory
    epub_files = mm_file_tools.find_files_of_type(directory, ".epub")
    for epub_file in tqdm.tqdm(epub_files):
        # Update the epub file with the metadata
        new_metadata = update_fields(mm_epub.get_info_from_epub(epub_file), metadata)
        mm_epub.update_epub_info(epub_file, new_metadata) 

def user_update_file(file:str):
    """
    Update one specific CBZ or EPUB file with user provided metadata.
    """
    # Read info from the given file
    full_file = abspath(file)
    updating_metadata = mm_archive.get_empty_metadata()
    extension = html_string_tools.html.get_extension(full_file).lower()
    updating_metadata = mm_archive.get_metadata_from_user(mm_archive.get_empty_metadata(), True)
    # Update CBZ
    if extension == ".cbz":
        existing_metadata = mm_comic_archive.get_info_from_cbz(full_file)
        updating_metadata = update_fields(existing_metadata, updating_metadata)
        mm_comic_archive.update_cbz_info(full_file, updating_metadata)
    # Update EPUB
    if extension == ".epub":
        existing_metadata = mm_epub.get_info_from_epub(full_file)
        updating_metadata = update_fields(existing_metadata, updating_metadata)
        mm_epub.update_epub_info(full_file, updating_metadata)

def user_mass_update(directory:str):
    """
    Mass update all the CBZ and EPUB files in a given directory with user provided metadata.
    """
    # Get metadata to update
    updating_metadata = mm_archive.get_metadata_from_user(mm_archive.get_empty_metadata(), True)
    # Mass update cbz and epub files
    mass_update_cbzs(abspath(directory), updating_metadata)
    mass_update_epubs(abspath(directory), updating_metadata)

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
    args = parser.parse_args()
    # Check that directory is valid
    path = abspath(args.path)
    if not exists(path):
        python_print_tools.printer.color_print("Invalid path.", "red")
    elif isdir(path):
        user_mass_update(path)
    else:
        user_update_file(path)
