#!/usr/bin/env python3

from metadata_magic.main.meta_reader import get_empty_metadata
from metadata_magic.main.comic_archive.comic_archive import create_cbz
from metadata_magic.main.comic_archive.comic_archive import update_cbz_info
from metadata_magic.main.comic_archive.comic_archive import get_info_from_cbz
from metadata_magic.main.comic_archive.comic_xml import get_comic_xml
from metadata_magic.main.comic_archive.comic_xml import read_comic_info
from metadata_magic.main.file_tools.file_tools import get_temp_dir
from metadata_magic.main.file_tools.file_tools import create_zip
from metadata_magic.main.file_tools.file_tools import extract_zip
from metadata_magic.main.file_tools.file_tools import read_text_file
from metadata_magic.main.file_tools.file_tools import write_text_file
from os import listdir, mkdir, remove
from os.path import abspath, basename, exists, join

def test_create_cbz():
    """
    Tests the create_cbz function.
    """
    # Test creating a CBZ with loose files and no name
    cbz_directory = get_temp_dir("dvk_cbz_test")
    text_file = abspath(join(cbz_directory, "text.txt"))
    media_file = abspath(join(cbz_directory, "other.txt"))
    write_text_file(text_file, "TEXT!")
    write_text_file(media_file, "Yet more text.")
    assert exists(text_file)
    assert exists(media_file)
    cbz_file = create_cbz(cbz_directory)
    assert basename(cbz_file) == "dvk_cbz_test.cbz"
    assert exists(cbz_file)
    assert sorted(listdir(cbz_directory)) == ["dvk_cbz_test.cbz", "other"]
    sub_directory = abspath(join(cbz_directory, "other"))
    assert sorted(listdir(sub_directory)) == ["other.txt", "text.txt"]
    extract_directory = get_temp_dir("dvk_extract_test")
    assert extract_zip(cbz_file, extract_directory)
    assert sorted(listdir(extract_directory)) == ["other"]
    sub_directory = abspath(join(extract_directory, "other"))
    assert sorted(listdir(sub_directory)) == ["other.txt", "text.txt"]
    # Test creating CBZ with existing directories and a Name
    cbz_directory = get_temp_dir("dvk_cbz_test")
    directory_a = abspath(join(cbz_directory, "AA"))
    directory_b = abspath(join(cbz_directory, "BB"))
    text_file = abspath(join(directory_a, "text.txt"))
    media_file = abspath(join(directory_b, "media.png"))
    mkdir(directory_a)
    mkdir(directory_b)
    write_text_file(text_file, "Text in A")
    write_text_file(media_file, "Not actually png")
    assert exists(text_file)
    assert exists(media_file)
    cbz_file = create_cbz(cbz_directory, "Totally Cool!")
    assert basename(cbz_file) == "Totally Cool!.cbz"
    assert exists(cbz_file)
    assert exists(directory_a)
    assert exists(directory_b)
    extract_directory = get_temp_dir("dvk_extract_test")
    assert extract_zip(cbz_file, extract_directory)
    assert sorted(listdir(extract_directory)) == ["AA", "BB"]
    directory_a = abspath(join(extract_directory, "AA"))
    directory_b = abspath(join(extract_directory, "BB"))
    assert listdir(directory_a) == ["text.txt"]
    assert listdir(directory_b) == ["media.png"]
    # Test creating CBZ with metadata
    remove(cbz_file)
    metadata = get_empty_metadata()
    metadata["title"] = "What Fun!"
    metadata["artist"] = "Person"
    cbz_file = create_cbz(cbz_directory, "New", metadata=metadata)
    assert sorted(listdir(cbz_directory)) == ["AA", "BB", "New.cbz"]
    extract_directory = get_temp_dir("dvk_extract_test")
    assert extract_zip(cbz_file, extract_directory)
    assert sorted(listdir(extract_directory)) == ["AA", "BB", "ComicInfo.xml"]
    read_meta = read_comic_info(abspath(join(extract_directory, "ComicInfo.xml")))
    assert read_meta["title"] == "What Fun!"
    assert read_meta["artist"] == "Person"
    # Test creating CBZ while removing remaining files
    remove(cbz_file)
    media_file = abspath(join(cbz_directory, "Another_one.txt"))
    write_text_file(media_file, "Some more text.")
    assert exists(media_file)
    cbz_file = create_cbz(cbz_directory, "Another", metadata=metadata, remove_files=True)
    assert listdir(cbz_directory) == ["Another.cbz"]
    extract_directory = get_temp_dir("dvk_extract_test")
    assert extract_zip(cbz_file, extract_directory)
    assert sorted(listdir(extract_directory)) == ["AA", "Another_one.txt", "BB", "ComicInfo.xml"]
    # Test creating CBZ with metadata and no subdirectories
    cbz_directory = get_temp_dir("dvk_cbz_test")
    text_file = abspath(join(cbz_directory, "new"))
    media_file = abspath(join(cbz_directory, "things.txt"))
    write_text_file(text_file, "NEWER")
    write_text_file(media_file, "More things")
    assert exists(text_file)
    assert exists(media_file)
    cbz_file = create_cbz(cbz_directory, "new", metadata=metadata, remove_files=True)
    assert listdir(cbz_directory) == ["new.cbz"]
    extract_directory = get_temp_dir("dvk_extract_test")
    assert extract_zip(cbz_file, extract_directory)
    assert sorted(listdir(extract_directory)) == ["ComicInfo.xml", "new-2"]
    sub_directory = abspath(join(extract_directory, "new-2"))
    assert sorted(listdir(sub_directory)) == ["new", "things.txt"]
    # Test that CBZ is only updated with new metadata if CBZ already exists
    metadata["title"] = "New!"
    metadata["tags"] = "Some, More, Stuff"
    cbz_file = create_cbz(cbz_directory, "new", metadata=metadata)
    assert listdir(cbz_directory) == ["new.cbz"]
    extract_directory = get_temp_dir("dvk_extract_test")
    assert extract_zip(cbz_file, extract_directory)
    assert sorted(listdir(extract_directory)) == ["ComicInfo.xml", "new-2"]
    sub_directory = abspath(join(extract_directory, "new-2"))
    assert sorted(listdir(sub_directory)) == ["new", "things.txt"]
    read_meta = read_comic_info(abspath(join(extract_directory, "ComicInfo.xml")))
    assert read_meta["title"] == "New!"
    assert read_meta["tags"] == "Some,More,Stuff"
    assert read_meta["artist"] == "Person"
    # Test creating a CBZ with no files
    cbz_directory = get_temp_dir("dvk_cbz_test")
    assert create_cbz(cbz_directory) is None

