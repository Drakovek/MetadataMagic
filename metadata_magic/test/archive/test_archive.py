#!/usr/bin/env python3

import os
import shutil
import tempfile
import metadata_magic.test as mm_test
import metadata_magic.config as mm_config
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive as mm_archive
import metadata_magic.archive.epub as mm_epub
import metadata_magic.archive.comic_archive as mm_comic_archive
from os.path import abspath, join
from PIL import Image

def test_get_directory_archive_type():
    """
    Tests the get_directory_archive_type function.
    """
    # Test getting "epub" from folder with text files
    assert mm_archive.get_directory_archive_type(mm_test.PAIR_TEXT_DIRECTORY) == "epub"
    assert mm_archive.get_directory_archive_type(mm_test.PAIR_DIRECTORY) == "epub"
    # Test getting cbz from folder with images
    assert mm_archive.get_directory_archive_type(mm_test.PAIR_IMAGE_DIRECTORY) == "cbz"
    # Test getting "cbz" from subdirectory with images
    with tempfile.TemporaryDirectory() as temp_dir:
        image_subdir = abspath(join(temp_dir, "images"))
        shutil.copytree(mm_test.PAIR_IMAGE_DIRECTORY, image_subdir)
        assert mm_archive.get_directory_archive_type(temp_dir) == "cbz"
    # Test that None is returned from a directory with no relevant files
    assert mm_archive.get_directory_archive_type(mm_test.PAIR_VIDEO_DIRECTORY) is None

def test_get_empty_metadata():
    """
    Tests the get_empty_metadata function.
    """
    meta = mm_archive.get_empty_metadata()
    assert meta["title"] is None
    assert meta["series"] is None
    assert meta["series_number"] is None
    assert meta["series_total"] is None
    assert meta["description"] is None
    assert meta["date"] is None
    assert meta["writers"] is None
    assert meta["artists"] is None
    assert meta["cover_artists"] is None
    assert meta["publisher"] is None
    assert meta["tags"] is None
    assert meta["url"] is None
    assert meta["age_rating"] == None
    assert meta["score"] is None
    assert meta["page_count"] is None

def test_get_info_from_jsons():
    """
    Tests the get_info_from_jsons function.
    """
    # Test getting metadata from the lead JSON file in a directory
    config = mm_config.get_config([])
    metadata = mm_archive.get_info_from_jsons(mm_test.PAIR_IMAGE_DIRECTORY, config)
    assert metadata["title"] == "LRG"
    assert metadata["series"] is None
    assert metadata["series_number"] is None
    assert metadata["series_total"] is None
    assert metadata["description"] == "This is a description! And Another Line."
    assert metadata["date"] == "1969-07-21"
    assert metadata["writers"] == ["Multiple", "People"]
    assert metadata["artists"] == ["Multiple", "People"]
    assert metadata["cover_artists"] == ["Multiple", "People"]
    assert metadata["publisher"] == "DVK Test"
    assert metadata["tags"] == ["1", "2", "3", "4"]
    assert metadata["url"] == "https://www.non-existant-website.ca/thing/"
    assert metadata["age_rating"] == "X18+"
    assert metadata["score"] is None
    assert metadata["page_count"] is None
    # Test getting metadata from JSONs only in subdirectories
    with tempfile.TemporaryDirectory() as temp_dir:
        text_directory = abspath(join(temp_dir, "text"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, text_directory)
        metadata = mm_archive.get_info_from_jsons(temp_dir, config)
        assert metadata["title"] == "HTML"
        assert metadata["series"] is None
        assert metadata["series_number"] is None
        assert metadata["series_total"] is None
        assert metadata["description"] == "Nothing special!"
        assert metadata["date"] is None
        assert metadata["writers"] == ["AAA"]
        assert metadata["artists"] is None
        assert metadata["cover_artists"] is None
        assert metadata["publisher"] is None
        assert metadata["tags"] is None
        assert metadata["url"] is None
        assert metadata["score"] is None
        assert metadata["age_rating"] == "Unknown"
        assert metadata["page_count"] is None

def test_get_info_from_archive():
    """
    Tests the get_info_from_archive function.
    """
    # Test getting metadata from an EPUB file
    epub_file = abspath(join(mm_test.ARCHIVE_EPUB_DIRECTORY, "basic.epub"))
    metadata = mm_archive.get_info_from_archive(epub_file)
    assert metadata["title"] == "Básic EPUB"
    assert metadata["series"] == "Books"
    assert metadata["series_number"] == "0.5"
    assert metadata["series_total"] is None
    assert metadata["description"] == "Simple Description"
    assert metadata["date"] == "2020-01-01"
    assert metadata["writers"] == ["Multiple", "Writers"]
    assert metadata["artists"] == ["Different", "Artists"]
    assert metadata["cover_artists"] == ["Cover", "Artists"]
    assert metadata["publisher"] == "BookCo"
    assert metadata["tags"] == ["This", "&", "That"]
    assert metadata["url"] == "/placeholder/"
    assert metadata["age_rating"] == "Everyone"
    assert metadata["score"] == "4"
    assert metadata["page_count"] == "1"
    assert metadata["cover_id"] is None
    # Test getting metadata from a CBZ file
    cbz_file = abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "basic.CBZ"))
    metadata = mm_archive.get_info_from_archive(cbz_file)
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
    # Test getting metadata from a non-archive file
    text_file = abspath(join(mm_test.BASIC_TEXT_DIRECTORY, "latin1.txt"))
    assert mm_archive.get_info_from_archive(text_file) == mm_archive.get_empty_metadata()

