#!/usr/bin/env python3

import os
from os.path import abspath, join

TEST_DIRECTORY = abspath(join(abspath(join(abspath(__file__), os.pardir)), "test_files"))

# BASIC FILE DIRECTORIES
BASIC_DIRECTORY = abspath(join(TEST_DIRECTORY, "basic_files"))
BASIC_TEXT_DIRECTORY = abspath(join(BASIC_DIRECTORY, "text"))
BASIC_HTML_DIRECTORY = abspath(join(BASIC_DIRECTORY, "html"))

# JSON PAIR DIRECTORIES
PAIR_DIRECTORY = abspath(join(TEST_DIRECTORY, "json_pairs"))
PAIR_GIF_DIRECTORY = abspath(join(PAIR_DIRECTORY, "gifs"))
PAIR_IMAGE_DIRECTORY = abspath(join(PAIR_DIRECTORY, "images"))
PAIR_TEXT_DIRECTORY = abspath(join(PAIR_DIRECTORY, "text"))
PAIR_VIDEO_DIRECTORY = abspath(join(PAIR_DIRECTORY, "videos"))
PAIR_MISSING_DIRECTORY = abspath(join(PAIR_DIRECTORY, "missing"))

# ARCHIVE FILE DIRECTORIES
ARCHIVE_DIRECTORY = abspath(join(TEST_DIRECTORY, "archive_files"))
ARCHIVE_CBZ_DIRECTORY = abspath(join(ARCHIVE_DIRECTORY, "cbzs"))
ARCHIVE_EPUB_DIRECTORY = abspath(join(ARCHIVE_DIRECTORY, "epubs"))
ARCHIVE_SERIES_DIRECTORY = abspath(join(ARCHIVE_DIRECTORY, "series"))

# ARCHIVE INTERNAL DIRECTORIES
ARCHIVE_INTERNAL_DIRECTORY = abspath(join(TEST_DIRECTORY, "archive_internal"))
EPUB_INTERNAL_DIRECTORY = abspath(join(ARCHIVE_INTERNAL_DIRECTORY, "epub_internal"))
COMIC_XML_DIRECTORY = abspath(join(ARCHIVE_INTERNAL_DIRECTORY, "comic_xml"))

# ERROR TEST DIRECTORIES
ERROR_TEST_DIRECTORY = abspath(join(TEST_DIRECTORY, "error_tests"))
ZIP_CONFLICT_DIRECTORY = abspath(join(ERROR_TEST_DIRECTORY, "zip_conflicts"))
JSON_ERROR_DIRECTORY = abspath(join(ERROR_TEST_DIRECTORY, "json_error"))
ARCHIVE_ERROR_DIRECTORY = abspath(join(ERROR_TEST_DIRECTORY, "archive_error"))
