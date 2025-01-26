#!/usr/bin/env python3

import os
import shutil
import tempfile
import metadata_magic.test as mm_test
import metadata_magic.config as mm_config
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive as mm_archive
import metadata_magic.archive.epub as mm_epub
import metadata_magic.archive.bulk_archive as mm_bulk_archive
import metadata_magic.archive.comic_archive as mm_comic_archive
from os.path import abspath, join

def test_archive_all_media():
    """
    Tests the archive_all_media function.
    """
    # Test bulk archiving JSON-image pairs
    config = mm_config.get_config([])
    with tempfile.TemporaryDirectory() as temp_dir:
        image_directory = abspath(join(temp_dir, "images"))
        shutil.copytree(mm_test.PAIR_IMAGE_DIRECTORY, image_directory)
        mm_bulk_archive.archive_all_media(image_directory, config)
        assert sorted(os.listdir(image_directory)) == [".empty", "aaa.json", "aaa.webp", "bare.PNG.cbz", "long.epub"]
        # Check contents of CBZ file generated from image JSON pair
        cbz_file = abspath(join(image_directory, "bare.PNG.cbz"))
        read_metadata = mm_comic_archive.get_info_from_cbz(cbz_file)
        assert read_metadata["title"] == "Émpty"
        assert read_metadata["page_count"] == "1"
        assert read_metadata["description"] is None
        assert read_metadata["artists"] is None
        cbz_extracted = abspath(join(temp_dir, "cbz_extracted"))
        os.mkdir(cbz_extracted)
        assert mm_file_tools.extract_zip(cbz_file, cbz_extracted)
        assert sorted(os.listdir(cbz_extracted)) == ["ComicInfo.xml", "Empty"]
        cbz_extracted = abspath(join(cbz_extracted, "Empty"))
        assert sorted(os.listdir(cbz_extracted)) == ["Empty.json", "Empty.png"]
        # Check contents of the EPUB generated from image and text from JSON description
        epub_file = abspath(join(image_directory, "long.epub"))
        read_metadata = mm_epub.get_info_from_epub(epub_file)
        assert read_metadata["title"] == "LÑG"
        assert read_metadata["artists"] == ["Long Artist"]
        assert read_metadata["writers"] == ["Long Artist"]
        assert read_metadata["age_rating"] == "X18+"
        assert read_metadata["page_count"] == "1"
        assert read_metadata["cover_id"] == "image1"
        assert read_metadata["date"] is None
        epub_extracted = abspath(join(temp_dir, "epub_extracted"))
        os.mkdir(epub_extracted)
        assert mm_file_tools.extract_zip(epub_file, epub_extracted)
        assert sorted(os.listdir(epub_extracted)) == ["EPUB", "META-INF", "mimetype"]
        epub_extracted = abspath(join(epub_extracted, "EPUB"))
        epub_extracted = abspath(join(epub_extracted, "content"))
        assert sorted(os.listdir(epub_extracted)) == ["LNG.xhtml", "back_cover_image.xhtml", "cover_image.xhtml"]
    # Test bulk archiving JSON-text pairs
    with tempfile.TemporaryDirectory() as temp_dir:
        text_directory = abspath(join(temp_dir, "text"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, text_directory)
        mm_bulk_archive.archive_all_media(temp_dir, config)
        assert sorted(os.listdir(text_directory)) == ["text 02.txt.epub", "text 1.epub"]
        # Check the contents of EPUB generated from an JSON-HTML pair
        epub_file = abspath(join(text_directory, "text 1.epub"))
        read_metadata = mm_epub.get_info_from_epub(epub_file)
        assert read_metadata["title"] == "HTML"
        assert read_metadata["writers"] == ["AAA"]
        assert read_metadata["page_count"] == "1"
        assert read_metadata["artists"] is None
        assert read_metadata["date"] is None
        epub_extracted = abspath(join(temp_dir, "text1_extracted"))
        os.mkdir(epub_extracted)
        assert mm_file_tools.extract_zip(epub_file, epub_extracted)
        assert sorted(os.listdir(epub_extracted)) == ["EPUB", "META-INF", "mimetype"]
        epub_extracted = abspath(join(epub_extracted, "EPUB"))
        epub_extracted = abspath(join(epub_extracted, "content"))
        assert sorted(os.listdir(epub_extracted)) == ["HTML.xhtml", "cover_image.xhtml"]
        # Check the contents of EPUB generated from an JSON-txt pair
        epub_file = abspath(join(text_directory, "text 02.txt.epub"))
        read_metadata = mm_epub.get_info_from_epub(epub_file)
        assert read_metadata["title"] == "TXT"
        assert read_metadata["writers"] == ["BBB"]
        assert read_metadata["page_count"] == "1"
        assert read_metadata["artists"] is None
        assert read_metadata["date"] is None
        epub_extracted = abspath(join(temp_dir, "text2_extracted"))
        os.mkdir(epub_extracted)
        assert mm_file_tools.extract_zip(epub_file, epub_extracted)
        assert sorted(os.listdir(epub_extracted)) == ["EPUB", "META-INF", "mimetype"]
        epub_extracted = abspath(join(epub_extracted, "EPUB"))
        epub_extracted = abspath(join(epub_extracted, "content"))
        assert sorted(os.listdir(epub_extracted)) == ["TXT.xhtml", "cover_image.xhtml"]
    # Test bulk archiving while formatting the titles, and ignoring unpaired
    base_directory = abspath(join(mm_test.EPUB_INTERNAL_DIRECTORY, "multiple"))
    with tempfile.TemporaryDirectory() as temp_dir:
        multiple_directory = abspath(join(temp_dir, "multiple"))
        shutil.copytree(base_directory, multiple_directory)
        mm_bulk_archive.archive_all_media(temp_dir, config, format_title=True)
        files = sorted(os.listdir(multiple_directory))
        assert len(files) == 6
        assert files[0] == ".test"
        assert files[1] == "[AA] Part 1.epub"
        assert files[2] == "[BB] Image 1.cbz"
        assert files[3] == "[CC] Part 2.epub"
        assert files[4] == "[DD] Image 2.cbz"
        assert files[5] == "ignore"
        assert os.listdir(abspath(join(multiple_directory, "ignore"))) == ["sub.txt"]
        # Test that titles were formatted
        read_metadata = mm_archive.get_info_from_archive(abspath(join(multiple_directory, "[AA] Part 1.epub")))
        assert read_metadata["title"] == "Book"
        read_metadata = mm_archive.get_info_from_archive(abspath(join(multiple_directory, "[BB] Image 1.cbz")))
        assert read_metadata["title"] == "Image"
        read_metadata = mm_archive.get_info_from_archive(abspath(join(multiple_directory, "[CC] Part 2.epub")))
        assert read_metadata["title"] == "Book"
        read_metadata = mm_archive.get_info_from_archive(abspath(join(multiple_directory, "[DD] Image 2.cbz")))
        assert read_metadata["title"] == "Image"
    # Test that image isn't converted to an EPUB with a greater cutoff point for the description length
    config = mm_config.get_config([])
    with tempfile.TemporaryDirectory() as temp_dir:
        image_directory = abspath(join(temp_dir, "images"))
        shutil.copytree(mm_test.PAIR_IMAGE_DIRECTORY, image_directory)
        mm_bulk_archive.archive_all_media(image_directory, config, description_length=2000000)
        assert sorted(os.listdir(image_directory)) == [".empty", "aaa.json", "aaa.webp", "bare.PNG.cbz", "long.cbz"]

def test_extract_cbz():
    """
    Tests the extract_cbz function
    """
    # Test extracting CBZ file into a containing directory
    base_file = abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "NoPage.cbz"))
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_file = abspath(join(temp_dir, "NoPage.cbz"))
        shutil.copy(base_file, cbz_file)
        assert mm_bulk_archive.extract_cbz(cbz_file, temp_dir, create_folder=True, remove_structure=False)
        assert sorted(os.listdir(temp_dir)) == ["NoPage", "NoPage.cbz"]
        internal_dir = abspath(join(temp_dir, "NoPage"))
        assert sorted(os.listdir(internal_dir)) == ["B.jpeg", "ComicInfo.xml", "G.jpg", "R.png"]
    # Test extracting CBZ file with no containing directory
    base_file = abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "basic.CBZ"))
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_file = abspath(join(temp_dir, "basic.CBZ"))
        shutil.copy(base_file, cbz_file)
        assert mm_bulk_archive.extract_cbz(cbz_file, temp_dir, create_folder=False, remove_structure=False)
        assert sorted(os.listdir(temp_dir)) == ["Comic", "ComicInfo.xml", "basic.CBZ"]
        internal_dir = abspath(join(temp_dir, "Comic"))
        assert sorted(os.listdir(internal_dir)) == ["Comic.jpg"]
    # Test extracting CBZ file while removing structure with no containing directory
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_file = abspath(join(temp_dir, "basic.CBZ"))
        shutil.copy(base_file, cbz_file)
        assert mm_bulk_archive.extract_cbz(cbz_file, temp_dir, create_folder=False, remove_structure=True)
        assert sorted(os.listdir(temp_dir)) == ["Comic.jpg", "basic.CBZ"]
    # Test extracting CBZ file while removing structure with a containing directory
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_file = abspath(join(temp_dir, "basic.CBZ"))
        shutil.copy(base_file, cbz_file)
        assert mm_bulk_archive.extract_cbz(cbz_file, temp_dir, create_folder=True, remove_structure=True)
        assert sorted(os.listdir(temp_dir)) == ["basic", "basic.CBZ"]
        internal_dir = abspath(join(temp_dir, "basic"))
        assert sorted(os.listdir(internal_dir)) == ["Comic.jpg"]
    # Test extracting a non-CBZ file
    base_file = abspath(join(mm_test.BASIC_TEXT_DIRECTORY, "latin1.txt"))
    with tempfile.TemporaryDirectory() as temp_dir:
        text_file = abspath(join(temp_dir, "latin1.txt"))
        shutil.copy(base_file, text_file)
        assert not mm_bulk_archive.extract_cbz(text_file, temp_dir)
        assert os.listdir(temp_dir) == ["latin1.txt"]

