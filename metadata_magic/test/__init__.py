#!/usr/bin/env python3

import os
from os.path import abspath, join

TEST_DIRECTORY = abspath(join(abspath(join(abspath(__file__), os.pardir)), "test_files"))

# BASIC FILE DIRECTORIES
BASIC_DIRECTORY = abspath(join(TEST_DIRECTORY, "basic_files"))
BASIC_TEXT_DIRECTORY = abspath(join(BASIC_DIRECTORY, "text"))

# JSON PAIR DIRECTORIES
PAIR_DIRECTORY = abspath(join(TEST_DIRECTORY, "json_pairs"))
PAIR_GIF_DIRECTORY = abspath(join(PAIR_DIRECTORY, "gifs"))
PAIR_IMAGE_DIRECTORY = abspath(join(PAIR_DIRECTORY, "images"))
PAIR_TEXT_DIRECTORY = abspath(join(PAIR_DIRECTORY, "text"))
PAIR_VIDEO_DIRECTORY = abspath(join(PAIR_DIRECTORY, "videos"))

# ARCHIVE FILE DIRECTORIES
ARCHIVE_DIRECTORY = abspath(join(TEST_DIRECTORY, "archive_files"))
ARCHIVE_CBZ_DIRECTORY = abspath(join(ARCHIVE_DIRECTORY, "cbzs"))
ARCHIVE_EPUB_DIRECTORY = abspath(join(ARCHIVE_DIRECTORY, "epubs"))
