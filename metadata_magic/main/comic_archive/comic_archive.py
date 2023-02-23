#!/usr/bin/env python3

from argparse import ArgumentParser
from os import getcwd, listdir, mkdir, pardir, remove
from os.path import abspath, basename, exists, isdir, join, relpath
from html_string_tools.main.html_string_tools import get_extension
from metadata_magic.main.comic_archive.comic_xml import get_comic_xml
from metadata_magic.main.comic_archive.comic_xml import generate_info_from_jsons
from metadata_magic.main.comic_archive.comic_xml import get_empty_metadata
from metadata_magic.main.comic_archive.comic_xml import read_comic_info
from metadata_magic.main.rename.sort_rename import sort_alphanum
from python_print_tools.main.python_print_tools import color_print
from tempfile import gettempdir
from tqdm import tqdm
from re import findall
from re import sub as resub
from shutil import copy, rmtree
from zipfile import BadZipFile, is_zipfile, ZipFile

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

def create_cbz(directory:str) -> str:
    """
    Creates a cbz archive containing all the files in a given directory.
    
    :param directory: Directory with files to compress into archive
    :type directory: str, required
    :return: Full path of the created cbz archive
    :rtype: str
    """
    try:
        # Get filenames
        full_directory = abspath(directory)
        cbz = abspath(join(full_directory, basename(full_directory) + ".cbz"))
        # Simply update filename if cbz already exists
        if exists(cbz):
            xml_file = abspath(join(full_directory, "ComicInfo.xml"))
            metadata = read_comic_info(xml_file)
            update_cbz_info(cbz, metadata)
            return cbz
        # Get list of files in the directory
        files = listdir(full_directory)
        for i in range(0, len(files)):
            files[i] = abspath(join(full_directory, files[i]))
        # Expand list of files to include subdirectories
        for file in files:
            if isdir(file):
                sub_files = listdir(file)
                for i in range(0, len(sub_files)):
                    files.append(abspath(join(file, sub_files[i])))
        # Create empty cbz file
        with ZipFile(cbz, "w") as out_file: pass
        assert exists(cbz)
        # Write contents of directory to cbz file
        for file in tqdm(files):
            relative = relpath(file, full_directory)
            with ZipFile(cbz, "a") as out_file:
                out_file.write(file, relative)
        # Return the path of the written cbz archive
        return cbz
    except FileNotFoundError:
        return None

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
    try:
        with ZipFile(file, mode="r") as zfile:
            zfile.extract("ComicInfo.xml", path=extract_dir)
    except (BadZipFile, KeyError): return get_empty_metadata()
    xml_file = abspath(join(extract_dir, "ComicInfo.xml"))
    assert exists(xml_file)
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
        with ZipFile(cbz_file, mode="r") as ext_file:
            ext_file.extractall(path=temp_dir)
        # Create/Overwrite ComicInfo.xml file
        xml = get_comic_xml(metadata)
        xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
        with open(xml_file, "w") as out_file:
            out_file.write(xml)
        # Pack files into archive
        new_cbz = create_cbz(temp_dir)
        # Replace the old cbz file
        remove(file)
        copy(new_cbz, file)
        remove(new_cbz)

def get_comic_info_from_path(path:str) -> dict:
    """
    Attempts to get comic metadata from a given path in either cbz, standalone ComicInfo.xml, or JSON format.
    In order of preference, metadata is gathered from cbz, ComicInfo.xml, then JSON.
    
    :param path: Path for either a directory or cbz file
    :type path: str, required
    :return: Comic metadata
    :rtype: dict
    """
    # Get full path
    full_path = abspath(path)
    empty = get_empty_metadata()
    empty["age_rating"] = "Unknown"
    # Check if cbz file is present
    cbz_file = None
    if not isdir(full_path):
        cbz_file = full_path
    else:
        files = listdir(full_path)
        files = sort_alphanum(files)
        for file in files:
            if get_extension(file) == ".cbz":
                cbz_file = abspath(join(full_path, file))
                break
    # Try to get info from cbz file, if available
    if cbz_file is not None:
        try:
            metadata = get_info_from_cbz(cbz_file)
        except FileNotFoundError: metadata = get_empty_metadata()
        if not metadata == get_empty_metadata() and not metadata == empty:
            return metadata
        else:
            full_path = abspath(join(cbz_file, pardir))
    # Get metadata from XML file, if available
    xml_file = abspath(join(full_path, "ComicInfo.xml"))
    if exists(xml_file):
        metadata = read_comic_info(xml_file)
        if not metadata == get_empty_metadata() and not metadata == empty:
            return metadata
    # Get metadata from JSONS
    try:
        metadata = generate_info_from_jsons(full_path)
        return metadata
    except FileNotFoundError: return get_empty_metadata()

def create_or_update_cbz(path:str, metadata:dict) -> str:
    """
    Attempts to either create a cbz archive or update an existing archive.
    If a cbz file or directory containing cbz file is given, existing cbz is updated with giben metadata.
    If a directory not containing cbz file is given, contents of the directory are archived as cbz.
    
    :param path: Path to either a directory or cbz file
    :type path: str, required
    :param metadata: Metadata to use when creating ComicInfo.xml
    :type metadata: dict, required
    :return: Path of the created or updated cbz file
    :rtype: str
    """
    # Check if path is a directory
    cbz_file = None
    full_path = abspath(path)
    if isdir(full_path):
        # Create ComicInfo.xml from metadata
        xml = get_comic_xml(metadata)
        with open(abspath(join(full_path, "ComicInfo.xml")), "w") as out_file:
            out_file.write(xml)
        # See if cbz file already exists
        files = listdir(full_path)
        files = sort_alphanum(files)
        for file in files:
            if get_extension(file) == ".cbz":
                cbz_file = abspath(join(full_path, file))
                break
        if cbz_file is None:
            # Create cbz archive
            print("Creating archive:")
            cbz_file = create_cbz(full_path)
            return cbz_file
    # Update cbz file if applicable
    if cbz_file is None:
        cbz_file = full_path
    update_cbz_info(cbz_file, metadata)
    return cbz_file
    
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
    # Get default metadata
    full_path = abspath(path)
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
    create_or_update_cbz(full_path, metadata)

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
            
if __name__ == "__main__":
    main()
