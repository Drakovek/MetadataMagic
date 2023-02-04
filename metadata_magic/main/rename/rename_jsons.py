#!/usr/bin/env python3

from argparse import ArgumentParser
from html_string_tools.main.html_string_tools import get_extension
from os import getcwd
from os.path import abspath, basename, exists
from metadata_magic.main.meta_finder import get_pairs
from metadata_magic.main.meta_reader import load_metadata
from metadata_magic.main.rename.rename_tools import rename_file
from python_print_tools.main.python_print_tools import color_print
from tqdm import tqdm

def rename_json_pairs(path:str, add_id:bool=False):
    """
    Renames all JSON-media pairs of files to match the title found in the JSON metadata
    
    :param path: Path of the directory containing JSON pairs
    :type path: str, required
    :param add_id: Whether to include the media ID in the filename, defaults to False
    :type add_id: bool, optional
    """
    # Get JSON pairs
    pairs = get_pairs(path)
    # Rename each pair
    print("Renaming JSON and media files:")
    for pair in tqdm(pairs):
        # Get paths from the pair
        json = pair["json"]
        media = pair["media"]
        # Read JSON file and get title
        meta = load_metadata(json)
        title = meta["title"]
        if title is None:
            title = basename(media)
            extension = get_extension(title)
            title = title[:len(title) - len(extension)]
        # Add ID if specified
        media_id = meta["id"]
        if add_id and media_id is not None:
            title = f"[{media_id}] {title}"
        # Rename JSON
        new_file = rename_file(json, title)
        # Rename media
        try:
            title = basename(new_file)
            extension = get_extension(title)
            title = title[:len(title) - len(extension)]
            rename_file(media, title)
        except TypeError: pass

def main():
    """
    Sets up the parser for the user to rename JSON files.
    """
    # Set up argument parser
    parser = ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory in which to rename JSONs and media.",
            nargs="?",
            type=str,
            default=str(getcwd()))
    parser.add_argument(
            "-i",
            "--id",
            help="Add media ID to the beginning of renamed files.",
            action="store_true")
    args = parser.parse_args()
    # Check that directory is valid
    directory = abspath(args.directory)
    if not exists(directory):
        color_print("Invalid directory.", "red")
    else:
        rename_json_pairs(directory, args.id)
        color_print("Finished renaming.", "green")

if __name__ == "__main__":
    main()