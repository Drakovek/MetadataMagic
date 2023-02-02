#!/usr/bin/env python3

from metadata_magic.main.comic_archive.comic_archive import get_temp_dir
from metadata_magic.main.error_finding.missing_media import find_missing_media
from metadata_magic.test.temp_file_tools import create_text_file
from os import mkdir, pardir
from os.path import abspath, basename, join, exists

def test_find_missing_media():
    """
    Test the find_missing_media function.
    """
    # Test with empty directory
    temp_dir = get_temp_dir()
    assert exists(temp_dir)
    assert find_missing_media(temp_dir) == []
    # Test with no unlinked files
    sub = abspath(join(temp_dir, "sub"))
    mkdir(sub)
    create_text_file(abspath(join(temp_dir, "main.json")), "BLAH")
    create_text_file(abspath(join(temp_dir, "main.png")), "BLAH")
    create_text_file(abspath(join(sub, "unlinked.txt")), "BLAH")
    assert find_missing_media(temp_dir) == []
    # Test with unlinked files
    create_text_file(abspath(join(temp_dir, "unlinked.json")), "BLAH")
    create_text_file(abspath(join(temp_dir, "thing.json")), "BLAH")
    create_text_file(abspath(join(sub, "next.json")), "BLAH")
    missing_media = find_missing_media(temp_dir)
    assert len(missing_media) == 3
    assert basename(missing_media[0]) == "next.json"
    assert abspath(join(missing_media[0], pardir)) == sub
    assert basename(missing_media[1]) == "thing.json"
    assert abspath(join(missing_media[1], pardir)) == temp_dir
    assert basename(missing_media[2]) == "unlinked.json"
    assert abspath(join(missing_media[2], pardir)) == temp_dir