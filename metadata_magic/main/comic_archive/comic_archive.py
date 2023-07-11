#!/usr/bin/env python3

from argparse import ArgumentParser
from os import getcwd, listdir, mkdir, pardir, remove
from os.path import abspath, basename, exists, isdir, join, relpath
from html_string_tools.main.html_string_tools import get_extension
from metadata_magic.main.file_tools.file_tools import create_zip, extract_file_from_zip, extract_zip, get_temp_dir
from metadata_magic.main.comic_archive.comic_xml import get_comic_xml
from metadata_magic.main.comic_archive.comic_xml import generate_info_from_jsons
from metadata_magic.main.meta_reader import get_empty_metadata
from metadata_magic.main.comic_archive.comic_xml import read_comic_info
from metadata_magic.main.rename.rename_tools import sort_alphanum
from python_print_tools.main.python_print_tools import color_print
from tqdm import tqdm
from re import findall
from re import sub as resub
from shutil import copy, move, rmtree
from zipfile import is_zipfile
from metadata_magic.test.temp_file_tools import create_text_file

def create_cbz(directory:str, name:str=None, metadata:dict=None, remove_files:bool=False) -> str:
    """
    Creates a cbz archive containing the files of a given directory.
    
    :param directory: Directory with files to archive
    :type directory: str, required
    :param name: Name of the CBZ file, will use default name if not present, defaults to None
    :type name: str, optional
    :param metadata: Metadata to include as ComicInfo.xml, defaults to None
    :type metadata: dict, optional
    :param remove_files: Whether to delete the files now in the archive once the CBZ is completed, defaults to False
    :type remove_files: bool, optional
    :return: Path of the newly created CBZ file
    :rtype: str
    """
    # Return None if directory is empty
    full_directory = abspath(directory)
    if len(listdir(full_directory)) == 0:
        return None
    # Create CBZ filename
    filename = basename(full_directory) + ".cbz"
    if name is not None:
        filename = f"{name}.cbz"
    cbz_file = abspath(join(full_directory, filename))
    # Update CBZ if it already exists
    if exists(cbz_file):
        if metadata is not None:
            update_cbz_info(cbz_file, metadata)
        return cbz_file
    # Check if there are existing directories
    move_files = True
    files = sort_alphanum(listdir(full_directory))
    for file in files:
        if isdir(abspath(join(full_directory, file))):
            move_files = False
            break
    # Move files if required
    if move_files:
        # Create new folder to contain files
        folder_name = files[0][:len(files[0]) - len(get_extension(files[0]))]
        new_folder = abspath(join(full_directory, folder_name))
        mkdir(new_folder)
        # Move existing files to the new folder
        for file in files:
            current_file = abspath(join(full_directory, file))
            new_file = abspath(join(new_folder, file))
            move(current_file, new_file)
    # Create metadata file, if specified
    meta_file = abspath(join(full_directory, "ComicInfo.xml"))
    if metadata is not None:
        create_text_file(meta_file, get_comic_xml(metadata))
    # Create cbz file
    assert create_zip(full_directory, cbz_file)
    # Remove all old files besides the CBZ, if specified.
    if remove_files:
        files = listdir(full_directory)
        for file in files:
            full_file = abspath(join(full_directory, file))
            if isdir(full_file):
                rmtree(full_file)
            elif not full_file == cbz_file:
                remove(full_file)
    # Remove ComicInfo.xml file, if exists
    if exists(meta_file):
        remove(meta_file)
    # Return CBZ file
    return cbz_file

def get_info_from_cbz(cbz_file:str) -> dict:
    """
    Extracts ComicInfo.xml from a given .cbz file and returns the metadata as a dict.
    
    :param cbz_file: Path to a .cbz file
    :type cbz_file: str, required
    :return: Dictionary containing metadata from the .cbz file
    :rtype: dict
    """
    # Create temporary directory
    file = abspath(cbz_file)
    extract_dir = get_temp_dir("dvk_meta_extract")
    assert exists(extract_dir)
    # Extract ComicInfo.xml from given file
    xml_file = extract_file_from_zip(cbz_file, extract_dir, "ComicInfo.xml")
    if xml_file is None or not exists(xml_file):
        return get_empty_metadata()
    # Read XML file
    return read_comic_info(xml_file)

