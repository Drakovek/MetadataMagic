#!/usr/bin/env python3

from metadata_magic.main.meta_reader import get_empty_metadata
from metadata_magic.main.comic_archive.comic_xml import get_comic_xml
from metadata_magic.main.error_finding.missing_fields import find_missing_fields
from metadata_magic.main.error_finding.missing_fields import find_missing_comic_info
from metadata_magic.main.comic_archive.comic_archive import create_cbz
from metadata_magic.main.file_tools.file_tools import get_temp_dir
from metadata_magic.main.file_tools.file_tools import create_zip
from metadata_magic.main.file_tools.file_tools import write_text_file
from os import listdir, mkdir, remove
from os.path import abspath, basename, exists, join
from shutil import copy

def test_find_missing_comic_info():
    """
    Tests the find_missing_comic_info function.
    """
    # Create CBZ test files
    temp_dir = get_temp_dir()
    cbz_build_dir = get_temp_dir("dvk_cbz_builder")
    text_file = abspath(join(cbz_build_dir, "text.txt"))
    write_text_file(text_file, "This is text")
    assert exists(text_file)
    cbz_file = create_cbz(cbz_build_dir, "no-meta")
    assert exists(cbz_file)
    copy(cbz_file, abspath(join(temp_dir, basename(cbz_file))))
    remove(cbz_file)
    cbz_file = create_cbz(cbz_build_dir, "empty-meta", metadata=get_empty_metadata())
    assert exists(cbz_file)
    copy(cbz_file, abspath(join(temp_dir, basename(cbz_file))))
    remove(cbz_file)
    metadata = get_empty_metadata()
    metadata["title"] = "Bare Minimum"
    cbz_file = create_cbz(cbz_build_dir, "some-meta", metadata=metadata)
    assert exists(cbz_file)
    copy(cbz_file, abspath(join(temp_dir, basename(cbz_file))))
    remove(cbz_file)
    assert sorted(listdir(temp_dir)) == ["empty-meta.cbz", "no-meta.cbz", "some-meta.cbz"]
    # Test finding CBZ files with no metadata
    missing = find_missing_comic_info(temp_dir)
    assert len(missing) == 2
    assert basename(missing[0]) == "empty-meta.cbz"
    assert basename(missing[1]) == "no-meta.cbz"
    # Test finding CBZ files with metadata in the wrong place
    sub_dir = abspath(join(cbz_build_dir, "sub"))
    mkdir(sub_dir)
    metadata_file = abspath(join(sub_dir, "ComicInfo.xml"))
    write_text_file(metadata_file, get_comic_xml(metadata))
    assert exists(metadata_file)
    cbz_file = abspath(join(temp_dir, "internal-meta.cbz"))
    create_zip(cbz_build_dir, cbz_file)
    assert sorted(listdir(temp_dir)) == ["empty-meta.cbz", "internal-meta.cbz", "no-meta.cbz", "some-meta.cbz"]
    missing = find_missing_comic_info(temp_dir)
    assert len(missing) == 3
    assert basename(missing[0]) == "empty-meta.cbz"
    assert basename(missing[1]) == "internal-meta.cbz"
    assert basename(missing[2]) == "no-meta.cbz"

