#!/usr/bin/env python3

import os
import re
import math
import tqdm
import argparse
import python_print_tools.printer
import metadata_magic.sort as mm_sort
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive as mm_archive
from os.path import abspath, basename, exists
from typing import List

def get_default_labels(directory:str) -> List[dict]:
    """
    Returns a list of archive files in the given directory with labels indicating their number in a series.
    Each entry in the returned list contains "file" key for the file path, and "label" key for the number label.
    If the archives already contain metadata for their place in a series, that series number will be used as the label.
    Otherwise, the series order will be determined alphabetically by filename, starting with "1.0"
    
    :param directory: Directory in which to search for media archive files
    :type directory: str, required
    :return: List of dictionaries containing file paths to archives and labels for their number in a series
    :rtype: List[dict]
    """
    
    # Get all archive files
    archive_files = mm_file_tools.find_files_of_type(directory, [".cbz", ".epub"], include_subdirectories=False)
    archive_files = mm_sort.sort_alphanum(archive_files)
    # Set labels based on the current sequence information
    base_label = 100000
    label_num = base_label
    labeled_files = []
    for archive_file in archive_files:
        # Get the series number
        label = mm_archive.get_info_from_archive(archive_file)["series_number"]
        # Add the label num if there is no series number
        if label is None:
            label = f"{label_num}.0"
            label_num += 1
        # Add file and label to the list of files
        labeled_files.append({"file":archive_file, "label":label})
    # Sort the files by label
    labeled_files = mm_sort.sort_dictionaries_alphanum(labeled_files, "label")
    # Relabel the files if there was no sequence info found
    if label_num - base_label == len(labeled_files):
        labeled_files = label_files(labeled_files, 0, "1.0")
    # Return the files with default labels
    return labeled_files

def label_files(files:List[dict], index:int, label:str) -> List[dict]:
    """
    Labels a list of files with series numbers.
    The first file will use the given label, with subsequent files using the next available integers.
    
    :param files: List of dicts with "file" and "label" fields to add labels to
    :type files: List[dict], required
    :param index: Index of the first item in the file list to be relabeled
    :type index: int, required
    :param label: The label for the first item to be relabeled
    :type label: str, required
    :return: List of dicts with "file" and "label" fields, newly labeled
    :rtype: List[dict]
    """
    # Return the existing file list if the given label isn't a proper number
    try:
        label_value = float(label)
    except ValueError:
        return files
    # Return the existing file list if the list is out of range
    if index < 0 or index > len(files) -1:
        return files
    # Get the next integer
    next_int = math.floor(label_value) + 1
    # Get the first label
    first_label = label
    if not "." in first_label:
        first_label = f"{label}.0"
    first_label = re.sub(r"^0+(?=[0-9])|(?<=[0-9])0+$", "", first_label)
    # Add Labels
    new_files = []
    new_files.extend(files)
    new_files[index]["label"] = first_label
    for i in range(index+1, len(new_files)):
        new_files[i]["label"] = f"{next_int}.0"
        next_int += 1
    # Return the new file list
    return new_files

def write_series(files:List[dict], series_title:str):
    """
    Updates the given archives to include the given series info in their metadata.
    
    :param files: Files with their corresponding series number labels, as returned by get_default_labels.
    :type files: List[dict], required
    :param series_title: Title of the series
    :type series_title: str, required
    """
    # Get the series total
    series_total = str(math.ceil(float(files[len(files)-1]["label"])))
    # Run through all given files in the series
    for file in tqdm.tqdm(files):
        # Read Metadata from the archive
        metadata = mm_archive.get_info_from_archive(file["file"])
        # Set the series metadata
        metadata["series"] = series_title
        metadata["series_number"] = file["label"]
        metadata["series_total"] = series_total
        # Update the metadata
        mm_archive.update_archive_info(file["file"], metadata)

