#!/usr/bin/env python3

from os import listdir, mkdir
from os.path import abspath, basename, exists, isdir, join
from metadata_magic.main.comic_archive.comic_archive import create_cb7
from metadata_magic.main.comic_archive.comic_archive import create_cbz
from metadata_magic.main.comic_archive.comic_archive import get_info_from_archive
from metadata_magic.main.comic_archive.comic_archive import get_temp_dir
from metadata_magic.main.comic_archive.comic_xml import get_comic_xml
from metadata_magic.main.comic_archive.comic_xml import get_empty_metadata
from metadata_magic.main.comic_archive.series_info import get_comic_archives
from metadata_magic.main.comic_archive.series_info import label_files_with_numbers
from metadata_magic.main.comic_archive.series_info import list_file_labels
from metadata_magic.main.comic_archive.series_info import write_series_info
from metadata_magic.test.temp_file_tools import create_text_file

def test_get_comic_archives():
    """
    Tests the get_comic_archives function.
    """
    temp_dir = get_temp_dir()
    create_text_file(abspath(join(temp_dir, "aaa.cbz")), "Blah")
    create_text_file(abspath(join(temp_dir, "not-comic.txt")), "Not")
    create_text_file(abspath(join(temp_dir, "Book.cb7")), "Really")
    create_text_file(abspath(join(temp_dir, "Text.cbz")), "Important")
    create_text_file(abspath(join(temp_dir, "Other.cbz")), "At All")
    mkdir(abspath(join(temp_dir, "sub")))
    assert len(listdir(temp_dir)) == 6
    archives = get_comic_archives(temp_dir)
    print(archives)
    assert len(archives) == 4
    assert basename(archives[0]) == "aaa.cbz"
    assert basename(archives[1]) == "Book.cb7"
    assert basename(archives[2]) == "Other.cbz"
    assert basename(archives[3]) == "Text.cbz"

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
    files = label_files_with_numbers(files, 0, "1.0")
    assert files[0]["file"] == "/non/doesn't.txt"
    assert files[1]["file"] == "/non/matter.txt"
    assert files[2]["file"] == "/non/at.txt"
    assert files[3]["file"] == "/non/all.txt"
    assert files[0]["label"] == "1.0"
    assert files[1]["label"] == "2.0"
    assert files[2]["label"] == "3.0"
    assert files[3]["label"] == "4.0"
    # Test adding integer label
    files = label_files_with_numbers(files, 0, "3.0")
    assert files[0]["label"] == "3.0"
    assert files[1]["label"] == "4.0"
    assert files[2]["label"] == "5.0"
    assert files[3]["label"] == "6.0"
    files = label_files_with_numbers(files, 2, "9.0")
    assert files[0]["label"] == "3.0"
    assert files[1]["label"] == "4.0"
    assert files[2]["label"] == "9.0"
    assert files[3]["label"] == "10.0"
    # Test adding decimal label
    files = label_files_with_numbers(files, 1, "5.25")
    assert files[0]["label"] == "3.0"
    assert files[1]["label"] == "5.25"
    assert files[2]["label"] == "6.0"
    assert files[3]["label"] == "7.0"
    files = label_files_with_numbers(files, 3, "6.5")
    assert files[0]["label"] == "3.0"
    assert files[1]["label"] == "5.25"
    assert files[2]["label"] == "6.0"
    assert files[3]["label"] == "6.5"
    # Test labelling list with invalid index
    files = label_files_with_numbers(files, -54, "8.0")
    assert files[0]["label"] == "3.0"
    assert files[1]["label"] == "5.25"
    assert files[2]["label"] == "6.0"
    assert files[3]["label"] == "6.5"
    files = label_files_with_numbers(files, 4, "8.0")
    assert files[0]["label"] == "3.0"
    assert files[1]["label"] == "5.25"
    assert files[2]["label"] == "6.0"
    assert files[3]["label"] == "6.5"
    files = label_files_with_numbers(files, 34, "8.0")
    assert files[0]["label"] == "3.0"
    assert files[1]["label"] == "5.25"
    assert files[2]["label"] == "6.0"
    assert files[3]["label"] == "6.5"
    # Test labelling list with invalid label
    files = label_files_with_numbers(files, 2, "not a number")
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
    temp_dir = get_temp_dir()
    cbz_sub = abspath(join(temp_dir, "cbz_sub"))
    mkdir(cbz_sub)
    assert isdir(cbz_sub)
    metadata = get_empty_metadata()
    metadata["title"] = "This is CBZ"
    metadata["description"] = "Some words."
    xml = get_comic_xml(metadata)
    xml_file = abspath(join(cbz_sub, "ComicInfo.xml"))
    create_text_file(xml_file, xml)
    assert exists(xml_file)
    cbz_file = create_cbz(cbz_sub)
    assert exists(cbz_file)
    # Create test cb7 file
    cb7_sub = abspath(join(temp_dir, "cb7_sub"))
    mkdir(cb7_sub)
    assert isdir(cb7_sub)
    metadata = get_empty_metadata()
    metadata["title"] = "This is a 7z cb7 archive"
    metadata["description"] = "Other words."
    xml = get_comic_xml(metadata)
    xml_file = abspath(join(cb7_sub, "ComicInfo.xml"))
    create_text_file(xml_file, xml)
    assert exists(xml_file)
    cb7_file = create_cb7(cb7_sub)
    assert exists(cb7_file)
    # Test that existing metadata is intact
    read_meta = get_info_from_archive(cbz_file)
    assert read_meta["title"] == "This is CBZ"
    assert read_meta["description"] == "Some words."
    assert read_meta["series"] is None
    assert read_meta["series_number"] is None
    read_meta = get_info_from_archive(cb7_file)
    assert read_meta["title"] == "This is a 7z cb7 archive"
    assert read_meta["description"] == "Other words."
    assert read_meta["series"] is None
    assert read_meta["series_number"] is None
    # Test writing series info
    files = [{"file":cbz_file, "label":"1.0"}]
    files.append({"file":cb7_file, "label":"5.3"})
    write_series_info(files, "Name of Series!")
    read_meta = get_info_from_archive(cbz_file)
    assert read_meta["title"] == "This is CBZ"
    assert read_meta["description"] == "Some words."
    assert read_meta["series"] == "Name of Series!"
    assert read_meta["series_number"] == "1.0"
    read_meta = get_info_from_archive(cb7_file)
    assert read_meta["title"] == "This is a 7z cb7 archive"
    assert read_meta["description"] == "Other words."
    assert read_meta["series"] == "Name of Series!"
    assert read_meta["series_number"] == "5.3"

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
    labels = list_file_labels(files)
    assert labels == "1.0) Here.txt\n2.8) Are.cbz\n39.5) Some.cb7\n40.0) Things.cbz"