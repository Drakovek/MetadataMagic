#!/usr/bin/env python3

import os
import re
import tqdm
import argparse
import html_string_tools.html
import python_print_tools.printer
import metadata_magic.sort as mm_sort
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.meta_finder as mm_meta_finder
import metadata_magic.meta_reader as mm_meta_reader
import metadata_magic.archive.archive as mm_archive
from os.path import abspath, basename, exists, isdir, join
from typing import List

def get_file_friendly_text(string:str) -> str:
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
    new_text = re.sub(r"\.\s*\.\s*\.", "…", new_text)
    # Replace special latin characters
    new_text = re.sub("[À-Å]", "A", new_text)
    new_text = re.sub("[È-Ë]", "E", new_text)
    new_text = re.sub("[Ì-Ï]", "I", new_text)
    new_text = re.sub("[Ò-Ö]", "O", new_text)
    new_text = re.sub("[Ù-Ü]", "U", new_text)
    new_text = re.sub("[à-å]", "a", new_text)
    new_text = re.sub("[è-ë]", "e", new_text)
    new_text = re.sub("[ì-ï]", "i", new_text)
    new_text = re.sub("[ò-ö]", "o", new_text)
    new_text = re.sub("[ù-ü]", "u", new_text)
    new_text = re.sub("[ýÿ]", "y", new_text)
    new_text = new_text.replace("Ñ", "N")
    new_text = new_text.replace("Ý", "Y")
    new_text = new_text.replace("ñ", "n")
    # Replace -> Arrow with "to"
    new_text = re.sub(r"(?<=\s)-+>(?=\s)", "to", new_text)
    # Replace all invalid characters
    new_text = re.sub(r'<|>|\"|\/|\\|\||\?|\*|\.+$', "-", new_text)
    # Remove whitespace and hyphens at begining and end of text
    new_text = re.sub(r"^[\s-]+|[\s-]+$", "", new_text)
    # Remove duplicate spacers
    new_text = re.sub("-{2,}", "-", new_text)
    new_text = re.sub(" {2,}", " ", new_text)
    # Remove hanging hyphens
    new_text = re.sub(r"(?<= )-(?=[^ \-])|(?<=[^ \-])-(?= )", "", new_text)
    # Remove any remaining whitespace & heading/trailing periods
    new_text = re.sub(r"^[\s\.\-]+|[\s\.\-]+$", "", new_text)
    # Return "0" if there is no text
    if new_text == "":
        return "0"
    # Return modified string
    return new_text

def get_available_filename(rename_files:List[str], new_filename:str, end_path:str) -> str:
    """
    Returns a filename as close as possible to the desired filename in a given directory
    Number will be appended to filename if file already exists with that name.
    
    :param rename_files: List of files intended to be renamed, used for extension
    :type rename_files: List[str], required
    :param new_filename: Filename to set new file to
    :type new_filename: str, required
    :param end_path: Path to check for already existing files within
    :type end_path: str, required
    :return: Name of the new filename
    :rtype: str
    """
    # Get the prefered new filename
    filename = get_file_friendly_text(new_filename)
    # Get the list of file extensions
    extensions = []
    for rename_file in rename_files:
        extensions.append(html_string_tools.html.get_extension(rename_file))
    # Update name if the filename already exists
    file_num = 1
    base_filename = filename
    full_end_path = abspath(end_path)
    loop = True
    while loop:
        loop = False
        for extension in extensions:
            if exists(abspath(join(full_end_path, f"{filename}{extension}"))):
                file_num += 1
                filename = f"{base_filename}-{file_num}"
                loop = True
                break
    # Return the filename
    return filename

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
    extension = html_string_tools.html.get_extension(file)
    filename = get_file_friendly_text(new_filename)
    # Do nothing if the filename is already accurate
    if basename(path) == f"{filename}{extension}":
        return path
    # Update filename if file already exists
    parent_dir = abspath(join(path, os.pardir))
    filename = get_available_filename([file], new_filename, parent_dir)
    # Rename file
    try:
        new_file = abspath(join(parent_dir, f"{filename}{extension}"))
        os.rename(path, new_file)
        return new_file
    except FileNotFoundError:
        return None

def get_string_from_metadata(metadata:dict, template:str) -> str:
    """
    Returns a text string based on given metadata and a string template.
    Keys in the template marked as {key} will be replaced with the key values in metadata.
    
    :param metadata: Dictionary with metadata key-value pairs
    :type metadata: dict, required
    :param template: Metadata string template
    :type template: str, required
    :return: String containing metadata as defined by the template
    :rtype: str
    """
    # Find all keys in the template string
    filename = template
    keys = re.findall(r"(?<={)[^}]+(?=})", template)
    # Replace all the keys in the string with their values
    for key in keys:
        # Attempt to get the key
        try:
            value = metadata[key]
        except KeyError:
            try:
                value = metadata["original"][key]
            except KeyError: return None
        # Check if series number is valid and needed if specified
        if key == "series_number":
            try:
                # Get the padded series number
                padded = re.findall("^[0-9]+", value)[0].zfill(2)
                value = re.sub(r"^[0-9]+", padded, value)
                value = re.sub(r"\.0+$", "", value)
                # Check that the file isn't 1 of 1
                total = metadata["series_total"]
                assert total is None or not float(total) == 1 or not float(value) == 1
            except (AssertionError, IndexError, KeyError, TypeError, ValueError): return None
        # Return none if the key is empty
        if value is None:
            return None
        # Convert the value to a string, if necessary
        if isinstance(value, list):
            value = ",".join(value)
        filename = filename.replace(f"{{{key}}}", str(value))
    # Remove all key references that weren't found in the metadata
    filename = re.sub(r"{[^}]*}", "", filename).strip()
    # Return the filename
    return filename

