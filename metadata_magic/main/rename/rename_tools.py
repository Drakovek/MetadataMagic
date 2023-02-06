#!/usr/bin/env python3

from html_string_tools.main.html_string_tools import get_extension
from os import rename, pardir
from os.path import abspath, basename, exists, join
from re import sub as resub

def create_filename(string:str) -> str:
    """
    Creates a string suitable for a filename from a given string.
    :param string: Any string to convert into filename
    :type string: str, required
    :return: String with all invalid characters removed or replaced
    :rtype: str
    """
    # Replace elipses
    new_text = resub("\\.\\s*\\.\\s*\\.", "…", string)
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
    new_text = resub("<|>|:|\"|\\/|\\\\|\\||\\?|\\*|\\.+$", "-", new_text)
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
        filename = f"{base_filename}{num}"
        num += 1
    # Rename file
    try:
        new_file = abspath(join(parent,f"{filename}{extension}"))
        rename(path, new_file)
        return new_file
    except FileNotFoundError:
        return None