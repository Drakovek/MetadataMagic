#!/usr/bin/env python3

import os
import re
import shutil
import html_string_tools
import metadata_magic.sort as mm_sort
import metadata_magic.rename as mm_rename
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.comic_xml as mm_comic_xml
from os.path import abspath, basename, exists, isdir, join

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
    if len(os.listdir(full_directory)) == 0:
        return None
    # Create CBZ filename
    filename = mm_rename.get_available_filename(["a.cbz"], basename(full_directory), full_directory)
    if name is not None:
        filename = mm_rename.get_available_filename(["a.cbz"], name, full_directory)
    cbz_file = abspath(join(full_directory, f"{filename}.cbz"))
    # Check if there are existing directories
    move_files = True
    files = mm_sort.sort_alphanum(os.listdir(full_directory))
    for file in files:
        if isdir(abspath(join(full_directory, file))):
            move_files = False
            break
    # Move files if required
    if move_files:
        # Create new folder to contain files
        folder_name = name
        if folder_name is None:
            try:
                folder_name = metadata["title"]
                assert folder_name is not None
            except (AssertionError, KeyError, TypeError):
                folder_name = files[0][:len(files[0]) - len(html_string_tools.html.get_extension(files[0]))]
        folder_name = mm_rename.get_file_friendly_text(folder_name)
        folder_name = mm_rename.get_available_filename(["AAAAAAAAAA"], folder_name, full_directory)
        new_folder = abspath(join(full_directory, folder_name))
        os.mkdir(new_folder)
        # Move existing files to the new folder
        for file in files:
            if not file == "ComicInfo.xml":
                current_file = abspath(join(full_directory, file))
                new_file = abspath(join(new_folder, file))
                shutil.move(current_file, new_file)
    # Create metadata file, if specified
    meta_file = abspath(join(full_directory, "ComicInfo.xml"))
    if metadata is not None:
        mm_file_tools.write_text_file(meta_file, mm_comic_xml.get_comic_xml(metadata))
    # Create cbz file
    assert mm_file_tools.create_zip(full_directory, cbz_file)
    # Remove all old files besides the CBZ, if specified.
    if remove_files:
        files = os.listdir(full_directory)
        for file in files:
            full_file = abspath(join(full_directory, file))
            if isdir(full_file):
                shutil.rmtree(full_file)
            elif not full_file == cbz_file:
                os.remove(full_file)
    # Remove ComicInfo.xml file, if exists
    if exists(meta_file):
        os.remove(meta_file)
    # Return CBZ file
    return cbz_file

def get_info_from_cbz(cbz_file:str, check_subdirectories:bool=True) -> dict:
    """
    Extracts ComicInfo.xml from a given .cbz file and returns the metadata as a dict.
    
    :param cbz_file: Path to a .cbz file
    :type cbz_file: str, required
    :param check_subdirectories: Whether to check subdirectories for metadata file, defaults to True
    :type check_subdirectories: bool, optional
    :return: Dictionary containing metadata from the .cbz file
    :rtype: dict
    """
    # Create temporary directory
    file = abspath(cbz_file)
    extract_dir = mm_file_tools.get_temp_dir("dvk_meta_extract")
    assert exists(extract_dir)
    # Extract ComicInfo.xml from given file
    xml_file = mm_file_tools.extract_file_from_zip(cbz_file, extract_dir, "ComicInfo.xml", check_subdirectories)
    if xml_file is None or not exists(xml_file):
        return mm_archive.get_empty_metadata()
    # Read XML file
    return mm_comic_xml.read_comic_info(xml_file)

def update_cbz_info(cbz_file:str, metadata:dict):
    """
    Replaces the ComicInfo.xml file in a given .cbz file to reflect the given metadata
    
    :param cbz_file: Path of the .cbz file to update
    :type cbz_file: str, required
    :param metadata: Metadata to use for the new ComicInfo.xml file
    :type metadata: dict
    """
    # Extract cbz into temp file
    full_cbz_file = abspath(cbz_file)
    temp_dir = mm_file_tools.get_temp_dir("dvk_comic_info")
    if mm_file_tools.extract_zip(full_cbz_file, temp_dir):
        # Delete existing ComicInfo.xml files
        xml_files = mm_file_tools.find_files_of_type(temp_dir, ".xml")
        for xml_file in xml_files:
            if basename(xml_file) == "ComicInfo.xml":
                os.remove(xml_file)
        # Pack files into archive using new metadata
        new_cbz = create_cbz(temp_dir, name=metadata["title"], metadata=metadata)
        # Replace the old cbz file
        os.remove(full_cbz_file)
        shutil.copy(new_cbz, full_cbz_file)
        os.remove(new_cbz)