def test_get_info_from_cbz():
    """
    Tests the get_info_from_cbz file
    """
    # Create test cbz file.
    temp_dir = get_temp_dir()
    metadata = get_empty_metadata()
    metadata["title"] = "CBZ Title!"
    metadata["tags"] = "Some,Tags"
    text_file = abspath(join(temp_dir, "text.txt"))
    write_text_file(text_file, "Text")
    assert exists(text_file)
    cbz_file = create_cbz(temp_dir, metadata=metadata)
    assert exists(cbz_file)
    # Test extracting the ComicInfo from .cbz file
    read_meta = get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "CBZ Title!"
    assert read_meta["tags"] == "Some,Tags"
    # Test trying to get ComicInfo when not present in .cbz file
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    write_text_file(text_file, "Total Text")
    assert exists(text_file)
    cbz_file = create_cbz(temp_dir)
    assert len(listdir(temp_dir)) == 2
    assert exists(cbz_file)
    read_meta = get_info_from_cbz(cbz_file)
    assert read_meta["title"] is None
    assert read_meta["artist"] is None
    # Test if file is not cbz
    text_file = abspath(join(temp_dir, "text.txt"))
    write_text_file(text_file, "Text")
    read_meta = get_info_from_cbz(text_file)
    assert read_meta["title"] is None
    assert read_meta["artist"] is None
    # Test if ComicInfo.xml is not in the home directory
    temp_dir = get_temp_dir()
    sub_dir = abspath(join(temp_dir, "Internal"))
    text_file = abspath(join(sub_dir, "Thing.txt"))
    metadata_file = abspath(join(sub_dir, "ComicInfo.xml"))
    metadata = get_empty_metadata()
    metadata["title"] = "Internal!"
    metadata["artist"] = "New Person"
    metadata["description"] = "Some words."
    mkdir(sub_dir)
    write_text_file(text_file, "Text")
    write_text_file(metadata_file, get_comic_xml(metadata))
    assert exists(text_file)
    assert exists(metadata_file)
    cbz_file = abspath(join(temp_dir, "manual.cbz"))
    assert create_zip(temp_dir, cbz_file)
    assert exists(cbz_file)
    read_meta = get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "Internal!"
    assert read_meta["artist"] == "New Person"
    assert read_meta["description"] == "Some words."
    assert read_meta["publisher"] is None
    # Test getting metadata if instructed to not search subdirectories
    assert get_info_from_cbz(cbz_file, False) == get_empty_metadata()
    

