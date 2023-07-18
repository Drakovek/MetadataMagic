#!/usr/bin/env python3

from metadata_magic.main.file_tools.file_tools import find_files_of_type
from metadata_magic.main.file_tools.file_tools import extract_zip
from argparse import ArgumentParser
from os import getcwd, remove
from os.path import abspath, basename, exists
from python_print_tools.main.python_print_tools import color_print
from tqdm import tqdm

def extract_all(directory:str, create_folders:bool=True, remove_internals:bool=True, remove_metadata:bool=False):
    """
    Extracts all CBZ archive files in a given directory.
    CBZ contents will be extracted into the directory in which they reside.
    
    :param directory: Directory in which to extract cbz archives
    :type directory: str, required
    :param create_folders: Whether to create folders for each cbz archive to extract contents to, defaults to True
    :type create_folders: bool, optional
    :param remove_internals: Whether to remove redundant folders within the cbz when extracting, defaults to True
    :type remove_internals: bool, optional
    :param remove_metadata: Whether to remove the ComicInfo.xml file when extracting, defaults to False
    :type:remove_metadata: bool, optional
    """
    # Get a list of all the CBZ files in the given directory
    full_directory = abspath(directory)
    cbz_files = find_files_of_type(full_directory, ".cbz")
    # Set to remove ComicInfo.xml if specified
    remove_list = []
    if remove_metadata or not create_folders:
        remove_list = ["ComicInfo.xml", "comicinfo.xml"]
    # Run through all cbz files
    for cbz_file in tqdm(cbz_files):
        # Extract the cbz contents
        extract_zip(cbz_file, full_directory, create_folders, remove_internals, remove_list)
        # Delete the original cbz file
        remove(cbz_file)

def main():
    """
    Sets up the parser for extracting all cbz files.
    """
    # Set up argument parser
    parser = ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory to search for media within.",
            nargs="?",
            type=str,
            default=str(getcwd()))
    parser.add_argument(
            "-d",
            "--direct_extract",
            help="Directly extracts all files without container folders",
            action="store_true")
    parser.add_argument(
            "-r",
            "--remove_metadata",
            help="Removes the ComicInfo.xml metadata",
            action="store_true")
    args = parser.parse_args()
    # Check that directory is valid
    directory = abspath(args.directory)
    if not exists(directory):
        color_print("Invalid directory.", "red")
    else:
        # Ask whether or not to proceed
        proceed = "y"
        if args.direct_extract or args.remove_metadata:
            dir_name = basename(directory)
            color_print("WARNING!", "red")
            color_print(f"All comic book metadata in directory \"{dir_name}\" will be deleted!", "red")
            proceed = input("Extract Comic Contents? (Y/N): ").lower()
        if proceed == "y":
            extract_all(directory, create_folders=(not args.direct_extract), remove_internals=True, remove_metadata=args.remove_metadata)