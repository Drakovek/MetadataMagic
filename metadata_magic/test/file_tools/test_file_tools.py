#!/usr/bin/env python3

from metadata_magic.main.file_tools.file_tools import get_temp_dir
from metadata_magic.main.file_tools.file_tools import create_zip, extract_zip, extract_file_from_zip
from metadata_magic.main.file_tools.file_tools import write_text_file, read_text_file, write_json_file, read_json_file
from metadata_magic.main.rename.rename_tools import sort_alphanum
from os import mkdir, listdir, remove
from os.path import abspath, basename, exists, isdir, join

def test_get_temp_dir():
    """
    Tests the get_temp_dir function.
    """
    # Test creating temporary directories
    temp_dir = get_temp_dir("dvk_test_thing")
    assert exists(temp_dir)
    assert isdir(temp_dir)
    assert basename(temp_dir) == "dvk_test_thing"
    # Test that all files are deleted when overwriting temp dir
    text_file = abspath(join(temp_dir, "text.txt"))
    sub_dir = abspath(join(temp_dir, "sub"))
    other_file = abspath(join(sub_dir, "other.txt"))
    mkdir(sub_dir)
    write_text_file(text_file, "Test text.")
    write_text_file(other_file, "Other!")
    assert exists(text_file)
    assert exists(other_file)
    assert exists(sub_dir)
    assert isdir(sub_dir)
    temp_dir = get_temp_dir("dvk_test_thing")
    assert len(listdir(temp_dir)) == 0
    assert not exists(text_file)
    assert not exists(other_file)
    assert not exists(sub_dir)
    assert not isdir(sub_dir)

def test_read_write_text_file():
    """
    Tests the write_text_file and read_text_file functions.
    """
    # Test writing a text file
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    assert not exists(text_file)
    write_text_file(text_file, "This is some text!")
    assert exists(text_file)
    assert read_text_file(text_file) == "This is some text!"
    # Test overwriting a text file
    write_text_file(text_file, "Different text now.\nYay!")
    assert read_text_file(text_file) == "Different text now.\nYay!"
    # Test reading a non-text file
    sub_dir = abspath(join(temp_dir, "directory"))
    mkdir(sub_dir)
    assert exists(sub_dir)
    assert read_text_file(sub_dir) is None
    # Test writing to invalid location
    sub_dir = abspath(join(temp_dir, "non-existant"))
    text_file = abspath(join(sub_dir, "new.txt"))
    write_text_file(text_file, "Some stuff")
    assert sorted(listdir(temp_dir)) == ["directory", "text.txt"]

def test_read_write_json_file():
    """
    Tests the write_json_file and read_json_file functions.
    """
    # Test writing a JSON file
    temp_dir = get_temp_dir()
    json_file = abspath(join(temp_dir, "test.json"))
    assert not exists(json_file)
    write_json_file(json_file, {"key":"pair", "Thing":"Other"})
    assert exists(json_file)
    assert read_json_file(json_file) == {"key":"pair", "Thing":"Other"}
    # Test overwriting a JSON file
    write_json_file(json_file, {"all":"new"})
    assert read_json_file(json_file) == {"all":"new"}
    # Test reading a non-JSON file
    sub_dir = abspath(join(temp_dir, "directory"))
    mkdir(sub_dir)
    assert exists(sub_dir)
    assert read_json_file(sub_dir) == {}
    text_file = abspath(join(temp_dir, "text.txt"))
    write_text_file(text_file, "Not a JSON")
    assert read_json_file(text_file) == {}
    # Test writing to invalid location
    sub_dir = abspath(join(temp_dir, "non-existant"))
    text_file = abspath(join(sub_dir, "new.json"))
    write_json_file(text_file, {"new":"key"})
    assert sorted(listdir(temp_dir)) == ["directory", "test.json", "text.txt"]

