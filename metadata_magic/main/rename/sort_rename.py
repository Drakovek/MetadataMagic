#!/usr/bin/env python3

from argparse import ArgumentParser
from metadata_magic.main.meta_finder import get_pairs
from metadata_magic.main.rename.rename_tools import create_filename
from metadata_magic.main.rename.rename_tools import rename_file
from metadata_magic.main.rename.rename_tools import sort_alphanum
from os import getcwd, listdir, pardir
from os.path import abspath, basename, exists, isdir, join
from python_print_tools.main.python_print_tools import color_print
from tqdm import tqdm
from re import findall
from re import sub as resub

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
    filenames = sort_alphanum(listdir(base))
    # Get JSON pairs
    pairs = get_pairs(base)
    sort_pairs = []
    for i in range(0, len(filenames)):
        sort_pairs.append(None)
    # Add pairs to sorted list in order
    for pair in pairs:
        # Skip pair if not in the right directory
        if not abspath(join(pair["json"], pardir)) == base:
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
    name_num = findall("#+", name)
    if len(name_num) > 0:
        pad_num = len(name_num[0])
    print("Renaming Files:")
    for i in tqdm(range(0, len(sort_pairs))):
        # Set the filename
        filename = str(i+start_index)
        if pad_num == 0:
            filename = f"{name} {filename}"
        else:
            # Replace # with item number
            while len(filename) < pad_num:
                filename = f"0{filename}"
            filename = resub("#+", filename, name, 1)
        # Rename media file
        rename_file(sort_pairs[i]["media"], filename)
        # Rename json file, if it exits
        if sort_pairs[i]["json"] is not None:
            rename_file(sort_pairs[i]["json"], filename)

def main():
    """
    Sets up the parser for renaming files in a sorted order
    """
    # Set up argument parser
    parser = ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory to search for JSONs within.",
            nargs="?",
            type=str,
            default=str(getcwd()))
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
        color_print("Invalid directory.", "red")
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

if __name__ == "__main__":
    main()