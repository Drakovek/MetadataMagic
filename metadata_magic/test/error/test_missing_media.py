#!/usr/bin/env python3

import os
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.error.missing_media as mm_missing_media
from os.path import abspath, basename, exists, join

def test_find_missing_media():
    """
    Test the find_missing_media function.
    """
    # Test with empty directory
    temp_dir = mm_file_tools.get_temp_dir()
    assert exists(temp_dir)
    assert mm_missing_media.find_missing_media(temp_dir) == []
    # Test with no unlinked files
    sub = abspath(join(temp_dir, "sub"))
    os.mkdir(sub)
    mm_file_tools.write_text_file(abspath(join(temp_dir, "main.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "main.png")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub, "unlinked.txt")), "BLAH")
    assert mm_missing_media.find_missing_media(temp_dir) == []
    # Test with unlinked files
    mm_file_tools.write_text_file(abspath(join(temp_dir, "unlinked.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "thing.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub, "next.json")), "BLAH")
    missing_media = mm_missing_media.find_missing_media(temp_dir)
    assert len(missing_media) == 3
    assert basename(missing_media[0]) == "next.json"
    assert abspath(join(missing_media[0], os.pardir)) == sub
    assert basename(missing_media[1]) == "thing.json"
    assert abspath(join(missing_media[1], os.pardir)) == temp_dir
    assert basename(missing_media[2]) == "unlinked.json"
    assert abspath(join(missing_media[2], os.pardir)) == temp_dir
