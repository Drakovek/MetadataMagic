#!/usr/bin/env python3

from argparse import ArgumentParser
from html_string_tools.main.html_string_tools import get_extension
from math import floor
from metadata_magic.main.comic_archive.comic_archive import get_info_from_archive
from metadata_magic.main.comic_archive.comic_archive import update_archive_info
from metadata_magic.main.rename.sort_rename import sort_alphanum
from os import name as os_name
from os import getcwd, listdir, system
from os.path import abspath, basename, exists, join
from typing import List

def get_comic_archives(path:str) -> List[str]:
    """
    Returns a sorted list of all the comic book archives in a given directory.
    Does not include sub-directories.
    
    :param path: Path of the directory to search
    :type path: str, required
    :return: Sorted list of all the comic archives in the given directory
    :rtype: list[str]
    """
    # Get list of files in the directory
    full_directory = abspath(path)
    files = listdir(full_directory)
    # Remove all directories that aren't comic archives
    for i in range(len(files)-1,-1,-1):
        extension = get_extension(files[i])
        if not extension == ".cbz" and not extension == ".cb7":
            del files[i]
    # Sort list of files
    files = sort_alphanum(files)
    # Get full directory for all listed files
    for i in range(0, len(files)):
        files[i] = abspath(join(full_directory, files[i]))
    # Return list of files
    return files

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
    for file in files:
        # Read metadata from archive
        metadata = get_info_from_archive(file["file"])
        # Add series info to metadata
        metadata["series"] = series_title
        metadata["series_number"] = file["label"]
        # Write metadata back into archive
        update_archive_info(file["file"], metadata)

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
    args = parser.parse_args()
    # Check that directory is valid
    directory = abspath(args.directory)
    if not exists(directory):
        color_print("Invalid directory.", "red")
    else:
        set_series_info(directory)
            
if __name__ == "__main__":
    main()