#!/usr/bin/env python3

import os
import shutil
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.comic_archive as mm_comic_archive
import metadata_magic.archive.extract_all as mm_extract_all
from os.path import abspath, exists, join

def test_extract_all():
    """
    Tests the extract_all function.
    """
    # Create test cbz files
    temp_dir = mm_file_tools.get_temp_dir()
    cbz_builder = mm_file_tools.get_temp_dir("dvk_test_cbz_builder")
    text_file = abspath(join(cbz_builder, "text.txt"))
    mm_file_tools.write_text_file(text_file, "This is text.")
    assert exists(text_file)
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Some Title"
    cbz_file = mm_comic_archive.create_cbz(cbz_builder, "One", metadata=metadata)
    assert exists(cbz_file)
    shutil.move(cbz_file, abspath(join(temp_dir, "simple.cbz")))
    cbz_builder = mm_file_tools.get_temp_dir("dvk_test_cbz_builder")
    sub_dir_1 = abspath(join(cbz_builder, "1-sub"))
    sub_dir_2 = abspath(join(cbz_builder, "2-sub"))
    media_file = abspath(join(sub_dir_1, "media.png"))
    text_file = abspath(join(sub_dir_2, "text.txt"))
    os.mkdir(sub_dir_1)
    os.mkdir(sub_dir_2)
    mm_file_tools.write_text_file(media_file, "Media")
    mm_file_tools.write_text_file(text_file, "Text")
    assert exists(media_file)
    assert exists(text_file)
    cbz_file = mm_comic_archive.create_cbz(cbz_builder, "Two", metadata=metadata)
    assert exists(cbz_file)
    shutil.move(cbz_file, abspath(join(temp_dir, "subs.cbz")))
    assert sorted(os.listdir(temp_dir)) == ["simple.cbz", "subs.cbz"]
    # Test extracting cbz files
    temp_dir_2 = mm_file_tools.get_temp_dir("dvk_test_extract")
    extract_dir = abspath(join(temp_dir_2, "new"))
    shutil.copytree(temp_dir, extract_dir)
    assert sorted(os.listdir(extract_dir)) == ["simple.cbz", "subs.cbz"]
    mm_extract_all.extract_all(extract_dir, remove_internals=False)
    assert sorted(os.listdir(extract_dir)) == ["simple", "subs"]
    sub_dir = abspath(join(extract_dir, "simple"))
    assert sorted(os.listdir(sub_dir)) == ["ComicInfo.xml", "One"]
    assert os.listdir(abspath(join(sub_dir, "One"))) == ["text.txt"]
    sub_dir = abspath(join(extract_dir, "subs"))
    assert sorted(os.listdir(sub_dir)) == ["1-sub", "2-sub", "ComicInfo.xml"]
    assert os.listdir(abspath(join(sub_dir, "1-sub"))) == ["media.png"]
    assert os.listdir(abspath(join(sub_dir, "2-sub"))) == ["text.txt"]
    # Test extracting cbz files while removing the ComicInfo.xml file
    shutil.rmtree(extract_dir)
    shutil.copytree(temp_dir, extract_dir)
    assert sorted(os.listdir(extract_dir)) == ["simple.cbz", "subs.cbz"]
    mm_extract_all.extract_all(extract_dir, remove_internals=False, remove_metadata=True)
    assert sorted(os.listdir(extract_dir)) == ["simple", "subs"]
    sub_dir = abspath(join(extract_dir, "simple"))
    assert sorted(os.listdir(sub_dir)) == ["One"]
    assert os.listdir(abspath(join(sub_dir, "One"))) == ["text.txt"]
    sub_dir = abspath(join(extract_dir, "subs"))
    assert sorted(os.listdir(sub_dir)) == ["1-sub", "2-sub"]
    assert os.listdir(abspath(join(sub_dir, "1-sub"))) == ["media.png"]
    assert os.listdir(abspath(join(sub_dir, "2-sub"))) == ["text.txt"]
    # Test extracting cbz into the base directory
    shutil.rmtree(extract_dir)
    shutil.copytree(temp_dir, extract_dir)
    assert sorted(os.listdir(extract_dir)) == ["simple.cbz", "subs.cbz"]
    mm_extract_all.extract_all(extract_dir, create_folders=False, remove_internals=False)
    assert sorted(os.listdir(extract_dir)) == ["1-sub", "2-sub", "One"]
    assert os.listdir(abspath(join(extract_dir, "1-sub"))) == ["media.png"]
    assert os.listdir(abspath(join(extract_dir, "2-sub"))) == ["text.txt"]
    assert os.listdir(abspath(join(extract_dir, "One"))) == ["text.txt"]
    # Test extracting cbz files without the internal folder
    shutil.rmtree(extract_dir)
    shutil.copytree(temp_dir, extract_dir)
    assert sorted(os.listdir(extract_dir)) == ["simple.cbz", "subs.cbz"]
    mm_extract_all.extract_all(extract_dir, remove_internals=True, remove_metadata=True)
    assert sorted(os.listdir(extract_dir)) == ["simple", "subs"]
    assert os.listdir(abspath(join(extract_dir, "simple"))) == ["text.txt"]
    sub_dir = abspath(join(extract_dir, "subs"))
    assert sorted(os.listdir(sub_dir)) == ["1-sub", "2-sub"]
    assert os.listdir(abspath(join(sub_dir, "1-sub"))) == ["media.png"]
    assert os.listdir(abspath(join(sub_dir, "2-sub"))) == ["text.txt"]
    # Test extracting files without internal folder directly into the base directory
    shutil.rmtree(extract_dir)
    shutil.copytree(temp_dir, extract_dir)
    assert sorted(os.listdir(extract_dir)) == ["simple.cbz", "subs.cbz"]
    mm_extract_all.extract_all(extract_dir, create_folders=False, remove_internals=True, remove_metadata=True)
    assert sorted(os.listdir(extract_dir)) == ["1-sub", "2-sub", "text.txt"]
    assert os.listdir(abspath(join(extract_dir, "1-sub"))) == ["media.png"]
    assert os.listdir(abspath(join(extract_dir, "2-sub"))) == ["text.txt"]
