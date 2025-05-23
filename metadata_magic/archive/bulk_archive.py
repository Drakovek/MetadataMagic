#!/usr/bin/env python3

import os
import re
import tqdm
import shutil
import argparse
import tempfile
import traceback
import html_string_tools
import python_print_tools
import metadata_magic.config as mm_config
import metadata_magic.error as mm_error
import metadata_magic.rename as mm_rename
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.meta_finder as mm_meta_finder
import metadata_magic.archive as mm_archive
import metadata_magic.archive.epub as mm_epub
import metadata_magic.archive.mkv as mm_mkv
import metadata_magic.archive.comic_archive as mm_comic_archive
from os.path import abspath, basename, exists, isdir, join

def archive_all_media(directory:str, config:dict,
            format_title:bool=False, description_length:int=1000) -> bool:
    """
    Takes all supported JSON-media pairs and archives them into their appropriate media archives.
    Text files are archived into EPUB files.
    Image files are archived into CBZ files.
    
    :param directory: Directory in which to search for JSON-media pairs and archive files
    :type directory: str, required
    :param config: Dictionary of a metadata-magic config file
    :type config: dict, required
    :param format_title: Whether to format media titles before archiving, defaults to False
    :type format_title: bool, optional
    :param description_length: Length that a description can be before being used as an ebook, defaults to 1000
    :type description_length: int, optional
    :return: Whether archiving files was successful
    :rtype: bool
    """
    # Get all JSON-media pairs in the directory
    full_directory = abspath(directory)
    pairs = mm_meta_finder.get_pairs(full_directory, print_info=False)
    # Run through each pair
    media_extensions = []
    media_extensions.extend(mm_archive.SUPPORTED_IMAGES)
    media_extensions.extend(mm_archive.SUPPORTED_TEXT)
    for pair in tqdm.tqdm(pairs):
        try:
            # Ignore if the extension is not supported
            extension = html_string_tools.get_extension(pair["media"]).lower()
            if extension not in media_extensions:
                continue
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy JSON and media into temp directory
                new_json = abspath(join(temp_dir, basename(pair["json"])))
                new_media = abspath(join(temp_dir, basename(pair["media"])))
                shutil.copy(pair["json"], new_json)
                shutil.copy(pair["media"], new_media)
                # Get metadata from the JSON
                metadata = mm_archive.get_info_from_jsons(temp_dir, config)
                # Format the title if specified
                if format_title:
                    metadata["title"] = mm_archive.format_title(metadata["title"])
                # Rename files to fit the title
                title = mm_rename.get_file_friendly_text(metadata["title"], ascii_only=True)
                mm_rename.rename_file(new_json, title)
                mm_rename.rename_file(new_media, title)
                # Create the archive file
                archive_file = None
                if extension in mm_archive.SUPPORTED_IMAGES:
                    # Create an epub if the description is too long
                    if metadata["description"] is None or len(metadata["description"]) < description_length:
                        archive_file = mm_comic_archive.create_cbz(temp_dir, name=title, metadata=metadata)
                    else:
                        new_pair = mm_meta_finder.get_pairs(temp_dir, print_info=False)[0]
                        new_media = new_pair["media"]
                        new_json = new_pair["json"]
                        archive_file = mm_epub.create_epub_from_description(new_json, new_media, metadata, temp_dir, config)
                elif extension in mm_archive.SUPPORTED_TEXT:
                    with tempfile.TemporaryDirectory() as image_dir:
                        chapters = mm_epub.get_default_chapters(temp_dir, title=title)
                        chapters = mm_epub.add_cover_to_chapters(chapters, metadata, image_dir)
                        archive_file = mm_epub.create_epub(chapters, metadata, temp_dir)
                assert exists(archive_file)
                # Copy archive to the original directory
                parent = abspath(join(pair["json"], os.pardir))
                filename = basename(pair["json"])
                filename = filename[:len(filename) - 5]
                filename = mm_rename.get_available_filename([archive_file], filename, parent)
                extension = html_string_tools.get_extension(archive_file).lower()
                new_archive = join(parent, f"{filename}{extension}")
                shutil.copy(archive_file, new_archive)
                assert exists(new_archive)
                # Delete the original files
                os.remove(pair["json"])
                os.remove(pair["media"])
        except:
            # Archiving failed
            traceback.print_exc()
            python_print_tools.color_print(f"Failed Archiving \"{pair['media']}\"", "red")
            return False
    return True

def extract_cbz(cbz_file:str, output_directory:str,
            create_folder:bool=True, remove_structure:bool=False) -> bool:
    """
    Extracts the contents of a CBZ file into a given directory.
    
    :param cbz_file: Path to CBZ file to extract
    :type cbz_file: str, required
    :param output_directory: Directory to extract CBZ file to
    :type output_directory: str, required
    :param create_folder: Whether to create a subfolder to contain the contents of this CBZ, defaults to True
    :type create_folder: bool, optional
    :param remove_structure: Whether to remove the CBZ structure and metadata leaving only images, defaults to False
    :type remove_structure: bool, optional
    :return: Whether extracting files was successful
    :rtype: bool
    """
    remove_list = []
    if remove_structure:
        remove_list = ["ComicInfo.xml", "comicinfo.xml"]
    full_directory = abspath(output_directory)
    return mm_file_tools.extract_zip(cbz_file, full_directory, create_folder=create_folder,
            remove_internal=remove_structure, delete_files=remove_list)

