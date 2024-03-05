#!/usr/bin/env python3

import os
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.series as mm_series
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.bulk_archive as mm_bulk_archive
from os.path import abspath, basename, join

def test_get_default_labels():
    """
    Tests the get_default_labels function.
    """
    # Create test files
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1 Text.txt")), "Text")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "1 Text.json")), {"title": "Text"})
    mm_file_tools.write_text_file(abspath(join(temp_dir, "A Text.txt")), "Text")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "A Text.json")), {"title": "More Text"})
    mm_file_tools.write_text_file(abspath(join(temp_dir, "10 Image.png")), "Text")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "10 Image.json")), {"title": "Image"})
    mm_file_tools.write_text_file(abspath(join(temp_dir, "B Image.png")), "Text")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "B Image.json")), {"title": "B Image"})
    mm_file_tools.write_text_file(abspath(join(temp_dir, "unimportant.txt")), "Text")
    sub_dir = abspath(join(temp_dir, "sub"))
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(abspath(join(sub_dir, "deep.cbz")), "Text")
    mm_bulk_archive.archive_all_media(temp_dir)
    assert sorted(os.listdir(temp_dir)) == ["1 Text.epub", "10 Image.cbz",
            "A Text.epub", "B Image.cbz", "sub", "unimportant.txt"]
    assert sorted(os.listdir(sub_dir)) == ["deep.cbz"]
    # Test getting default labels with no sequence information
    files = mm_series.get_default_labels(temp_dir)
    assert len(files) == 4
    assert basename(files[0]["file"]) == "1 Text.epub"
    assert files[0]["label"] == "1.0"
    assert basename(files[1]["file"]) == "10 Image.cbz"
    assert files[1]["label"] == "2.0"
    assert basename(files[2]["file"]) == "A Text.epub"
    assert files[2]["label"] == "3.0"
    assert basename(files[3]["file"]) == "B Image.cbz"
    assert files[3]["label"] == "4.0"
    # Test getting default labels with existing sequence information
    metadata = mm_archive.get_empty_metadata()
    metadata["cover_id"] = None
    metadata["series"] = "Thing"
    metadata["series_number"] = "1.0"
    mm_archive.update_archive_info(abspath(join(temp_dir, "A Text.epub")), metadata)
    metadata["series_number"] = "1.25"
    mm_archive.update_archive_info(abspath(join(temp_dir, "1 Text.epub")), metadata)
    metadata["series_number"] = "2.456"
    mm_archive.update_archive_info(abspath(join(temp_dir, "B Image.cbz")), metadata)
    files = mm_series.get_default_labels(temp_dir)
    assert len(files) == 4
    assert basename(files[0]["file"]) == "A Text.epub"
    assert files[0]["label"] == "1.0"
    assert basename(files[1]["file"]) == "1 Text.epub"
    assert files[1]["label"] == "1.25"
    assert basename(files[2]["file"]) == "B Image.cbz"
    assert files[2]["label"] == "2.456"
    assert basename(files[3]["file"]) == "10 Image.cbz"
    assert files[3]["label"] == "100000.0"

