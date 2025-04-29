#!/usr/bin/env python3

import os
import re
import shutil
import tempfile
import traceback
import html_string_tools
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive as mm_archive
import metadata_magic.rename as mm_rename
import metadata_magic.archive.comic_xml as mm_comic_xml
from ffmpeg import FFmpeg
from ffmpeg.errors import FFmpegError
from os.path import abspath, basename, exists, join

def create_mkv(directory:str, name:str=None, metadata:dict=None, remove_files:bool=False) -> str:
    """
    Creates an MKV file based on a directory containing a video file and possibly a JSON metadata file.
    Adds proprietary metadata (based on the ComicInfo.xml metadata, not officially supported).

    :param directory: Directory to search for video and metadata within
    :type directory: str, required
    :param name: Name of the MKV video file to create, defaults to None
    :type name: str, optional
    :param metadata: Metadata dict to use when creating the MKV, defaults to None
    :type metadata: dict, optional
    :param remove_files: Whether to delete the original video and metadata files, defaults to False
    :type remove_files: bool, optional
    :return: Full path of the created MKV file, None if creating the file failed
    :rtype: str
    """
    # Find the video file in the given directory
    videos = mm_file_tools.find_files_of_type(abspath(directory), mm_archive.SUPPORTED_VIDEO, False)
    if not len(videos) == 1: return None
    base_video = videos[0]
    # Get the JSON information for the video, if available
    base_filename = base_video[:len(base_video) - len(html_string_tools.get_extension(base_video))]
    json_file = f"{base_filename}.json"
    if not exists(json_file):
        json_file = f"{base_video}.json"
    if not exists(json_file):
        json_file = None
    # Get the filename for the mkv file to create
    mkv_file = mm_rename.get_available_filename(["a.mkv"], basename(base_filename), abspath(directory))
    if name is not None:
        mkv_file = mm_rename.get_available_filename(["a.mkv"], name, abspath(directory))
    mkv_file = abspath(join(directory, f"{mkv_file}.mkv"))
    # Create the VideoInfo.xml file
    with tempfile.TemporaryDirectory() as temp_dir:
        xml_file = abspath(join(temp_dir, "VideoInfo.xml"))
        try:
            xml = mm_comic_xml.get_comic_xml(metadata)
            mm_file_tools.write_text_file(xml_file, xml)
        except (KeyError, TypeError):
            return None
        # Create the main metadata for the mkv file
        try:
            title = re.sub("[\"']", "", metadata["title"])
        except TypeError:
            title = abspath(mkv_file)[:-4]
        metadata = {"metadata":f"title={title}"}
        metadata.update({"attach:s:t:0":xml_file})
        metadata.update({"metadata:s:t:0":"mimetype=text/xml"})
        # Add metadata for the original JSON, if available
        if json_file is not None:
            metadata.update({"attach:s:t:1":json_file})
            metadata.update({"metadata:s:t:1":"mimetype=application/json"})
        # Create MKV file
        try:
            main = FFmpeg().input(base_video).output(mkv_file, map=["0", "-0:t"], **metadata, c="copy")
            main.execute()
        except FFmpegError as error:
            traceback.print_exc()
            return None
    # Return the mkv file
    if exists(mkv_file):
        # Delete old files, if specified
        if remove_files:
            os.remove(base_video)
            if json_file is not None:
                os.remove(json_file)
        return mkv_file
    return None

def get_info_from_mkv(mkv_file:str) -> dict:
    """
    Returns the metadata information for a given .mkv file.
    Unlike other archives, this returns both the video metadata, and the original paired JSON metadata.
    Video metadata is stored in the "metadata" key, and JSON metadata in the "original" key

    :param mkv_file: MKV file to extract attachments and get metadata from
    :type mkv_file: str, required
    :return: Dictionary containing video metadata and original JSON metadata
    :rtype: dict
    """
    # Create the temporary space to extract metadata
    with tempfile.TemporaryDirectory() as extract_dir:
        attachment_dir = abspath(join(extract_dir, "attachements"))
        os.mkdir(attachment_dir)
        # Extract all attachments from the mkv file
        attachment_num = 0
        while True:
            try:
                num_files = len(os.listdir(attachment_dir))
                extract_file = abspath(join(attachment_dir, f"{attachment_num}"))
                empty_file = abspath(join(extract_dir, f"{attachment_num}.mkv"))
                metadata = {f"dump_attachment:t:{attachment_num}":extract_file}
                main = FFmpeg().input(mkv_file, **metadata).output(empty_file, map=["0", "-0:v", "-0:a"], c="copy")
                main.execute()
                assert not num_files == len(os.listdir(attachment_dir))
                attachment_num += 1
            except (AssertionError, FFmpegError):
                break
        # Find and read the original JSON metadata
        json_metadata = {}
        for filename in os.listdir(attachment_dir):
            full_file = abspath(join(attachment_dir, filename))
            json_metadata = mm_file_tools.read_json_file(full_file)
            if not json_metadata == {}:
                break
        # Find and read the video metadata
        video_metadata = mm_archive.get_empty_metadata()
        for filename in os.listdir(attachment_dir):
            full_file = abspath(join(attachment_dir, filename))
            video_metadata = mm_comic_xml.read_comic_info(full_file)
            if video_metadata["title"] is not None or video_metadata["url"] is not None:
                break
    # Return the metadata
    return {"original":json_metadata, "metadata":video_metadata}

def update_mkv_info(mkv_file, metadata:dict):
    """
    Updates a given MKV file to contain the new given metadata.
    Original JSON metadata will not be affected.

    :param mkv_file: Path to the MKV file to update
    :type mkv_file: str, required
    :param metadata: Metadata dict to use for new metadata
    :type metadata: dict, required
    """
    # Copy the mkv file to a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        base_mkv = abspath(join(temp_dir, "AAA.mkv"))
        shutil.copy(abspath(mkv_file), base_mkv)
        # Recreate the original JSON, if present in the file
        original_metadata = get_info_from_mkv(base_mkv)
        if not original_metadata["original"] == {}:
            json_file = abspath(join(temp_dir, "AAA.json"))
            mm_file_tools.write_json_file(json_file, original_metadata["original"])
        # Create a new MKV file with the given metadata
        new_mkv = create_mkv(abspath(temp_dir), "BBB", metadata)
        # Delete the old mkv and replace with the new one, if available
        if new_mkv is not None:
            os.remove(abspath(mkv_file))
            shutil.move(new_mkv, abspath(mkv_file))

def remove_all_mkv_metadata(mkv_file:str):
    """
    Strips all existing metadata from a given MKV file.

    :param mkv_file: Path to the MKV file to remove metadata from.
    :type mkv_file: str, required
    """
    try:
        assert html_string_tools.get_extension(mkv_file).lower() == ".mkv"
        # Create a temporary directory for creating the MKV with stripped metadata
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create new MKV file with attachments stripped
            new_mkv = abspath(join(temp_dir, "new.mkv"))
            main = FFmpeg().input(abspath(mkv_file)).output(new_mkv, map=["0", "-0:t"], c="copy")
            main.execute()
            # Replace the original MKV if creating the MKV file was successful
            assert exists(new_mkv)
            os.remove(abspath(mkv_file))
            shutil.copy(new_mkv, abspath(mkv_file))
    except (AssertionError, FFmpegError): pass