def test_update_archive_info():
    """
    Test the update_archive_info function.
    """
    # Test updating an CBZ file
    base_file = abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "basic.CBZ"))
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_file = abspath(join(temp_dir, "basic.CBZ"))
        shutil.copy(base_file, cbz_file)
        read_metadata = mm_comic_archive.get_info_from_cbz(cbz_file)
        assert read_metadata["title"] == "Cómic"
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "New Comic Title"
        metadata["artists"] = ["New", "Artists"]
        mm_archive.update_archive_info(cbz_file, metadata)
        read_metadata = mm_comic_archive.get_info_from_cbz(cbz_file)
        assert read_metadata["title"] == "New Comic Title"
        assert read_metadata["artists"] == ["New", "Artists"]
        assert read_metadata["writers"] is None
        assert read_metadata["publisher"] is None
    # Test updating an EPUB file without updating the cover image
    base_file = abspath(join(mm_test.ARCHIVE_EPUB_DIRECTORY, "small.epub"))
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_file = abspath(join(temp_dir, "small.epub"))
        shutil.copy(base_file, epub_file)
        read_metadata = mm_epub.get_info_from_epub(epub_file)
        assert read_metadata["title"] is None
        assert read_metadata["description"] == "Small Cover"
        assert os.stat(epub_file).st_size < 10000
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "New Epub Title"
        metadata["writers"] = ["Updated", "Writers"]
        metadata["cover_id"] = None
        mm_archive.update_archive_info(epub_file, metadata)
        assert os.stat(epub_file).st_size < 10000
        read_metadata = mm_epub.get_info_from_epub(epub_file)
        assert read_metadata["title"] == "New Epub Title"
        assert read_metadata["writers"] == ["Updated", "Writers"]
        assert read_metadata["artists"] is None
        assert read_metadata["publisher"] is None
    # Test updating EPUB file metadata and cover image
    base_file = abspath(join(mm_test.ARCHIVE_EPUB_DIRECTORY, "small.epub"))
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_file = abspath(join(temp_dir, "small.epub"))
        shutil.copy(base_file, epub_file)
        read_metadata = mm_epub.get_info_from_epub(epub_file)
        assert read_metadata["title"] is None
        assert read_metadata["description"] == "Small Cover"
        assert os.stat(epub_file).st_size < 10000
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "New Cover"
        metadata["writers"] = ["AAAAA"]
        metadata["cover_id"] = "image1"
        mm_archive.update_archive_info(epub_file, metadata, update_cover=True)
        assert os.stat(epub_file).st_size > 30000
        read_metadata = mm_epub.get_info_from_epub(epub_file)
        assert read_metadata["title"] == "New Cover"
        assert read_metadata["writers"] == ["AAAAA"]
        assert read_metadata["artists"] is None
        assert read_metadata["publisher"] is None
    # Test attempting to update non-archive files
    base_file = abspath(join(mm_test.BASIC_TEXT_DIRECTORY, "unicode.txt"))
    with tempfile.TemporaryDirectory() as temp_dir:
        text_file = abspath(join(temp_dir, "unicode.txt"))
        shutil.copy(base_file, text_file)
        mm_archive.update_archive_info(text_file, metadata)
        assert mm_file_tools.read_text_file(text_file) == "This is ünicode."
    base_file = abspath(join(mm_test.BASIC_DIRECTORY, "archive.zip"))
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_file = abspath(join(temp_dir, "archive.zip"))
        shutil.copy(base_file, zip_file)
        assert os.stat(zip_file).st_size == 784
        mm_archive.update_archive_info(zip_file, metadata)
        assert os.stat(zip_file).st_size == 784

