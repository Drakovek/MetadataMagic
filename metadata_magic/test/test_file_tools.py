#!/usr/bin/env python3

import os
import shutil
import tempfile
import metadata_magic.test as mm_test
import metadata_magic.file_tools as mm_file_tools
from os.path import abspath, basename, join

def test_read_text_file():
    """
    Tests the read_text_file function.
    """
    # Test reading a basic unicode text file
    text_directory = abspath(join(mm_test.BASIC_DIRECTORY, "text"))
    text_file = abspath(join(text_directory, "unicode.txt"))
    assert mm_file_tools.read_text_file(text_file) == "This is ünicode."
    # Test reading non-unicode text files
    text_file = abspath(join(text_directory, "latin1.txt"))
    assert mm_file_tools.read_text_file(text_file) == "This is lätin1."
    text_file = abspath(join(text_directory, "cp437.TXT"))
    assert mm_file_tools.read_text_file(text_file) == "This is cp437."
    # Test reading a non-text file
    assert mm_file_tools.read_text_file(mm_test.BASIC_DIRECTORY) is None

def test_write_text_file():
    """
    Tests the write_text_file function.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test writing a basic text file
        text_file = abspath(join(temp_dir, "test.txt"))
        mm_file_tools.write_text_file(text_file, "This is text!")
        assert mm_file_tools.read_text_file(text_file) == "This is text!"
        # Test overwriting a text file
        mm_file_tools.write_text_file(text_file, "New\nText.")
        assert mm_file_tools.read_text_file(text_file) == "New\nText."
        # Test writing to an invalid location
        fake_text_file = abspath(join("/non/existant/dir/", "fake.txt"))
        mm_file_tools.write_text_file(fake_text_file, "Thing")
        assert os.listdir(abspath(temp_dir)) == ["test.txt"]

def test_read_json_file():
    """
    Tests the read_json_file function.
    """
    # Test reading a basic unicode JSON file
    json_directory = abspath(join(mm_test.BASIC_DIRECTORY, "json"))
    json_file = abspath(join(json_directory, "unicode.json"))
    json = mm_file_tools.read_json_file(json_file)
    assert json["name"] == "vãlue"
    assert json["number"] == 25
    assert json["boolean"] == False
    assert json["internal"] == {"key":"another"}
    # Test reading a non-unicode JSON file
    json_file = abspath(join(json_directory, "latin1.JSON"))
    json = mm_file_tools.read_json_file(json_file)
    assert json["new"] == "Títle"
    # Test reading a non-JSON file
    json_file = abspath(join(mm_test.BASIC_DIRECTORY, "unicode.txt"))
    assert mm_file_tools.read_json_file(json_file) == {}
    assert mm_file_tools.read_json_file(mm_test.BASIC_DIRECTORY) == {}

def test_write_json_file():
    """
    Tests the write_json_file function.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test writing a JSON file
        dictionary = {"name":"title", "num":42, "boolean":True}
        json_file = abspath(join(temp_dir, "test.json"))
        mm_file_tools.write_json_file(json_file, dictionary)
        assert mm_file_tools.read_json_file(json_file) == dictionary
        # Test overwriting a JSON file
        mm_file_tools.write_json_file(json_file, {"A":"B"})
        assert mm_file_tools.read_json_file(json_file) == {"A":"B"}
        # Test writing a JSON file to an invalid location
        fake_json_file = abspath(join("/non/existant/dir/", "fake.json"))
        mm_file_tools.write_json_file(fake_json_file, "Thing")
        assert os.listdir(abspath(temp_dir)) == ["test.json"]