def test_create_zip():
    """
    Tests the create_zip function.
    """
    # Test Creating Zip with loose files
    temp_dir = get_temp_dir()
    media_file = abspath(join(temp_dir, "media.jpg")) 
    text_file = abspath(join(temp_dir, "text.txt"))
    write_text_file(media_file, "This is not a photo.")
    write_text_file(text_file, "TEXT!")
    assert exists(media_file)
    assert exists(text_file)
    zip_file = abspath(join(temp_dir, "file.zip"))
    assert not exists(zip_file)
    assert create_zip(temp_dir, zip_file)
    assert exists(zip_file)
    extracted = abspath(join(temp_dir, "extracted"))
    mkdir(extracted)
    assert extract_zip(zip_file, extracted)
    assert sort_alphanum(listdir(extracted)) == ["media.jpg", "text.txt"]
    assert read_text_file(abspath(join(extracted, "media.jpg"))) == "This is not a photo."
    assert read_text_file(abspath(join(extracted, "text.txt"))) == "TEXT!"
    # Test Creating Zip with internal directories
    temp_dir = get_temp_dir()
    sub_dir = abspath(join(temp_dir, "sub"))
    deep_dir = abspath(join(sub_dir, "deep"))
    mkdir(sub_dir)
    mkdir(deep_dir)
    media_file = abspath(join(temp_dir, "main.txt"))
    sub_file = abspath(join(sub_dir, "subtext.txt"))
    deep_file = abspath(join(deep_dir, "deep.png"))
    write_text_file(media_file, "This is text.")
    write_text_file(sub_file, "Deeper text")
    write_text_file(deep_file, "Deepest yet.")
    assert exists(media_file)
    assert exists(sub_file)
    assert exists(deep_file)
    zip_file = abspath(join(temp_dir, "new.zip"))
    assert not exists(zip_file)
    assert create_zip(temp_dir, zip_file)
    assert exists(zip_file)
    extracted = abspath(join(temp_dir, extracted))
    mkdir(extracted)
    assert extract_zip(zip_file, extracted)
    assert sort_alphanum(listdir(extracted)) == ["main.txt", "sub"]
    extracted = abspath(join(extracted, "sub"))
    assert sort_alphanum(listdir(extracted)) == ["deep", "subtext.txt"]
    extracted = abspath(join(extracted, "deep"))
    assert sort_alphanum(listdir(extracted)) == ["deep.png"]
    assert read_text_file(abspath(join(extracted, "deep.png"))) == "Deepest yet."

