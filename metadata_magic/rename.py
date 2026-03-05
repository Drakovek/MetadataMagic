#!/usr/bin/env python3

import os
import re
import copy
import tqdm
import argparse
import html_string_tools
import python_print_tools
import metadata_magic.config as mm_config
import metadata_magic.meta_finder as mm_meta_finder
import metadata_magic.meta_reader as mm_meta_reader
import metadata_magic.archive as mm_archive
import python_file_tools as pft
from metadata_magic.meta_reader import get_string_from_metadata
from os.path import abspath, basename, isdir, exists, join
from typing import List

def rename_archives(path:str, template:str, ascii_only:bool=False):
    """
    Rename all the media archives in a given directory based on their metadata and a string template
    
    :param path: Path to the directory in which to rename media archives
    :type path: str, required
    :param template: Metadata string template to use for filename, as used in get_string_from_metadata function.
    :type template: str, required
    :param ascii_only: Whether to only allow basic ASCII characters, defaults to False
    :type ascii_only: bool, optional
    """
    # Get all media archives
    archive_files = pft.find_files_of_type(path, mm_archive.ARCHIVE_EXTENSIONS)
    # Run through each archive file
    for archive_file in tqdm.tqdm(archive_files):
        # Get the filename for the archive file
        metadata = mm_archive.get_info_from_archive(archive_file)
        try:
            # Don't rename if the filename is already correct or metadata can't be found
            filename = get_string_from_metadata(metadata, template)
            filename = pft.get_file_friendly_text(filename, ascii_only)
            assert not filename == "0"
            assert not filename == re.sub(r"\.[^\.]{0,5}$", "", basename(archive_file))
        except (AssertionError, AttributeError): continue
        # Get available filename
        parent = abspath(join(archive_file, os.pardir))
        filename = pft.get_available_filename(archive_file, filename, parent)
        # Rename the archive file
        pft.rename_file(archive_file, filename)

def rename_json_pairs(path:str, template:str, config:str, ascii_only:bool=False):
    """
    Rename all the json-media pairs in a given directory based on their metadata and a string template
    
    :param path: Path to the directory in which to rename JSONs and media
    :type path: str, required
    :param template: Metadata string template to use for filename, as used in get_string_from_metadata function.
    :type template: str, required
    :param config: Dictionary of a metadata-magic config file
    :type config: dict, required
    :param ascii_only: Whether to only allow basic ASCII characters, defaults to False
    :type ascii_only: bool, optional
    """ 
    # Get all JSON pairs
    pairs = mm_meta_finder.get_pairs(path)
    # Run through each pair
    print("Renaming JSON and media files:")
    for pair in tqdm.tqdm(pairs):
        # Get paths from the pair
        json = pair["json"]
        media = pair["media"]
        # Get the base filename
        metadata = mm_meta_reader.load_metadata(json, config, media)
        filename = get_string_from_metadata(metadata, template)
        # Don't rename if the filename is already correct or metadata can't be found
        try:
            filename = pft.get_file_friendly_text(filename, ascii_only)
            assert not filename == "0"
            assert not filename == basename(json)[:len(basename(json))-5]
        except (AssertionError, AttributeError): continue
        # Get the available filenames for media and json
        parent = abspath(join(json, os.pardir))
        filename = pft.get_available_filename([media, json], filename, parent)
        # Rename files
        pft.rename_file(json, filename)
        pft.rename_file(media, filename)

