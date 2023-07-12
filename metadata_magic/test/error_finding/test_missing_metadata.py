#!/usr/bin/env python3

from metadata_magic.main.error_finding.missing_metadata import find_missing_metadata
from metadata_magic.main.file_tools.file_tools import get_temp_dir
from metadata_magic.main.file_tools.file_tools import write_text_file
from os import mkdir, pardir
from os.path import abspath, basename, exists, join

def test_find_missing_metadata():
    """
    Tests the find_missing_metadata function.
    """
    # Test with empty directory
    temp_dir = get_temp_dir()
    assert exists(temp_dir)
    assert find_missing_metadata(temp_dir) == []
    # Test with no unlinked files
    sub = abspath(join(temp_dir, "sub"))
    mkdir(sub)
    write_text_file(abspath(join(temp_dir, "main.json")), "BLAH")
    write_text_file(abspath(join(temp_dir, "main.png")), "BLAH")
    write_text_file(abspath(join(sub, "unlinked.json")), "BLAH")
    assert find_missing_metadata(temp_dir) == []
    # Test with unlinked files
    write_text_file(abspath(join(temp_dir, "unlinked.txt")), "BLAH")
    write_text_file(abspath(join(temp_dir, "thing.jpg")), "BLAH")
    write_text_file(abspath(join(sub, "next.cbz")), "BLAH")
    missing_metadata = find_missing_metadata(temp_dir)
    assert len(missing_metadata) == 3
    assert basename(missing_metadata[0]) == "next.cbz"
    assert abspath(join(missing_metadata[0], pardir)) == sub
    assert basename(missing_metadata[1]) == "thing.jpg"
    assert abspath(join(missing_metadata[1], pardir)) == temp_dir
    assert basename(missing_metadata[2]) == "unlinked.txt"
    assert abspath(join(missing_metadata[2], pardir)) == temp_dir
