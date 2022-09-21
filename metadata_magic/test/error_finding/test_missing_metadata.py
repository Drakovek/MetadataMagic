#!/usr/bin/env python3

from metadata_magic.main.error_finding.missing_metadata import find_missing_metadata
from metadata_magic.test.temp_dir import get_temp_dir
from os import mkdir, pardir
from os.path import abspath, basename, join, exists

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
    with open(abspath(join(temp_dir, "main.json")), "w") as out_file:
        out_file.write("BLAH")
    with open(abspath(join(temp_dir, "main.png")), "w") as out_file:
        out_file.write("BLAH")
    with open(abspath(join(sub, "unlinked.json")), "w") as out_file:
        out_file.write("BLAH")
    assert find_missing_metadata(temp_dir) == []
    # Test with unlinked files
    with open(abspath(join(temp_dir, "unlinked.txt")), "w") as out_file:
        out_file.write("BLAH")
    with open(abspath(join(temp_dir, "thing.jpg")), "w") as out_file:
        out_file.write("BLAH")
    with open(abspath(join(sub, "next.cbz")), "w") as out_file:
        out_file.write("BLAH")
    missing_metadata = find_missing_metadata(temp_dir)
    assert len(missing_metadata) == 3
    assert basename(missing_metadata[0]) == "next.cbz"
    assert abspath(join(missing_metadata[0], pardir)) == sub
    assert basename(missing_metadata[1]) == "thing.jpg"
    assert abspath(join(missing_metadata[1], pardir)) == temp_dir
    assert basename(missing_metadata[2]) == "unlinked.txt"
    assert abspath(join(missing_metadata[2], pardir)) == temp_dir