def test_find_missing_fields():
    """
    Tests the find_missing_fields function.
    """
    # Create CBZ test file A
    temp_dir = get_temp_dir()
    cbz_build_dir = get_temp_dir("dvk_cbz_builder")
    text_file = abspath(join(cbz_build_dir, "text.txt"))
    write_text_file(text_file, "This is text!!!")
    assert exists(text_file)
    metadata = get_empty_metadata()
    metadata["series"] = "The Series"
    metadata["description"] = "Description"
    metadata["tags"] = "More Stuff"
    metadata["score"] = 5
    cbz_file = create_cbz(cbz_build_dir, "CBZ-A", metadata=metadata)
    assert exists(cbz_file)
    copy(cbz_file, abspath(join(temp_dir, basename(cbz_file))))
    remove(cbz_file)
    # Create CBZ test file B
    metadata = get_empty_metadata()
    metadata["title"] = "Comic Book B"
    metadata["description"] = "Something"
    metadata["date"] = "2054-03-29"
    metadata["tags"] = "something"
    metadata["url"] = "/page/thing"
    metadata["score"] = 2
    cbz_file = create_cbz(cbz_build_dir, "CBZ-B", metadata=metadata)
    assert exists(cbz_file)
    copy(cbz_file, abspath(join(temp_dir, basename(cbz_file))))
    remove(cbz_file)
    # Create CBZ test file C
    metadata = get_empty_metadata()
    metadata["date"] = "2040-12-03"
    metadata["artist"] = "Person"
    metadata["publisher"] = "New Thing LLC"
    metadata["url"] = "HopefullyNotReal.website"
    metadata["age_rating"] = "Everyone"
    cbz_file = create_cbz(cbz_build_dir, "CBZ-C", metadata=metadata)
    assert exists(cbz_file)
    copy(cbz_file, abspath(join(temp_dir, basename(cbz_file))))
    remove(cbz_file)
    # Create CBZ test file D
    metadata = get_empty_metadata()
    metadata["title"] = "Comic Book D"
    metadata["series"] = "The Series"
    metadata["writer"] = "Different Person"
    metadata["tags"] = "these,are,tags"
    metadata["age_rating"] = "Teen"
    cbz_file = create_cbz(cbz_build_dir, "CBZ-D", metadata=metadata)
    assert exists(cbz_file)
    copy(cbz_file, abspath(join(temp_dir, basename(cbz_file))))
    remove(cbz_file)
    assert sorted(listdir(temp_dir)) == ["CBZ-A.cbz", "CBZ-B.cbz", "CBZ-C.cbz", "CBZ-D.cbz"]
    # Test finding missing title
    missing = find_missing_fields(temp_dir, ["title"])
    assert len(missing) == 2
    assert basename(missing[0]) == "CBZ-A.cbz"
    assert basename(missing[1]) == "CBZ-C.cbz"
    # Test finding missing series
    missing = find_missing_fields(temp_dir, ["series"])
    assert len(missing) == 2
    assert basename(missing[0]) == "CBZ-B.cbz"
    assert basename(missing[1]) == "CBZ-C.cbz"
    # Test finding missing description
    missing = find_missing_fields(temp_dir, ["description"])
    assert len(missing) == 2
    assert basename(missing[0]) == "CBZ-C.cbz"
    assert basename(missing[1]) == "CBZ-D.cbz"
    # Test finding missing date
    missing = find_missing_fields(temp_dir, ["date"])
    assert len(missing) == 2
    assert basename(missing[0]) == "CBZ-A.cbz"
    assert basename(missing[1]) == "CBZ-D.cbz"
    # Test finding missing artist
    missing = find_missing_fields(temp_dir, ["artist", "writer"])
    assert len(missing) == 2
    assert basename(missing[0]) == "CBZ-A.cbz"
    assert basename(missing[1]) == "CBZ-B.cbz"
    # Test finding missing publisher
    missing = find_missing_fields(temp_dir, ["publisher"])
    assert len(missing) == 3
    assert basename(missing[0]) == "CBZ-A.cbz"
    assert basename(missing[1]) == "CBZ-B.cbz"
    assert basename(missing[2]) == "CBZ-D.cbz"
    # Test finding missing tags
    missing = find_missing_fields(temp_dir, ["tags"])
    assert len(missing) == 1
    assert basename(missing[0]) == "CBZ-C.cbz"
    # Test finding missing url
    missing = find_missing_fields(temp_dir, ["url"])
    assert len(missing) == 2
    assert basename(missing[0]) == "CBZ-A.cbz"
    assert basename(missing[1]) == "CBZ-D.cbz"
    # Test finding missing age_rating
    missing = find_missing_fields(temp_dir, ["age_rating"], null_value="Unknown")
    assert len(missing) == 2
    assert basename(missing[0]) == "CBZ-A.cbz"
    assert basename(missing[1]) == "CBZ-B.cbz"
    # Test finding missing score
    missing = find_missing_fields(temp_dir, ["score"])
    assert len(missing) == 2
    assert basename(missing[0]) == "CBZ-C.cbz"
    assert basename(missing[1]) == "CBZ-D.cbz"