def test_extract_epub():
    """
    Tests the extract_epub function.
    """
    # Test extracting EPUB file into a containing directory
    base_file = abspath(join(mm_test.ARCHIVE_EPUB_DIRECTORY, "long.EPUB"))
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_file = abspath(join(temp_dir, "long.EPUB"))
        shutil.copy(base_file, epub_file)
        assert mm_bulk_archive.extract_epub(epub_file, temp_dir, create_folder=True, remove_structure=False)
        assert sorted(os.listdir(temp_dir)) == ["long", "long.EPUB"]
        internal_dir = abspath(join(temp_dir, "long"))
        assert sorted(os.listdir(internal_dir)) == ["EPUB", "META-INF", "mimetype"]
        internal_dir = abspath(join(internal_dir, "EPUB"))
        internal_dir = abspath(join(internal_dir, "content"))
        assert sorted(os.listdir(internal_dir)) == ["Chapter 1.xhtml", "Chapter 2.xhtml", "Chapter 3.xhtml", "cover_image.xhtml"]
    # Test extracting EPUB file with no containing directory
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_file = abspath(join(temp_dir, "long.EPUB"))
        shutil.copy(base_file, epub_file)
        assert mm_bulk_archive.extract_epub(epub_file, temp_dir, create_folder=False, remove_structure=False)
        assert sorted(os.listdir(temp_dir)) == ["EPUB", "META-INF", "long.EPUB", "mimetype"]
        internal_dir = abspath(join(temp_dir, "EPUB"))
        internal_dir = abspath(join(internal_dir, "content"))
        assert sorted(os.listdir(internal_dir)) == ["Chapter 1.xhtml", "Chapter 2.xhtml", "Chapter 3.xhtml", "cover_image.xhtml"]
    # Test extracting EPUB file while removing structure with no containing directory
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_file = abspath(join(temp_dir, "long.EPUB"))
        shutil.copy(base_file, epub_file)
        assert mm_bulk_archive.extract_epub(epub_file, temp_dir, create_folder=False, remove_structure=True)
        assert sorted(os.listdir(temp_dir)) == ["Chapter 1.txt", "Chapter 2.txt", "Chapter 3.txt", "long.EPUB"]
    # Test extracting EPUB file while removing structure with a containing directory
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_file = abspath(join(temp_dir, "long.EPUB"))
        shutil.copy(base_file, epub_file)
        assert mm_bulk_archive.extract_epub(epub_file, temp_dir, create_folder=True, remove_structure=True)
        assert sorted(os.listdir(temp_dir)) == ["long", "long.EPUB"]
        internal_dir = abspath(join(temp_dir, "long"))
        assert sorted(os.listdir(internal_dir)) == ["Chapter 1.txt", "Chapter 2.txt", "Chapter 3.txt"]
    # Test extracting non-EPUB files
    base_file = abspath(join(mm_test.BASIC_TEXT_DIRECTORY, "latin1.txt"))
    with tempfile.TemporaryDirectory() as temp_dir:
        text_file = abspath(join(temp_dir, "latin1.txt"))
        shutil.copy(base_file, text_file)
        assert not mm_bulk_archive.extract_epub(text_file, temp_dir)
        assert os.listdir(temp_dir) == ["latin1.txt"]
    base_file = abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "basic.CBZ"))
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_file = abspath(join(temp_dir, "basic.CBZ"))
        shutil.copy(base_file, cbz_file)
        assert not mm_bulk_archive.extract_epub(cbz_file, temp_dir, remove_structure=True)
        assert os.listdir(temp_dir) == ["basic.CBZ"]

