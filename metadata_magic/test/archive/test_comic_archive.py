#!/usr/bin/env python3

import os
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.comic_xml as mm_comic_xml
import metadata_magic.archive.comic_archive as mm_comic_archive
from os.path import abspath, basename, exists, join

def test_create_cbz():
    """
    Tests the create_cbz function.
    """
    # Test creating a CBZ with loose files and no name
    cbz_directory = mm_file_tools.get_temp_dir("dvk_cbz_test")
    text_file = abspath(join(cbz_directory, "text.txt"))
    media_file = abspath(join(cbz_directory, "other.txt"))
    mm_file_tools.write_text_file(text_file, "TEXT!")
    mm_file_tools.write_text_file(media_file, "Yet more text.")
    assert exists(text_file)
    assert exists(media_file)
    cbz_file = mm_comic_archive.create_cbz(cbz_directory)
    assert basename(cbz_file) == "dvk_cbz_test.cbz"
    assert exists(cbz_file)
    assert sorted(os.listdir(cbz_directory)) == ["dvk_cbz_test.cbz", "other"]
    sub_directory = abspath(join(cbz_directory, "other"))
    assert sorted(os.listdir(sub_directory)) == ["other.txt", "text.txt"]
    extract_directory = mm_file_tools.get_temp_dir("dvk_extract_test")
    assert mm_file_tools.extract_zip(cbz_file, extract_directory)
    assert sorted(os.listdir(extract_directory)) == ["other"]
    sub_directory = abspath(join(extract_directory, "other"))
    assert sorted(os.listdir(sub_directory)) == ["other.txt", "text.txt"]
    # Test creating CBZ with existing directories and a Name
    cbz_directory = mm_file_tools.get_temp_dir("dvk_cbz_test")
    directory_a = abspath(join(cbz_directory, "AA"))
    directory_b = abspath(join(cbz_directory, "BB"))
    text_file = abspath(join(directory_a, "text.txt"))
    media_file = abspath(join(directory_b, "media.png"))
    os.mkdir(directory_a)
    os.mkdir(directory_b)
    mm_file_tools.write_text_file(text_file, "Text in A")
    mm_file_tools.write_text_file(media_file, "Not actually png")
    assert exists(text_file)
    assert exists(media_file)
    cbz_file = mm_comic_archive.create_cbz(cbz_directory, "Totally Cool!")
    assert basename(cbz_file) == "Totally Cool!.cbz"
    assert exists(cbz_file)
    assert exists(directory_a)
    assert exists(directory_b)
    extract_directory = mm_file_tools.get_temp_dir("dvk_extract_test")
    assert mm_file_tools.extract_zip(cbz_file, extract_directory)
    assert sorted(os.listdir(extract_directory)) == ["AA", "BB"]
    directory_a = abspath(join(extract_directory, "AA"))
    directory_b = abspath(join(extract_directory, "BB"))
    assert os.listdir(directory_a) == ["text.txt"]
    assert os.listdir(directory_b) == ["media.png"]
    # Test creating CBZ with metadata
    os.remove(cbz_file)
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "What Fun!"
    metadata["artists"] = "Person"
    cbz_file = mm_comic_archive.create_cbz(cbz_directory, "New", metadata=metadata)
    assert sorted(os.listdir(cbz_directory)) == ["AA", "BB", "New.cbz"]
    extract_directory = mm_file_tools.get_temp_dir("dvk_extract_test")
    assert mm_file_tools.extract_zip(cbz_file, extract_directory)
    assert sorted(os.listdir(extract_directory)) == ["AA", "BB", "ComicInfo.xml"]
    read_meta = mm_comic_xml.read_comic_info(abspath(join(extract_directory, "ComicInfo.xml")))
    assert read_meta["title"] == "What Fun!"
    assert read_meta["artists"] == "Person"
    # Test creating CBZ while removing remaining files
    os.remove(cbz_file)
    media_file = abspath(join(cbz_directory, "Another_one.txt"))
    mm_file_tools.write_text_file(media_file, "Some more text.")
    assert exists(media_file)
    cbz_file = mm_comic_archive.create_cbz(cbz_directory, "Another", metadata=metadata, remove_files=True)
    assert os.listdir(cbz_directory) == ["Another.cbz"]
    extract_directory = mm_file_tools.get_temp_dir("dvk_extract_test")
    assert mm_file_tools.extract_zip(cbz_file, extract_directory)
    assert sorted(os.listdir(extract_directory)) == ["AA", "Another_one.txt", "BB", "ComicInfo.xml"]
    # Test creating CBZ with metadata and no subdirectories
    cbz_directory = mm_file_tools.get_temp_dir("dvk_cbz_test")
    text_file = abspath(join(cbz_directory, "new"))
    media_file = abspath(join(cbz_directory, "things.txt"))
    mm_file_tools.write_text_file(text_file, "NEWER")
    mm_file_tools.write_text_file(media_file, "More things")
    assert exists(text_file)
    assert exists(media_file)
    cbz_file = mm_comic_archive.create_cbz(cbz_directory, "new", metadata=metadata, remove_files=True)
    assert sorted(os.listdir(cbz_directory)) == ["new.cbz"]
    extract_directory = mm_file_tools.get_temp_dir("dvk_extract_test")
    assert mm_file_tools.extract_zip(cbz_file, extract_directory)
    assert sorted(os.listdir(extract_directory)) == ["ComicInfo.xml", "new-2"]
    sub_directory = abspath(join(extract_directory, "new-2"))
    assert sorted(os.listdir(sub_directory)) == ["new", "things.txt"]
    # Test if an existing CBZ file with the given name already exists
    metadata["title"] = "New!"
    metadata["tags"] = "Some, More, Stuff"
    cbz_file = mm_comic_archive.create_cbz(cbz_directory, "new", metadata=metadata)
    assert sorted(os.listdir(cbz_directory)) == ["new", "new-2.cbz"]
    extract_directory = mm_file_tools.get_temp_dir("dvk_extract_test")
    assert mm_file_tools.extract_zip(cbz_file, extract_directory)
    assert sorted(os.listdir(extract_directory)) == ["ComicInfo.xml", "new"]
    sub_directory = abspath(join(extract_directory, "new"))
    assert sorted(os.listdir(sub_directory)) == ["new.cbz"]
    read_meta = mm_comic_xml.read_comic_info(abspath(join(extract_directory, "ComicInfo.xml")))
    assert read_meta["title"] == "New!"
    assert read_meta["tags"] == "Some,More,Stuff"
    assert read_meta["artists"] == "Person"
    # Test extra ComicInfo.xml file is not created
    cbz_directory = mm_file_tools.get_temp_dir("dvk_cbz_test")
    text_file = abspath(join(cbz_directory, "text.txt"))
    metadata_file = abspath(join(cbz_directory, "ComicInfo.xml"))
    mm_file_tools.write_text_file(text_file, "This is text.")
    mm_file_tools.write_text_file(metadata_file, "metadata")
    assert exists(text_file)
    assert exists(metadata_file)
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "New Metadata"
    cbz_file = mm_comic_archive.create_cbz(cbz_directory, "Meta", metadata=metadata)
    assert exists(cbz_file)
    extract_directory = mm_file_tools.get_temp_dir("dvk_extract_test")
    assert mm_file_tools.extract_zip(cbz_file, extract_directory)
    assert sorted(os.listdir(extract_directory)) == ["ComicInfo.xml", "Meta"]
    sub_dir = abspath(join(extract_directory, "Meta"))
    assert sorted(os.listdir(sub_dir)) == ["text.txt"]    
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "New Metadata"
    assert read_meta["artists"] is None
    # Test creating a CBZ with no files
    cbz_directory = mm_file_tools.get_temp_dir("dvk_cbz_test")
    assert mm_comic_archive.create_cbz(cbz_directory) is None
    # Test that dotfiles are not included
    cbz_directory = mm_file_tools.get_temp_dir("dvk_cbz_test")
    text_file = abspath(join(cbz_directory, "text.txt"))
    dot_file = abspath(join(cbz_directory, ".other"))
    mm_file_tools.write_text_file(text_file, "TEXT!")
    mm_file_tools.write_text_file(dot_file, "Don't Include")
    assert exists(text_file)
    assert exists(dot_file)
    cbz_file = mm_comic_archive.create_cbz(cbz_directory, "dot")
    assert basename(cbz_file) == "dot.cbz"
    assert exists(cbz_file)
    assert sorted(os.listdir(cbz_directory)) == ["dot", "dot.cbz"]
    sub_directory = abspath(join(cbz_directory, "dot"))
    assert sorted(os.listdir(sub_directory)) == [".other", "text.txt"]
    extract_directory = mm_file_tools.get_temp_dir("dvk_extract_test")
    assert mm_file_tools.extract_zip(cbz_file, extract_directory)
    assert sorted(os.listdir(extract_directory)) == ["dot"]
    sub_directory = abspath(join(extract_directory, "dot"))
    assert sorted(os.listdir(sub_directory)) == ["text.txt"]

