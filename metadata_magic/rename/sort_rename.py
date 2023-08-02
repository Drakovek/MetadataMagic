#!/usr/bin/env python3

import os
import re
import tqdm
import argparse
import python_print_tools.printer
import metadata_magic.meta_finder as mm_meta_finder
import metadata_magic.rename.rename_tools as mm_rename_tools
from os.path import abspath, basename, exists, isdir, join

def sort_rename(path:str, name:str, start_index:int=1):
    """
    Renames all files in a given path to a common title, sequenced in order with numbers.
    JSON-media pairs are renamed to the same name, all other files named separately.
    "#" Characters in name are converted to actual index number when renaming.
    Number of "#" characters corresponds to the number of padded digits for the index.
    
    :param path: Path of the files to rename
    :type path: str, required
    :param name: Common title for renaming files
    :type name: str, required
    :param start_index: The first number to start with when renaming, defaults to 1
    :type start_index: int, optional
    """
    # Get sorted list of files
    base = abspath(path)
    filenames = mm_rename_tools.sort_alphanum(os.listdir(base))
    # Get JSON pairs
    pairs = mm_meta_finder.get_pairs(base)
    sort_pairs = []
    for i in range(0, len(filenames)):
        sort_pairs.append(None)
    # Add pairs to sorted list in order
    for pair in pairs:
        # Skip pair if not in the right directory
        if not abspath(join(pair["json"], os.pardir)) == base:
            continue
        # Add pair to sorted pair list
        index = filenames.index(basename(pair["media"]))
        filenames[index] = None
        sort_pairs[index] = pair
        index = filenames.index(basename(pair["json"]))
        filenames[index] = None
    # Add remaining non-paired items to sorted list
    for i in range(0, len(filenames)):
        if filenames[i] is not None and not filenames[i] == "ComicInfo.xml" and not isdir(abspath(join(base, filenames[i]))):
            file = abspath(join(base, filenames[i]))
            pair = {"json":None, "media":file}
            sort_pairs[i] = pair
    # Delete empty entries in the sort_pairs list
    for i in range(len(sort_pairs)-1,-1,-1):
        if sort_pairs[i] is None:
            del sort_pairs[i]
    # Rename files in order
    pad_num = 0
    name_num = re.findall("#+", name)
    if len(name_num) > 0:
        pad_num = len(name_num[0])
    print("Renaming Files:")
    for i in tqdm.tqdm(range(0, len(sort_pairs))):
        # Set the filename
        filename = str(i+start_index)
        if pad_num == 0:
            filename = f"{name} {filename}"
        else:
            # Replace # with item number
            while len(filename) < pad_num:
                filename = f"0{filename}"
            filename = re.sub("#+", filename, name, 1)
        # Rename media file
        mm_rename_tools.rename_file(sort_pairs[i]["media"], filename)
        # Rename json file, if it exits
        if sort_pairs[i]["json"] is not None:
            mm_rename_tools.rename_file(sort_pairs[i]["json"], filename)

def main():
    """
    Sets up the parser for renaming files in a sorted order
    """
    # Set up argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory to search for JSONs within.",
            nargs="?",
            type=str,
            default=str(os.getcwd()))
    parser.add_argument(
            "-n",
            "--name",
            help="Base name for renaming files.",
            nargs="?",
            type=str,
            default=None)
    parser.add_argument(
            "-i",
            "--index",
            help="Index number to start with when renaming.",
            nargs="?",
            type=str,
            default=None)
    args = parser.parse_args()
    # Check that directory is valid
    directory = abspath(args.directory)
    if not exists(directory):
        python_print_tools.printer.color_print("Invalid directory.", "red")
    else:
        # Get name if not already given
        name = args.name
        if name is None:
            name = str(input("Rename Title: "))
        # Get index number
        try:
            index = int(args.index)
        except (TypeError, ValueError): index = 1
        # Start renaming
        sort_rename(directory, name, index)
