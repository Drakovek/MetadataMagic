#!/usr/bin/env python3

import os
import metadata_magic.file_tools as mm_file_tools
from os.path import abspath, basename, exists, isdir, join

def test_get_temp_dir():
    """
    Tests the get_temp_dir function.
    """
    # Test creating temporary directories
    temp_dir = mm_file_tools.get_temp_dir("dvk_test_thing")
    assert exists(temp_dir)
    assert isdir(temp_dir)
    assert basename(temp_dir) == "dvk_test_thing"
    # Test that all files are deleted when overwriting temp dir
    text_file = abspath(join(temp_dir, "text.txt"))
    sub_dir = abspath(join(temp_dir, "sub"))
    other_file = abspath(join(sub_dir, "other.txt"))
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(text_file, "Test text.")
    mm_file_tools.write_text_file(other_file, "Other!")
    assert exists(text_file)
    assert exists(other_file)
    assert exists(sub_dir)
    assert isdir(sub_dir)
    temp_dir = mm_file_tools.get_temp_dir("dvk_test_thing")
    assert len(os.listdir(temp_dir)) == 0
    assert not exists(text_file)
    assert not exists(other_file)
    assert not exists(sub_dir)
    assert not isdir(sub_dir)

def test_read_write_text_file():
    """
    Tests the write_text_file and read_text_file functions.
    """
    # Test writing a text file
    temp_dir = mm_file_tools.get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    assert not exists(text_file)
    mm_file_tools.write_text_file(text_file, "This is some text!")
    assert exists(text_file)
    assert mm_file_tools.read_text_file(text_file) == "This is some text!"
    # Test overwriting a text file
    mm_file_tools.write_text_file(text_file, "Different text now.\nYay!")
    assert mm_file_tools.read_text_file(text_file) == "Different text now.\nYay!"
    # Test reading a non-text file
    sub_dir = abspath(join(temp_dir, "directory"))
    os.mkdir(sub_dir)
    assert exists(sub_dir)
    assert mm_file_tools.read_text_file(sub_dir) is None
    # Test writing to invalid location
    sub_dir = abspath(join(temp_dir, "non-existant"))
    text_file = abspath(join(sub_dir, "new.txt"))
    mm_file_tools.write_text_file(text_file, "Some stuff")
    assert sorted(os.listdir(temp_dir)) == ["directory", "text.txt"]
    # Test reading a non-unicode formatted text file
    iso_file = abspath(join(temp_dir, "iso.txt"))
    with open(iso_file, "w", encoding="ISO-8859-15") as out_file:
        out_file.write("--This is not ständard ünicode--")
    assert exists(iso_file)
    assert mm_file_tools.read_text_file(iso_file) == "--This is not ständard ünicode--"

def test_read_write_json_file():
    """
    Tests the write_json_file and read_json_file functions.
    """
    # Test writing a JSON file
    temp_dir = mm_file_tools.get_temp_dir()
    json_file = abspath(join(temp_dir, "test.json"))
    assert not exists(json_file)
    mm_file_tools.write_json_file(json_file, {"key":"pair", "Thing":"Other"})
    assert exists(json_file)
    assert mm_file_tools.read_json_file(json_file) == {"key":"pair", "Thing":"Other"}
    # Test overwriting a JSON file
    mm_file_tools.write_json_file(json_file, {"all":"new"})
    assert mm_file_tools.read_json_file(json_file) == {"all":"new"}
    # Test reading a non-JSON file
    sub_dir = abspath(join(temp_dir, "directory"))
    os.mkdir(sub_dir)
    assert exists(sub_dir)
    assert mm_file_tools.read_json_file(sub_dir) == {}
    text_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "Not a JSON")
    assert mm_file_tools.read_json_file(text_file) == {}
    # Test writing to invalid location
    sub_dir = abspath(join(temp_dir, "non-existant"))
    text_file = abspath(join(sub_dir, "new.json"))
    mm_file_tools.write_json_file(text_file, {"new":"key"})
    assert sorted(os.listdir(temp_dir)) == ["directory", "test.json", "text.txt"]