def test_update_cbz_info():
    """
    Tests the update_cbz_info function.
    """
    # Create a test cbz file
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "other.txt"))
    metadata = get_empty_metadata()
    metadata["title"] = "Old Title."
    metadata["tags"] = "Some,Tags"
    write_text_file(text_file, "This is text!")
    assert exists(text_file)
    cbz_file = create_cbz(temp_dir, metadata=metadata)
    assert exists(cbz_file)
    # Update cbz with new info
    metadata["title"] = "New Title!!!"
    metadata["artist"] = "Dude"
    metadata["tags"] = "Something,Else"
    update_cbz_info(cbz_file, metadata)
    read_meta = get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "New Title!!!"
    assert read_meta["artist"] == "Dude"
    assert read_meta["tags"] == "Something,Else"
    # Test that all other archived files are still present
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    assert extract_zip(cbz_file, extract_dir)
    assert sorted(listdir(extract_dir)) == ["ComicInfo.xml", "Old Title"]
    assert listdir(abspath(join(extract_dir, "Old Title"))) == ["other.txt"]
    # Test updating cbz that had no comic info in the first place
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    other_file = abspath(join(temp_dir, "other.txt"))
    write_text_file(text_file, "This is text!")
    write_text_file(other_file, "More text!")
    assert exists(text_file)
    assert exists(other_file)
    cbz_file = create_cbz(temp_dir)
    assert exists(cbz_file)
    read_meta = get_info_from_cbz(cbz_file)
    assert read_meta["title"] is None
    update_cbz_info(cbz_file, metadata)
    read_meta = get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "New Title!!!"
    assert read_meta["artist"] == "Dude"
    assert read_meta["tags"] == "Something,Else"
    # Test that files are present
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    assert extract_zip(cbz_file, extract_dir)
    assert sorted(listdir(extract_dir)) == ["ComicInfo.xml", "other"]
    assert sorted(listdir(abspath(join(extract_dir, "other")))) == ["other.txt", "text.txt"]
    # Test trying to update non-cbz file
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    write_text_file(text_file, "Some text")
    update_cbz_info(text_file, metadata)
    assert exists(text_file)
    assert read_text_file(text_file) == "Some text"
    # Test updating cbz with ComicInfo.xml mixed in with media files
    temp_dir = get_temp_dir()
    sub_dir = abspath(join(temp_dir, "Internal"))
    text_file = abspath(join(sub_dir, "Thing.txt"))
    media_file = abspath(join(temp_dir, "Other.png"))
    metadata_file = abspath(join(sub_dir, "ComicInfo.xml"))
    mkdir(sub_dir)
    write_text_file(text_file, "Text")
    write_text_file(media_file, "This is media")
    write_text_file(metadata_file, get_comic_xml(metadata))
    assert exists(text_file)
    assert exists(media_file)
    assert exists(metadata_file)
    cbz_file = abspath(join(temp_dir, "manual.cbz"))
    assert create_zip(temp_dir, cbz_file)
    assert exists(cbz_file)
    metadata = get_empty_metadata()
    metadata["title"] = "Updated!"
    metadata["artist"] = "New"
    update_cbz_info(cbz_file, metadata)
    read_meta = get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "Updated!"
    assert read_meta["artist"] == "New"
    assert read_meta["description"] is None
    extract_dir = abspath(join(temp_dir, "extracted"))
    mkdir(extract_dir)
    assert extract_zip(cbz_file, extract_dir)
    assert sorted(listdir(extract_dir)) == ["ComicInfo.xml", "Internal", "Other.png"]
    sub_dir = abspath(join(extract_dir, "Internal"))
    assert listdir(sub_dir) == ["Thing.txt"]
    # Test that updating adds the correctly named internal folder
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    write_text_file(text_file, "text")
    assert exists(text_file)
    cbz_file = abspath(join(temp_dir, "internal.cbz"))
    assert create_zip(temp_dir, cbz_file)
    assert exists(cbz_file)
    metadata["title"] = "Should Reflect Inside."
    update_cbz_info(cbz_file, metadata)
    read_meta = get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "Should Reflect Inside."
    assert read_meta["artist"] == "New"
    assert read_meta["description"] is None
    extract_dir = abspath(join(temp_dir, "extracted"))
    mkdir(extract_dir)
    assert extract_zip(cbz_file, extract_dir)
    assert sorted(listdir(extract_dir)) == ["ComicInfo.xml", "Should Reflect Inside"]
    sub_dir = abspath(join(extract_dir, "Should Reflect Inside"))
    assert listdir(sub_dir) == ["text.txt"]