def rename_archives(path:str, template:str):
    """
    Rename all the media archives in a given directory based on their metadata and a string template
    
    :param path: Path to the directory in which to rename media archives
    :type path: str, required
    :param template: Metadata string template to use for filename, as used in get_string_from_metadata function.
    :type template: str, required
    """
    # Get all media archives
    archive_files = mm_file_tools.find_files_of_type(path, [".cbz", ".epub"])
    # Run through each archive file
    for archive_file in tqdm.tqdm(archive_files):
        # Get the filename for the archive file
        metadata = mm_archive.get_info_from_archive(archive_file)
        try:
            # Don't rename if the filename is already correct or metadata can't be found
            filename = get_file_friendly_text(get_string_from_metadata(metadata, template))
            assert not filename == re.sub(r"\.[^\.]{0,5}$", "", basename(archive_file))
        except (AssertionError, AttributeError): continue
        # Get available filename
        parent = abspath(join(archive_file, os.pardir))
        filename = get_available_filename(archive_file, filename, parent)
        # Rename the archive file
        rename_file(archive_file, filename)

def rename_json_pairs(path:str, template:str):
    """
    Rename all the json-media pairs in a given directory based on their metadata and a string template
    
    :param path: Path to the directory in which to rename JSONs and media
    :type path: str, required
    :param template: Metadata string template to use for filename, as used in get_string_from_metadata function.
    :type template: str, required
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
        metadata = mm_meta_reader.load_metadata(json, media)
        filename = get_string_from_metadata(metadata, template)
        # Don't rename if the filename is already correct or metadata can't be found
        try:
            filename = get_file_friendly_text(filename)
            assert not filename == basename(json)[:len(basename(json))-5]
        except (AssertionError, AttributeError): continue
        # Get the available filenames for media and json
        parent = abspath(join(json, os.pardir))
        filename = get_available_filename([media, json], filename, parent)
        # Rename files
        rename_file(json, filename)
        rename_file(media, filename)

def sort_rename(path:str, template:str, index:int=1):
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
    for file in mm_sort.sort_alphanum(os.listdir(full_path)):
        if file in used_files:
            continue
        full_file = abspath(join(full_path, file))
        if not isdir(full_file):
            pairs.append({"json":None, "media":full_file})
    # Update the template
    try:
        updated_template = template
        number_string = re.findall(r"#+(?=[^#]*$)", template)[0]
    except IndexError:
        number_string = "##"
        if not index == 1 or len(pairs) > 1:
            updated_template = f"{template} [##]"
    # Rename all the files
    for i in range(0, len(pairs)):
        # Don't rename if the filename is already correct
        filename = re.sub(r"#+(?=[^#]*$)", str(i+index).zfill(len(number_string)), updated_template)
        filename = get_file_friendly_text(filename)
        if filename == re.sub(r"\.[^\.]{0,5}$", "", basename(pairs[i]["media"])):
            continue
        # Rename the media and JSON files
        filename = get_available_filename([pairs[i]["media"], "a.json"], filename, full_path)
        rename_file(pairs[i]["media"], filename)
        if pairs[i]["json"] is not None:
            rename_file(pairs[i]["json"], filename)

def user_sort_rename(path:str):
    """
    Prompts the user for info needed for the sort_rename function.
    
    :param path: Path of the directory in which to rename files
    :type path: str, required
    """
    # Get the default template based on filenames in the given directory
    title = None
    for file in mm_sort.sort_alphanum(os.listdir(path)):
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
    # Rename files
    sort_rename(path, template, index)

def user_metadata_rename(path:str):
    """
    Prompts the user for info needed for the rename_archives and rename_json_pairs functions.
    
    :param path: Path of the directory in which to rename files
    :type path: str, required
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
    rename_archives(path, template)
    rename_json_pairs(path, template)

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
    args = parser.parse_args()
    # Check that directory is valid
    directory = abspath(args.directory)
    if not exists(directory):
        python_print_tools.printer.color_print("Invalid directory.", "red")
    else:
        if args.metadata_rename and args.sort_rename:
            python_print_tools.printer.color_print("Choose only one renaming option.", "red")
        elif not args.metadata_rename and not args.sort_rename:
            python_print_tools.printer.color_print("Choose a renaming option.", "red")   
        elif args.sort_rename:
            user_sort_rename(directory)
        elif args.metadata_rename:
            user_metadata_rename(directory)
