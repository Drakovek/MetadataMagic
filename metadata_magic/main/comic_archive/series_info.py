#!/usr/bin/env python3

from argparse import ArgumentParser
from metadata_magic.main.comic_archive.comic_archive import get_info_from_cbz
from metadata_magic.main.comic_archive.comic_archive import update_cbz_info
from html_string_tools.main.html_string_tools import get_extension
from math import floor
from metadata_magic.main.rename.sort_rename import sort_alphanum
from os import name as os_name
from os import getcwd, listdir, system
from os.path import abspath, basename, exists, isdir, join
from python_print_tools.main.python_print_tools import color_print
from tqdm import tqdm
from typing import List

def get_comic_archives(path:str, include_subdirs:bool=False) -> List[str]:
    """
    Returns a sorted list of all the comic book archives in a given directory.
    
    :param path: Path of the directory to search
    :type path: str, required
    :param include_subdirs: Whether to include comic archive in sub-directories, defaults to False
    :type include_subdirs: bool, optional
    :return: Sorted list of all the comic archives in the given directory
    :rtype: list[str]
    """
    # Look through all files in the directory for comic archive files
    archives = []
    directories = [abspath(path)]
    while len(directories) > 0:
        # Get all files in the directory
        cur_files = sort_alphanum(listdir(directories[0]))
        # Run through all files in the directory
        for file in cur_files:
            full_file = abspath(join(directories[0], file))
            if include_subdirs and isdir(full_file):
                # Add file to list of subdirectories if searching subdirs is specified
                directories.append(full_file)
            if get_extension(full_file) == ".cbz":
                # Add file to archive list if it is a comic archive
                archives.append(full_file)
        # Remove the directory currently being searched through
        del directories[0]
    # Return list of comic archives
    return archives

def label_files_with_numbers(files:List[dict], index:int, label:str) -> List[dict]:
    """
    Gives label numbers to correspond with a list of files.
    All labels after the given index are given integer values coming after the given label.
    
    :param files: List of sorted files with paired labels, keys are "label" and "file"
    :type files: list[dict], required
    :param index: Index to start numbering from
    :type index: int, required
    :param label: Label to start with, should be a formatted like a float or int
    :type label: str, required
    :return: List of files with updated label numbers
    :rtype: list[dict]
    """
    # Return existing list if label is not a valid number
    try:
        label_float = float(label)
    except ValueError: return files
    # Return existing list if index is out of range
    if index < 0 or index > len(files)-1:
        return files
    # Get the next integer
    next_int = floor(label_float) + 1
    # Relabel files
    new_files = files
    new_files[index]["label"] = label
    for i in range(index+1, len(new_files)):
        new_files[i]["label"] = f"{next_int}.0"
        next_int += 1
    # Return relabeled files
    return new_files

def write_series_info(files:List[dict], series_title:str):
    """
    Writes series title and number based on given title and file labels.
    
    :param files: List of sorted files with paired labels, keys are "label" and "file"
    :type files: list[dict], required
    :param series_title: Title of the series
    :type series_title: str, required
    """
    for file in tqdm(files):
        # Read metadata from archive
        metadata = get_info_from_cbz(file["file"])
        # Add series info to metadata
        metadata["series"] = series_title
        metadata["series_number"] = file["label"]
        metadata["series_total"] = str(len(files))
        # Write metadata back into archive
        update_cbz_info(file["file"], metadata)

def list_file_labels(files:List[dict]) -> str:
    """
    Returns a human-readable string showing a list of files with their numbered label.
    
    :param files: List of sorted files with paired labels, keys are "label" and "file"
    :type files: list[dict], required
    :return: String showing files with labels
    :rtype: str
    """
    file_list = files[0]["label"] + ") " + basename(files[0]["file"])
    for i in range(1, len(files)):
        file_list = f"{file_list}\n"
        file_list = file_list + files[i]["label"] + ") " + basename(files[i]["file"])
    return file_list

def clear_terminal():
    """
    Clears the terminal
    """
    if os_name == "nt":
        system("cls")
    else:
        system("clear")

def set_series_info(path:str):
    """
    Sets series name and number for comic archives in a given path based on user input.
    
    :param path: Directory containing comic archive files
    :type path: str, required
    """
    # Get the title for the series
    series_title = str(input("Series Title: "))
    # Get sorted list of comic archives
    archives = get_comic_archives(path)
    # Create labels for the list
    files = []
    for archive in archives:
        files.append({"file":archive, "label":"0"})
    files = label_files_with_numbers(files, 0, "1.0")
    # Relabel files if the user requests it
    while len(files) > 0:
        # Show instructions to user
        print(list_file_labels(files))
        print("\n[E] Edit")
        print("[W] Write Series Info")
        print("[Q] Quit Without Saving")
        response = str(input("Response: ")).lower()
        # Get user response
        if response == "e":
            # Get index of item to edit
            index = -1
            response = input("Item to edit: ")
            for i in range(0, len(files)):
                if files[i]["label"] == response:
                    index = i
                    break
            # Get the new label
            response = input("Number: ")
            files = label_files_with_numbers(files, index, response)
        elif response == "w":
            write_series_info(files, series_title)
            break
        elif response == "q":
            break
        # Clear the terminal
        clear_terminal()

def set_single_series(path:str):
    """
    Sets series name and number as being the same as the title for archives that are considered singles or one-shots
    
    :param path: Directory containing comic archive files
    :type path: str, required
    """
    # Print all comic archives
    archives = get_comic_archives(path, True)
    for archive in archives:
        print(basename(archive))
    # Ask if user wants to set all sequences as singles
    if input("Set all archives as single comics? (Y/N):").lower() == "y":
        # Set the series info for each archive
        for archive in tqdm(archives):
            metadata = get_info_from_cbz(archive)
            metadata["series"] = metadata["title"]
            metadata["series_number"] = "1.0"
            metadata["series_total"] = "1"
            update_cbz_info(archive, metadata)

def main():
    """
    Sets up the parser for adding series info to archives.
    """
    # Set up argument parser
    parser = ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory containing comic archives.",
            nargs="?",
            type=str,
            default=str(getcwd()))
    parser.add_argument(
            "-s",
            "--single",
            help="Use user summary instead of summary in metadata.",
            action="store_true")
    args = parser.parse_args()
    # Check that directory is valid
    directory = abspath(args.directory)
    if not exists(directory):
        color_print("Invalid directory.", "red")
    else:
        # Check whether to add as full series or as one-shots
        if args.single:
            set_single_series(directory)
        else:
            set_series_info(directory)
            
if __name__ == "__main__":
    main()