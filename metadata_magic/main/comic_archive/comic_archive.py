#!/usr/bin/env python3

from os import listdir
from os.path import abspath, basename, exists, isdir, join, relpath
from py7zr import SevenZipFile
from tqdm import tqdm
from zipfile import ZipFile

def create_cbz(directory:str) -> str:
    """
    Creates a cbz archive containing all the files in a given directory.
    
    :param directory: Directory with files to compress into archive
    :type directory: str, required
    :return: Full path of the created cbz archive
    :rtype: str
    """
    try:
        # Get filenames
        full_directory = abspath(directory)
        cbz = abspath(join(full_directory, basename(full_directory) + ".cbz"))
        # Get list of files in the directory
        files = listdir(full_directory)
        for i in range(0, len(files)):
            files[i] = abspath(join(full_directory, files[i]))
        # Expand list of files to include subdirectories
        for file in files:
            if isdir(file):
                sub_files = listdir(file)
                for i in range(0, len(sub_files)):
                    files.append(abspath(join(file, sub_files[i])))
        # Create empty cbz file
        with ZipFile(cbz, "w") as out_file: pass
        assert exists(cbz)
        # Write contents of directory to cbz file
        for file in tqdm(files):
            relative = relpath(file, full_directory)
            with ZipFile(cbz, "a") as out_file:
                out_file.write(file, relative)
        # Return the path of the written cbz archive
        return cbz
    except FileNotFoundError:
        return None

def create_cb7(directory:str) -> str:
    """
    Creates a cb7 archive containing all the files in a given directory.
    
    :param directory: Directory with files to compress into archive
    :type directory: str, required
    :return: Full path of the created cb7 archive
    :rtype: str
    """
    try:
        # Get filenames
        full_directory = abspath(directory)
        cb7 = abspath(join(full_directory, basename(full_directory) + ".cb7"))
        # Get list of files in the directory
        files = listdir(full_directory)
        # Create empty cb7 file
        with SevenZipFile(cb7, "w") as out_file: pass
        assert exists(cb7)
        # Write contents of directory to cb7 file
        for file in tqdm(files):
            full_file = abspath(join(full_directory, file))
            with SevenZipFile(cb7, "a") as out_file:
                out_file.writeall(full_file, basename(file))
        # Return the path of the written cb7 archive
        return cb7
    except FileNotFoundError:
        return None