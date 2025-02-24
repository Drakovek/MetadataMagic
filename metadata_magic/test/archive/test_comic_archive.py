#!/usr/bin/env python3

import os
import shutil
import tempfile
import metadata_magic.test as mm_test
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive as mm_archive
import metadata_magic.archive.comic_xml as mm_comic_xml
import metadata_magic.archive.comic_archive as mm_comic_archive
from os.path import abspath, exists, join

def test_create_cbz():
    """
    Tests the create_cbz function.
    """
    # Test creating a CBZ file with no metadata, ignoring dotfiles
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_directory = abspath(join(temp_dir, "extract"))
        os.mkdir(extract_directory)
        image_directory = abspath(join(temp_dir, "images"))
        shutil.copytree(mm_test.PAIR_IMAGE_DIRECTORY, image_directory)
        cbz_file = mm_comic_archive.create_cbz(image_directory)
        assert sorted(os.listdir(image_directory)) == [".empty", "aaa", "images.cbz"]
        mm_file_tools.extract_zip(cbz_file, extract_directory)
        assert sorted(os.listdir(extract_directory)) == ["aaa"]
        files = sorted(os.listdir(abspath(join(extract_directory, "aaa"))))
        assert files == ["aaa.json", "aaa.webp", "bare.PNG.json", "bare.png", "long.JPG", "long.JSON"]
    # Test creating a CBZ file with a name and existing directories
    with tempfile.TemporaryDirectory() as temp_dir:
        a_directory = abspath(join(temp_dir, "[AA]"))
        b_directory = abspath(join(temp_dir, "[BB]"))
        shutil.copytree(mm_test.PAIR_IMAGE_DIRECTORY, a_directory)
        shutil.copytree(mm_test.PAIR_IMAGE_DIRECTORY, b_directory)
        cbz_file = mm_comic_archive.create_cbz(temp_dir, "TITLE!")
        assert sorted(os.listdir(temp_dir)) == ["TITLE!.cbz", "[AA]", "[BB]"]
        extract_directory = abspath(join(temp_dir, "extract"))
        os.mkdir(extract_directory)
        mm_file_tools.extract_zip(cbz_file, extract_directory)
        assert sorted(os.listdir(extract_directory)) == ["[AA]", "[BB]"]
        files = sorted(os.listdir(abspath(join(extract_directory, "[AA]"))))
        assert files == ["aaa.json", "aaa.webp", "bare.PNG.json", "bare.png", "long.JPG", "long.JSON"]
        files = sorted(os.listdir(abspath(join(extract_directory, "[BB]"))))
        assert files == ["aaa.json", "aaa.webp", "bare.PNG.json", "bare.png", "long.JPG", "long.JSON"]
    # Test creating a CBZ file with metadata, getting page count automatically
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_directory = abspath(join(temp_dir, "extract"))
        os.mkdir(extract_directory)
        image_directory = abspath(join(temp_dir, "images"))
        shutil.copytree(mm_test.PAIR_IMAGE_DIRECTORY, image_directory)
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "Name"
        metadata["artists"] = ["Multiple", "Artists"]
        cbz_file = mm_comic_archive.create_cbz(image_directory, metadata=metadata)
        assert sorted(os.listdir(image_directory)) == [".empty", "Name", "images.cbz"]
        mm_file_tools.extract_zip(cbz_file, extract_directory)
        assert sorted(os.listdir(extract_directory)) == ["ComicInfo.xml", "Name"]
        files = sorted(os.listdir(abspath(join(extract_directory, "Name"))))
        assert files == ["aaa.json", "aaa.webp", "bare.PNG.json", "bare.png", "long.JPG", "long.JSON"]
        xml_file = abspath(join(extract_directory, "ComicInfo.xml"))
        read_meta = mm_comic_xml.read_comic_info(xml_file)
        assert read_meta["title"] == "Name"
        assert read_meta["artists"] == ["Multiple", "Artists"]
        assert read_meta["page_count"] == "2"
    # Test creating CBZ file while removing remaining files, overwriting the page count
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_directory = abspath(join(temp_dir, "extract"))
        os.mkdir(extract_directory)
        image_directory = abspath(join(temp_dir, "images"))
        shutil.copytree(mm_test.PAIR_IMAGE_DIRECTORY, image_directory)
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "Delete"
        metadata["artists"] = ["Person"]
        metadata["page_count"] = "42"
        cbz_file = mm_comic_archive.create_cbz(image_directory, "AAA", metadata=metadata, remove_files=True)
        assert sorted(os.listdir(image_directory)) == ["AAA.cbz"]
        mm_file_tools.extract_zip(cbz_file, extract_directory)
        assert sorted(os.listdir(extract_directory)) == ["AAA", "ComicInfo.xml"]
        files = sorted(os.listdir(abspath(join(extract_directory, "AAA"))))
        assert files == ["aaa.json", "aaa.webp", "bare.PNG.json", "bare.png", "long.JPG", "long.JSON"]
        xml_file = abspath(join(extract_directory, "ComicInfo.xml"))
        read_meta = mm_comic_xml.read_comic_info(xml_file)
        assert read_meta["title"] == "Delete"
        assert read_meta["artists"] == ["Person"]
        assert read_meta["page_count"] == "2"
    # Test creating CBZ file with metadata and existing subdirectories
    with tempfile.TemporaryDirectory() as temp_dir:
        a_directory = abspath(join(temp_dir, "01"))
        b_directory = abspath(join(temp_dir, "02"))
        shutil.copytree(mm_test.PAIR_IMAGE_DIRECTORY, a_directory)
        shutil.copytree(mm_test.PAIR_IMAGE_DIRECTORY, b_directory)
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "Subdirs"
        metadata["artists"] = ["New"]
        cbz_file = mm_comic_archive.create_cbz(temp_dir, "TITLE!", metadata=metadata)
        assert sorted(os.listdir(temp_dir)) == ["01", "02", "TITLE!.cbz"]
        extract_directory = abspath(join(temp_dir, "extract"))
        os.mkdir(extract_directory)
        mm_file_tools.extract_zip(cbz_file, extract_directory)
        assert sorted(os.listdir(extract_directory)) == ["01", "02", "ComicInfo.xml"]
        files = sorted(os.listdir(abspath(join(extract_directory, "01"))))
        assert files == ["aaa.json", "aaa.webp", "bare.PNG.json", "bare.png", "long.JPG", "long.JSON"]
        files = sorted(os.listdir(abspath(join(extract_directory, "02"))))
        assert files == ["aaa.json", "aaa.webp", "bare.PNG.json", "bare.png", "long.JPG", "long.JSON"]
        xml_file = abspath(join(extract_directory, "ComicInfo.xml"))
        read_meta = mm_comic_xml.read_comic_info(xml_file)
        assert read_meta["title"] == "Subdirs"
        assert read_meta["artists"] == ["New"]
        assert read_meta["page_count"] == "4"
    # Test that any existing ComicInfo.xml files are replaced
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_directory = abspath(join(temp_dir, "extract"))
        os.mkdir(extract_directory)
        image_directory = abspath(join(temp_dir, "images"))
        shutil.copytree(mm_test.PAIR_IMAGE_DIRECTORY, image_directory)
        mm_file_tools.write_text_file(abspath(join(image_directory, "ComicInfo.xml")), "AAA")
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "Replaced"
        metadata["artists"] = ["New"]
        cbz_file = mm_comic_archive.create_cbz(image_directory, metadata=metadata)
        assert sorted(os.listdir(image_directory)) == [".empty", "Replaced", "images.cbz"]
        mm_file_tools.extract_zip(cbz_file, extract_directory)
        assert sorted(os.listdir(extract_directory)) == ["ComicInfo.xml", "Replaced"]
        files = sorted(os.listdir(abspath(join(extract_directory, "Replaced"))))
        assert files == ["aaa.json", "aaa.webp", "bare.PNG.json", "bare.png", "long.JPG", "long.JSON"]
        xml_file = abspath(join(extract_directory, "ComicInfo.xml"))
        read_meta = mm_comic_xml.read_comic_info(xml_file)
        assert read_meta["title"] == "Replaced"
        assert read_meta["artists"] == ["New"]
        assert read_meta["page_count"] == "2"
    # Test creating a CBZ file fails if there are no internal files, or only dotfiles
    with tempfile.TemporaryDirectory() as temp_dir:
        assert mm_comic_archive.create_cbz(temp_dir) is None
        mm_file_tools.write_text_file(abspath(join(temp_dir, ".01")), "AAA")
        mm_file_tools.write_text_file(abspath(join(temp_dir, ".aa")), "AAA")
        mm_file_tools.write_text_file(abspath(join(temp_dir, ".02")), "AAA")
        assert mm_comic_archive.create_cbz(temp_dir) is None

