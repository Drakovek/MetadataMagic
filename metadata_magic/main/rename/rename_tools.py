#!/usr/bin/env python3

from _functools import cmp_to_key
from html_string_tools.main.html_string_tools import get_extension
from os import rename, pardir
from os.path import abspath, basename, exists, join
from re import findall
from re import sub as resub
from typing import List

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

def create_filename(string:str) -> str:
    """
    Creates a string suitable for a filename from a given string.
    :param string: Any string to convert into filename
    :type string: str, required
    :return: String with all invalid characters removed or replaced
    :rtype: str
    """
    # Replace colons
    new_text = string.replace(":", " - ")
    # Replace elipses
    new_text = resub("\\.\\s*\\.\\s*\\.", "…", new_text)
    # Replace special latin characters
    new_text = resub("[À-Å]", "A", new_text)
    new_text = resub("[È-Ë]", "E", new_text)
    new_text = resub("[Ì-Ï]", "I", new_text)
    new_text = resub("[Ò-Ö]", "O", new_text)
    new_text = resub("[Ù-Ü]", "U", new_text)
    new_text = resub("[à-å]", "a", new_text)
    new_text = resub("[è-ë]", "e", new_text)
    new_text = resub("[ì-ï]", "i", new_text)
    new_text = resub("[ò-ö]", "o", new_text)
    new_text = resub("[ù-ü]", "u", new_text)
    new_text = resub("[ýÿ]", "y", new_text)
    new_text = new_text.replace("Ñ", "N")
    new_text = new_text.replace("Ý", "Y")
    new_text = new_text.replace("ñ", "n")
    # Replace all invalid characters
    new_text = resub("<|>|\"|\\/|\\\\|\\||\\?|\\*|\\.+$", "-", new_text)
    # Remove whitespace and hyphens at begining and end of text
    new_text = resub("^[\\s-]+|[\\s-]+$", "", new_text)
    # Remove duplicate spacers
    new_text = resub("-{2,}", "-", new_text)
    new_text = resub(" {2,}", " ", new_text)
    # Remove hanging hyphens
    new_text = resub("(?<= )-(?=[^ \\-])|(?<=[^ \\-])-(?= )", "", new_text)
    # Remove any remaining whitespace & trailing periods
    new_text = resub("^\\s+|[\\s\\.\\-]+$", "", new_text)
    # Return "0" if there is no text
    if new_text == "":
        return "0"
    # Return modified string
    return new_text

def rename_file(file:str, new_filename:str) -> str:
    """
    Renames a given file to a given filename.
    Filename will be modified with create_filename to be appropriate.
    Number will be appended to filename if file already exists with that name.
    
    :param file: Path of the file to rename
    :type file: str, required
    :param new_filename: Filename to set new file to
    :type new_filename: str, required
    :return: Path of the file after being renamed, None if rename failed
    :rtype: str
    """
    # Get the prefered new filename
    path = abspath(file)
    extension = get_extension(file)
    filename = create_filename(new_filename)
    # Do nothing if the filename is already accurate
    if basename(path) == f"{filename}{extension}":
        return path
    # Update filename if file already exists
    num = 2
    base_filename = filename
    parent = abspath(join(path, pardir))
    while exists(abspath(join(parent,f"{filename}{extension}"))):
        filename = f"{base_filename}-{num}"
        num += 1
    # Rename file
    try:
        new_file = abspath(join(parent,f"{filename}{extension}"))
        rename(path, new_file)
        return new_file
    except FileNotFoundError:
        return None
