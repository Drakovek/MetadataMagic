#!/usr/bin/env python3

from metadata_magic.main.comic_archive.comic_archive import create_cbz
from metadata_magic.main.comic_archive.comic_archive import get_temp_dir
from metadata_magic.main.comic_archive.comic_archive import get_info_from_cbz
from metadata_magic.main.comic_archive.comic_archive import update_cbz_info
from metadata_magic.main.comic_archive.comic_xml import get_comic_xml
from metadata_magic.main.comic_archive.comic_xml import get_empty_metadata
from metadata_magic.test.temp_file_tools import create_text_file, read_text_file
from os import listdir, mkdir, pardir, remove
from os.path import abspath, basename, exists, isdir, join
from zipfile import ZipFile

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
    create_text_file(text_file, "Test text.")
    create_text_file(other_file, "Other!")
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

def test_create_cbz():
    """
    Tests the create_cbz function
    """
    # Test creating a cbz file with loose files
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    create_text_file(text_file, "Some text!")
    other_file = abspath(join(temp_dir, "other.txt"))
    create_text_file(other_file, "Other text file.")
    assert exists(text_file)
    assert exists(other_file)
    cbz = create_cbz(temp_dir)
    assert exists(cbz)
    assert basename(cbz) == basename(temp_dir) + ".cbz"
    assert abspath(join(cbz, pardir)) == temp_dir
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with ZipFile(cbz, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 2
    assert exists(abspath(join(extract_dir, "text.txt")))
    assert exists(abspath(join(extract_dir, "other.txt")))
    # Test creating a cbz file with internal directories
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "main.txt"))
    sub_dir = abspath(join(temp_dir, "sub"))
    other_file = abspath(join(sub_dir, "sub_text.txt"))
    mkdir(sub_dir)
    create_text_file(text_file, "TEXT!")
    create_text_file(other_file, "sub")
    assert exists(text_file)
    assert exists(sub_dir)
    assert exists(other_file)
    cbz = create_cbz(temp_dir)
    assert exists(cbz)
    assert basename(cbz) == basename(temp_dir) + ".cbz"
    assert abspath(join(cbz, pardir)) == temp_dir
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with ZipFile(cbz, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 2
    assert exists(abspath(join(extract_dir, "main.txt")))
    sub = abspath(join(extract_dir, "sub"))
    assert exists(sub)
    assert isdir(sub)
    assert exists(abspath(join(sub, "sub_text.txt")))
    # Test creating cbz file with multiple internal directories
    temp_dir = get_temp_dir()
    sub_dir = abspath(join(temp_dir, "sub"))
    deeper = abspath(join(sub_dir, "deeper"))
    text_file = abspath(join(temp_dir, "text.txt"))
    sub_file = abspath(join(sub_dir, "sub.txt"))
    other_sub = abspath(join(sub_dir, "sub2.txt"))
    deep_file = abspath(join(deeper, "deep.txt"))
    mkdir(sub_dir)
    mkdir(deeper)
    create_text_file(text_file, "This is text!")
    create_text_file(sub_file, "Subtext?")
    create_text_file(other_sub, "More subtext.")
    create_text_file(deep_file, "Even deeper!!!")
    assert isdir(sub_dir)
    assert isdir(deeper)
    assert exists(text_file)
    assert exists(sub_file)
    assert exists(other_sub)
    assert exists(deep_file)
    cbz = create_cbz(temp_dir)
    assert exists(cbz)
    assert basename(cbz) == basename(temp_dir) + ".cbz"
    assert abspath(join(cbz, pardir)) == temp_dir
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with ZipFile(cbz, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 2
    assert exists(abspath(join(extract_dir, "text.txt")))
    sub_dir = abspath(join(extract_dir, "sub"))
    assert isdir(sub_dir)
    assert len(listdir(sub_dir)) == 3
    assert exists(abspath(join(sub_dir, "sub.txt")))
    assert exists(abspath(join(sub_dir, "sub2.txt")))
    deeper = abspath(join(sub_dir, "deeper"))
    assert isdir(deeper)
    assert len(listdir(deeper)) == 1
    assert exists(abspath(join(deeper, "deep.txt")))
    # Test that cbz is only updated if cbz already exists
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "file.txt"))
    create_text_file(text_file, "This is some text!")
    assert exists(text_file)
    cbz = create_cbz(temp_dir)
    assert basename(cbz) == "dvk_meta_magic.cbz"
    assert exists(cbz)
    assert get_info_from_cbz(cbz) == get_empty_metadata()
    metadata = get_empty_metadata()
    metadata["title"] = "Updated!"
    metadata["tags"] = "Some,Tags!"
    xml = get_comic_xml(metadata)
    xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
    create_text_file(xml_file, xml)
    assert exists(xml_file)
    cbz = create_cbz(temp_dir)
    read_metadata = get_info_from_cbz(cbz)
    assert read_metadata["title"] == "Updated!"
    assert read_metadata["tags"] == "Some,Tags!"
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with ZipFile(cbz, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 2
    text_file = abspath(join(extract_dir, "file.txt"))
    assert exists(text_file)
    assert exists(abspath(join(extract_dir, "ComicInfo.xml")))
    assert read_text_file(text_file) == "This is some text!"
    # Test same update with no ComicInfo
    remove(xml_file)
    assert not exists(xml_file)
    assert create_cbz(temp_dir) is None
    read_metadata = get_info_from_cbz(cbz)
    assert read_metadata["title"] == "Updated!"
    assert read_metadata["tags"] == "Some,Tags!"
    # Test with non-existant file
    assert create_cbz("/non/existant/dir") is None

def test_get_info_from_cbz():
    """
    Tests the get_info_from_cbz function.
    """
    # Create test cbz file.
    temp_dir = get_temp_dir()
    xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
    metadata = get_empty_metadata()
    metadata["title"] = "CBZ Title!"
    metadata["tags"] = "Some,Tags"
    xml = get_comic_xml(metadata)
    create_text_file(xml_file, xml)
    assert exists(xml_file)
    cbz_file = create_cbz(temp_dir)
    assert len(listdir(temp_dir)) == 2
    assert exists(cbz_file)
    # Test extracting the ComicInfo from .cbz file
    read_meta = get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "CBZ Title!"
    assert read_meta["tags"] == "Some,Tags"
    # Test trying to get ComicInfo when not present in .cbz file
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    create_text_file(text_file, "Total Text")
    assert exists(text_file)
    cbz_file = create_cbz(temp_dir)
    assert len(listdir(temp_dir)) == 2
    assert exists(cbz_file)
    read_meta = get_info_from_cbz(cbz_file)
    assert read_meta["title"] is None
    assert read_meta["artist"] is None
    # Test if file is not cbz
    read_meta = get_info_from_cbz(text_file)
    assert read_meta["title"] is None
    assert read_meta["artist"] is None

def test_update_cbz_info():
    """
    Tests the update_cbz_info function.
    """
    # Create a test cbz file
    temp_dir = get_temp_dir()
    xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
    text_file = abspath(join(temp_dir, "other.txt"))
    metadata = get_empty_metadata()
    metadata["title"] = "Old title."
    metadata["tags"] = "Some,Tags"
    xml = get_comic_xml(metadata)
    create_text_file(xml_file, xml)
    create_text_file(text_file, "This is text!")
    assert exists(xml_file)
    assert exists(text_file)
    cbz_file = create_cbz(temp_dir)
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
    with ZipFile(cbz_file, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 2
    assert exists(abspath(join(extract_dir, "other.txt")))
    assert exists(abspath(join(extract_dir, "ComicInfo.xml")))
    # Test updating cbz that had no comic info in the first place
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    other_file = abspath(join(temp_dir, "other.txt"))
    create_text_file(text_file, "This is text!")
    create_text_file(other_file, "More text!")
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
    with ZipFile(cbz_file, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 3
    assert exists(abspath(join(extract_dir, "text.txt")))
    assert exists(abspath(join(extract_dir, "other.txt")))
    assert exists(abspath(join(extract_dir, "ComicInfo.xml")))
    # Test trying to update non-cbz file
    update_cbz_info(text_file, metadata)
    assert exists(text_file)
    assert read_text_file(text_file) == "This is text!"
