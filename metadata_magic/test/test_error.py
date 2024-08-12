#!/usr/bin/env python3

import os
import shutil
import tempfile
import metadata_magic.test as mm_test
import metadata_magic.error as mm_error
import metadata_magic.config as mm_config
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.bulk_archive as mm_bulk_archive
import metadata_magic.archive.comic_archive as mm_comic_archive
import metadata_magic.archive.epub as mm_epub
from os.path import abspath, basename, exists, join

def test_find_long_descriptions():
    """
    Tests the find_long_descriptions function.
    """
    # Copy folders to test error detection
    config = mm_config.DEFAULT_CONFIG
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_directory = abspath(join(temp_dir, "cbzs"))
        epub_directory = abspath(join(temp_dir, "epubs"))
        shutil.copytree(mm_test.ARCHIVE_CBZ_DIRECTORY, cbz_directory)
        shutil.copytree(mm_test.ARCHIVE_EPUB_DIRECTORY, epub_directory)
        # Test finding archives with long descriptions
        long = mm_error.find_long_descriptions(temp_dir, config, 200)
        assert len(long) == 2
        assert basename(long[0]) == "NoPage.cbz"
        assert basename(long[1]) == "long.EPUB"
    # Test finding JSONs with long descriptions
    long = mm_error.find_long_descriptions(mm_test.PAIR_DIRECTORY, config, 200)
    assert len(long) == 1
    assert basename(long[0]) == "long.JSON"
    assert abspath(join(long[0], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY

def test_find_missing_media():
    """
    Test the find_missing_media function.
    """
    missing = mm_error.find_missing_media(mm_test.PAIR_DIRECTORY)
    assert len(missing) == 2
    assert basename(missing[0]) == "missing-media.json"
    assert abspath(join(missing[0], os.pardir)) == mm_test.PAIR_MISSING_DIRECTORY
    assert basename(missing[1]) == "no-media.json"
    assert abspath(join(missing[1], os.pardir)) == mm_test.PAIR_DIRECTORY

def test_find_missing_metadata():
    """
    Tests the find_missing_metadata function.
    """
    missing = mm_error.find_missing_metadata(mm_test.PAIR_DIRECTORY)
    assert len(missing) == 3
    assert basename(missing[0]) == ".empty"
    assert abspath(join(missing[0], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert basename(missing[1]) == "missing-metadata.txt"
    assert abspath(join(missing[1], os.pardir)) == mm_test.PAIR_DIRECTORY
    assert basename(missing[2]) == "no-metadata.txt"
    assert abspath(join(missing[2], os.pardir)) == mm_test.PAIR_MISSING_DIRECTORY

def test_find_missing_fields():
    """
    Tests the find_missing_fields function.
    """
    # Copy folders to test error detection
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_directory = abspath(join(temp_dir, "cbzs"))
        epub_directory = abspath(join(temp_dir, "epubs"))
        shutil.copytree(mm_test.ARCHIVE_CBZ_DIRECTORY, cbz_directory)
        shutil.copytree(mm_test.ARCHIVE_EPUB_DIRECTORY, epub_directory)
        # Test finding archives with a missing title
        missing = mm_error.find_missing_fields(temp_dir, ["title"])
        assert len(missing) == 2
        assert basename(missing[0]) == "empty.cbz"
        assert basename(missing[1]) == "small.epub"
        # Test finding archives with missing series info
        missing = mm_error.find_missing_fields(temp_dir, ["series"])
        assert len(missing) == 4
        assert basename(missing[0]) == "empty.cbz"
        assert basename(missing[1]) == "NoPage.cbz"
        assert basename(missing[2]) == "long.EPUB"
        assert basename(missing[3]) == "small.epub"
        # Test finding archives with missing artists
        missing = mm_error.find_missing_fields(temp_dir, ["artists"])
        assert len(missing) == 2
        assert basename(missing[0]) == "empty.cbz"
        assert basename(missing[1]) == "small.epub"
        # Test finding archives with missing artists and writes
        missing = mm_error.find_missing_fields(temp_dir, ["artists", "writers"])
        assert len(missing) == 1
        assert basename(missing[0]) == "empty.cbz"
        # Test finding archives with missing age rating
        missing = mm_error.find_missing_fields(temp_dir, ["age_rating"])
        assert len(missing) == 4
        assert basename(missing[0]) == "empty.cbz"
        assert basename(missing[1]) == "SubInfo.CBZ"
        assert basename(missing[2]) == "long.EPUB"
        assert basename(missing[3]) == "small.epub"
        # Test finding archives with a missing field that doesn't exist
        missing = mm_error.find_missing_fields(temp_dir, ["non_existant"])
        assert len(missing) == 7
        assert basename(missing[0]) == "basic.CBZ"
        assert basename(missing[1]) == "empty.cbz"
        assert basename(missing[2]) == "NoPage.cbz"
        assert basename(missing[3]) == "SubInfo.CBZ"
        assert basename(missing[4]) == "basic.epub"
        assert basename(missing[5]) == "long.EPUB"
        assert basename(missing[6]) == "small.epub"
