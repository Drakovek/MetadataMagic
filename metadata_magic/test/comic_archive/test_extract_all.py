#!/usr/bin/env python3

from metadata_magic.main.meta_reader import get_empty_metadata
from metadata_magic.main.comic_archive.comic_archive import create_cbz
from metadata_magic.main.comic_archive.extract_all import extract_all
from metadata_magic.main.file_tools.file_tools import get_temp_dir
from metadata_magic.main.file_tools.file_tools import write_text_file
from os import listdir, mkdir
from os.path import abspath, exists, join
from shutil import copytree, move, rmtree

def test_extract_all():
    """
    Tests the extract_all function.
    """
    # Create test cbz files
    temp_dir = get_temp_dir()
    cbz_builder = get_temp_dir("dvk_test_cbz_builder")
    text_file = abspath(join(cbz_builder, "text.txt"))
    write_text_file(text_file, "This is text.")
    assert exists(text_file)
    metadata = get_empty_metadata()
    metadata["title"] = "Some Title"
    cbz_file = create_cbz(cbz_builder, "One", metadata=metadata)
    assert exists(cbz_file)
    move(cbz_file, abspath(join(temp_dir, "simple.cbz")))
    cbz_builder = get_temp_dir("dvk_test_cbz_builder")
    sub_dir_1 = abspath(join(cbz_builder, "1-sub"))
    sub_dir_2 = abspath(join(cbz_builder, "2-sub"))
    media_file = abspath(join(sub_dir_1, "media.png"))
    text_file = abspath(join(sub_dir_2, "text.txt"))
    mkdir(sub_dir_1)
    mkdir(sub_dir_2)
    write_text_file(media_file, "Media")
    write_text_file(text_file, "Text")
    assert exists(media_file)
    assert exists(text_file)
    cbz_file = create_cbz(cbz_builder, "Two", metadata=metadata)
    assert exists(cbz_file)
    move(cbz_file, abspath(join(temp_dir, "subs.cbz")))
    assert sorted(listdir(temp_dir)) == ["simple.cbz", "subs.cbz"]
    # Test extracting cbz files
    temp_dir_2 = get_temp_dir("dvk_test_extract")
    extract_dir = abspath(join(temp_dir_2, "new"))
    copytree(temp_dir, extract_dir)
    assert sorted(listdir(extract_dir)) == ["simple.cbz", "subs.cbz"]
    extract_all(extract_dir, remove_internals=False)
    assert sorted(listdir(extract_dir)) == ["simple", "subs"]
    sub_dir = abspath(join(extract_dir, "simple"))
    assert sorted(listdir(sub_dir)) == ["ComicInfo.xml", "One"]
    assert listdir(abspath(join(sub_dir, "One"))) == ["text.txt"]
    sub_dir = abspath(join(extract_dir, "subs"))
    assert sorted(listdir(sub_dir)) == ["1-sub", "2-sub", "ComicInfo.xml"]
    assert listdir(abspath(join(sub_dir, "1-sub"))) == ["media.png"]
    assert listdir(abspath(join(sub_dir, "2-sub"))) == ["text.txt"]
    # Test extracting cbz files while removing the ComicInfo.xml file
    rmtree(extract_dir)
    copytree(temp_dir, extract_dir)
    assert sorted(listdir(extract_dir)) == ["simple.cbz", "subs.cbz"]
    extract_all(extract_dir, remove_internals=False, remove_metadata=True)
    assert sorted(listdir(extract_dir)) == ["simple", "subs"]
    sub_dir = abspath(join(extract_dir, "simple"))
    assert sorted(listdir(sub_dir)) == ["One"]
    assert listdir(abspath(join(sub_dir, "One"))) == ["text.txt"]
    sub_dir = abspath(join(extract_dir, "subs"))
    assert sorted(listdir(sub_dir)) == ["1-sub", "2-sub"]
    assert listdir(abspath(join(sub_dir, "1-sub"))) == ["media.png"]
    assert listdir(abspath(join(sub_dir, "2-sub"))) == ["text.txt"]
    # Test extracting cbz into the base directory
    rmtree(extract_dir)
    copytree(temp_dir, extract_dir)
    assert sorted(listdir(extract_dir)) == ["simple.cbz", "subs.cbz"]
    extract_all(extract_dir, create_folders=False, remove_internals=False)
    assert sorted(listdir(extract_dir)) == ["1-sub", "2-sub", "One"]
    assert listdir(abspath(join(extract_dir, "1-sub"))) == ["media.png"]
    assert listdir(abspath(join(extract_dir, "2-sub"))) == ["text.txt"]
    assert listdir(abspath(join(extract_dir, "One"))) == ["text.txt"]
    # Test extracting cbz files without the internal folder
    rmtree(extract_dir)
    copytree(temp_dir, extract_dir)
    assert sorted(listdir(extract_dir)) == ["simple.cbz", "subs.cbz"]
    extract_all(extract_dir, remove_internals=True, remove_metadata=True)
    assert sorted(listdir(extract_dir)) == ["simple", "subs"]
    assert listdir(abspath(join(extract_dir, "simple"))) == ["text.txt"]
    sub_dir = abspath(join(extract_dir, "subs"))
    assert sorted(listdir(sub_dir)) == ["1-sub", "2-sub"]
    assert listdir(abspath(join(sub_dir, "1-sub"))) == ["media.png"]
    assert listdir(abspath(join(sub_dir, "2-sub"))) == ["text.txt"]
    # Test extracting files without internal folder directly into the base directory
    rmtree(extract_dir)
    copytree(temp_dir, extract_dir)
    assert sorted(listdir(extract_dir)) == ["simple.cbz", "subs.cbz"]
    extract_all(extract_dir, create_folders=False, remove_internals=True, remove_metadata=True)
    assert sorted(listdir(extract_dir)) == ["1-sub", "2-sub", "text.txt"]
    assert listdir(abspath(join(extract_dir, "1-sub"))) == ["media.png"]
    assert listdir(abspath(join(extract_dir, "2-sub"))) == ["text.txt"]