def extract_epub(epub_file:str, output_directory:str,
            create_folder:bool=True, remove_structure:bool=False) -> bool:
    """
    Extracts the contents of a EPUB file into a given directory.
    
    :param epub_file: Path to EPUB file to extract
    :type epub_file: str, required
    :param output_directory: Directory to extract EPUB file to
    :type output_directory: str, required
    :param create_folder: Whether to create a subfolder to contain the contents of this CBZ, defaults to True
    :type create_folder: bool, optional
    :param remove_structure: Whether to remove the EPUB structure and metadata leaving only original files, defaults to False
    :type remove_structure: bool, optional
    :return: Whether extracting files was successful
    :rtype: bool
    """
    # Extract with structure intact if specified
    full_directory = abspath(output_directory)
    if not remove_structure:
        return mm_file_tools.extract_zip(epub_file, full_directory, create_folder=create_folder)
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract epub to temp folder
        mm_file_tools.extract_zip(epub_file, temp_dir)
        # Get the folder containing the original files
        original_dir = abspath(join(temp_dir, "EPUB"))
        original_dir = abspath(join(original_dir, "original"))
        if not exists(original_dir):
            return False
        # Create directory to copy files into, if specified
        copy_dir = full_directory
        if create_folder:
            folder_name = re.sub(r"\..{1,6}$", "", basename(epub_file))
            folder_name = mm_rename.get_available_filename(["AAAAAAAA"], folder_name, full_directory)
            copy_dir = abspath(join(full_directory, folder_name))
            os.mkdir(copy_dir)
        # Copy files from epub
        for original_file in sorted(os.listdir(original_dir)):
            full_file = abspath(join(original_dir, original_file))
            filename = re.sub(r"\..{1,6}$", "", original_file)
            filename = mm_rename.get_available_filename([original_file], filename, copy_dir)
            filename = filename + html_string_tools.get_extension(full_file)
            new_file = abspath(join(copy_dir, filename))
            if isdir(full_file):
                shutil.copytree(full_file, new_file)
            else:
                shutil.copy(full_file, new_file)
            assert exists(new_file)
    return True

def extract_mkv(mkv_file:str, output_directory:str) -> bool:
    """
    Extracts the contents of an mkv file to a given directory.
    Really just extracts the original JSON metadata, if embedded in the file.

    :param mkv_file: Path to MKV file to extract
    :type mkv_file: str, required
    :param output_directory: Directory to extract MKV file to
    :type output_directory: str, required
    :return: Whether extracting files was successful
    :rtype: bool
    """
    metadata = mm_mkv.get_info_from_mkv(mkv_file)
    # Create JSON metadata file, if appropriate
    if not metadata["original"] == {}:
        filename = basename(mkv_file)[:-4]
        filename = mm_rename.get_available_filename(["AAA.json"], filename, abspath(output_directory))
        json_file = abspath(join(output_directory, f"{filename}.json"))
        mm_file_tools.write_json_file(json_file, metadata["original"])
        # Remove existing metadata from the mkv file
        mm_mkv.remove_all_mkv_metadata(mkv_file)
    return True

def extract_all_archives(directory:str, create_folders:bool=True, remove_structure:bool=False) -> bool:
    """
    Extracts the contents of all media archive files in the given directory.
    Supports .epub and .cbz files.
    
    :param directory: Directory to containing archives and to extract archive contents into
    :type directory: str
    :param create_folders: Whether to create subfolders to contain the contents of each archive, defaults to True
    :type create_folders: bool, optional
    :param remove_structure: Whether to remove the archive structure and metadata leaving only original files, defaults to False
    :type remove_structure: bool, optional
    :return: Whether extracting files was successful
    :rtype: bool
    """
    # Get a list of all archive files
    archives = mm_file_tools.find_files_of_type(directory, mm_archive.ARCHIVE_EXTENSIONS)
    # Extract each archive
    for archive in tqdm.tqdm(archives):
        try:
            # Extract archives
            remove_archive = True
            parent_dir = abspath(join(archive, os.pardir))
            extension = html_string_tools.get_extension(archive).lower()
            if extension == ".cbz":
                assert extract_cbz(archive, parent_dir, create_folder=create_folders,
                        remove_structure=remove_structure)
            elif extension == ".epub":
                assert extract_epub(archive, parent_dir, create_folder=create_folders,
                        remove_structure=remove_structure)
            elif extension == ".mkv":
                remove_archive = False
                assert extract_mkv(archive, parent_dir)
            else:
                assert False
        except AssertionError:
            # Extracting archive failed
            python_print_tools.color_print(f"Failed Extracting \"{archive}\"", "red")
            return False
        # Remove the existing archive
        if remove_archive:
            os.remove(archive)
    return True

def main():
    """
    Sets up the parser for the user bulk archive or extract media.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory containing media files.",
            nargs="?",
            type=str,
            default=str(os.getcwd()))
    parser.add_argument(
            "-d",
            "--description-length",
            help="Length at which descriptions will be used as ebook text.",
            nargs="?",
            type=int,
            default=mm_error.LONG_DESCRIPTION)
    parser.add_argument(
            "-e",
            "--extract",
            help="Extract existing media archive files",
            action="store_true")
    parser.add_argument(
            "-f",
            "--format-titles",
            help="Formats titles when archiving media",
            action="store_true")
    args = parser.parse_args()
    # Check that directory is valid
    directory = abspath(args.directory)
    if not exists(directory):
        python_print_tools.color_print("Invalid directory.", "red")
    else:
        if args.extract:
            if input("Remove archive structure? (Y/[N]): ").lower() == "y":
                if input("Directory structure and metadata will be deleted. Are you sure? (Y/[N]): ").lower() == "y":
                    print("Extracting media archives...")
                    extract_all_archives(directory, create_folders=False, remove_structure=True)
            else:
                print("Extracting media archives...")
                extract_all_archives(directory, create_folders=True, remove_structure=False)
        else:
            print("Archiving media files...")
            config_paths = mm_config.get_default_config_paths()
            config = mm_config.get_config(config_paths)
            archive_all_media(directory, config, args.format_titles, args.description_length)
