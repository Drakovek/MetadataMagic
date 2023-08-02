#!/usr/bin/env python3

import os
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.error.missing_metadata as mm_missing_metadata
from os.path import abspath, basename, join, exists

def test_find_missing_metadata():
    """
    Tests the find_missing_metadata function.
    """
    # Test with empty directory
    temp_dir = mm_file_tools.get_temp_dir()
    assert exists(temp_dir)
    assert mm_missing_metadata.find_missing_metadata(temp_dir) == []
    # Test with no unlinked files
    sub = abspath(join(temp_dir, "sub"))
    os.mkdir(sub)
    mm_file_tools.write_text_file(abspath(join(temp_dir, "main.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "main.png")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub, "unlinked.json")), "BLAH")
    assert mm_missing_metadata.find_missing_metadata(temp_dir) == []
    # Test with unlinked files
    mm_file_tools.write_text_file(abspath(join(temp_dir, "unlinked.txt")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "thing.jpg")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub, "next.cbz")), "BLAH")
    missing_metadata = mm_missing_metadata.find_missing_metadata(temp_dir)
    assert len(missing_metadata) == 3
    assert basename(missing_metadata[0]) == "next.cbz"
    assert abspath(join(missing_metadata[0], os.pardir)) == sub
    assert basename(missing_metadata[1]) == "thing.jpg"
    assert abspath(join(missing_metadata[1], os.pardir)) == temp_dir
    assert basename(missing_metadata[2]) == "unlinked.txt"
    assert abspath(join(missing_metadata[2], os.pardir)) == temp_dir