def test_find_files_of_type():
    """
    Tests the find_files_of_type function.
    """
    # Test finding all files of a given extension
    temp_dir = mm_file_tools.get_temp_dir()
    temp_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(temp_file, "Not")
    temp_file = abspath(join(temp_dir, "new.txt"))
    mm_file_tools.write_text_file(temp_file, "Important")
    temp_file = abspath(join(temp_dir, "other.png"))
    mm_file_tools.write_text_file(temp_file, "At")
    temp_file = abspath(join(temp_dir, "blah.thing"))
    mm_file_tools.write_text_file(temp_file, "All")
    assert sorted(os.listdir(temp_dir)) == ["blah.thing", "new.txt", "other.png", "text.txt"]
    files = mm_file_tools.find_files_of_type(temp_dir, ".txt")
    assert len(files) == 2
    assert basename(files[0]) == "new.txt"
    assert basename(files[1]) == "text.txt"
    assert exists(files[0])
    assert exists(files[1])
    assert mm_file_tools.find_files_of_type(temp_dir, ".thing") == [temp_file]
    assert mm_file_tools.find_files_of_type(temp_dir, ".nope") == []
    # Test finding files inside subdirectories
    sub_directory = abspath(join(temp_dir, "sub"))
    deep_directory = abspath(join(temp_dir, "deep.txt"))
    os.mkdir(sub_directory)
    os.mkdir(deep_directory)
    temp_file = abspath(join(sub_directory, "sub.txt"))
    mm_file_tools.write_text_file(temp_file, "Still")
    temp_file = abspath(join(deep_directory, "deep.png"))
    mm_file_tools.write_text_file(temp_file, "Nothing")
    files = mm_file_tools.find_files_of_type(temp_dir, ".txt")
    assert len(files) == 3
    assert basename(files[0]) == "new.txt"
    assert basename(files[1]) == "sub.txt"
    assert basename(files[2]) == "text.txt"
    files = mm_file_tools.find_files_of_type(temp_dir, ".png", include_subdirectories=True)
    assert len(files) == 2
    assert basename(files[0]) == "deep.png"
    assert basename(files[1]) == "other.png"
    assert files[0] == temp_file
    # Test finding files, not including subdirectories
    files = mm_file_tools.find_files_of_type(temp_dir, ".txt", include_subdirectories=False)
    assert len(files) == 2
    assert basename(files[0]) == "new.txt"
    assert basename(files[1]) == "text.txt"
    # Test finding files with inverted extension
    files = mm_file_tools.find_files_of_type(temp_dir, ".txt", inverted=True)
    assert len(files) == 3
    assert basename(files[0]) == "blah.thing"
    assert basename(files[1]) == "deep.png"
    assert basename(files[2]) == "other.png"
    # Test finding files of multiple types
    files = mm_file_tools.find_files_of_type(temp_dir, [".txt", ".png"], include_subdirectories=False)
    assert len(files) == 3
    assert basename(files[0]) == "new.txt"
    assert basename(files[1]) == "other.png"
    assert basename(files[2]) == "text.txt"
    # Test finding files of multiple types with inverted extension
    files = mm_file_tools.find_files_of_type(temp_dir, [".txt", ".png"], inverted=True, include_subdirectories=False)
    assert len(files) == 1
    assert basename(files[0]) == "blah.thing"

def test_directory_contains():
    """
    Tests the directory_contains function.
    """
    # Test with single directory
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "text.txt")), "AAA")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "image.PNG")), "AAA")
    assert mm_file_tools.directory_contains(temp_dir, [".txt"])
    assert mm_file_tools.directory_contains(temp_dir, [".png"])
    assert mm_file_tools.directory_contains(temp_dir, [".blah", ".txt"])
    assert not mm_file_tools.directory_contains(temp_dir, [".jpg"])
    assert not mm_file_tools.directory_contains(temp_dir, [".pdf", ".mp4"])
    # Test with subdirectories
    sub_dir = abspath(join(temp_dir, "sub"))
    deep_dir = abspath(join(sub_dir, "deep"))
    os.mkdir(sub_dir)
    os.mkdir(deep_dir)
    mm_file_tools.write_text_file(abspath(join(sub_dir, "doc.pdf")), "AAA")
    mm_file_tools.write_text_file(abspath(join(sub_dir, "video.mkv")), "AAA")
    assert mm_file_tools.directory_contains(temp_dir, [".txt"], True)
    assert mm_file_tools.directory_contains(temp_dir, [".png"], True)
    assert mm_file_tools.directory_contains(temp_dir, [".pdf"], True)
    assert mm_file_tools.directory_contains(temp_dir, [".mkv"], True)
    assert mm_file_tools.directory_contains(temp_dir, [".mkv", ".pdf"], True)
    assert not mm_file_tools.directory_contains(temp_dir, [".mkv", ".pdf"], False)
    assert mm_file_tools.directory_contains(temp_dir, [".txt"], False)

