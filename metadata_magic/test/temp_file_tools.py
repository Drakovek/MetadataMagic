#!/usr/bin/env python3

from json import dump as dump_json
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

def create_text_file(file:str, text:str):
    """
    Cretes a file containing the given text.
    
    :param file: Path of the file to create
    :type file: str, required
    :param text: Text to save in the file
    :type text: str, required
    """
    try:
        full_path = abspath(file)
        with open(full_path, "w") as out_file:
            out_file.write(text)
    except FileNotFoundError: pass

def create_json_file(file:str, contents:dict):
    """
    Cretes a JSON file containing the given dictionary as contents.
    
    :param file: Path of the file to create
    :type file: str, required
    :param text: Contents to save as JSON
    :type text: str, required
    """
    try:
        full_path = abspath(file)
        with open(full_path, "w") as out_file:
            dump_json(contents, out_file)
    except FileNotFoundError: pass

def read_text_file(file:str) -> str:
    """
    Reads the content of a given text file.
    
    :param file: Path of the file to read
    :type file: str, required
    :return: Text contained in the given file
    :rtype: str
    """
    try:
        with open (file) as in_file:
            content = in_file.read()
        return content
    except FileNotFoundError: return ""