def write_series_single(archive_file:str):
    """
    Updates a given archive's metadata to include series information as a standalone work.
    The series title will be the same as the archive title, and the series will be set as 1 of 1.
    
    :param archive_file: Path to the archive file to be updated
    :type archive_file: str, required
    """
    # Read metadata from the archive file
    full_file = abspath(archive_file)
    metadata = mm_archive.get_info_from_archive(full_file)
    # Set the series info
    metadata["series"] = metadata["title"]
    metadata["series_number"] = "1.0"
    metadata["series_total"] = "1"
    # Update the metadata
    mm_archive.update_archive_info(full_file, metadata)

def get_series_string(files:List[dict]) -> str:
    """
    Returns a user-readable string showing the current series numbers for each given file.
    
    :param files: Files with their corresponding series number labels, as returned by get_default_labels.
    :type files: List[dict], required
    :return: User readable string showing series info
    :rtype: str
    """
    # Get the length of block for characters of each field
    entry_length = 5
    file_length = 4
    for file in files:
        if len(basename(file["file"])) > file_length:
            file_length = len(basename(file["file"]))
        if len(file["label"]) > entry_length:
            entry_length = len(file["label"])
    entry_length += 4
    # Set the header for the series labels
    total_length = entry_length + file_length
    series_string = "-" * total_length
    series_string = f"{{:<{file_length}}}\n{series_string}".format("FILE")
    series_string = f"{{:<{entry_length}}}{series_string}".format("ENTRY")
    # Get a string for each archive file
    for file in files:
        # Get the label
        entry_string = f"{{:<{entry_length}}}".format(file["label"])
        # Get the file value
        entry_string = f"{entry_string}{{:<{file_length}}}".format(basename(file["file"]))
        # Add to the overall string
        series_string = f"{series_string}\n{entry_string}"
    # Return the series string
    return series_string

def set_series_from_user(directory:str):
    """
    Asks the user for information about series info, then updates metadata of archives in the given directory.
    
    :param directory: Directory containing media archives to update with series information.
    :type directory: str, required
    """
    # Get the title for the series
    series_title = input("Series Title: ")
    # Get the list of archive files and their default labels
    labeled_files = get_default_labels(directory)
    # Relabel the files if the user requests
    while len(labeled_files) > 0:
        # Clear the terminal
        python_print_tools.printer.clear_console()
        # Show instructions to user
        print(get_series_string(labeled_files))
        print()
        print("[E] Edit")
        print("[R] Reset")
        print("[W] Write Series Info")
        print("[Q] Quit Without Saving")
        # Get user response
        response = str(input("Response: ")).lower()
        if response == "e":
            # Ask the user what item to edit
            try:
                entry_value = float(input("Item to edit: "))
            except ValueError: continue
            # Get the indes of the item to edit
            index = -1
            for i in range(0, len(labeled_files)):
                if float(labeled_files[i]["label"]) == entry_value:
                    index = i
                    break
            # Get and set the new label
            entry_value = input("Number: ")
            labeled_files = label_files(labeled_files, index, entry_value)
        elif response == "r":
            # Sort and relabel all files alphabetically
            labeled_files = mm_sort.sort_dictionaries_alphanum(labeled_files, "file")
            labeled_files = label_files(labeled_files, 0, "1")
        elif response == "w": 
            write_series(labeled_files, series_title)
            break
        elif response == "q":
            break

def main():
    """
    Sets up the parser for adding series info to archives.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory containing media archives.",
            nargs="?",
            type=str,
            default=str(os.getcwd()))
    parser.add_argument(
            "-s",
            "--standalone",
            help="Set media series as being one of one",
            action="store_true")
    args = parser.parse_args()
    # Check that directory is valid
    directory = abspath(args.directory)
    if not exists(directory):
        python_print_tools.printer.color_print("Invalid directory.", "red")
    else:
        # Check whether to add as full series or as one-shots
        if not args.standalone:
            set_series_from_user(directory)
        elif input("Mark all archives in this directory as standalone entries? (Y/[N]): ").lower() == "y":
            archive_files = mm_file_tools.find_files_of_type(directory, [".cbz", ".epub"])
            for archive_file in tqdm.tqdm(archive_files):
                write_series_single(archive_file)
        
