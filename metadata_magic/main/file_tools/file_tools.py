#!/usr/bin/env python3

from json import dump as dump_json
from json import load as load_json
from json import JSONDecodeError
from html_string_tools.main.html_string_tools import get_extension
from os import listdir, mkdir, remove
from os.path import abspath, basename, exists, isdir, join, relpath
from metadata_magic.main.rename.rename_tools import get_available_filename
from shutil import copy, copytree, rmtree
from tempfile import gettempdir
from typing import List
from zipfile import BadZipFile, ZipFile, ZIP_DEFLATED

def get_temp_dir(folder_name:str="dvk_meta_magic") -> str:
    """
    Creates and returns test directory.

    :param folder_name: Name to give the temporary directory, defaults to "dvk_meta_magic"
    :type folder_name: str, optional
    :return: File path of the test directory
    :rtype: str
    """
    temp_dir = abspath(join(abspath(gettempdir()), folder_name))
    if(exists(temp_dir)):
        rmtree(temp_dir)
    mkdir(temp_dir)
    return temp_dir

def write_text_file(file:str, text:str):
    """
    Writes a file containing the given text.
    Will overwrite existing files
    
    :param file: Path of the file to create
    :type file: str, required
    :param text: Text to save in the file
    :type text: str, required
    """
    try:
        full_path = abspath(file)
        with open(full_path, "w") as out_file:
            out_file.write(text)
    except FileNotFoundError: pass

def read_text_file(file:str) -> str:
    """
    Reads the content of a given text file.
    
    :param file: Path of the file to read
    :type file: str, required
    :return: Text contained in the given file
    :rtype: str
    """
    try:
        full_path = abspath(file)
        with open (full_path) as in_file:
            return in_file.read()
    except (FileNotFoundError, IsADirectoryError, UnicodeDecodeError): return None

def write_json_file(file:str, contents:dict):
    """
    Writes a JSON file containing the given dictionary as contents.
    
    :param file: Path of the file to create
    :type file: str, required
    :param text: Contents to save as JSON
    :type text: str, required
    """
    try:
        full_path = abspath(file)
        with open(full_path, "w") as out_file:
            dump_json(contents, out_file)
    except FileNotFoundError: pass

def read_json_file(file:str) -> dict:
    """
    Returns the contents of a given JSON file as a dictionary.
    
    :param file: JSON file to read.
    :type file: str, required
    :return: Contents of the JSON file
    :rtype: dict
    """
    try:
        full_path = abspath(file)
        with open(full_path) as in_file:
            return load_json(in_file)
    except (FileNotFoundError, IsADirectoryError, JSONDecodeError): return {}


def create_zip(directory:str, zip_file:str, compress_level:int=9) -> bool:
    """
    Creates a zip file with all the files and subdirectories within a given directory.
    
    :param directory: Directory with files to archive into a zip file
    :type directory: str, required
    :param zip_file: Path of the zip file to be created
    :type zip_file: str, required
    :param compress_level: Level of compression from min 0 to max 9, defaults to 9
    :type compress_level: int, optional
    :return: Whether a zip file was successfully created
    :rtype: bool
    """
    # Get list of files in the directory
    full_directory = abspath(directory)
    files = listdir(full_directory)
    for i in range(0, len(files)):
        files[i] = abspath(join(full_directory, files[i]))
    # Expand list of files to include subdirectories
    for file in files:
        if isdir(file):
            sub_files = listdir(file)
            for i in range(0, len(sub_files)):
                files.append(abspath(join(file, sub_files[i])))
    # Create empty zip file
    with ZipFile(zip_file, "w", compression=ZIP_DEFLATED, compresslevel=compress_level) as out_file: pass
    if not exists(zip_file):
        return False
    # Write contents of directory to zip file
    for file in files:
        relative = relpath(file, full_directory)
        with ZipFile(zip_file, "a", compression=ZIP_DEFLATED, compresslevel=compress_level) as out_file:
            out_file.write(file, relative)
    # Return if the zip file was successfully created
    return exists(zip_file)

def extract_zip(zip_file:str, extract_directory:str, create_folder:bool=False,
                remove_internal:bool=False, delete_files:List[str]=[]) -> bool:
    """
    Extracts a ZIP file into a given directory.
    
    :param zip_file: Path to ZIP file to extract
    :type zip_file: str, required
    :param extract_directory: Directory in which to extract ZIP contents
    :type extract_directory: str, required
    :param create_folder: Whether to create a folder within the given directory to hold contents, defaults to False
    :type create_folder: bool, optional
    :param remove_internal: Whether to remove redundant internal folder, defaults to False
    :type remove_internal: bool, optional
    :param delete_files: List of filenames to delete if desired, defaults to []
    :type delete_files: list[str], optional
    :return: Whether the files were extracted successfully
    :rtype: bool
    """
    # Get temporary directory
    temp_dir = get_temp_dir("dvk-unzip")
    # Unzip files into temp directory
    try:
        with ZipFile(zip_file, mode="r") as file:
            file.extractall(path=temp_dir)
    except BadZipFile: return False
    # Create new extraction subfolder if specified
    main_dir = abspath(extract_directory)
    new_dir = abspath(extract_directory)
    if create_folder:
        filename = basename(zip_file)
        filename = filename[:len(filename) - len(get_extension(filename))]
        filename = get_available_filename("AAAAAAAAAA", filename, main_dir)
        new_dir = abspath(join(main_dir, filename))
        mkdir(new_dir)
    # Delete listed files
    for file in delete_files:
        full_file = abspath(join(temp_dir, file))
        if exists(full_file):
            remove(full_file)
    # Remove internal folder if specified
    if remove_internal and len(listdir(temp_dir)) == 1:
        full_file = abspath(join(temp_dir, listdir(temp_dir)[0]))
        if isdir(full_file):
            temp_dir = full_file
    # Copy files to new directory
    files = listdir(temp_dir)
    for file in files:
        filename = file[:len(file) - len(get_extension(file))]
        filename = get_available_filename(file, filename, new_dir)
        current_file = abspath(join(temp_dir, file))
        new_file = abspath(join(new_dir, filename))
        if isdir(current_file):
            copytree(current_file, new_file)
        else:
            copy(current_file, new_file)
    return True

def extract_file_from_zip(zip_file:str, extract_directory:str, extract_file:str) -> str:
    """
    Attempts to extract a single file from a ZIP archive given a filename.
    
    :param zip_file: ZIP archive to extract a file from.
    :type zip_file: str, required
    :param extract_directory: Directory in which to extract the file.
    :type extract_directory: str, required
    :param extract_file: Filename of the file to be extracted
    :type extract_file: str, required
    :return: Path of the extracted file, None if file couldn't be extracted
    :rtype: str
    """
    # Get temporary directory
    temp_dir = get_temp_dir("dvk_unzip_single")
    # Extract into temporary directory
    try:
        with ZipFile(zip_file, mode="r") as zfile:
            zfile.extract(extract_file, path=temp_dir)
            extracted = abspath(join(temp_dir, extract_file))
            new_file = abspath(join(extract_directory, extract_file))
            # Update file if it already exists
            if exists(new_file):
                filename = extract_file[:len(extract_file) - len(get_extension(extract_file))]
                filename = get_available_filename(extracted, filename, extract_directory)
                new_file = abspath(join(extract_directory, filename))
            # Copy file to new location
            copy(extracted, new_file)
            return new_file
    except (BadZipFile, KeyError): return None