def update_cbz_info(cbz_file:str, metadata:dict):
    """
    Replaces the ComicInfo.xml file in a given .cbz file to reflect the given metadata
    
    :param cbz_file: Path of the .cbz file to update
    :type cbz_file: str, required
    :param metadata: Metadata to use for the new ComicInfo.xml file
    :type metadata: dict
    """
    # Check if given file is a valid cbz file
    file = abspath(cbz_file)
    if is_zipfile(file):
        # Extract cbz into temp file
        temp_dir = get_temp_dir("dvk_comic_info")
        extract_zip(cbz_file, temp_dir)
        # Create/Overwrite ComicInfo.xml file
        xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
        create_text_file(xml_file, get_comic_xml(metadata))
        # Pack files into archive
        new_cbz = create_cbz(temp_dir)
        # Replace the old cbz file
        remove(file)
        copy(new_cbz, file)
        remove(new_cbz)
    
def create_comic_archive(path:str,
                rp_description:bool=False,
                rp_date:bool=False,
                rp_artists:bool=False,
                rp_publisher:bool=False,
                rp_url:bool=False,
                rp_tags:bool=False,
                rp_age:bool=False,
                rp_score:bool=False):
    """
    Creates a comic archive using the files in a directory and metadata from the user.
    
    :param path: Directory with files to archive, or existing .cbz file
    :type path: str, required
    :param rp_description: Whether to replace the description from gathered metadata, defaults to False
    :type rp_description: bool, optional
    :param rp_date: Whether to replace the date from gathered metadata, defaults to False
    :type rp_date: bool, optional
    :param rp_artists: Whether to replace the artists/writers from gathered metadata, defaults to False
    :type rp_artists: bool, optional
    :param rp_publisher: Whether to replace the publisher from gathered metadata, defaults to False
    :type rp_publiser: bool, optional
    :param rp_url: Whether to replace the URL from gathered metadata, defaults to False
    :type rp_url: bool, optional
    :param rp_tags: Whether to replace the tags from gathered metadata, defaults to False
    :type rp_tags: bool, optional
    :param rp_age: Whether to replace the age rating from gathered metadata, defaults to False
    :type rp_age: bool, optional
    :param rp_score: Whether to replace the score from gathered metadata, defaults to False
    :type rp_score: bool, optional
    """
    # Check if there is an existing .cbz file to update
    filename = None
    full_path = abspath(path)
    files = listdir(full_path)
    if len(files) == 1 and get_extension(files[0]) == ".cbz":
        # Get metadata from the .cbz file
        filename = files[0][:len(files[0]-4)]
        metadata = get_info_from_cbz(abspath(join(full_path, files[0])))
    else:
        # Get metadate from any existing JSON files
        metadata = generate_info_from_jsons(full_path)
    metadata = get_comic_info_from_path(full_path)
    # Remove metadata fields the user wishes to replace
    if rp_description:
        metadata["description"] = None
    if rp_date:
        metadata["date"] = None
    if rp_artists:
        metadata["artist"] = None
        metadata["writer"] = None
        metadata["cover_artist"] = None
    if rp_publisher:
        metadata["publisher"] = None
    if rp_url:
        metadata["url"] = None
    if rp_tags:
        metadata["tags"] = None
    if rp_age:
        metadata["age_rating"] = None
    # Get the title
    title = metadata["title"]
    if title is None:
        metadata["title"] = str(input("Title: "))
    else:
        title = str(input(f"Title (Default is \"{title}\"): "))
        if not title == "":
            metadata["title"] = title
    # Get the description
    if metadata["description"] is None:
        description = str(input("Description: "))
        if not description == "":
            metadata["description"] = description
    # Get the date
    if metadata["date"] is None:
        date = ""
        regex = "(19[7-9][0-9]|2[0-1][0-9]{2})\\-(0[1-9]|1[0-2])\\-(0[1-9]|[1-2][0-9]|3[0-1])"
        while len(findall(regex, date)) == 0:
            date = str(input("Date (YYYY-MM-DD): "))
        metadata["date"] = date
    # Get the Main Artist
    artist = metadata["artist"]
    if artist is None:
        artist = str(input("Artist: "))
        if not artist == "":
            metadata["artist"] = artist
    # Get the Cover Artist
    if metadata["cover_artist"] is None:
        cover = str(input(f"Cover Artist (Default is \"{artist}\"): "))
        if not cover == "":
            metadata["cover_artist"] = cover
        elif not artist == "":
            metadata["cover_artist"] = artist
    # Get the Writer
    if metadata["writer"] is None:
        writer = str(input(f"Writer (Default is \"{artist}\"): "))
        if not writer == "":
            metadata["writer"] = writer
        elif not artist == "":
            metadata["writer"] = artist
    # Get the Publisher
    if metadata["publisher"] is None:
        publisher = str(input("Publisher: "))
        if not publisher == "":
            metadata["publisher"] = publisher
    # Get the URL
    if metadata["url"] is None:
        url = str(input("URL: "))
        if not url == "":
            metadata["url"] = url
    # Get tags
    if metadata["tags"] is None:
        url = str(input("Tags: "))
        if not url == "":
            metadata["tags"] = resub("\\s*,\\s*", ",", url)
    # Get age rating
    while metadata["age_rating"] is None:
        print("0) Unknown\n1) Everyone\n2) Teen\n3) Mature 17+\n4) X18+")
        age = str(input("Age Rating: "))
        if age == "0":
            metadata["age_rating"] = "Unknown"
        if age == "1":
            metadata["age_rating"] = "Everyone"
        if age == "2":
            metadata["age_rating"] = "Teen"
        if age == "3":
            metadata["age_rating"] = "Mature 17+"
        if age == "4":
            metadata["age_rating"] = "X18+"
    # Get score
    if rp_score:
        score = str(input("Score (Range 0-5): "))
        if not score == "":
            metadata["score"] = score
    # Create/Update .cbz
    create_cbz(full_path, name=filename, metadata=metadata)

