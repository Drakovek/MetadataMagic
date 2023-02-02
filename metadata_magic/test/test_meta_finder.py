#!/usr/bin/env python3

from metadata_magic.main.comic_archive.comic_archive import get_temp_dir
from metadata_magic.main.meta_finder import get_pairs, separate_files
from metadata_magic.test.temp_file_tools import create_text_file
from os import mkdir
from os.path import abspath, basename, join, exists

def test_separate_files():
    """
    Tests the separate_files function
    """
    # Test with an empty folder
    temp_dir = get_temp_dir()
    assert exists(temp_dir)
    jsons, media = separate_files(temp_dir)
    assert jsons == []
    assert media == []
    # Test only in main directory
    create_text_file(abspath(join(temp_dir, "main.json")), "BLAH")
    create_text_file(abspath(join(temp_dir, "other.json")), "BLAH")
    create_text_file(abspath(join(temp_dir, "image.png")), "BLAH")
    create_text_file(abspath(join(temp_dir, "thing.txt")), "BLAH")
    jsons, media = separate_files(temp_dir)
    assert len(jsons) == 2
    assert basename(jsons[0]) == "main.json"
    assert basename(jsons[1]) == "other.json"
    assert len(media) == 2
    assert basename(media[0]) == "image.png"
    assert basename(media[1]) == "thing.txt"
    # Test with sub-directories
    sub1 = abspath(join(temp_dir, "sub1"))
    sub2 = abspath(join(temp_dir, "sub2"))
    mkdir(sub1)
    mkdir(sub2)
    assert exists(sub1)
    assert exists(sub2)
    create_text_file(abspath(join(sub1, "sub.json")), "BLAH")
    create_text_file(abspath(join(sub2, "more.jpeg")), "BLAH")
    jsons, media = separate_files(temp_dir)
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
    temp_dir = get_temp_dir()
    assert exists(temp_dir)
    assert get_pairs(temp_dir) == []
    # Test with unpaired files
    create_text_file(abspath(join(temp_dir, "unlinked.json")), "BLAH")
    create_text_file(abspath(join(temp_dir, "thing.txt")), "BLAH")
    assert get_pairs(temp_dir) == []
    # Test paired JSONs with extensions in filename
    sub = abspath(join(temp_dir, "sub"))
    mkdir(sub)
    create_text_file(abspath(join(temp_dir, "linked.png.json")), "BLAH")
    create_text_file(abspath(join(temp_dir, "linked.png")), "BLAH")
    create_text_file(abspath(join(sub, "other.txt.json")), "BLAH")
    create_text_file(abspath(join(sub, "other.txt")), "BLAH")
    pairs = get_pairs(temp_dir)
    assert len(pairs) == 2
    assert basename(pairs[0]["media"]) == "linked.png"
    assert basename(pairs[0]["json"]) == "linked.png.json"
    assert basename(pairs[1]["media"]) == "other.txt"
    assert basename(pairs[1]["json"]) == "other.txt.json"
    # Test JSON with wrong extension in filename
    create_text_file(abspath(join(sub, "unmatched.zip.json")), "BLAH")
    create_text_file(abspath(join(sub, "unmatched.cbz")), "BLAH")
    pairs = get_pairs(temp_dir)
    assert len(pairs) == 2
    # Test paired JSONs without extensions in filename
    create_text_file(abspath(join(temp_dir, "media.jpg")), "BLAH")
    create_text_file(abspath(join(temp_dir, "media.json")), "BLAH")
    create_text_file(abspath(join(sub, "next thing.ogg")), "BLAH")
    create_text_file(abspath(join(sub, "next thing.json")), "BLAH")
    pairs = get_pairs(temp_dir)
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
    create_text_file(abspath(join(sub, "different.json")), "BLAH")
    create_text_file(abspath(join(temp_dir, "different.gif")), "BLAH")
    pairs = get_pairs(temp_dir)
    assert len(pairs) == 4