def test_get_info_from_cbz():
    """
    Tests the get_info_from_cbz file
    """
    # Create test cbz file.
    temp_dir = mm_file_tools.get_temp_dir()
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "CBZ Title!"
    metadata["tags"] = "Some,Tags"
    text_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "Text")
    assert exists(text_file)
    cbz_file = mm_comic_archive.create_cbz(temp_dir, metadata=metadata)
    assert exists(cbz_file)
    # Test extracting the ComicInfo from .cbz file
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "CBZ Title!"
    assert read_meta["tags"] == "Some,Tags"
    # Test trying to get ComicInfo when not present in .cbz file
    temp_dir = mm_file_tools.get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "Total Text")
    assert exists(text_file)
    cbz_file = mm_comic_archive.create_cbz(temp_dir)
    assert len(os.listdir(temp_dir)) == 2
    assert exists(cbz_file)
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
    assert read_meta["title"] is None
    assert read_meta["artists"] is None
    # Test if file is not cbz
    text_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "Text")
    read_meta = mm_comic_archive.get_info_from_cbz(text_file)
    assert read_meta == mm_archive.get_empty_metadata()
    zip_file = abspath(join(temp_dir, "not_cbz.cbz"))
    mm_file_tools.create_zip(temp_dir, zip_file)
    read_meta = mm_comic_archive.get_info_from_cbz(zip_file)
    assert read_meta == mm_archive.get_empty_metadata()
    # Test if ComicInfo.xml is not in the home directory
    temp_dir = mm_file_tools.get_temp_dir()
    sub_dir = abspath(join(temp_dir, "Internal"))
    text_file = abspath(join(sub_dir, "Thing.txt"))
    metadata_file = abspath(join(sub_dir, "ComicInfo.xml"))
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Internal!"
    metadata["artists"] = "New Person"
    metadata["description"] = "Some words."
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(text_file, "Text")
    mm_file_tools.write_text_file(metadata_file, mm_comic_xml.get_comic_xml(metadata))
    assert exists(text_file)
    assert exists(metadata_file)
    cbz_file = abspath(join(temp_dir, "manual.cbz"))
    assert mm_file_tools.create_zip(temp_dir, cbz_file)
    assert exists(cbz_file)
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "Internal!"
    assert read_meta["artists"] == "New Person"
    assert read_meta["description"] == "Some words."
    assert read_meta["publisher"] is None
    # Test getting metadata if instructed to not search subdirectories
    assert mm_comic_archive.get_info_from_cbz(cbz_file, False) == mm_archive.get_empty_metadata()
    
