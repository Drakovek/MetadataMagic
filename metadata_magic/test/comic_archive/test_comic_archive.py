#!/usr/bin/env python3

from metadata_magic.main.comic_archive.comic_archive import create_cb7
from metadata_magic.main.comic_archive.comic_archive import create_cbz
from metadata_magic.main.comic_archive.comic_archive import get_temp_dir
from metadata_magic.main.comic_archive.comic_archive import get_info_from_cb7
from metadata_magic.main.comic_archive.comic_archive import get_info_from_cbz
from metadata_magic.main.comic_archive.comic_archive import get_info_from_archive
from metadata_magic.main.comic_archive.comic_archive import update_cb7_info
from metadata_magic.main.comic_archive.comic_archive import update_cbz_info
from metadata_magic.main.comic_archive.comic_archive import update_archive_info
from metadata_magic.main.comic_archive.comic_xml import get_comic_xml
from metadata_magic.main.comic_archive.comic_xml import get_empty_metadata
from metadata_magic.test.temp_file_tools import create_text_file, read_text_file
from os import listdir, mkdir, pardir, rename
from os.path import abspath, basename, exists, isdir, join
from py7zr import SevenZipFile
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
    # Test with non-existant file
    assert create_cbz("/non/existant/dir") is None

def test_create_cb7():
    """
    Tests the create_cb7 function
    """
    # Test creating a cb7 file with loose files
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    create_text_file(text_file, "Some text!")
    other_file = abspath(join(temp_dir, "other.txt"))
    create_text_file(other_file, "Other text file.")
    assert exists(text_file)
    assert exists(other_file)
    cb7 = create_cb7(temp_dir)
    assert exists(cb7)
    assert basename(cb7) == basename(temp_dir) + ".cb7"
    assert abspath(join(cb7, pardir)) == temp_dir
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with SevenZipFile(cb7, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 2
    assert exists(abspath(join(extract_dir, "text.txt")))
    assert exists(abspath(join(extract_dir, "other.txt")))
    # Test creating a cb7 file with internal directories
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
    cb7 = create_cb7(temp_dir)
    assert exists(cb7)
    assert basename(cb7) == basename(temp_dir) + ".cb7"
    assert abspath(join(cb7, pardir)) == temp_dir
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with SevenZipFile(cb7, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 2
    assert exists(abspath(join(extract_dir, "main.txt")))
    sub = abspath(join(extract_dir, "sub"))
    assert exists(sub)
    assert isdir(sub)
    assert exists(abspath(join(sub, "sub_text.txt")))
    # Test creating cb7 file with multiple internal directories
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
    cb7 = create_cb7(temp_dir)
    assert exists(cb7)
    assert basename(cb7) == basename(temp_dir) + ".cb7"
    assert abspath(join(cb7, pardir)) == temp_dir
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with SevenZipFile(cb7, mode="r") as file:
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
    # Test with non-existant file
    assert create_cb7("/non/existant/dir") is None

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

def test_get_info_from_cb7():
    """
    Tests the get_info_from_cb7 function.
    """
    # Create test cb7 file.
    temp_dir = get_temp_dir()
    xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
    metadata = get_empty_metadata()
    metadata["title"] = "CB7 Title!"
    metadata["tags"] = "Some,Tags"
    xml = get_comic_xml(metadata)
    create_text_file(xml_file, xml)
    assert exists(xml_file)
    cb7_file = create_cb7(temp_dir)
    assert len(listdir(temp_dir)) == 2
    assert exists(cb7_file)
    # Test extracting the ComicInfo from .cb7 file
    read_meta = get_info_from_cb7(cb7_file)
    assert read_meta["title"] == "CB7 Title!"
    assert read_meta["tags"] == "Some,Tags"
    # Test trying to get ComicInfo when not present in .cb7 file
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    create_text_file(text_file, "Total Text")
    assert exists(text_file)
    cb7_file = create_cb7(temp_dir)
    assert len(listdir(temp_dir)) == 2
    assert exists(cb7_file)
    read_meta = get_info_from_cb7(cb7_file)
    assert read_meta["title"] is None
    assert read_meta["artist"] is None
    # Test if file is not cb7
    read_meta = get_info_from_cb7(text_file)
    assert read_meta["title"] is None
    assert read_meta["artist"] is None

def test_update_cb7_info():
    """
    Tests the update_cb7_info function.
    """
    # Create a test cb7 file
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
    cb7_file = create_cb7(temp_dir)
    assert exists(cb7_file)
    # Update cb7 with new info
    metadata["title"] = "New Title!!!"
    metadata["artist"] = "Dude"
    metadata["tags"] = "Something,Else"
    update_cb7_info(cb7_file, metadata)
    read_meta = get_info_from_cb7(cb7_file)
    assert read_meta["title"] == "New Title!!!"
    assert read_meta["artist"] == "Dude"
    assert read_meta["tags"] == "Something,Else"
    # Test that all other archived files are still present
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with SevenZipFile(cb7_file, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 2
    assert exists(abspath(join(extract_dir, "other.txt")))
    assert exists(abspath(join(extract_dir, "ComicInfo.xml")))
    # Test updating cb7 that had no comic info in the first place
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    other_file = abspath(join(temp_dir, "other.txt"))
    create_text_file(text_file, "This is text!")
    create_text_file(other_file, "More text!")
    assert exists(text_file)
    assert exists(other_file)
    cb7_file = create_cb7(temp_dir)
    assert exists(cb7_file)
    read_meta = get_info_from_cb7(cb7_file)
    assert read_meta["title"] is None
    update_cb7_info(cb7_file, metadata)
    read_meta = get_info_from_cb7(cb7_file)
    assert read_meta["title"] == "New Title!!!"
    assert read_meta["artist"] == "Dude"
    assert read_meta["tags"] == "Something,Else"
    # Test that files are present
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with SevenZipFile(cb7_file, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 3
    assert exists(abspath(join(extract_dir, "text.txt")))
    assert exists(abspath(join(extract_dir, "other.txt")))
    assert exists(abspath(join(extract_dir, "ComicInfo.xml")))
    # Test trying to update non-cb7 file
    update_cb7_info(text_file, metadata)
    assert exists(text_file)
    assert read_text_file(text_file) == "This is text!"

def test_get_info_from_archive():
    """
    Tests the get_info_from_archive function.
    """
    # Create a test .cbz file
    temp_dir = get_temp_dir()
    xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
    text_file = abspath(join(temp_dir, "other.txt"))
    metadata = get_empty_metadata()
    metadata["title"] = "This is CBZ"
    metadata["tags"] = "Tag things,yay"
    xml = get_comic_xml(metadata)
    create_text_file(xml_file, xml)
    create_text_file(text_file, "This is text!")
    assert exists(xml_file)
    assert exists(text_file)
    cbz_file = create_cbz(temp_dir)
    assert exists(cbz_file)
    # Test getting info from .cbz
    read_meta = get_info_from_archive(cbz_file)
    assert read_meta["title"] == "This is CBZ"
    assert read_meta["tags"] == "Tag things,yay"
    # Create a test .cb7 file
    temp_dir = get_temp_dir()
    xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
    text_file = abspath(join(temp_dir, "new.txt"))
    metadata = get_empty_metadata()
    metadata["title"] = "CB7 this time."
    metadata["tags"] = "more,tags"
    xml = get_comic_xml(metadata)
    create_text_file(xml_file, xml)
    create_text_file(text_file, "This is text!")
    assert exists(xml_file)
    assert exists(text_file)
    cb7_file = create_cb7(temp_dir)
    assert exists(cb7_file)
    # Test getting info from .cb7
    read_meta = get_info_from_archive(cb7_file)
    assert read_meta["title"] == "CB7 this time."
    assert read_meta["tags"] == "more,tags"
    # Test getting info from improperly labeled cbz
    temp_dir = get_temp_dir()
    xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
    text_file = abspath(join(temp_dir, "other.txt"))
    metadata = get_empty_metadata()
    metadata["title"] = "Not Labeled"
    metadata["description"] = "words"
    xml = get_comic_xml(metadata)
    create_text_file(xml_file, xml)
    create_text_file(text_file, "This is text!")
    assert exists(xml_file)
    assert exists(text_file)
    archive_file = create_cbz(temp_dir)
    rename(archive_file, abspath(join(temp_dir, "weird_extension.dvk")))
    assert not exists(cbz_file)
    cbz_file = abspath(join(temp_dir, "weird_extension.dvk"))
    assert exists(cbz_file)
    read_meta = get_info_from_archive(cbz_file)
    assert read_meta["title"] == "Not Labeled"
    assert read_meta["tags"] is None
    assert read_meta["description"] == "words"
    # Test getting info from improperly labeled cb7
    temp_dir = get_temp_dir()
    xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
    text_file = abspath(join(temp_dir, "other.txt"))
    metadata = get_empty_metadata()
    metadata["title"] = "Also Unlabeled"
    metadata["description"] = "thing"
    xml = get_comic_xml(metadata)
    create_text_file(xml_file, xml)
    create_text_file(text_file, "This is text!")
    assert exists(xml_file)
    assert exists(text_file)
    archive_file = create_cb7(temp_dir)
    rename(archive_file, abspath(join(temp_dir, "ext.dvk")))
    assert not exists(cbz_file)
    cb7_file = abspath(join(temp_dir, "ext.dvk"))
    assert exists(cb7_file)
    read_meta = get_info_from_archive(cb7_file)
    assert read_meta["title"] == "Also Unlabeled"
    assert read_meta["tags"] is None
    assert read_meta["description"] == "thing"
    # Test getting info from non-archive file
    read_meta = get_info_from_archive(text_file)
    assert read_meta["title"] is None
    assert read_meta["description"] is None

def test_update_archive_info():
    """
    Test the update_archive function.
    """
    # Create a test .cbz file
    temp_dir = get_temp_dir()
    xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
    text_file = abspath(join(temp_dir, "other.txt"))
    metadata = get_empty_metadata()
    metadata["title"] = "This is CBZ"
    metadata["tags"] = "Tag things,yay"
    xml = get_comic_xml(metadata)
    create_text_file(xml_file, xml)
    create_text_file(text_file, "This is text!")
    assert exists(xml_file)
    assert exists(text_file)
    cbz_file = create_cbz(temp_dir)
    assert exists(cbz_file)
    # Tests updating info in .cbz
    metadata = get_empty_metadata()
    metadata["title"] = "New Title"
    metadata["description"] = "blah"
    update_archive_info(cbz_file, metadata)
    read_meta = get_info_from_cbz(cbz_file)
    assert read_meta["title"] == "New Title"
    assert read_meta["description"] == "blah"
    # Create a test .cb7 file
    temp_dir = get_temp_dir()
    xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
    text_file = abspath(join(temp_dir, "other.txt"))
    metadata = get_empty_metadata()
    metadata["title"] = "Unimportant"
    metadata["description"] = "Won't Exist"
    xml = get_comic_xml(metadata)
    create_text_file(xml_file, xml)
    create_text_file(text_file, "This is text!")
    assert exists(xml_file)
    assert exists(text_file)
    cb7_file = create_cb7(temp_dir)
    assert exists(cb7_file)
    # Test updating info in .cb7
    metadata = get_empty_metadata()
    metadata["title"] = "Thing"
    metadata["description"] = "Other Thing"
    update_archive_info(cb7_file, metadata)
    read_meta = get_info_from_cb7(cb7_file)
    assert read_meta["title"] == "Thing"
    assert read_meta["description"] == "Other Thing"
    # Test updating info in improperly labeled cbz
    temp_dir = get_temp_dir()
    xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
    text_file = abspath(join(temp_dir, "other.txt"))
    metadata = get_empty_metadata()
    metadata["title"] = "Bleh"
    xml = get_comic_xml(metadata)
    create_text_file(xml_file, xml)
    create_text_file(text_file, "This is text!")
    assert exists(xml_file)
    assert exists(text_file)
    cbz_file = create_cbz(temp_dir)
    rename(cbz_file, abspath(join(temp_dir, "new.dvk")))
    assert not exists(cbz_file)
    cbz_file = abspath(join(temp_dir, "new.dvk"))
    assert exists(cbz_file)
    metadata = get_empty_metadata()
    metadata["title"] = "New"
    metadata["description"] = "Thing"
    update_archive_info(cbz_file, metadata)
    read_meta = get_info_from_archive(cbz_file)
    assert read_meta["title"] == "New"
    assert read_meta["description"] == "Thing"
    # Test updating info in improperly labeled cb7
    temp_dir = get_temp_dir()
    xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
    text_file = abspath(join(temp_dir, "other.txt"))
    metadata = get_empty_metadata()
    metadata["title"] = "Bleh"
    xml = get_comic_xml(metadata)
    create_text_file(xml_file, xml)
    create_text_file(text_file, "This is text!")
    assert exists(xml_file)
    assert exists(text_file)
    cb7_file = create_cb7(temp_dir)
    rename(cb7_file, abspath(join(temp_dir, "new.dvk")))
    assert not exists(cb7_file)
    cb7_file = abspath(join(temp_dir, "new.dvk"))
    assert exists(cb7_file)
    metadata = get_empty_metadata()
    metadata["title"] = "Other"
    metadata["description"] = "Words"
    update_archive_info(cbz_file, metadata)
    read_meta = get_info_from_archive(cbz_file)
    assert read_meta["title"] == "Other"
    assert read_meta["description"] == "Words"
    # Test updating info in non-archive
    update_archive_info(text_file, metadata)
    assert read_text_file(text_file) == "This is text!"