def test_create_zip():
    """
    Tests the create_zip function.
    """
    # Test Creating Zip with loose files
    temp_dir = mm_file_tools.get_temp_dir()
    media_file = abspath(join(temp_dir, "media.jpg")) 
    text_file = abspath(join(temp_dir, "text.txt"))
    dot_file = abspath(join(temp_dir, ".dontinclude"))
    mm_file_tools.write_text_file(media_file, "This is not a photo.")
    mm_file_tools.write_text_file(text_file, "TEXT!")
    mm_file_tools.write_text_file(dot_file, "Do Not Include")
    assert exists(media_file)
    assert exists(text_file)
    assert exists(dot_file)
    zip_file = abspath(join(temp_dir, "file.zip"))
    assert not exists(zip_file)
    assert mm_file_tools.create_zip(temp_dir, zip_file)
    assert exists(zip_file)
    extracted = abspath(join(temp_dir, "extracted"))
    os.mkdir(extracted)
    assert mm_file_tools.extract_zip(zip_file, extracted)
    assert sorted(os.listdir(extracted)) == ["media.jpg", "text.txt"]
    assert mm_file_tools.read_text_file(abspath(join(extracted, "media.jpg"))) == "This is not a photo."
    assert mm_file_tools.read_text_file(abspath(join(extracted, "text.txt"))) == "TEXT!"
    # Test Creating Zip with internal directories
    temp_dir = mm_file_tools.get_temp_dir()
    sub_dir = abspath(join(temp_dir, "sub"))
    deep_dir = abspath(join(sub_dir, "deep"))
    os.mkdir(sub_dir)
    os.mkdir(deep_dir)
    media_file = abspath(join(temp_dir, "main.txt"))
    sub_file = abspath(join(sub_dir, "subtext.txt"))
    deep_file = abspath(join(deep_dir, "deep.png"))
    deep_dot = abspath(join(deep_dir, ".dontinclude"))
    mm_file_tools.write_text_file(media_file, "This is text.")
    mm_file_tools.write_text_file(sub_file, "Deeper text")
    mm_file_tools.write_text_file(deep_file, "Deepest yet.")
    mm_file_tools.write_text_file(deep_dot, "NO")
    assert exists(media_file)
    assert exists(sub_file)
    assert exists(deep_file)
    assert exists(deep_dot)
    zip_file = abspath(join(temp_dir, "new.zip"))
    assert not exists(zip_file)
    assert mm_file_tools.create_zip(temp_dir, zip_file)
    assert exists(zip_file)
    extracted = abspath(join(temp_dir, "extracted"))
    os.mkdir(extracted)
    assert mm_file_tools.extract_zip(zip_file, extracted)
    assert sorted(os.listdir(extracted)) == ["main.txt", "sub"]
    extracted = abspath(join(extracted, "sub"))
    assert sorted(os.listdir(extracted)) == ["deep", "subtext.txt"]
    extracted = abspath(join(extracted, "deep"))
    assert sorted(os.listdir(extracted)) == ["deep.png"]
    assert mm_file_tools.read_text_file(abspath(join(extracted, "deep.png"))) == "Deepest yet."
    # Test Creating Mimetype
    temp_dir = mm_file_tools.get_temp_dir()
    media_file = abspath(join(temp_dir, "main.txt"))
    mm_file_tools.write_text_file(media_file, "This is text.")
    assert exists(media_file)
    zip_file = abspath(join(temp_dir, "mime.zip"))
    assert not exists(zip_file)
    assert mm_file_tools.create_zip(temp_dir, zip_file, 8, "filetype")
    assert exists(zip_file)
    extracted = abspath(join(temp_dir, "extracted"))
    os.mkdir(extracted)
    assert mm_file_tools.extract_zip(zip_file, extracted)
    assert sorted(os.listdir(extracted)) == ["main.txt", "mimetype"]
    assert mm_file_tools.read_text_file(abspath(join(extracted, "main.txt"))) == "This is text."
    assert mm_file_tools.read_text_file(abspath(join(extracted, "mimetype"))) == "filetype"