def main():
    """
    Sets up the parser for creating a comic archive.
    """
    # Set up argument parser
    parser = ArgumentParser()
    parser.add_argument(
            "path",
            help="Path to directory or existing .cbz file.",
            nargs="?",
            type=str,
            default=str(getcwd()))
    parser.add_argument(
            "-s",
            "--summary",
            help="Use user summary instead of summary in metadata.",
            action="store_true")
    parser.add_argument(
            "-d",
            "--date",
            help="Use user date instead of date in metadata.",
            action="store_true")
    parser.add_argument(
            "-a",
            "--artists",
            help="Use user artists instead of artists in metadata.",
            action="store_true")
    parser.add_argument(
            "-p",
            "--publisher",
            help="Use user publisher instead of publisher in metadata.",
            action="store_true")
    parser.add_argument(
            "-u",
            "--url",
            help="Use user URL instead of URL in metadata.",
            action="store_true")
    parser.add_argument(
            "-t",
            "--tags",
            help="Use user tags instead of tags in metadata.",
            action="store_true")
    parser.add_argument(
            "-r",
            "--rating",
            help="Use user age rating instead of rating in metadata.",
            action="store_true")
    parser.add_argument(
            "-g",
            "--grade",
            help="Use user grade/score instead of score in metadata.",
            action="store_true")
    args = parser.parse_args()
    # Check that directory is valid
    path = abspath(args.path)
    if not exists(path):
        color_print("Invalid path.", "red")
    else:
        # Create the comic archive
        create_comic_archive(path,
                rp_description=args.summary,
                rp_date=args.date,
                rp_artists=args.artists,
                rp_publisher=args.publisher,
                rp_url=args.url,
                rp_tags=args.tags,
                rp_age=args.rating,
                rp_score=args.grade)