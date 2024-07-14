#!/usr/bin/env python3

import os
from os.path import abspath, join

TEST_DIRECTORY = abspath(join(abspath(join(abspath(__file__), os.pardir)), "test_files"))
BASIC_DIRECTORY = abspath(join(TEST_DIRECTORY, "basic_files"))