def test_extract_all_archives():
    """
    Tests the extract_all_archives function.
    """
    # Test extracting archives without removing the internal structure
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_directory = abspath(join(temp_dir, "cbzs"))
        epub_directory = abspath(join(temp_dir, "epubs"))
        shutil.copytree(mm_test.ARCHIVE_CBZ_DIRECTORY, cbz_directory)
        shutil.copytree(mm_test.ARCHIVE_EPUB_DIRECTORY, epub_directory)
        assert mm_bulk_archive.extract_all_archives(temp_dir, create_folders=True, remove_structure=False)
        assert sorted(os.listdir(cbz_directory)) == ["NoPage", "SubInfo", "basic", "empty"]
        assert sorted(os.listdir(abspath(join(cbz_directory, "basic")))) == ["Comic", "ComicInfo.xml"]
        assert sorted(os.listdir(epub_directory)) == ["basic", "long", "small"]
        assert sorted(os.listdir(abspath(join(epub_directory, "basic")))) == ["EPUB", "META-INF", "mimetype"]
    # Test extracting archives while removing the internal structure
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_directory = abspath(join(temp_dir, "cbzs"))
        epub_directory = abspath(join(temp_dir, "epubs"))
        os.mkdir(cbz_directory)
        os.mkdir(epub_directory)
        shutil.copy(abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "basic.CBZ")), cbz_directory)
        shutil.copy(abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "NoPage.cbz")), cbz_directory)
        shutil.copy(abspath(join(mm_test.ARCHIVE_EPUB_DIRECTORY, "long.EPUB")), epub_directory)
        shutil.copy(abspath(join(mm_test.ARCHIVE_EPUB_DIRECTORY, "small.epub")), epub_directory)
        assert mm_bulk_archive.extract_all_archives(temp_dir, create_folders=False, remove_structure=True)
        assert sorted(os.listdir(cbz_directory)) == ["B.jpeg", "Comic.jpg", "G.jpg", "R.png"]
        assert sorted(os.listdir(epub_directory)) == ["Chapter 1.txt", "Chapter 2.txt", "Chapter 3.txt", "Text.txt"]
    # Test extracting invalid archives
    with tempfile.TemporaryDirectory() as temp_dir:
        fake_cbz = abspath(join(temp_dir, "fake.cbz"))
        fake_epub = abspath(join(temp_dir, "fake.epub"))
        shutil.copy(abspath(join(mm_test.BASIC_TEXT_DIRECTORY, "unicode.txt")), fake_cbz)
        shutil.copy(abspath(join(mm_test.BASIC_TEXT_DIRECTORY, "unicode.txt")), fake_epub)
        assert not mm_bulk_archive.extract_all_archives(temp_dir, create_folders=True, remove_structure=False)
        assert sorted(os.listdir(temp_dir)) == ["fake.cbz", "fake.epub"]