def sort_rename(path:str, rename_template:str, index:int=1, file_pattern:str=".*"):
    """
    Renames all the files in a directory to a standard name with index numbers.
    File numbers will be in the order that the files were originally sorted alpha-numerically.
    JSON-Media pairs will share the same index number.
    Files in sub-directories are not renamed.
    
    The template string will be the base filename for renaming the files.
    Instances of "#" in the template will be replaced with the index number.
    The index number will be padded with zeros to match the "#" string (Ex. "#" -> "1", "###" -> "001")
    If no "#" characters are in the template, the index number will be appended to the end of the base name.
    
    :param path: Path of the files to rename
    :type path: str, required
    :param template: Template to use for the new filenames
    :type template: str, required
    :param index: The first index number to use when renaming, defaults to 1
    :type index: int, optional
    """
    # Get list of JSON pairs
    full_path = abspath(path)
    pairs = mm_meta_finder.get_pairs(full_path)
    # Remove files in subdirectories
    used_files = []
    for i in range(len(pairs)-1, -1, -1):
        if not abspath(join(pairs[i]["json"], os.pardir)) == full_path:
            del pairs[i]
            continue
        used_files.append(basename(pairs[i]["json"]))
        used_files.append(basename(pairs[i]["media"]))
    # Get the rest of files left in the directory
    for file in pft.sort.sort_alphanum(os.listdir(full_path)):
        if file in used_files:
            continue
        full_file = abspath(join(full_path, file))
        if not isdir(full_file):
            pairs.append({"json":None, "media":full_file})
    # Delete pairs that don't match the file pattern
    for i in range(len(pairs)-1, -1, -1):
        if len(re.findall(file_pattern, basename(pairs[i]["media"]), flags=re.IGNORECASE)) < 1:
            del pairs[i]
    # Update the template
    try:
        new_rename_template = copy.deepcopy(rename_template)
        number_string = re.findall(r"#+(?=[^#]*$)", new_rename_template)[0]
    except IndexError:
        number_string = "##"
        if not index == 1 or len(pairs) > 1:
            new_rename_template = f"{rename_template} [##]"
    # Rename all the files
    for i in range(0, len(pairs)):
        # Don't rename if the filename is already correct
        filename = re.sub(r"#+(?=[^#]*$)", str(i+index).zfill(len(number_string)), new_rename_template)
        filename = pft.get_file_friendly_text(filename)
        if filename == re.sub(r"\.[^\.]{0,5}$", "", basename(pairs[i]["media"])):
            continue
        # Rename the media and JSON files
        filename = pft.get_available_filename([pairs[i]["media"], "a.json"], filename, full_path)
        pft.rename_file(pairs[i]["media"], filename)
        if pairs[i]["json"] is not None:
            pft.rename_file(pairs[i]["json"], filename)

def user_sort_rename(path:str):
    """
    Prompts the user for info needed for the sort_rename function.
    
    :param path: Path of the directory in which to rename files
    :type path: str, required
    """
    # Get the default template based on filenames in the given directory
    title = None
    for file in pft.sort.sort_alphanum(os.listdir(path)):
        if not isdir(abspath(join(path, file))):
            title = re.sub(r"\..{0,6}$", "", file)
            break
    title = mm_archive.format_title(title)
    # Get the rename template
    template = mm_archive.get_string_from_user("Sort Rename Template", title)
    # Get the starting index
    index = None
    while index == None:
        try:
            index = mm_archive.get_string_from_user("Starting Index", "1")
            index = int(index)
        except ValueError: index = None
    # Get the filename pattern
    file_pattern = mm_archive.get_string_from_user("File pattern", r".*")
    # Rename files
    sort_rename(path, template, index, file_pattern)

def user_metadata_rename(path:str, ascii_only:bool=False):
    """
    Prompts the user for info needed for the rename_archives and rename_json_pairs functions.
    
    :param path: Path of the directory in which to rename files
    :type path: str, required
    :param ascii_only: Whether to only allow basic ASCII characters, defaults to False
    :type ascii_only: bool, optional
    """
    # Get what type of template the user wants.
    print("Rename in the format \"[options] title\"")
    print("A - Artist")
    print("D - Date")
    result = input("\nOptions or \"C\" for Custom: ").lower()
    # Create the template
    if result == "c":
        print("Include Metadata Fields in format \"{key}\"")
        template = input("Template: ")
    else:
        template = ""
        if "a" in result:
            template = "{artists}"
        if "d" in result:
            template = f"{template}_{{date}}"
        template = re.sub(r"^_*", "", template)
        template = f"[{template}] {{title}}"
        template = re.sub(r"^\s*\[\]\s", "", template)
    template = template.strip()
    # Rename files
    config_paths = mm_config.get_default_config_paths()
    config = mm_config.get_config(config_paths)
    rename_archives(path, template, ascii_only=ascii_only)
    rename_json_pairs(path, template, config, ascii_only=ascii_only)

def main():
    """
    Sets up the parser for the user to rename files.
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
            "-m",
            "--metadata-rename",
            help="Renames files based on their metadata.",
            action="store_true")
    parser.add_argument(
            "-s",
            "--sort-rename",
            help="Renames files to a template name with index numbers.",
            action="store_true")
    parser.add_argument(
            "-a",
            "--ascii-only",
            help="Only uses strict ASCII characters",
            action="store_true")
    args = parser.parse_args()
    # Check that directory is valid
    directory = abspath(args.directory)
    if not exists(directory):
        python_print_tools.color_print("Invalid directory.", "red")
    else:
        if args.metadata_rename and args.sort_rename:
            python_print_tools.color_print("Choose only one renaming option.", "red")
        elif not args.metadata_rename and not args.sort_rename:
            python_print_tools.color_print("Choose a renaming option.", "red")
        elif args.sort_rename:
            user_sort_rename(directory)
        elif args.metadata_rename:
            user_metadata_rename(directory, args.ascii_only)