def test_extract_zip():
    """
    Tests the extract_zip function.
    """
    # Test extracting zip with added directory
    zip_dir = mm_file_tools.get_temp_dir("dvk_zip_test")
    text_file = abspath(join(zip_dir, "text.txt"))
    zip_file = abspath(join(zip_dir, "Name!.zip"))
    mm_file_tools.write_text_file(text_file, "This is text!")
    assert exists(text_file)
    assert mm_file_tools.create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = mm_file_tools.get_temp_dir("dvk_extract_test")
    assert mm_file_tools.extract_zip(zip_file, extract_dir, create_folder=True)
    assert os.listdir(extract_dir) == ["Name!"]
    sub_dir = abspath(join(extract_dir, "Name!"))
    assert os.listdir(sub_dir) == ["text.txt"]
    read_file = abspath(join(sub_dir, "text.txt"))
    assert mm_file_tools.read_text_file(read_file) == "This is text!"
    # Test if added directory already exists
    zip_dir = mm_file_tools.get_temp_dir("dvk_zip_test")
    text_file = abspath(join(zip_dir, "thing.txt"))
    zip_file = abspath(join(zip_dir, "duplicate.zip"))
    mm_file_tools.write_text_file(text_file, "This is a file")
    assert exists(text_file)
    assert mm_file_tools.create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = mm_file_tools.get_temp_dir("dvk_extract_test")
    duplicate_file = abspath(join(extract_dir, "duplicate"))
    mm_file_tools.write_text_file(duplicate_file, "test")
    assert sorted(os.listdir(extract_dir)) == ["duplicate"]
    assert mm_file_tools.extract_zip(zip_file, extract_dir, create_folder=True)
    assert sorted(os.listdir(extract_dir)) == ["duplicate", "duplicate-2"]
    sub_dir = abspath(join(extract_dir, "duplicate-2"))
    assert os.listdir(sub_dir) == ["thing.txt"]
    # Test extracting zip while removing given files
    zip_dir = mm_file_tools.get_temp_dir("dvk_zip_test")
    text_file = abspath(join(zip_dir, "text.txt"))
    media_file = abspath(join(zip_dir, "media.png"))
    delete_file = abspath(join(zip_dir, "meta.xml"))
    zip_file = abspath(join(zip_dir, "New.zip"))
    mm_file_tools.write_text_file(text_file, "some text")
    mm_file_tools.write_text_file(media_file, "Not an image")
    mm_file_tools.write_text_file(delete_file, "To be deleted")
    assert exists(text_file)
    assert exists(media_file)
    assert exists(delete_file)
    assert mm_file_tools.create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = mm_file_tools.get_temp_dir("dvk_extract_test")
    assert mm_file_tools. extract_zip(zip_file, extract_dir, delete_files=["extraneous.txt", "meta.xml"])
    assert sorted(os.listdir(extract_dir)) == ["media.png", "text.txt"]
    # Test extracting zip while removing internal folder
    zip_dir = mm_file_tools.get_temp_dir("dvk_zip_test")
    sub_zip_dir = abspath(join(zip_dir, "Internal"))
    text_file = abspath(join(sub_zip_dir, "deep.txt"))
    zip_file = abspath(join(zip_dir, "compressed.cbz"))
    os.mkdir(sub_zip_dir)
    mm_file_tools.write_text_file(text_file, "In a folder.")
    assert exists(text_file)
    assert mm_file_tools.create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = mm_file_tools.get_temp_dir("dvk_extract_test")
    assert mm_file_tools.extract_zip(zip_file, extract_dir, remove_internal=True)
    assert os.listdir(extract_dir) == ["deep.txt"]
    # Test that removing internal folder does not work with multiple files
    os.remove(zip_file)
    media_file = abspath(join(zip_dir, "media.jpg"))
    mm_file_tools.write_text_file(media_file, "media")
    assert exists(media_file)
    assert mm_file_tools.create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = mm_file_tools.get_temp_dir("dvk_extract_test")
    assert mm_file_tools.extract_zip(zip_file, extract_dir, remove_internal=True)
    assert sorted(os.listdir(extract_dir)) == ["Internal", "media.jpg"]
    sub_dir = abspath(join(extract_dir, "Internal"))
    assert os.listdir(sub_dir) == ["deep.txt"]
    # Test removing folder after internal files are deleted
    os.remove(zip_file)
    zip_file = abspath(join(zip_dir, "NoExtension"))
    assert mm_file_tools.create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = mm_file_tools.get_temp_dir("dvk_extract_test")
    assert mm_file_tools.extract_zip(zip_file, extract_dir, create_folder=True, remove_internal=True, delete_files=["media.jpg"])
    assert os.listdir(extract_dir) == ["NoExtension"]
    sub_dir = abspath(join(extract_dir, "NoExtension"))
    assert os.listdir(sub_dir) == ["deep.txt"]
    # Test if invalid zip file is given
    assert exists(text_file)
    extract_dir = mm_file_tools.get_temp_dir("dvk_extract_test")
    assert not mm_file_tools.extract_zip(text_file, extract_dir)
    # Test if extracted files already exist
    zip_dir = mm_file_tools.get_temp_dir("dvk_zip_test")
    sub_zip_dir = abspath(join(zip_dir, "Internal"))
    text_file = abspath(join(zip_dir, "text.txt"))
    media_file = abspath(join(sub_zip_dir, "deep.png"))
    zip_file = abspath(join(zip_dir, "Another One!.cbz"))
    os.mkdir(sub_zip_dir)
    mm_file_tools.write_text_file(text_file, "this is text")
    mm_file_tools.write_text_file(media_file, "media")
    assert exists(text_file)
    assert exists(media_file)
    assert mm_file_tools.create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = mm_file_tools.get_temp_dir("dvk_extract_test")
    sub_dir = abspath(join(extract_dir, "Internal"))
    duplicate_file = abspath(join(extract_dir, "text.txt"))
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(duplicate_file, "Different Text")
    assert exists(sub_dir)
    assert exists(duplicate_file)
    assert mm_file_tools.extract_zip(zip_file, extract_dir)
    assert sorted(os.listdir(extract_dir)) == ["Internal", "Internal-2", "text-2.txt", "text.txt"]
    assert mm_file_tools.read_text_file(abspath(join(extract_dir, "text-2.txt"))) == "this is text"
    assert mm_file_tools.read_text_file(abspath(join(extract_dir, "text.txt"))) == "Different Text"
    assert os.listdir(abspath(join(extract_dir, "Internal"))) == []
    assert os.listdir(abspath(join(extract_dir, "Internal-2"))) == ["deep.png"]