def test_get_info_from_cbz():
    """
    Tests the get_info_from_cbz file
    """
    # Test getting metadata info from a CBZ file
    cbz_file = abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "basic.CBZ"))
    metadata = mm_comic_archive.get_info_from_cbz(cbz_file)
    assert metadata["title"] == "Cómic"
    assert metadata["series"] == "Basic"
    assert metadata["series_number"] == "2.5"
    assert metadata["series_total"] == "5"
    assert metadata["description"] == "Simple Description."
    assert metadata["date"] == "2012-12-21"
    assert metadata["writers"] == ["Author"]
    assert metadata["artists"] == ["Illustrator"]
    assert metadata["cover_artists"] == ["CoverArtist"]
    assert metadata["publisher"] == "DVK"
    assert metadata["tags"] == ["Multiple", "Tags"]
    assert metadata["url"] == "/non/existant/"
    assert metadata["age_rating"] == "Everyone"
    assert metadata["score"] == "3"
    assert metadata["page_count"] == "36"
    # Test getting metadata from separate CBZ file
    base_file = abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "NoPage.cbz"))
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_file = abspath(join(temp_dir, "NoPage.cbz"))
        shutil.copy(base_file, cbz_file)
        # Test that page count is not already in cbz file
        extract_dir = abspath(join(temp_dir, "extract"))
        os.mkdir(extract_dir)
        mm_file_tools.extract_zip(cbz_file, extract_dir)
        assert sorted(os.listdir(extract_dir)) == ["B.jpeg", "ComicInfo.xml", "G.jpg", "R.png"]
        xml_file = abspath(join(extract_dir, "ComicInfo.xml"))
        metadata = read_meta = mm_comic_xml.read_comic_info(xml_file)
        assert metadata["title"] == "No Page"
        assert metadata["page_count"] is None
        # Test generating the page count if not already present in the metadata
        metadata = mm_comic_archive.get_info_from_cbz(cbz_file)
        assert metadata["page_count"] == "3"
        assert metadata["title"] == "No Page"
        assert metadata["series"] is None
        assert metadata["series_number"] is None
        assert metadata["series_total"] is None
        assert metadata["description"].startswith("Lorem ipsum odor amet, consectetuer")
        assert metadata["date"] == "2023-04-13"
        assert metadata["writers"] == ["Author"]
        assert metadata["artists"] == ["Different", "People"]
        assert metadata["cover_artists"] == ["CoverArtist"]
        assert metadata["publisher"] == "DVK"
        assert metadata["tags"] is None
        assert metadata["url"] is None
        assert metadata["age_rating"] == "Teen"
        assert metadata["score"] is None
        # Test that page count has been added to the metadata after reading
        shutil.rmtree(extract_dir)
        os.mkdir(extract_dir)
        mm_file_tools.extract_zip(cbz_file, extract_dir)
        assert sorted(os.listdir(extract_dir)) == ["ComicInfo.xml", "No Page"]
        xml_file = abspath(join(extract_dir, "ComicInfo.xml"))
        metadata = read_meta = mm_comic_xml.read_comic_info(xml_file)
        assert metadata["title"] == "No Page"
        assert metadata["page_count"] == "3"
    # Test if the ComicInfo.xml file is not in the home directory
    base_file = abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "SubInfo.CBZ"))
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test that file structure is still intact
        cbz_file = abspath(join(temp_dir, "SubInfo.cbz"))
        shutil.copy(base_file, cbz_file)
        extract_dir = abspath(join(temp_dir, "extract"))
        os.mkdir(extract_dir)
        mm_file_tools.extract_zip(cbz_file, extract_dir)
        assert sorted(os.listdir(extract_dir)) == ["Internal"]
        # Test getting metadata not in the home directory
        metadata = mm_comic_archive.get_info_from_cbz(cbz_file)
        assert metadata["title"] == "Internal"
        assert metadata["series"] == "Internal"
        assert metadata["series_number"] == "1.0"
        assert metadata["series_total"] == "1"
        assert metadata["description"] is None
        assert metadata["date"] is None
        assert metadata["writers"] is None
        assert metadata["artists"] == ["Drawer"]
        assert metadata["cover_artists"] == ["Person"]
        assert metadata["publisher"] == None
        assert metadata["tags"] == ["A", "B"]
        assert metadata["url"] == "/page/"
        assert metadata["age_rating"] == "Unknown"
        assert metadata["score"] == "5"
        assert metadata["page_count"] == "12"
        # Test that metadata won't be searched for in subdirectories if not instructed
        metadata = mm_comic_archive.get_info_from_cbz(cbz_file, False)
        assert metadata == mm_archive.get_empty_metadata()
    # Test if ComicInfo.xml is not present in the CBZ file
    cbz_file = abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "empty.cbz"))
    metadata = mm_comic_archive.get_info_from_cbz(cbz_file)
    assert metadata == mm_archive.get_empty_metadata()
    
