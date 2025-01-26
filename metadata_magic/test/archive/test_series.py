#!/usr/bin/env python3

import shutil
import tempfile
import metadata_magic.test as mm_test
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive as mm_archive
import metadata_magic.archive.series as mm_series
from os.path import abspath, basename, join

def test_get_default_labels():
    """
    Tests the get_default_labels function.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test getting the default labels based on sequence information
        series_directory = abspath(join(temp_dir, "series"))
        shutil.copytree(mm_test.ARCHIVE_SERIES_DIRECTORY, series_directory)
        labels = mm_series.get_default_labels(series_directory)
        assert len(labels) == 5
        assert basename(labels[0]["file"]) == "1.cbz"
        assert labels[0]["label"] == "1.0"
        assert basename(labels[1]["file"]) == "10.epub"
        assert labels[1]["label"] == "1.5"
        assert basename(labels[2]["file"]) == "2.cbz"
        assert labels[2]["label"] == "2.0"
        assert basename(labels[3]["file"]) == "00A.cbz"
        assert labels[3]["label"] == "100000.0"
        assert basename(labels[4]["file"]) == "00B.epub"
        assert labels[4]["label"] == "100001.0"
        # Remove All Sequence information
        for file in mm_file_tools.find_files_of_type(temp_dir, mm_archive.ARCHIVE_EXTENSIONS):
            metadata = mm_archive.get_info_from_archive(file)
            metadata["series"] = None
            metadata["series_number"] = None
            metadata["series_total"] = None
            mm_archive.update_archive_info(file, metadata)
        # Test getting the default labels based on filename alone
        labels = mm_series.get_default_labels(series_directory)
        assert len(labels) == 5
        assert basename(labels[0]["file"]) == "00A.cbz"
        assert labels[0]["label"] == "1.0"
        assert basename(labels[1]["file"]) == "00B.epub"
        assert labels[1]["label"] == "2.0"
        assert basename(labels[2]["file"]) == "1.cbz"
        assert labels[2]["label"] == "3.0"
        assert basename(labels[3]["file"]) == "2.cbz"
        assert labels[3]["label"] == "4.0"
        assert basename(labels[4]["file"]) == "10.epub"
        assert labels[4]["label"] == "5.0"

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
    # Test writing series information
    with tempfile.TemporaryDirectory() as temp_dir:
        series_directory = abspath(join(temp_dir, "series"))
        shutil.copytree(mm_test.ARCHIVE_SERIES_DIRECTORY, series_directory)
        labels = mm_series.get_default_labels(series_directory)
        labels[0]["label"] = "0.0"
        labels[1]["label"] = "0.5"
        labels[2]["label"] = "1.0"
        labels[3]["label"] = "1.25"
        labels[4]["label"] = "2.0"
        mm_series.write_series(labels, "Series Test")
        metadata = mm_archive.get_info_from_archive(abspath(join(series_directory, "1.cbz")))
        assert metadata["title"] == "CBZ A"
        assert metadata["series"] == "Series Test"
        assert metadata["series_number"] == "0.0"
        assert metadata["series_total"] == "2"
        metadata = mm_archive.get_info_from_archive(abspath(join(series_directory, "10.epub")))
        assert metadata["title"] == "EPUB A"
        assert metadata["series"] == "Series Test"
        assert metadata["series_number"] == "0.5"
        assert metadata["series_total"] is None
        metadata = mm_archive.get_info_from_archive(abspath(join(series_directory, "2.cbz")))
        assert metadata["title"] == "CBZ B"
        assert metadata["series"] == "Series Test"
        assert metadata["series_number"] == "1.0"
        assert metadata["series_total"] == "2"
        metadata = mm_archive.get_info_from_archive(abspath(join(series_directory, "00A.cbz")))
        assert metadata["title"] == "CBZ C"
        assert metadata["series"] == "Series Test"
        assert metadata["series_number"] == "1.25"
        assert metadata["series_total"] == "2"
        metadata = mm_archive.get_info_from_archive(abspath(join(series_directory, "00B.epub")))
        assert metadata["title"] == "EPUB B"
        assert metadata["series"] == "Series Test"
        assert metadata["series_number"] == "2.0"
        assert metadata["series_total"] is None

def test_write_series_single():
    """
    Tests the write_series_single function.
    """
    # Test setting a CBZ file as a single archive
    base_file = abspath(join(mm_test.ARCHIVE_SERIES_DIRECTORY, "00A.cbz"))
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_file = abspath(join(temp_dir, "00A.cbz"))
        shutil.copy(base_file, cbz_file)
        mm_series.write_series_single(cbz_file)
        metadata = mm_archive.get_info_from_archive(cbz_file)
        assert metadata["title"] == "CBZ C"
        assert metadata["series"] == "CBZ C"
        assert metadata["series_number"] == "1.0"
        assert metadata["series_total"] == "1"
    # Test setting an EPUB file as a single archive
    base_file = abspath(join(mm_test.ARCHIVE_SERIES_DIRECTORY, "00B.epub"))
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_file = abspath(join(temp_dir, "00B.epub"))
        shutil.copy(base_file, epub_file)
        mm_series.write_series_single(epub_file)
        metadata = mm_archive.get_info_from_archive(epub_file)
        assert metadata["title"] == "EPUB B"
        assert metadata["series"] == "EPUB B"
        assert metadata["series_number"] == "1.0"
        assert metadata["series_total"] is None

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
