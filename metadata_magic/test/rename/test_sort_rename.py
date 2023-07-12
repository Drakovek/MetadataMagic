#!/usr/bin/env python3

from metadata_magic.main.file_tools.file_tools import get_temp_dir
from metadata_magic.main.rename.sort_rename import sort_rename
from metadata_magic.main.file_tools.file_tools import write_text_file
from os import listdir, mkdir
from os.path import abspath, exists, isdir, join

def test_sort_rename():
    """
    Tests the sort_rename function.
    """
    # Create test files
    temp_dir = get_temp_dir()
    unlinked1 = abspath(join(temp_dir, "Unlinked 01.txt"))
    unlinked2 = abspath(join(temp_dir, "Unlinked 10.png"))
    unlinked3 = abspath(join(temp_dir, "Unlinked 120.jpg"))
    write_text_file(unlinked1, "TEXT")
    write_text_file(unlinked2, "TEXT")
    write_text_file(unlinked3, "TEXT")
    assert exists(unlinked1)
    assert exists(unlinked2)
    assert exists(unlinked3)
    # Test sorting unlinked files
    sort_rename(temp_dir, "Renamed")
    filenames = sorted(listdir(temp_dir))
    assert len(filenames) == 3
    assert filenames[0] == "Renamed 1.txt"
    assert filenames[1] == "Renamed 2.png"
    assert filenames[2] == "Renamed 3.jpg"
    # Create test JSON files
    json1 = abspath(join(temp_dir, "Renamed 1.json"))
    json2 = abspath(join(temp_dir, "Renamed 2.png.json"))
    json3 = abspath(join(temp_dir, "Renamed 3.json"))
    write_text_file(json1, "JSON")
    write_text_file(json2, "JSON")
    write_text_file(json3, "JSON")
    assert exists(json1)
    assert exists(json2)
    assert exists(json3)
    # Test sorting json-media pairs
    sort_rename(temp_dir, "Paired!")
    filenames = sorted(listdir(temp_dir))
    assert len(filenames) == 6
    assert filenames[0] == "Paired! 1.json"
    assert filenames[1] == "Paired! 1.txt"
    assert filenames[2] == "Paired! 2.json"
    assert filenames[3] == "Paired! 2.png"
    assert filenames[4] == "Paired! 3.jpg"
    assert filenames[5] == "Paired! 3.json"
    # Create more unlinked media
    unlinked1 = abspath(join(temp_dir, "Paired! 2.5.json"))
    unlinked2 = abspath(join(temp_dir, "Unlinked.zip"))
    write_text_file(unlinked1, "TEST")
    write_text_file(unlinked2, "TEST")
    assert exists(unlinked1)
    assert exists(unlinked2)
    # Test sorting combination of json pairs and standalone media
    sort_rename(temp_dir, "combined")
    filenames = sorted(listdir(temp_dir))
    assert len(filenames) == 8
    assert filenames[0] == "combined 1.json"
    assert filenames[1] == "combined 1.txt"
    assert filenames[2] == "combined 2.json"
    assert filenames[3] == "combined 2.png"
    assert filenames[4] == "combined 3.json"
    assert filenames[5] == "combined 4.jpg"
    assert filenames[6] == "combined 4.json"
    assert filenames[7] == "combined 5.zip"
    # Test number replacement
    sort_rename(temp_dir, "[##] Thing")
    filenames = sorted(listdir(temp_dir))
    assert len(filenames) == 8
    assert filenames[0] == "[01] Thing.json"
    assert filenames[1] == "[01] Thing.txt"
    assert filenames[2] == "[02] Thing.json"
    assert filenames[3] == "[02] Thing.png"
    assert filenames[4] == "[03] Thing.json"
    assert filenames[5] == "[04] Thing.jpg"
    assert filenames[6] == "[04] Thing.json"
    assert filenames[7] == "[05] Thing.zip"
    # Test number replacement when starting past 1
    sort_rename(temp_dir, "New - P### - #2", 12)
    filenames = sorted(listdir(temp_dir))
    assert len(filenames) == 8
    assert filenames[0] == "New - P012 - #2.json"
    assert filenames[1] == "New - P012 - #2.txt"
    assert filenames[2] == "New - P013 - #2.json"
    assert filenames[3] == "New - P013 - #2.png"
    assert filenames[4] == "New - P014 - #2.json"
    assert filenames[5] == "New - P015 - #2.jpg"
    assert filenames[6] == "New - P015 - #2.json"
    assert filenames[7] == "New - P016 - #2.zip"
    sort_rename(temp_dir, "Different", 3)
    filenames = sorted(listdir(temp_dir))
    assert len(filenames) == 8
    assert filenames[0] == "Different 3.json"
    assert filenames[1] == "Different 3.txt"
    assert filenames[2] == "Different 4.json"
    assert filenames[3] == "Different 4.png"
    assert filenames[4] == "Different 5.json"
    assert filenames[5] == "Different 6.jpg"
    assert filenames[6] == "Different 6.json"
    assert filenames[7] == "Different 7.zip"
    # Test when directories are included
    directory1 = abspath(join(temp_dir, "AAA"))
    directory2 = abspath(join(temp_dir, "Sub"))
    directory3 = abspath(join(temp_dir, "different 5"))
    mkdir(directory1)
    mkdir(directory2)
    mkdir(directory3)
    assert exists(directory1)
    assert exists(directory2)
    assert exists(directory3)
    assert isdir(directory1)
    assert isdir(directory2)
    assert isdir(directory3)
    sort_rename(temp_dir, "Final")
    filenames = sorted(listdir(temp_dir))
    assert len(filenames) == 11
    assert filenames[0] == "AAA"
    assert filenames[1] == "Final 1.json"
    assert filenames[2] == "Final 1.txt"
    assert filenames[3] == "Final 2.json"
    assert filenames[4] == "Final 2.png"
    assert filenames[5] == "Final 3.json"
    assert filenames[6] == "Final 4.jpg"
    assert filenames[7] == "Final 4.json"
    assert filenames[8] == "Final 5.zip"
    assert filenames[9] == "Sub"
    assert filenames[10] == "different 5"
    # Test with pairs in subdirectories
    part1 = abspath(join(directory2, "pair.json"))
    part2 = abspath(join(directory2, "pair.jpg"))
    write_text_file(part1, "Name")
    write_text_file(part2, "Name")
    assert exists(part1)
    assert exists(part2)
    sort_rename(temp_dir, "Middle")
    filenames = sorted(listdir(temp_dir))
    assert len(filenames) == 11
    assert filenames[0] == "AAA"
    assert filenames[1] == "Middle 1.json"
    assert filenames[2] == "Middle 1.txt"
    assert filenames[3] == "Middle 2.json"
    assert filenames[4] == "Middle 2.png"
    assert filenames[5] == "Middle 3.json"
    assert filenames[6] == "Middle 4.jpg"
    assert filenames[7] == "Middle 4.json"
    assert filenames[8] == "Middle 5.zip"
    assert filenames[9] == "Sub"
    assert filenames[10] == "different 5"
    # Test that ComicInfo.xml is not renamed
    test_dir = get_temp_dir()
    xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
    other_file = abspath(join(temp_dir, "blah.txt"))
    last_file = abspath(join(temp_dir, "final.png"))
    write_text_file(xml_file, "Not")
    write_text_file(other_file, "Actually")
    write_text_file(last_file, "Important")
    assert exists(xml_file)
    assert exists(other_file)
    assert exists(last_file)
    sort_rename(temp_dir, "Not Comic [##]")
    filenames = sorted(listdir(temp_dir))
    assert len(filenames) == 3
    assert filenames[0] == "ComicInfo.xml"
    assert filenames[1] == "Not Comic [01].txt"
    assert filenames[2] == "Not Comic [02].png"
