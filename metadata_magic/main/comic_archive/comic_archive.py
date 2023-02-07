#!/usr/bin/env python3

from argparse import ArgumentParser
from os import getcwd, listdir, mkdir, remove
from os.path import abspath, basename, exists, isdir, join, relpath
from metadata_magic.main.comic_archive.comic_xml import get_comic_xml
from metadata_magic.main.comic_archive.comic_xml import generate_info_from_jsons
from metadata_magic.main.comic_archive.comic_xml import get_empty_metadata
from metadata_magic.main.comic_archive.comic_xml import read_comic_info
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

def create_comic_archive(directory:str,
                rp_description:bool=False,
                rp_date:bool=False,
                rp_artists:bool=False,
                rp_publisher:bool=False,
                rp_url:bool=False,
                rp_tags:bool=False):
    """
    Creates a comic archive using the files in a directory and metadata from the user.
    
    :param directory: Directory with files to archive 
    :type directory: str, required
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
    """
    # Get default metadata
    full_directory = abspath(directory)
    metadata = generate_info_from_jsons(full_directory)
    # Get existing ComicInfo.xml info, if applicable
    xml_file = abspath(join(full_directory, "ComicInfo.xml"))
    if exists(xml_file):
        metadata = read_comic_info(xml_file)
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
    # Write metadata to ComicInfo XML
    xml = get_comic_xml(metadata)
    with open(xml_file, "w") as out_file:
        out_file.write(xml)
    # Archive files
    print("Creating archive:")
    create_cbz(full_directory)

def main():
    """
    Sets up the parser for creating a comic archive.
    """
    # Set up argument parser
    parser = ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory containing files to archive.",
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
    args = parser.parse_args()
    # Check that directory is valid
    directory = abspath(args.directory)
    if not exists(directory):
        color_print("Invalid directory.", "red")
    else:
        # Create the comic archive
        create_comic_archive(directory,
                rp_description=args.summary,
                rp_date=args.date,
                rp_artists=args.artists,
                rp_publisher=args.publisher,
                rp_url=args.url,
                rp_tags=args.tags)
            
if __name__ == "__main__":
    main()