def test_extract_zip():
    """
    Tests the extract_zip function.
    """
    # Get file paths
    zip_file = abspath(join(mm_test.BASIC_DIRECTORY, "archive.zip"))
    text_directory = abspath(join(mm_test.BASIC_DIRECTORY, "text"))
    non_zip_file = abspath(join(text_directory, "unicode.txt"))
    # Test extracting a zip file
    with tempfile.TemporaryDirectory() as temp_dir:
        assert mm_file_tools.extract_zip(zip_file, temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["DELETE.txt", "Internal", "metadata.json"]
        internal_dir = abspath(join(temp_dir, "Internal"))
        assert sorted(os.listdir(internal_dir)) == ["Text1.txt", "Text2.txt"]
        text_file = abspath(join(temp_dir, "DELETE.txt"))
        assert mm_file_tools.read_text_file(text_file) == "Delete Me!"
    # Test extracting a zip file with an added container directory
    with tempfile.TemporaryDirectory() as temp_dir:
        assert mm_file_tools.extract_zip(zip_file, temp_dir, create_folder=True)
        assert os.listdir(temp_dir) == ["archive"]
        archive_dir = abspath(join(temp_dir, "archive"))
        assert sorted(os.listdir(archive_dir)) == ["DELETE.txt", "Internal", "metadata.json"]
        internal_dir = abspath(join(archive_dir, "Internal"))
        assert sorted(os.listdir(internal_dir)) == ["Text1.txt", "Text2.txt"]
        text_file = abspath(join(internal_dir, "Text1.txt"))
        assert mm_file_tools.read_text_file(text_file) == "This is text!"
    # Test is the container directory already exists
    with tempfile.TemporaryDirectory() as temp_dir:
        duplicate_dir = abspath(join(temp_dir, "archive"))
        os.mkdir(duplicate_dir)
        assert mm_file_tools.extract_zip(zip_file, temp_dir, create_folder=True)
        assert sorted(os.listdir(temp_dir)) == ["archive", "archive-2"]
        archive_dir = abspath(join(temp_dir, "archive-2"))
        assert sorted(os.listdir(archive_dir)) == ["DELETE.txt", "Internal", "metadata.json"]
        internal_dir = abspath(join(archive_dir, "Internal"))
        assert sorted(os.listdir(internal_dir)) == ["Text1.txt", "Text2.txt"]
        text_file = abspath(join(internal_dir, "Text2.txt"))
        assert mm_file_tools.read_text_file(text_file) == "Another File."
    # Test extracting zip while deleting unwanted files
    with tempfile.TemporaryDirectory() as temp_dir:
        assert mm_file_tools.extract_zip(zip_file, temp_dir, delete_files=["DELETE.txt"])
        assert sorted(os.listdir(temp_dir)) == ["Internal", "metadata.json"]
        internal_dir = abspath(join(temp_dir, "Internal"))
        assert sorted(os.listdir(internal_dir)) == ["Text1.txt", "Text2.txt"]
        text_file = abspath(join(temp_dir, "metadata.json"))
        assert mm_file_tools.read_json_file(text_file) == {"title":"Zip Test"}
    # Test extracting zip while removing internal directory
    with tempfile.TemporaryDirectory() as temp_dir:
        delete = ["DELETE.txt", "metadata.json"]
        assert mm_file_tools.extract_zip(zip_file, temp_dir, create_folder=True, remove_internal=True, delete_files=delete)
        assert os.listdir(temp_dir) == ["archive"]
        archive_dir = abspath(join(temp_dir, "archive"))
        assert sorted(os.listdir(archive_dir)) == ["Text1.txt", "Text2.txt"]
    # Test that directory is not removed with external files
    with tempfile.TemporaryDirectory() as temp_dir:
        assert mm_file_tools.extract_zip(zip_file, temp_dir, remove_internal=True)
        assert sorted(os.listdir(temp_dir)) == ["DELETE.txt", "Internal", "metadata.json"]
        internal_dir = abspath(join(temp_dir, "Internal"))
        assert sorted(os.listdir(internal_dir)) == ["Text1.txt", "Text2.txt"]
    # Test if the extracted files already exist
    with tempfile.TemporaryDirectory() as temp_dir:
        mm_file_tools.write_text_file(abspath(join(temp_dir, "Text1.txt")), "A")
        mm_file_tools.write_text_file(abspath(join(temp_dir, "Text2.txt")), "B")
        delete = ["DELETE.txt", "metadata.json"]
        assert mm_file_tools.extract_zip(zip_file, temp_dir, remove_internal=True, delete_files=delete)
        assert sorted(os.listdir(temp_dir)) == ["Text1-2.txt", "Text1.txt", "Text2-2.txt", "Text2.txt"]
        text_file = abspath(join(temp_dir, "Text1-2.txt"))
        assert mm_file_tools.read_text_file(text_file) == "This is text!"
        text_file = abspath(join(temp_dir, "Text2-2.txt"))
        assert mm_file_tools.read_text_file(text_file) == "Another File."
    # Test that JSON pairs remain connected when renamed
    base_dir = mm_test.ZIP_CONFLICT_DIRECTORY
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_dir = abspath(join(temp_dir, "extract"))
        shutil.copytree(base_dir, extract_dir)
        zip_file = abspath(join(extract_dir, "blue.zip"))
        assert mm_file_tools.extract_zip(zip_file, extract_dir, remove_internal=True)
        files = sorted(os.listdir(extract_dir))
        assert len(files) == 7
        assert files[0] == "blue-2.json"
        assert files[1] == "blue-2.png"
        assert files[2] == "blue.jpg"
        assert files[3] == "blue.json"
        assert files[4] == "blue.zip"
        assert files[5] == "folder"
        assert files[6] == "folder-2"
        assert os.listdir(abspath(join(extract_dir, "folder"))) == ["outside.txt"]
        assert os.listdir(abspath(join(extract_dir, "folder-2"))) == ["internal.txt"]
    # Test if an invalid zip file is given
    with tempfile.TemporaryDirectory() as temp_dir:
        assert not mm_file_tools.extract_zip(non_zip_file, temp_dir)
        assert not mm_file_tools.extract_zip("/non/existant/", temp_dir)
        assert os.listdir(temp_dir) == []

def test_extract_file_from_zip():
    """
    Tests the extract_file_from_zip function.
    """
    # Get file paths
    zip_file = abspath(join(mm_test.BASIC_DIRECTORY, "archive.zip"))
    text_directory = abspath(join(mm_test.BASIC_DIRECTORY, "text"))
    non_zip_file = abspath(join(text_directory, "unicode.txt"))
    # Test extracting a file from a zip file
    with tempfile.TemporaryDirectory() as temp_dir:
        extracted = mm_file_tools.extract_file_from_zip(zip_file, temp_dir, "metadata.json")
        assert os.listdir(temp_dir) == ["metadata.json"]
        assert abspath(join(extracted, os.pardir)) == abspath(temp_dir)
        assert basename(extracted) == "metadata.json"
        assert mm_file_tools.read_json_file(extracted) == {"title":"Zip Test"}
    # Test extracting file from a subdirectory
    with tempfile.TemporaryDirectory() as temp_dir:
        extracted = mm_file_tools.extract_file_from_zip(zip_file, temp_dir, "Text1.txt", True)
        assert os.listdir(temp_dir) == ["Text1.txt"]
        assert abspath(join(extracted, os.pardir)) == abspath(temp_dir)
        assert basename(extracted) == "Text1.txt"
        assert mm_file_tools.read_text_file(extracted) == "This is text!"
    # Test if requested file is not present in the zip file
    with tempfile.TemporaryDirectory() as temp_dir:
        extracted = mm_file_tools.extract_file_from_zip(zip_file, temp_dir, "Nothing.txt", True)
        assert extracted is None
        extracted = mm_file_tools.extract_file_from_zip(zip_file, temp_dir, "Text1.txt")
        assert extracted is None
        assert os.listdir(temp_dir) == []
    # Test that directories cannot be extracted
    with tempfile.TemporaryDirectory() as temp_dir:
        extracted = mm_file_tools.extract_file_from_zip(zip_file, temp_dir, "Internal")
        assert extracted is None
        assert os.listdir(temp_dir) == []
    # Test if the extracted file already exists
    with tempfile.TemporaryDirectory() as temp_dir:
        mm_file_tools.write_text_file(abspath(join(temp_dir, "DELETE.txt")), "A")
        extracted = mm_file_tools.extract_file_from_zip(zip_file, temp_dir, "DELETE.txt")
        assert sorted(os.listdir(temp_dir)) == ["DELETE-2.txt", "DELETE.txt"]
        assert abspath(join(extracted, os.pardir)) == abspath(temp_dir)
        assert basename(extracted) == "DELETE-2.txt"
        assert mm_file_tools.read_text_file(extracted) == "Delete Me!"
    # Test extracting from an invalid zip file
    with tempfile.TemporaryDirectory() as temp_dir:
        extracted = mm_file_tools.extract_file_from_zip(non_zip_file, temp_dir, "DELETE.txt")
        assert extracted is None
        extracted = mm_file_tools.extract_file_from_zip("/non/existant/file", temp_dir, "DELETE.txt")
        assert extracted is None
        assert os.listdir(temp_dir) == []

def test_create_zip():
    """
    Tests the create_zip function.
    """
    # Get file paths
    json_directory = abspath(join(mm_test.BASIC_DIRECTORY, "json"))
    non_zip_file = abspath(join(json_directory, "unicode.json"))
    # Test creating a zip file
    with tempfile.TemporaryDirectory() as temp_dir:
        created_zip = abspath(join(temp_dir, "created.zip"))
        assert mm_file_tools.create_zip(json_directory, created_zip)
        assert mm_file_tools.extract_zip(created_zip, temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["created.zip", "latin1.JSON", "unicode.json"]
        json_file = abspath(join(temp_dir, "latin1.JSON"))
        assert mm_file_tools.read_json_file(json_file) == {"new": "Títle"}
    # Test creating a zip file with internal directories
    with tempfile.TemporaryDirectory() as temp_dir:
        created_zip = abspath(join(temp_dir, "created.zip"))
        assert mm_file_tools.create_zip(mm_test.BASIC_DIRECTORY, created_zip)
        assert mm_file_tools.extract_zip(created_zip, temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["archive.zip", "created.zip", "html", "json", "text"]
        internal_dir = abspath(join(temp_dir, "json"))
        assert sorted(os.listdir(internal_dir)) == ["latin1.JSON", "unicode.json"]
        internal_dir = abspath(join(temp_dir, "html"))
        assert sorted(os.listdir(internal_dir)) == ["badformat.html", "basic.html", "deviantart.htm", "unformatted.html"]
        internal_dir = abspath(join(temp_dir, "text"))
        assert sorted(os.listdir(internal_dir)) == ["cp437.TXT", "latin1.txt", "unicode.txt"]
        text_file = abspath(join(internal_dir, "cp437.TXT"))
        assert mm_file_tools.read_text_file(text_file) == "This is cp437."
    # Test adding a mimetype file
    with tempfile.TemporaryDirectory() as temp_dir:
        created_zip = abspath(join(temp_dir, "created.zip"))
        assert mm_file_tools.create_zip(json_directory, created_zip, mimetype="Thing")
        assert mm_file_tools.extract_zip(created_zip, temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["created.zip", "latin1.JSON", "mimetype", "unicode.json"]
        text_file = abspath(join(temp_dir, "mimetype"))
        assert mm_file_tools.read_text_file(text_file) == "Thing"

def test_find_files_of_type():
    """
    Tests the find_files_of_type function.
    """
    # Get file paths
    basic_directory = mm_test.BASIC_DIRECTORY
    text_directory = abspath(join(basic_directory, "text"))
    html_directory = abspath(join(basic_directory, "html"))
    json_directory = abspath(join(basic_directory, "json"))
    # Test finding all files of a given extension
    files = mm_file_tools.find_files_of_type(text_directory, ".txt")
    assert len(files) == 3
    assert basename(files[0]) == "cp437.TXT"
    assert basename(files[1]) == "latin1.txt"
    assert basename(files[2]) == "unicode.txt"
    assert mm_file_tools.find_files_of_type(text_directory, ".png") == []
    assert mm_file_tools.find_files_of_type(text_directory, ".json") == []
    assert mm_file_tools.find_files_of_type(basic_directory, ".txt", False) == []
    # Test finding files while including subdirectories
    files = mm_file_tools.find_files_of_type(basic_directory, ".txt")
    assert len(files) == 3
    files = mm_file_tools.find_files_of_type(basic_directory, [".json", ".zip"])
    assert len(files) == 3
    assert basename(files[0]) == "archive.zip"
    assert abspath(join(files[0], os.pardir)) == basic_directory
    assert basename(files[1]) == "latin1.JSON"
    assert abspath(join(files[1], os.pardir)) == json_directory
    assert basename(files[2]) == "unicode.json"
    assert abspath(join(files[2], os.pardir)) == json_directory
    # Test finding files with inverted extension
    files = mm_file_tools.find_files_of_type(basic_directory, [".txt"], inverted=True)
    assert len(files) == 7    
    assert basename(files[0]) == "archive.zip"
    assert abspath(join(files[0], os.pardir)) == basic_directory
    assert basename(files[1]) == "badformat.html"
    assert abspath(join(files[1], os.pardir)) == html_directory
    assert basename(files[2]) == "basic.html"
    assert abspath(join(files[2], os.pardir)) == html_directory
    assert basename(files[3]) == "deviantart.htm"
    assert abspath(join(files[3], os.pardir)) == html_directory
    assert basename(files[4]) == "unformatted.html"
    assert abspath(join(files[4], os.pardir)) == html_directory
    assert basename(files[5]) == "latin1.JSON"
    assert abspath(join(files[5], os.pardir)) == json_directory
    assert basename(files[6]) == "unicode.json"
    assert abspath(join(files[6], os.pardir)) == json_directory
    files = mm_file_tools.find_files_of_type(basic_directory, [".txt", ".json", ".htm", ".html"], inverted=True)
    assert len(files) == 1
    assert basename(files[0]) == "archive.zip"
    assert abspath(join(files[0], os.pardir)) == basic_directory

def test_directory_contains():
    """
    Tests the directory_contains function.
    """
    # Get file paths
    basic_directory = mm_test.BASIC_DIRECTORY
    text_directory = abspath(join(basic_directory, "text"))
    json_directory = abspath(join(basic_directory, "json"))
    # Test if a directory contains files without checking subdirectories
    assert mm_file_tools.directory_contains(basic_directory, ".zip", False)
    assert mm_file_tools.directory_contains(text_directory, ".txt")
    assert mm_file_tools.directory_contains(text_directory, [".txt", ".json"])
    assert not mm_file_tools.directory_contains(text_directory, ".t")
    assert not mm_file_tools.directory_contains(text_directory, ".json")
    assert not mm_file_tools.directory_contains(text_directory, [".json", ".png"])
    assert not mm_file_tools.directory_contains(basic_directory, ".txt", False)
    # Test if directory contains files while checking subdirectories
    assert mm_file_tools.directory_contains(basic_directory, ".zip")
    assert mm_file_tools.directory_contains(basic_directory, ".json")
    assert mm_file_tools.directory_contains(basic_directory, [".txt", ".png"])
    assert not mm_file_tools.directory_contains(basic_directory, ".png")
    assert not mm_file_tools.directory_contains(basic_directory, [".jpeg", ".png", ".pdf"])
