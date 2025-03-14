#!/usr/bin/env python3

import os
import metadata_magic.test as mm_test
import metadata_magic.meta_finder as mm_meta_finder
from os.path import abspath, basename, join

def test_separate_files():
    """
    Tests the separate_files function
    """
    # Check that all JSON files were found
    jsons, media = mm_meta_finder.separate_files(mm_test.PAIR_DIRECTORY)
    assert len(jsons) == 13
    assert basename(jsons[0]) == "a.large.json"
    assert abspath(join(jsons[0], os.pardir)) == mm_test.PAIR_GIF_DIRECTORY
    assert basename(jsons[1]) == "small.gif.json"
    assert abspath(join(jsons[1], os.pardir)) == mm_test.PAIR_GIF_DIRECTORY
    assert basename(jsons[2]) == "static.json"
    assert abspath(join(jsons[2], os.pardir)) == mm_test.PAIR_GIF_DIRECTORY
    assert basename(jsons[3]) == "aaa.json"
    assert abspath(join(jsons[3], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert basename(jsons[4]) == "bare.PNG.json"
    assert abspath(join(jsons[4], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert basename(jsons[5]) == "long.JSON"
    assert abspath(join(jsons[5], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert basename(jsons[6]) == "missing-media.json"
    assert abspath(join(jsons[6], os.pardir)) == mm_test.PAIR_MISSING_DIRECTORY
    assert basename(jsons[7]) == "no-media.json"
    assert abspath(join(jsons[7], os.pardir)) == mm_test.PAIR_DIRECTORY
    assert basename(jsons[8]) == "pair-2.json"
    assert abspath(join(jsons[8], os.pardir)) == mm_test.PAIR_DIRECTORY
    assert basename(jsons[9]) == "pair.json"
    assert abspath(join(jsons[9], os.pardir)) == mm_test.PAIR_DIRECTORY
    assert basename(jsons[10]) == "text 1.json"
    assert abspath(join(jsons[10], os.pardir)) == mm_test.PAIR_TEXT_DIRECTORY
    assert basename(jsons[11]) == "text 02.txt.JSON"
    assert abspath(join(jsons[11], os.pardir)) == mm_test.PAIR_TEXT_DIRECTORY
    assert basename(jsons[12]) == "A.A.json"
    assert abspath(join(jsons[12], os.pardir)) == mm_test.PAIR_VIDEO_DIRECTORY
    # Check that all non-JSON files were found
    assert len(media) == 14
    assert basename(media[0]) == "a.large.gif"
    assert abspath(join(media[0], os.pardir)) == mm_test.PAIR_GIF_DIRECTORY
    assert basename(media[1]) == "small.GIF"
    assert abspath(join(media[1], os.pardir)) == mm_test.PAIR_GIF_DIRECTORY
    assert basename(media[2]) == "static.gif"
    assert abspath(join(media[2], os.pardir)) == mm_test.PAIR_GIF_DIRECTORY
    assert basename(media[3]) == ".empty"
    assert abspath(join(media[3], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert basename(media[4]) == "aaa.webp"
    assert abspath(join(media[4], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert basename(media[5]) == "bare.png"
    assert abspath(join(media[5], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert basename(media[6]) == "long.JPG"
    assert abspath(join(media[6], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert basename(media[7]) == "missing-metadata.txt"
    assert abspath(join(media[7], os.pardir)) == mm_test.PAIR_DIRECTORY
    assert basename(media[8]) == "no-metadata.txt"
    assert abspath(join(media[8], os.pardir)) == mm_test.PAIR_MISSING_DIRECTORY
    assert basename(media[9]) == "pair-2.jpg"
    assert abspath(join(media[9], os.pardir)) == mm_test.PAIR_DIRECTORY
    assert basename(media[10]) == "pair.txt"
    assert abspath(join(media[10], os.pardir)) == mm_test.PAIR_DIRECTORY
    assert basename(media[11]) == "text 1.htm"
    assert abspath(join(media[11], os.pardir)) == mm_test.PAIR_TEXT_DIRECTORY
    assert basename(media[12]) == "text 02.TXT"
    assert abspath(join(media[12], os.pardir)) == mm_test.PAIR_TEXT_DIRECTORY
    assert basename(media[13]) == "A.A.mkv"
    assert abspath(join(media[13], os.pardir)) == mm_test.PAIR_VIDEO_DIRECTORY
    # Check that archive files are included
    jsons, media = mm_meta_finder.separate_files(mm_test.ARCHIVE_DIRECTORY)
    assert len(media) == 13
    assert jsons == []

def test_get_pairs_from_list():
    """
    Tests the get_pairs_from_list function.
    """
    # Test getting pairs
    jsons, media = mm_meta_finder.separate_files(mm_test.PAIR_IMAGE_DIRECTORY)
    pairs = mm_meta_finder.get_pairs_from_lists(jsons, media, False)
    assert len(pairs) == 3
    assert basename(pairs[0]["json"]) == "aaa.json"
    assert basename(pairs[0]["media"]) == "aaa.webp"
    assert abspath(join(pairs[0]["json"], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert abspath(join(pairs[0]["media"], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert basename(pairs[1]["json"]) == "bare.PNG.json"
    assert basename(pairs[1]["media"]) == "bare.png"
    assert abspath(join(pairs[1]["json"], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert abspath(join(pairs[1]["media"], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert basename(pairs[2]["json"]) == "long.JSON"
    assert basename(pairs[2]["media"]) == "long.JPG"
    assert abspath(join(pairs[2]["json"], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert abspath(join(pairs[2]["media"], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY

def test_get_pairs():
    """
    Tests the get_pairs function.
    """
    pairs = mm_meta_finder.get_pairs(mm_test.PAIR_DIRECTORY)
    assert len(pairs) == 11
    assert basename(pairs[0]["json"]) == "a.large.json"
    assert basename(pairs[0]["media"]) == "a.large.gif"
    assert abspath(join(pairs[0]["json"], os.pardir)) == mm_test.PAIR_GIF_DIRECTORY
    assert abspath(join(pairs[0]["media"], os.pardir)) == mm_test.PAIR_GIF_DIRECTORY
    assert basename(pairs[1]["json"]) == "small.gif.json"
    assert basename(pairs[1]["media"]) == "small.GIF"
    assert abspath(join(pairs[1]["json"], os.pardir)) == mm_test.PAIR_GIF_DIRECTORY
    assert abspath(join(pairs[1]["media"], os.pardir)) == mm_test.PAIR_GIF_DIRECTORY
    assert basename(pairs[2]["json"]) == "static.json"
    assert basename(pairs[2]["media"]) == "static.gif"
    assert abspath(join(pairs[2]["json"], os.pardir)) == mm_test.PAIR_GIF_DIRECTORY
    assert abspath(join(pairs[2]["media"], os.pardir)) == mm_test.PAIR_GIF_DIRECTORY
    assert basename(pairs[3]["json"]) == "aaa.json"
    assert basename(pairs[3]["media"]) == "aaa.webp"
    assert abspath(join(pairs[3]["json"], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert abspath(join(pairs[3]["media"], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert basename(pairs[4]["json"]) == "bare.PNG.json"
    assert basename(pairs[4]["media"]) == "bare.png"
    assert abspath(join(pairs[4]["json"], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert abspath(join(pairs[4]["media"], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert basename(pairs[5]["json"]) == "long.JSON"
    assert basename(pairs[5]["media"]) == "long.JPG"
    assert abspath(join(pairs[5]["json"], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert abspath(join(pairs[5]["media"], os.pardir)) == mm_test.PAIR_IMAGE_DIRECTORY
    assert basename(pairs[6]["json"]) == "pair-2.json"
    assert basename(pairs[6]["media"]) == "pair-2.jpg"
    assert abspath(join(pairs[6]["json"], os.pardir)) == mm_test.PAIR_DIRECTORY
    assert abspath(join(pairs[6]["media"], os.pardir)) == mm_test.PAIR_DIRECTORY
    assert basename(pairs[7]["json"]) == "pair.json"
    assert basename(pairs[7]["media"]) == "pair.txt"
    assert abspath(join(pairs[7]["json"], os.pardir)) == mm_test.PAIR_DIRECTORY
    assert abspath(join(pairs[7]["media"], os.pardir)) == mm_test.PAIR_DIRECTORY
    assert basename(pairs[8]["json"]) == "text 1.json"
    assert basename(pairs[8]["media"]) == "text 1.htm"
    assert abspath(join(pairs[8]["json"], os.pardir)) == mm_test.PAIR_TEXT_DIRECTORY
    assert abspath(join(pairs[8]["media"], os.pardir)) == mm_test.PAIR_TEXT_DIRECTORY
    assert basename(pairs[9]["json"]) == "text 02.txt.JSON"
    assert basename(pairs[9]["media"]) == "text 02.TXT"
    assert abspath(join(pairs[9]["json"], os.pardir)) == mm_test.PAIR_TEXT_DIRECTORY
    assert abspath(join(pairs[9]["media"], os.pardir)) == mm_test.PAIR_TEXT_DIRECTORY
    assert basename(pairs[10]["json"]) == "A.A.json"
    assert basename(pairs[10]["media"]) == "A.A.mkv"
    assert abspath(join(pairs[10]["json"], os.pardir)) == mm_test.PAIR_VIDEO_DIRECTORY
    assert abspath(join(pairs[10]["media"], os.pardir)) == mm_test.PAIR_VIDEO_DIRECTORY