def test_update_cbz_info():
    """
    Tests the update_cbz_info function.
    """
    # Create a test cbz file
    temp_dir = mm_file_tools.get_temp_dir()
    text_file = abspath(join(temp_dir, "other.txt"))
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Old Title."
    metadata["tags"] = "Some,Tags"
    mm_file_tools.write_text_file(text_file, "This is text!")
    assert exists(text_file)
    cbz_file = mm_comic_archive.create_cbz(temp_dir, metadata=metadata)
    assert exists(cbz_file)
    # Update cbz with new info
    metadata["title"] = "New Title!!!"
    metadata["artists"] = "Dude"
    metadata["tags"] = "Something,Else"
    mm_comic_archive.update_cbz_info(cbz_file, metadata)
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "New Title!!!"
    assert read_meta["artists"] == "Dude"
    assert read_meta["tags"] == "Something,Else"
    # Test that all other archived files are still present
    extract_dir = abspath(join(temp_dir, "ext"))
    os.mkdir(extract_dir)
    assert mm_file_tools.extract_zip(cbz_file, extract_dir)
    assert sorted(os.listdir(extract_dir)) == ["ComicInfo.xml", "Old Title"]
    assert os.listdir(abspath(join(extract_dir, "Old Title"))) == ["other.txt"]
    # Test updating cbz that had no comic info in the first place
    temp_dir = mm_file_tools.get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    other_file = abspath(join(temp_dir, "other.txt"))
    mm_file_tools.write_text_file(text_file, "This is text!")
    mm_file_tools.write_text_file(other_file, "More text!")
    assert exists(text_file)
    assert exists(other_file)
    cbz_file = mm_comic_archive.create_cbz(temp_dir)
    assert exists(cbz_file)
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
    assert read_meta["title"] is None
    mm_comic_archive.update_cbz_info(cbz_file, metadata)
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "New Title!!!"
    assert read_meta["artists"] == "Dude"
    assert read_meta["tags"] == "Something,Else"
    # Test that files are present
    extract_dir = abspath(join(temp_dir, "ext"))
    os.mkdir(extract_dir)
    assert mm_file_tools.extract_zip(cbz_file, extract_dir)
    assert sorted(os.listdir(extract_dir)) == ["ComicInfo.xml", "other"]
    assert sorted(os.listdir(abspath(join(extract_dir, "other")))) == ["other.txt", "text.txt"]
    # Test trying to update non-cbz file
    temp_dir = mm_file_tools.get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "Some text")
    mm_comic_archive.update_cbz_info(text_file, metadata)
    assert exists(text_file)
    assert mm_file_tools.read_text_file(text_file) == "Some text"
    # Test updating cbz with ComicInfo.xml mixed in with media files
    temp_dir = mm_file_tools.get_temp_dir()
    sub_dir = abspath(join(temp_dir, "Internal"))
    text_file = abspath(join(sub_dir, "Thing.txt"))
    media_file = abspath(join(temp_dir, "Other.png"))
    metadata_file = abspath(join(sub_dir, "ComicInfo.xml"))
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(text_file, "Text")
    mm_file_tools.write_text_file(media_file, "This is media")
    mm_file_tools.write_text_file(metadata_file, mm_comic_xml.get_comic_xml(metadata))
    assert exists(text_file)
    assert exists(media_file)
    assert exists(metadata_file)
    cbz_file = abspath(join(temp_dir, "manual.cbz"))
    assert mm_file_tools.create_zip(temp_dir, cbz_file)
    assert exists(cbz_file)
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Updated!"
    metadata["artists"] = "New,Names"
    mm_comic_archive.update_cbz_info(cbz_file, metadata)
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "Updated!"
    assert read_meta["artists"] == "New,Names"
    assert read_meta["description"] is None
    extract_dir = abspath(join(temp_dir, "extracted"))
    os.mkdir(extract_dir)
    assert mm_file_tools.extract_zip(cbz_file, extract_dir)
    assert sorted(os.listdir(extract_dir)) == ["ComicInfo.xml", "Internal", "Other.png"]
    sub_dir = abspath(join(extract_dir, "Internal"))
    assert os.listdir(sub_dir) == ["Thing.txt"]
    # Test that updating adds the correctly named internal folder
    temp_dir = mm_file_tools.get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "text")
    assert exists(text_file)
    cbz_file = abspath(join(temp_dir, "internal.cbz"))
    assert mm_file_tools.create_zip(temp_dir, cbz_file)
    assert exists(cbz_file)
    metadata["title"] = "Should Reflect Inside."
    mm_comic_archive.update_cbz_info(cbz_file, metadata)
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "Should Reflect Inside."
    assert read_meta["artists"] == "New,Names"
    assert read_meta["description"] is None
    extract_dir = abspath(join(temp_dir, "extracted"))
    os.mkdir(extract_dir)
    assert mm_file_tools.extract_zip(cbz_file, extract_dir)
    assert sorted(os.listdir(extract_dir)) == ["ComicInfo.xml", "Should Reflect Inside"]
    sub_dir = abspath(join(extract_dir, "Should Reflect Inside"))
    assert os.listdir(sub_dir) == ["text.txt"]
    # Test updating a non-cbz file
    temp_dir = mm_file_tools.get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "This is text!")
    mm_comic_archive.update_cbz_info(text_file, metadata)
    assert mm_file_tools.read_text_file(text_file) == "This is text!"