def test_label_files():
    """
    Tests the label_files function.
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
    files = mm_series.label_files(files, 0, "1.000")
    assert files[0]["file"] == "/non/doesn't.txt"
    assert files[1]["file"] == "/non/matter.txt"
    assert files[2]["file"] == "/non/at.txt"
    assert files[3]["file"] == "/non/all.txt"
    assert files[0]["label"] == "1.0"
    assert files[1]["label"] == "2.0"
    assert files[2]["label"] == "3.0"
    assert files[3]["label"] == "4.0"
    # Test adding integer label
    files = mm_series.label_files(files, 0, "30")
    assert files[0]["label"] == "30.0"
    assert files[1]["label"] == "31.0"
    assert files[2]["label"] == "32.0"
    assert files[3]["label"] == "33.0"
    files = mm_series.label_files(files, 2, "0092.0")
    assert files[0]["label"] == "30.0"
    assert files[1]["label"] == "31.0"
    assert files[2]["label"] == "92.0"
    assert files[3]["label"] == "93.0"
    # Test adding decimal label
    files = mm_series.label_files(files, 1, "50.25")
    assert files[0]["label"] == "30.0"
    assert files[1]["label"] == "50.25"
    assert files[2]["label"] == "51.0"
    assert files[3]["label"] == "52.0"
    files = mm_series.label_files(files, 3, "61.5")
    assert files[0]["label"] == "30.0"
    assert files[1]["label"] == "50.25"
    assert files[2]["label"] == "51.0"
    assert files[3]["label"] == "61.5"
    # Test labelling list with invalid index
    files = mm_series.label_files(files, -54, "8.0")
    assert files[0]["label"] == "30.0"
    assert files[1]["label"] == "50.25"
    assert files[2]["label"] == "51.0"
    assert files[3]["label"] == "61.5"
    files = mm_series.label_files(files, 4, "8.0")
    assert files[0]["label"] == "30.0"
    assert files[1]["label"] == "50.25"
    assert files[2]["label"] == "51.0"
    assert files[3]["label"] == "61.5"
    files = mm_series.label_files(files, 34, "8.0")
    assert files[0]["label"] == "30.0"
    assert files[1]["label"] == "50.25"
    assert files[2]["label"] == "51.0"
    assert files[3]["label"] == "61.5"
    # Test labelling list with invalid label
    files = mm_series.label_files(files, 2, "not a number")
    assert files[0]["label"] == "30.0"
    assert files[1]["label"] == "50.25"
    assert files[2]["label"] == "51.0"
    assert files[3]["label"] == "61.5"
    # Test that all file paths are still accurate
    assert files[0]["file"] == "/non/doesn't.txt"
    assert files[1]["file"] == "/non/matter.txt"
    assert files[2]["file"] == "/non/at.txt"
    assert files[3]["file"] == "/non/all.txt"

def test_write_series():
    """
    Tests the write_series function.
    """
    # Create test files
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "Book.txt")), "Text")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "Book.json")), {"title": "Book", "writer":"Name"})
    mm_file_tools.write_text_file(abspath(join(temp_dir, "Comic.jpg")), "Text")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "Comic.json")), {"title": "Comic", "writer":"Person"})
    mm_file_tools.write_text_file(abspath(join(temp_dir, "Other.png")), "Text")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "Other.json")), {"title": "Other", "artist":"Blah"})
    mm_bulk_archive.archive_all_media(temp_dir)
    assert sorted(os.listdir(temp_dir)) == ["Book.epub", "Comic.cbz", "Other.cbz"]
    book_file = abspath(join(temp_dir, "Book.epub"))
    comic_file = abspath(join(temp_dir, "Comic.cbz"))
    other_file = abspath(join(temp_dir, "Other.cbz"))
    # Test writing series info
    labeled_files = []
    labeled_files.append({"file":comic_file, "label":"1.0"})
    labeled_files.append({"file":book_file, "label":"1.5"})
    labeled_files.append({"file":other_file, "label":"2.0"})
    mm_series.write_series(labeled_files, "It's a Series!")
    metadata = mm_archive.get_info_from_archive(book_file)
    assert metadata["series"] == "It's a Series!"
    assert metadata["series_number"] == "1.5"
    assert metadata["series_total"] is None
    assert metadata["title"] == "Book"
    assert metadata["writers"] == "Name"
    metadata = mm_archive.get_info_from_archive(comic_file)
    assert metadata["series"] == "It's a Series!"
    assert metadata["series_number"] == "1.0"
    assert metadata["series_total"] == "2"
    assert metadata["title"] == "Comic"
    assert metadata["writers"] == "Person"
    metadata = mm_archive.get_info_from_archive(other_file)
    assert metadata["series"] == "It's a Series!"
    assert metadata["series_number"] == "2.0"
    assert metadata["series_total"] == "2"
    assert metadata["title"] == "Other"
    assert metadata["artists"] == "Blah"

def test_write_series_single():
    """
    Tests the write_series_single function.
    """
    # Create test files
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "Book.txt")), "Text")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "Book.json")), {"title": "Book", "writer":"Name"})
    mm_file_tools.write_text_file(abspath(join(temp_dir, "Comic.jpg")), "Text")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "Comic.json")), {"title": "Comic", "writer":"Person"})
    mm_bulk_archive.archive_all_media(temp_dir)
    assert sorted(os.listdir(temp_dir)) == ["Book.epub", "Comic.cbz"]
    book_file = abspath(join(temp_dir, "Book.epub"))
    comic_file = abspath(join(temp_dir, "Comic.cbz"))
    # Test setting the series info for epub
    mm_series.write_series_single(book_file)
    metadata = mm_archive.get_info_from_archive(book_file)
    assert metadata["series"] == "Book"
    assert metadata["series_number"] == "1.0"
    assert metadata["series_total"] is None
    assert metadata["title"] == "Book"
    assert metadata["writers"] == "Name"
    # Test setting the series info for cbz
    mm_series.write_series_single(comic_file)
    metadata = mm_archive.get_info_from_archive(comic_file)
    assert metadata["series"] == "Comic"
    assert metadata["series_number"] == "1.0"
    assert metadata["series_total"] == "1"
    assert metadata["title"] == "Comic"
    assert metadata["writers"] == "Person"

def test_get_series_string():
    """
    Tests the get_series_string function.
    """
    # Test with standard files and labels
    labeled_files = []
    labeled_files.append({"file":"/test_file.cbz", "label":"1.0"})
    labeled_files.append({"file":"/something.cbz", "label":"2.0"})
    labeled_files.append({"file":"/else.epub", "label":"2.5"})
    labeled_files.append({"file":"/another.cbz", "label":"3.0"})
    series_string = mm_series.get_series_string(labeled_files)
    compare = ""
    compare = f"{compare}ENTRY    FILE         \n"
    compare = f"{compare}----------------------\n"
    compare = f"{compare}1.0      test_file.cbz\n"
    compare = f"{compare}2.0      something.cbz\n"
    compare = f"{compare}2.5      else.epub    \n"
    compare = f"{compare}3.0      another.cbz  "
    assert series_string == compare
    # Test with long labels
    labeled_files = []
    labeled_files.append({"file":"/a_long_file_name.cbz", "label":"1000000.0"})
    labeled_files.append({"file":"/something_else.epub", "label":"1000001.0"})
    labeled_files.append({"file":"/a.cbz", "label":"1000002.0"})
    labeled_files.append({"file":"/Name.epub", "label":"1000003.0"})
    labeled_files.append({"file":"/Final File.epub", "label":"1000004.5"})
    series_string = mm_series.get_series_string(labeled_files)
    compare = ""
    compare = f"{compare}ENTRY        FILE                \n"
    compare = f"{compare}---------------------------------\n"
    compare = f"{compare}1000000.0    a_long_file_name.cbz\n"
    compare = f"{compare}1000001.0    something_else.epub \n"
    compare = f"{compare}1000002.0    a.cbz               \n"
    compare = f"{compare}1000003.0    Name.epub           \n"
    compare = f"{compare}1000004.5    Final File.epub     "
    assert series_string == compare