def test_extract_zip():
    """
    Tests the extract_zip function.
    """
    # Test extracting zip with added directory
    zip_dir = get_temp_dir("dvk_zip_test")
    text_file = abspath(join(zip_dir, "text.txt"))
    zip_file = abspath(join(zip_dir, "Name!.zip"))
    write_text_file(text_file, "This is text!")
    assert exists(text_file)
    assert create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = get_temp_dir("dvk_extract_test")
    assert extract_zip(zip_file, extract_dir, create_folder=True)
    assert listdir(extract_dir) == ["Name!"]
    sub_dir = abspath(join(extract_dir, "Name!"))
    assert listdir(sub_dir) == ["text.txt"]
    read_file = abspath(join(sub_dir, "text.txt"))
    assert read_text_file(read_file) == "This is text!"
    # Test if added directory already exists
    zip_dir = get_temp_dir("dvk_zip_test")
    text_file = abspath(join(zip_dir, "thing.txt"))
    zip_file = abspath(join(zip_dir, "duplicate.zip"))
    write_text_file(text_file, "This is a file")
    assert exists(text_file)
    assert create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = get_temp_dir("dvk_extract_test")
    duplicate_file = abspath(join(extract_dir, "duplicate"))
    write_text_file(duplicate_file, "test")
    assert sorted(listdir(extract_dir)) == ["duplicate"]
    assert extract_zip(zip_file, extract_dir, create_folder=True)
    assert sorted(listdir(extract_dir)) == ["duplicate", "duplicate-2"]
    sub_dir = abspath(join(extract_dir, "duplicate-2"))
    assert listdir(sub_dir) == ["thing.txt"]
    # Test extracting zip while removing given files
    zip_dir = get_temp_dir("dvk_zip_test")
    text_file = abspath(join(zip_dir, "text.txt"))
    media_file = abspath(join(zip_dir, "media.png"))
    delete_file = abspath(join(zip_dir, "meta.xml"))
    zip_file = abspath(join(zip_dir, "New.zip"))
    write_text_file(text_file, "some text")
    write_text_file(media_file, "Not an image")
    write_text_file(delete_file, "To be deleted")
    assert exists(text_file)
    assert exists(media_file)
    assert exists(delete_file)
    assert create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = get_temp_dir("dvk_extract_test")
    assert extract_zip(zip_file, extract_dir, delete_files=["extraneous.txt", "meta.xml"])
    assert sorted(listdir(extract_dir)) == ["media.png", "text.txt"]
    # Test extracting zip while removing internal folder
    zip_dir = get_temp_dir("dvk_zip_test")
    sub_zip_dir = abspath(join(zip_dir, "Internal"))
    text_file = abspath(join(sub_zip_dir, "deep.txt"))
    zip_file = abspath(join(zip_dir, "compressed.cbz"))
    mkdir(sub_zip_dir)
    write_text_file(text_file, "In a folder.")
    assert exists(text_file)
    assert create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = get_temp_dir("dvk_extract_test")
    assert extract_zip(zip_file, extract_dir, remove_internal=True)
    assert listdir(extract_dir) == ["deep.txt"]
    # Test that removing internal folder does not work with multiple files
    remove(zip_file)
    media_file = abspath(join(zip_dir, "media.jpg"))
    write_text_file(media_file, "media")
    assert exists(media_file)
    assert create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = get_temp_dir("dvk_extract_test")
    assert extract_zip(zip_file, extract_dir, remove_internal=True)
    assert sorted(listdir(extract_dir)) == ["Internal", "media.jpg"]
    sub_dir = abspath(join(extract_dir, "Internal"))
    assert listdir(sub_dir) == ["deep.txt"]
    # Test removing folder after internal files are deleted
    remove(zip_file)
    zip_file = abspath(join(zip_dir, "NoExtension"))
    assert create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = get_temp_dir("dvk_extract_test")
    assert extract_zip(zip_file, extract_dir, create_folder=True, remove_internal=True, delete_files=["media.jpg"])
    assert listdir(extract_dir) == ["NoExtension"]
    sub_dir = abspath(join(extract_dir, "NoExtension"))
    assert listdir(sub_dir) == ["deep.txt"]
    # Test if invalid zip file is given
    assert exists(text_file)
    extract_dir = get_temp_dir("dvk_extract_test")
    assert not extract_zip(text_file, extract_dir)
    # Test if extracted files already exist
    zip_dir = get_temp_dir("dvk_zip_test")
    sub_zip_dir = abspath(join(zip_dir, "Internal"))
    text_file = abspath(join(zip_dir, "text.txt"))
    media_file = abspath(join(sub_zip_dir, "deep.png"))
    zip_file = abspath(join(zip_dir, "Another One!.cbz"))
    mkdir(sub_zip_dir)
    write_text_file(text_file, "this is text")
    write_text_file(media_file, "media")
    assert exists(text_file)
    assert exists(media_file)
    assert create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = get_temp_dir("dvk_extract_test")
    sub_dir = abspath(join(extract_dir, "Internal"))
    duplicate_file = abspath(join(extract_dir, "text.txt"))
    mkdir(sub_dir)
    write_text_file(duplicate_file, "Different Text")
    assert exists(sub_dir)
    assert exists(duplicate_file)
    assert extract_zip(zip_file, extract_dir)
    assert sorted(listdir(extract_dir)) == ["Internal", "Internal-2", "text-2.txt", "text.txt"]
    assert read_text_file(abspath(join(extract_dir, "text-2.txt"))) == "this is text"
    assert read_text_file(abspath(join(extract_dir, "text.txt"))) == "Different Text"
    assert listdir(abspath(join(extract_dir, "Internal"))) == []
    assert listdir(abspath(join(extract_dir, "Internal-2"))) == ["deep.png"]

def test_extract_file_from_zip():
    """
    Tests the extract_file_from_zip function.
    """
    # Test extracting a file
    zip_dir = get_temp_dir("dvk_zip_test")
    sub_dir = abspath(join(zip_dir, "sub"))
    text_file = abspath(join(zip_dir, "text.txt"))
    media_file = abspath(join(zip_dir, "media.png"))
    sub_file = abspath(join(sub_dir, "deep.jpg"))
    mkdir(sub_dir)
    write_text_file(text_file, "This is text!")
    write_text_file(media_file, "More text!")
    write_text_file(sub_file, "too deep")
    assert exists(text_file)
    assert exists(media_file)
    assert exists(sub_file)
    zip_file = abspath(join(zip_dir, "zip.zip"))
    assert create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = get_temp_dir("dvk_extract_test")
    extracted = extract_file_from_zip(zip_file, extract_dir, "text.txt")
    assert exists(extracted)
    assert basename(extracted) == "text.txt"
    assert read_text_file(extracted) == "This is text!"
    # Test extracting a file if the file is not present in the ZIP file
    assert extract_file_from_zip(zip_file, extract_dir, "blah.txt") is None
    assert extract_file_from_zip(zip_file, extract_dir, "deep.jpg") is None
    # Test attempting to extract a directory
    assert extract_file_from_zip(zip_file, extract_dir, "sub") is None
    # Test extracting a file from a non-ZIP archive
    assert extract_file_from_zip(text_file, extract_dir, "blah.txt") is None
    # Test if file already exists
    extracted = extract_file_from_zip(zip_file, extract_dir, "text.txt")
    assert exists(extracted)
    assert basename(extracted) == "text-2.txt"