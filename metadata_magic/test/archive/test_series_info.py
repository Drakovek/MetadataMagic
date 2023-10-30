#!/usr/bin/env python3

import os
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.series_info as mm_series_info
import metadata_magic.archive.comic_archive as mm_comic_archive
from os.path import abspath, exists, join

def test_label_files_with_numbers():
    """
    Tests the label_files_with_numbers function.
    """
    # Create a list for testing
    files = []
    files.append({"label":"blah", "file":"/non/doesn't.txt"})
    files.append({"label":"blah", "file":"/non/matter.txt"})
    files.append({"label":"blah", "file":"/non/at.txt"})
    files.append({"label":"blah", "file":"/non/all.txt"})
    assert len(files) == 4
    assert files[0]["file"] == "/non/doesn't.txt"
    assert files[1]["file"] == "/non/matter.txt"
    assert files[2]["file"] == "/non/at.txt"
    assert files[3]["file"] == "/non/all.txt"
    # Test initializing list
    files = mm_series_info.label_files_with_numbers(files, 0, "1.0")
    assert files[0]["file"] == "/non/doesn't.txt"
    assert files[1]["file"] == "/non/matter.txt"
    assert files[2]["file"] == "/non/at.txt"
    assert files[3]["file"] == "/non/all.txt"
    assert files[0]["label"] == "1.0"
    assert files[1]["label"] == "2.0"
    assert files[2]["label"] == "3.0"
    assert files[3]["label"] == "4.0"
    # Test adding integer label
    files = mm_series_info.label_files_with_numbers(files, 0, "3.0")
    assert files[0]["label"] == "3.0"
    assert files[1]["label"] == "4.0"
    assert files[2]["label"] == "5.0"
    assert files[3]["label"] == "6.0"
    files = mm_series_info.label_files_with_numbers(files, 2, "9.0")
    assert files[0]["label"] == "3.0"
    assert files[1]["label"] == "4.0"
    assert files[2]["label"] == "9.0"
    assert files[3]["label"] == "10.0"
    # Test adding decimal label
    files = mm_series_info.label_files_with_numbers(files, 1, "5.25")
    assert files[0]["label"] == "3.0"
    assert files[1]["label"] == "5.25"
    assert files[2]["label"] == "6.0"
    assert files[3]["label"] == "7.0"
    files = mm_series_info.label_files_with_numbers(files, 3, "6.5")
    assert files[0]["label"] == "3.0"
    assert files[1]["label"] == "5.25"
    assert files[2]["label"] == "6.0"
    assert files[3]["label"] == "6.5"
    # Test labelling list with invalid index
    files = mm_series_info.label_files_with_numbers(files, -54, "8.0")
    assert files[0]["label"] == "3.0"
    assert files[1]["label"] == "5.25"
    assert files[2]["label"] == "6.0"
    assert files[3]["label"] == "6.5"
    files = mm_series_info.label_files_with_numbers(files, 4, "8.0")
    assert files[0]["label"] == "3.0"
    assert files[1]["label"] == "5.25"
    assert files[2]["label"] == "6.0"
    assert files[3]["label"] == "6.5"
    files = mm_series_info.label_files_with_numbers(files, 34, "8.0")
    assert files[0]["label"] == "3.0"
    assert files[1]["label"] == "5.25"
    assert files[2]["label"] == "6.0"
    assert files[3]["label"] == "6.5"
    # Test labelling list with invalid label
    files = mm_series_info.label_files_with_numbers(files, 2, "not a number")
    assert files[0]["label"] == "3.0"
    assert files[1]["label"] == "5.25"
    assert files[2]["label"] == "6.0"
    assert files[3]["label"] == "6.5"
    # Test that all file paths are still accurate
    assert files[0]["file"] == "/non/doesn't.txt"
    assert files[1]["file"] == "/non/matter.txt"
    assert files[2]["file"] == "/non/at.txt"
    assert files[3]["file"] == "/non/all.txt"

def test_write_series_info():
    """
    Tests the write_series_info function.
    """
    # Create test cbz file
    temp_dir = mm_file_tools.get_temp_dir()
    cbz_sub = abspath(join(temp_dir, "cbz_sub"))
    os.mkdir(cbz_sub)
    text_file = abspath(join(cbz_sub, "text.txt"))
    mm_file_tools.write_text_file(text_file, "This is text")
    assert exists(text_file)
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "This is CBZ"
    metadata["description"] = "Some words."
    cbz_file = mm_comic_archive.create_cbz(cbz_sub, metadata=metadata)
    assert exists(cbz_file)
    # Create second cbz file
    next_sub = abspath(join(temp_dir, "other_sub"))
    os.mkdir(next_sub)
    media_file = abspath(join(next_sub, "thing.png"))
    mm_file_tools.write_text_file(media_file, "Still text.")
    assert exists(media_file)
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "This is now also CBZ"
    metadata["description"] = "Other words."
    next_file = mm_comic_archive.create_cbz(next_sub, metadata=metadata)
    assert exists(next_file)
    # Test that existing metadata is intact
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "This is CBZ"
    assert read_meta["description"] == "Some words."
    assert read_meta["series"] is None
    assert read_meta["series_number"] is None
    read_meta = mm_comic_archive.get_info_from_cbz(next_file)
    assert read_meta["title"] == "This is now also CBZ"
    assert read_meta["description"] == "Other words."
    assert read_meta["series"] is None
    assert read_meta["series_number"] is None
    # Test writing series info
    files = [{"file":cbz_file, "label":"1.0"}]
    files.append({"file":next_file, "label":"5.3"})
    mm_series_info.write_series_info(files, "Name of Series!")
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "This is CBZ"
    assert read_meta["description"] == "Some words."
    assert read_meta["series"] == "Name of Series!"
    assert read_meta["series_number"] == "1.0"
    assert read_meta["series_total"] == "2"
    read_meta = mm_comic_archive.get_info_from_cbz(next_file)
    assert read_meta["title"] == "This is now also CBZ"
    assert read_meta["description"] == "Other words."
    assert read_meta["series"] == "Name of Series!"
    assert read_meta["series_number"] == "5.3"
    assert read_meta["series_total"] == "2"

def test_list_file_labels():
    """
    Tests the list_file_labels function.
    """
    # Test getting file labels
    files = []
    files.append({"label":"1.0", "file":"/non/Here.txt"})
    files.append({"label":"2.8", "file":"/non/Are.cbz"})
    files.append({"label":"39.5", "file":"/non/Some.cb7"})
    files.append({"label":"40.0", "file":"/non/Things.cbz"})
    labels = mm_series_info.list_file_labels(files)
    assert labels == "1.0) Here.txt\n2.8) Are.cbz\n39.5) Some.cb7\n40.0) Things.cbz"
