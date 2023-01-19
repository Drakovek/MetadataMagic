#!/usr/bin/env python3

from argparse import ArgumentParser
from _functools import cmp_to_key
from metadata_magic.main.meta_finder import get_pairs
from metadata_magic.main.rename.rename_tools import create_filename
from metadata_magic.main.rename.rename_tools import rename_file
from os import getcwd, listdir, pardir
from os.path import abspath, basename, exists, isdir, join
from python_print_tools.main.python_print_tools import color_print
from re import findall
from re import sub as resub
from typing import List
from tqdm import tqdm

def get_section(string:str) -> str:
    """
    Gets the first "section" of a given string.
    A section should contain either only text or only a number.
    
    :param string: String to get section from
    :type string: str, required
    :return: The first "section" of the given string
    :rtype: str
    """
    # Check if string starts with a number
    if len(findall("^[0-9]", string)) > 0:
        # Return number section if string starts with a number
        return findall("[0-9]+[0-9,\\.]*", string)[0]
    # Return non-number section if string doesn't start with number
    sections = findall("[^0-9]+", string)
    if len(sections) > 0:
        return sections[0]
    # Return empty string if no sections could be found
    return ""

def compare_sections(section1:str, section2:str) -> int:
    """
    Compares two sections alphanumerically.
    Returns -1 if section1 comes first, 1 if section2 comes first.
    Returns 0 if section1 and section2 are identical.
    
    :param section1: First section to compare
    :type section1: str, required
    :param section2: Second section to compare
    :type section2: str, required
    :return: Integer describing which section should come first
    :rtype: int
    """
    try:
        # Compare numbers, if applicable.
        float1 = float(section1.replace(",", ""))
        float2 = float(section2.replace(",", ""))
        if float1 > float2:
            return 1
        elif float1 < float2:
            return -1
        return 0
    except ValueError:
        # Return 0 if sections are identical
        if section1 == section2:
            return 0
        # Compare text values
        sort = sorted([section1, section2])
        if sort[0] == section1:
            return -1
        return 1

def compare_alphanum(string1:str, string2:str) -> int:
    """
    Compares two string alphanumerically.
    Returns -1 if string1 comes first, 1 if string2 comes first.
    Returns 0 if string1 and string2 are identical.
    
    :param string1: First string to compare
    :type string1: str, required
    :param string2: Second string to compare
    :type string1: str, required
    :return: Integer describing which string should come first
    :rtype: int
    """
    # Prepare strings for comparison
    compare = 0
    left1 = create_filename(string1).lower()
    left2 = create_filename(string2).lower()
    # Run through comparing strings section by section
    while compare == 0 and not left1 == "" and not left2 == "":
        # Get the first sections
        section1 = get_section(left1)
        section2 = get_section(left2)
        # Modify what's left of strings
        left1 = left1[len(section1):]
        left2 = left2[len(section2):]
        # Compare sections
        compare = compare_sections(section1, section2)
    # Compare full strings if comparing by section inconclusive
    if compare == 0:
        compare = compare_sections(f"T{string1}", f"T{string2}")
    # Return result
    return compare

def sort_alphanum(lst:List[str]) -> List[str]:
    """
    Sorts a given list alphanumerically.
    
    :param lst: List to sort
    :type lst: list[str], required
    :return: Sorted list
    :rtype: list[str]
    """
    comparator = cmp_to_key(compare_alphanum)
    return sorted(lst, key=comparator)

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
        if filenames[i] is not None and not isdir(abspath(join(base, filenames[i]))):
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