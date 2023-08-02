#!/usr/bin/env python3

import os
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.meta_finder as mm_meta_finder
from os.path import abspath, basename, exists, join

def test_separate_files():
    """
    Tests the separate_files function
    """
    # Test with an empty folder
    temp_dir = mm_file_tools.get_temp_dir()
    assert exists(temp_dir)
    jsons, media = mm_meta_finder.separate_files(temp_dir)
    assert jsons == []
    assert media == []
    # Test only in main directory
    mm_file_tools.write_text_file(abspath(join(temp_dir, "main.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "other.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "image.png")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "thing.txt")), "BLAH")
    jsons, media = mm_meta_finder.separate_files(temp_dir)
    assert len(jsons) == 2
    assert basename(jsons[0]) == "main.json"
    assert basename(jsons[1]) == "other.json"
    assert len(media) == 2
    assert basename(media[0]) == "image.png"
    assert basename(media[1]) == "thing.txt"
    # Test with sub-directories
    sub1 = abspath(join(temp_dir, "sub1"))
    sub2 = abspath(join(temp_dir, "sub2"))
    os.mkdir(sub1)
    os.mkdir(sub2)
    assert exists(sub1)
    assert exists(sub2)
    mm_file_tools.write_text_file(abspath(join(sub1, "sub.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub2, "more.jpeg")), "BLAH")
    jsons, media = mm_meta_finder.separate_files(temp_dir)
    assert len(jsons) == 3
    assert basename(jsons[0]) == "main.json"
    assert basename(jsons[1]) == "other.json"
    assert basename(jsons[2]) == "sub.json"
    assert len(media) == 3
    assert basename(media[0]) == "image.png"
    assert basename(media[1]) == "more.jpeg"
    assert basename(media[2]) == "thing.txt"

def test_get_pairs():
    """
    Tests the get_pairs function.
    """
    # Test with an empty folder
    temp_dir = mm_file_tools.get_temp_dir()
    assert exists(temp_dir)
    assert mm_meta_finder.get_pairs(temp_dir) == []
    # Test with unpaired files
    mm_file_tools.write_text_file(abspath(join(temp_dir, "unlinked.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "thing.txt")), "BLAH")
    assert mm_meta_finder.get_pairs(temp_dir) == []
    # Test paired JSONs with extensions in filename
    sub = abspath(join(temp_dir, "sub"))
    os.mkdir(sub)
    mm_file_tools.write_text_file(abspath(join(temp_dir, "linked.png.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "linked.png")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub, "other.txt.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub, "other.txt")), "BLAH")
    pairs = mm_meta_finder.get_pairs(temp_dir)
    assert len(pairs) == 2
    assert basename(pairs[0]["media"]) == "linked.png"
    assert basename(pairs[0]["json"]) == "linked.png.json"
    assert basename(pairs[1]["media"]) == "other.txt"
    assert basename(pairs[1]["json"]) == "other.txt.json"
    # Test JSON with wrong extension in filename
    mm_file_tools.write_text_file(abspath(join(sub, "unmatched.zip.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub, "unmatched.cbz")), "BLAH")
    pairs = mm_meta_finder.get_pairs(temp_dir)
    assert len(pairs) == 2
    # Test paired JSONs without extensions in filename
    mm_file_tools.write_text_file(abspath(join(temp_dir, "media.jpg")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "media.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub, "next thing.ogg")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub, "next thing.json")), "BLAH")
    pairs = mm_meta_finder.get_pairs(temp_dir)
    assert len(pairs) == 4
    assert basename(pairs[0]["media"]) == "linked.png"
    assert basename(pairs[0]["json"]) == "linked.png.json"
    assert basename(pairs[1]["media"]) == "media.jpg"
    assert basename(pairs[1]["json"]) == "media.json"
    assert basename(pairs[2]["media"]) == "next thing.ogg"
    assert basename(pairs[2]["json"]) == "next thing.json"
    assert basename(pairs[3]["media"]) == "other.txt"
    assert basename(pairs[3]["json"]) == "other.txt.json"
    # Test files with same names in different directories
    mm_file_tools.write_text_file(abspath(join(sub, "different.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "different.gif")), "BLAH")
    pairs = mm_meta_finder.get_pairs(temp_dir)
    assert len(pairs) == 4
