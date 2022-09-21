#!/usr/bin/env python3

from os import mkdir
from os.path import abspath, exists, join
from tempfile import gettempdir
from shutil import rmtree

def get_temp_dir() -> str:
    """
    Creates and returns test directory.

    :return: File path of the test directory
    :rtype: str
    """
    temp_dir = abspath(join(abspath(gettempdir()), "dvk_meta_magic"))
    if(exists(temp_dir)):
        rmtree(temp_dir)
    mkdir(temp_dir)
    return temp_dir