def test_extract_file_from_zip():
    """
    Tests the extract_file_from_zip function.
    """
    # Test extracting a file
    zip_dir = mm_file_tools.get_temp_dir("dvk_zip_test")
    sub_dir = abspath(join(zip_dir, "sub"))
    text_file = abspath(join(zip_dir, "text.txt"))
    media_file = abspath(join(zip_dir, "media.png"))
    sub_file = abspath(join(sub_dir, "deep.jpg"))
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(text_file, "This is text!")
    mm_file_tools.write_text_file(media_file, "More text!")
    mm_file_tools.write_text_file(sub_file, "too deep")
    assert exists(text_file)
    assert exists(media_file)
    assert exists(sub_file)
    zip_file = abspath(join(zip_dir, "zip.zip"))
    assert mm_file_tools.create_zip(zip_dir, zip_file)
    assert exists(zip_file)
    extract_dir = mm_file_tools.get_temp_dir("dvk_extract_test")
    extracted = mm_file_tools.extract_file_from_zip(zip_file, extract_dir, "text.txt")
    assert exists(extracted)
    assert basename(extracted) == "text.txt"
    assert mm_file_tools.read_text_file(extracted) == "This is text!"
    # Test extracting a file if the file is not present in the ZIP file
    assert mm_file_tools.extract_file_from_zip(zip_file, extract_dir, "blah.txt") is None
    assert mm_file_tools.extract_file_from_zip(zip_file, extract_dir, "deep.jpg") is None
    # Test attempting to extract a directory
    assert mm_file_tools.extract_file_from_zip(zip_file, extract_dir, "sub") is None
    # Test extracting a file from a non-ZIP archive
    assert mm_file_tools.extract_file_from_zip(text_file, extract_dir, "blah.txt") is None
    # Test if file already exists
    extracted = mm_file_tools.extract_file_from_zip(zip_file, extract_dir, "text.txt")
    assert exists(extracted)
    assert basename(extracted) == "text-2.txt"
    # Test extracting file from a subdirectory
    extracted = mm_file_tools.extract_file_from_zip(zip_file, extract_dir, "deep.jpg", check_subdirectories=True)
    assert exists(extracted)
    assert basename(extracted) == "deep.jpg"
    assert abspath(join(extracted, os.pardir)) == extract_dir
    assert mm_file_tools.read_text_file(extracted) == "too deep"
