#!/usr/bin/env python3

from metadata_magic.main.comic_archive.comic_archive import create_cb7
from metadata_magic.main.comic_archive.comic_archive import create_cbz
from metadata_magic.test.temp_file_tools import create_text_file, get_temp_dir
from os import listdir, mkdir, pardir, rename
from os.path import abspath, basename, exists, isdir, join
from py7zr import SevenZipFile
from zipfile import ZipFile

def test_create_cbz():
    """
    Tests the create_cbz function
    """
    # Test creating a cbz file with loose files
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    create_text_file(text_file, "Some text!")
    other_file = abspath(join(temp_dir, "other.txt"))
    create_text_file(other_file, "Other text file.")
    assert exists(text_file)
    assert exists(other_file)
    cbz = create_cbz(temp_dir)
    assert exists(cbz)
    assert basename(cbz) == basename(temp_dir) + ".cbz"
    assert abspath(join(cbz, pardir)) == temp_dir
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with ZipFile(cbz, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 2
    assert exists(abspath(join(extract_dir, "text.txt")))
    assert exists(abspath(join(extract_dir, "other.txt")))
    # Test creating a cbz file with internal directories
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "main.txt"))
    sub_dir = abspath(join(temp_dir, "sub"))
    other_file = abspath(join(sub_dir, "sub_text.txt"))
    mkdir(sub_dir)
    create_text_file(text_file, "TEXT!")
    create_text_file(other_file, "sub")
    assert exists(text_file)
    assert exists(sub_dir)
    assert exists(other_file)
    cbz = create_cbz(temp_dir)
    assert exists(cbz)
    assert basename(cbz) == basename(temp_dir) + ".cbz"
    assert abspath(join(cbz, pardir)) == temp_dir
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with ZipFile(cbz, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 2
    assert exists(abspath(join(extract_dir, "main.txt")))
    sub = abspath(join(extract_dir, "sub"))
    assert exists(sub)
    assert isdir(sub)
    assert exists(abspath(join(sub, "sub_text.txt")))
    # Test creating cbz file with multiple internal directories
    temp_dir = get_temp_dir()
    sub_dir = abspath(join(temp_dir, "sub"))
    deeper = abspath(join(sub_dir, "deeper"))
    text_file = abspath(join(temp_dir, "text.txt"))
    sub_file = abspath(join(sub_dir, "sub.txt"))
    other_sub = abspath(join(sub_dir, "sub2.txt"))
    deep_file = abspath(join(deeper, "deep.txt"))
    mkdir(sub_dir)
    mkdir(deeper)
    create_text_file(text_file, "This is text!")
    create_text_file(sub_file, "Subtext?")
    create_text_file(other_sub, "More subtext.")
    create_text_file(deep_file, "Even deeper!!!")
    assert isdir(sub_dir)
    assert isdir(deeper)
    assert exists(text_file)
    assert exists(sub_file)
    assert exists(other_sub)
    assert exists(deep_file)
    cbz = create_cbz(temp_dir)
    assert exists(cbz)
    assert basename(cbz) == basename(temp_dir) + ".cbz"
    assert abspath(join(cbz, pardir)) == temp_dir
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with ZipFile(cbz, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 2
    assert exists(abspath(join(extract_dir, "text.txt")))
    sub_dir = abspath(join(extract_dir, "sub"))
    assert isdir(sub_dir)
    assert len(listdir(sub_dir)) == 3
    assert exists(abspath(join(sub_dir, "sub.txt")))
    assert exists(abspath(join(sub_dir, "sub2.txt")))
    deeper = abspath(join(sub_dir, "deeper"))
    assert isdir(deeper)
    assert len(listdir(deeper)) == 1
    assert exists(abspath(join(deeper, "deep.txt")))
    # Test with non-existant file
    assert create_cbz("/non/existant/dir") is None

def test_create_cb7():
    """
    Tests the create_cb7 function
    """
    # Test creating a cb7 file with loose files
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    create_text_file(text_file, "Some text!")
    other_file = abspath(join(temp_dir, "other.txt"))
    create_text_file(other_file, "Other text file.")
    assert exists(text_file)
    assert exists(other_file)
    cb7 = create_cb7(temp_dir)
    assert exists(cb7)
    assert basename(cb7) == basename(temp_dir) + ".cb7"
    assert abspath(join(cb7, pardir)) == temp_dir
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with SevenZipFile(cb7, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 2
    assert exists(abspath(join(extract_dir, "text.txt")))
    assert exists(abspath(join(extract_dir, "other.txt")))
    # Test creating a cb7 file with internal directories
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "main.txt"))
    sub_dir = abspath(join(temp_dir, "sub"))
    other_file = abspath(join(sub_dir, "sub_text.txt"))
    mkdir(sub_dir)
    create_text_file(text_file, "TEXT!")
    create_text_file(other_file, "sub")
    assert exists(text_file)
    assert exists(sub_dir)
    assert exists(other_file)
    cb7 = create_cb7(temp_dir)
    assert exists(cb7)
    assert basename(cb7) == basename(temp_dir) + ".cb7"
    assert abspath(join(cb7, pardir)) == temp_dir
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with SevenZipFile(cb7, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 2
    assert exists(abspath(join(extract_dir, "main.txt")))
    sub = abspath(join(extract_dir, "sub"))
    assert exists(sub)
    assert isdir(sub)
    assert exists(abspath(join(sub, "sub_text.txt")))
    # Test creating cb7 file with multiple internal directories
    temp_dir = get_temp_dir()
    sub_dir = abspath(join(temp_dir, "sub"))
    deeper = abspath(join(sub_dir, "deeper"))
    text_file = abspath(join(temp_dir, "text.txt"))
    sub_file = abspath(join(sub_dir, "sub.txt"))
    other_sub = abspath(join(sub_dir, "sub2.txt"))
    deep_file = abspath(join(deeper, "deep.txt"))
    mkdir(sub_dir)
    mkdir(deeper)
    create_text_file(text_file, "This is text!")
    create_text_file(sub_file, "Subtext?")
    create_text_file(other_sub, "More subtext.")
    create_text_file(deep_file, "Even deeper!!!")
    assert isdir(sub_dir)
    assert isdir(deeper)
    assert exists(text_file)
    assert exists(sub_file)
    assert exists(other_sub)
    assert exists(deep_file)
    cb7 = create_cb7(temp_dir)
    assert exists(cb7)
    assert basename(cb7) == basename(temp_dir) + ".cb7"
    assert abspath(join(cb7, pardir)) == temp_dir
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with SevenZipFile(cb7, mode="r") as file:
        file.extractall(path=extract_dir)
    assert len(listdir(extract_dir)) == 2
    assert exists(abspath(join(extract_dir, "text.txt")))
    sub_dir = abspath(join(extract_dir, "sub"))
    assert isdir(sub_dir)
    assert len(listdir(sub_dir)) == 3
    assert exists(abspath(join(sub_dir, "sub.txt")))
    assert exists(abspath(join(sub_dir, "sub2.txt")))
    deeper = abspath(join(sub_dir, "deeper"))
    assert isdir(deeper)
    assert len(listdir(deeper)) == 1
    assert exists(abspath(join(deeper, "deep.txt")))
    # Test with non-existant file
    assert create_cb7("/non/existant/dir") is None