def test_update_cbz_info():
    """
    Tests the update_cbz_info function.
    """
    # Test updating a CBZ file
    base_file = abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "basic.CBZ"))
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_file = abspath(join(temp_dir, "basic.CBZ"))
        shutil.copy(base_file, cbz_file)
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "New Title"
        metadata["tags"] = ["New", "Tags"]
        mm_comic_archive.update_cbz_info(cbz_file, metadata)
        read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
        assert read_meta["title"] == "New Title"
        assert read_meta["series"] is None
        assert read_meta["series_number"] is None
        assert read_meta["series_total"] is None
        assert read_meta["description"] is None
        assert read_meta["date"] is None
        assert read_meta["writers"] is None
        assert read_meta["artists"] is None
        assert read_meta["cover_artists"] is None
        assert read_meta["publisher"] is None
        assert read_meta["tags"] == ["New", "Tags"]
        assert read_meta["url"] is None
        assert read_meta["age_rating"] == "Unknown"
        assert read_meta["score"]  is None
        assert read_meta["page_count"] == "1"
        # Test that the existing archived files are still present
        extract_dir = abspath(join(temp_dir, "extracted"))
        os.mkdir(extract_dir)
        mm_file_tools.extract_zip(cbz_file, extract_dir)
        assert sorted(os.listdir(extract_dir)) == ["Comic", "ComicInfo.xml"]
        sub_dir = abspath(join(extract_dir, "Comic"))
        assert sorted(os.listdir(sub_dir)) == ["Comic.jpg"]
    # Test updating a CBZ file with no existing metadata
    base_file = abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "empty.cbz"))
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_file = abspath(join(temp_dir, "basic.cbz"))
        shutil.copy(base_file, cbz_file)
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "Not Empty"
        metadata["artists"] = ["New", "People"]
        mm_comic_archive.update_cbz_info(cbz_file, metadata)
        read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
        assert read_meta["title"] == "Not Empty"
        assert read_meta["series"] is None
        assert read_meta["series_number"] is None
        assert read_meta["series_total"] is None
        assert read_meta["description"] is None
        assert read_meta["date"] is None
        assert read_meta["writers"] is None
        assert read_meta["artists"] == ["New", "People"]
        assert read_meta["cover_artists"] is None
        assert read_meta["publisher"] is None
        assert read_meta["tags"] is None
        assert read_meta["url"] is None
        assert read_meta["age_rating"] == "Unknown"
        assert read_meta["score"]  is None
        assert read_meta["page_count"] == "1"
        # Test that metadata has been added while keeping images intact
        extract_dir = abspath(join(temp_dir, "extracted"))
        os.mkdir(extract_dir)
        mm_file_tools.extract_zip(cbz_file, extract_dir)
        assert sorted(os.listdir(extract_dir)) == ["ComicInfo.xml", "Not Empty"]
        sub_dir = abspath(join(extract_dir, "Not Empty"))
        assert sorted(os.listdir(sub_dir)) == ["empty.jpg"]
    # Test updating a CBZ file with metadata in an internal directory
    base_file = abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "SubInfo.CBZ"))
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_file = abspath(join(temp_dir, "basic.CBZ"))
        shutil.copy(base_file, cbz_file)
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "Moved"
        metadata["publisher"] = "Publisher"
        mm_comic_archive.update_cbz_info(cbz_file, metadata)
        read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
        assert read_meta["title"] == "Moved"
        assert read_meta["series"] is None
        assert read_meta["series_number"] is None
        assert read_meta["series_total"] is None
        assert read_meta["description"] is None
        assert read_meta["date"] is None
        assert read_meta["writers"] is None
        assert read_meta["artists"] is None
        assert read_meta["cover_artists"] is None
        assert read_meta["publisher"] == "Publisher"
        assert read_meta["tags"] is None
        assert read_meta["url"] is None
        assert read_meta["age_rating"] == "Unknown"
        assert read_meta["score"]  is None
        assert read_meta["page_count"] == "1"
        # Test that metadata has been added while keeping images intact
        extract_dir = abspath(join(temp_dir, "extracted"))
        os.mkdir(extract_dir)
        mm_file_tools.extract_zip(cbz_file, extract_dir)
        assert sorted(os.listdir(extract_dir)) == ["ComicInfo.xml", "Internal"]
        sub_dir = abspath(join(extract_dir, "Internal"))
        assert sorted(os.listdir(sub_dir)) == ["Red.jpg"]

    # Test that updating a CBZ file with the same metadata causes no overwriting
    base_file = abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "SubInfo.CBZ"))
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_file = abspath(join(temp_dir, "basic.CBZ"))
        shutil.copy(base_file, cbz_file)
        metadata = mm_comic_archive.get_info_from_cbz(cbz_file)
        mm_comic_archive.update_cbz_info(cbz_file, metadata)
        assert mm_comic_archive.get_info_from_cbz(cbz_file) == metadata
        extract_dir = abspath(join(temp_dir, "extracted"))
        os.mkdir(extract_dir)
        mm_file_tools.extract_zip(cbz_file, extract_dir)
        assert sorted(os.listdir(extract_dir)) == ["Internal"]
        sub_dir = abspath(join(extract_dir, "Internal"))
        assert sorted(os.listdir(sub_dir)) == ["ComicInfo.xml", "Red.jpg"]
        # Check that file will be overwritten even with identical metadata, if specified
        mm_comic_archive.update_cbz_info(cbz_file, metadata, True)
        read_metadata = mm_comic_archive.get_info_from_cbz(cbz_file)
        assert metadata["title"] == "Internal"
        assert metadata["page_count"] == "12"
        extract_dir = abspath(join(temp_dir, "new_extracted"))
        os.mkdir(extract_dir)
        mm_file_tools.extract_zip(cbz_file, extract_dir)
        assert sorted(os.listdir(extract_dir)) == ["ComicInfo.xml", "Internal"]
        sub_dir = abspath(join(extract_dir, "Internal"))
        assert sorted(os.listdir(sub_dir)) == ["Red.jpg"]
    # Test attempting to update a non-cbz file
    metadata = mm_archive.get_empty_metadata()
    text_file = abspath(join(mm_test.BASIC_TEXT_DIRECTORY, "latin1.txt"))
    mm_comic_archive.update_cbz_info(text_file, metadata)
    assert exists(text_file)
    assert mm_file_tools.read_text_file(text_file) == "This is lätin1."