def test_format_title():
    """
    Tests the format_title function
    """
    # Test Removing a standalone number
    assert mm_archive.format_title("Test 123") == "Test"
    assert mm_archive.format_title("1 Number 01 ") == "1 Number"
    assert mm_archive.format_title("New Thing15") == "New Thing"
    assert mm_archive.format_title("1. A Thing") == "1. a Thing"
    assert mm_archive.format_title("12 13 B 14 C") == "12 13 B 14 C"
    assert mm_archive.format_title("Thing - 05") == "Thing"
    assert mm_archive.format_title("New - #05 ") == "New"
    # Test Removing number with total
    assert mm_archive.format_title("Something 1/2") == "Something"
    assert mm_archive.format_title("Other Name  17/43  ") == "Other Name"
    assert mm_archive.format_title("Another 1 / 2") == "Another"
    assert mm_archive.format_title("Text 1-0") == "Text"
    assert mm_archive.format_title("Title 12 - 43") == "Title"
    assert mm_archive.format_title("1/2 Name") == "1/2 Name"
    assert mm_archive.format_title("Two 1 / 2 Name") == "Two 1 / 2 Name"
    assert mm_archive.format_title("3-4 Thing") == "3-4 Thing"
    assert mm_archive.format_title("Title 1 of 3") == "Title"
    assert mm_archive.format_title("Name 4OF7") == "Name"
    # Test Removing number with number symbol
    assert mm_archive.format_title("4 Test #123") == "4 Test"
    assert mm_archive.format_title("Thing #1/2 ") == "Thing"
    assert mm_archive.format_title("Another # 16  ") == "Another"
    assert mm_archive.format_title("#1 Fan") == "#1 Fan"
    assert mm_archive.format_title("#1 #2 #3 Thing") == "#1 #2 #3 Thing"
    # Test Removing number with "page" or "part"
    assert mm_archive.format_title("Test Part 1") == "Test"
    assert mm_archive.format_title("Thing page2") == "Thing"
    assert mm_archive.format_title("Other P. 1/2 ") == "Other"
    assert mm_archive.format_title("Name Pg. 4 ") == "Name"
    assert mm_archive.format_title("Passof Page2-3") == "Passof"
    assert mm_archive.format_title("Test part1") == "Test"
    assert mm_archive.format_title("Thing Page 25") == "Thing"
    assert mm_archive.format_title("Other p.12 ") == "Other"
    assert mm_archive.format_title("Part 1 of 5 ") == "Part 1 of 5 "
    assert mm_archive.format_title("Some Pages 5") == "Some Pages"
    assert mm_archive.format_title("New Thing Pt. 23") == "New Thing"
    assert mm_archive.format_title("p.3 Something") == "P.3 Something"
    assert mm_archive.format_title("stoppage 5") == "Stoppage"
    assert mm_archive.format_title("rampart 10") == "Rampart"
    assert mm_archive.format_title("Tempt 12") == "Tempt"
    assert mm_archive.format_title("Stop. 5") == "Stop."
    assert mm_archive.format_title("Thing - Part 5") == "Thing"
    # Test Removing number with brackets or parenthesis
    assert mm_archive.format_title("Test[01]") == "Test"
    assert mm_archive.format_title("Name [Part 1/3] ") == "Name"
    assert mm_archive.format_title("Something [P. 4-5] ") == "Something"
    assert mm_archive.format_title("Thing [ #06 ]") == "Thing"
    assert mm_archive.format_title("Test(01)") == "Test"
    assert mm_archive.format_title("Name (page 3/6 ) ") == "Name"
    assert mm_archive.format_title("Another (page 4-6) ") == "Another"
    assert mm_archive.format_title("Thing ( #09 )") == "Thing"
    assert mm_archive.format_title("Next (page 1)") == "Next"
    assert mm_archive.format_title("Other (p. 1)") == "Other"
    assert mm_archive.format_title("(01) Thing") == "(01) Thing"
    assert mm_archive.format_title("Test (Not Num)") == "Test (Not Num)"
    assert mm_archive.format_title("Other [1] Thing") == "Other [1] Thing"
    assert mm_archive.format_title("Other (1") == "Other ("
    assert mm_archive.format_title("Other 12)") == "Other 12)"
    assert mm_archive.format_title("Thing [12)") == "Thing [12)"
    assert mm_archive.format_title("Thing [1") == "Thing ["
    assert mm_archive.format_title("Final 23]") == "Final 23]"
    # Test Removing starting brackets and capitalizing titles
    assert mm_archive.format_title("[Blah] some title ") == "Some Title"
    assert mm_archive.format_title("[2020-01-01] title of   thing part 2") == "Title of Thing"
    assert mm_archive.format_title("[A] of something for something") == "Of Something for Something"
    assert mm_archive.format_title("[B] part Of A title") == "Part of a Title"
    assert mm_archive.format_title("[B] part Of An object") == "Part of an Object"
    assert mm_archive.format_title("[ABC] This's A thing's") == "This's a Thing's"
    assert mm_archive.format_title("[ABC] this to that") == "This to That"
    assert mm_archive.format_title("[ABC] this And that") == "This and That"
    assert mm_archive.format_title("[ABC] thing the title") == "Thing the Title"
    assert mm_archive.format_title("[ABC] SOMETHING") == "SOMETHING"
    # Test Removing number with all options
    assert mm_archive.format_title("A Picture [Page #15/30]") == "A Picture"
    assert mm_archive.format_title("Something Else ( Part #1 / 2 ) ") == "Something Else"
    # Test that the original text is returned if there is nothing left
    assert mm_archive.format_title("34") == "34"
    assert mm_archive.format_title(" [1/5] ") == " [1/5] "
    # Test returning None if text is None
    assert mm_archive.format_title(None) is None

def test_generate_cover_image():
    """
    Tests the generate_cover_image function.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        image_file = abspath(join(temp_dir, "cover_image.jpg"))
        assert mm_archive.generate_cover_image("This is a title.", ["Drakovek", "Other"], image_file)
        assert os.listdir(temp_dir) == ["cover_image.jpg"]
        image = Image.open(image_file)
        assert image.size == (900, 1200)
