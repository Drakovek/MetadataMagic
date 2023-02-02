#!/usr/bin/env python3

from metadata_magic.main.comic_archive.comic_archive import get_temp_dir
from metadata_magic.main.rename.sort_rename import compare_alphanum
from metadata_magic.main.rename.sort_rename import compare_sections
from metadata_magic.main.rename.sort_rename import get_section
from metadata_magic.main.rename.sort_rename import sort_alphanum
from metadata_magic.main.rename.sort_rename import sort_rename
from metadata_magic.test.temp_file_tools import create_text_file
from os import listdir, mkdir
from os.path import abspath, exists, isdir, join

def test_get_section():
    """
    Tests the get_section_function.
    """
    # Test getting number sections
    assert get_section("12") == "12"
    assert get_section("123 Thing!") == "123"
    assert get_section("1.25Words") == "1.25"
    assert get_section("1,000 Next") == "1,000"
    assert get_section("1,523.26!Numbers") == "1,523.26"
    # Test getting non-number sections
    assert get_section("Just text.") == "Just text."
    assert get_section("Text, then Numbers.137") == "Text, then Numbers."
    # Test getting section from string that has none
    assert get_section("") == ""

def test_compare_sections():
    """
    Tests the compare_sections function.
    """
    # Test comparing just numbers
    assert compare_sections("25", "0025") == 0
    assert compare_sections("1,000", "1000") == 0
    assert compare_sections("2", "2.000") == 0
    assert compare_sections("2", "3") == -1
    assert compare_sections("54", "023") == 1
    assert compare_sections("1,200", "1250") == -1
    assert compare_sections("3,500", "3,000") == 1
    assert compare_sections("0105.3", "105.38") == -1
    assert compare_sections("1.5", "1.25") == 1
    # Test comparing just text
    assert compare_sections("text", "text") == 0
    assert compare_sections("abc", "def") == -1
    assert compare_sections("test", "blah") == 1
    assert compare_sections("un", "unfinished") == -1
    assert compare_sections("ending", "end") == 1
    # Test comparing text and numbers
    assert compare_sections("43", "text") == -1
    assert compare_sections("other", "5.8") == 1
    # Test with missing sections
    assert compare_sections("", "540") == -1
    assert compare_sections("0", "") == 1
    assert compare_sections("", "word") == -1
    assert compare_sections("other", "")

def test_compare_alphanum():
    """
    Tests the compare_alphanum function.
    """
    # Test identical strings
    assert compare_alphanum("", "") == 0
    assert compare_alphanum("23 test", "23 test") == 0
    # Test comparing by number
    assert compare_alphanum("Test 4", "  test 10") == -1
    assert compare_alphanum("  Thing 34.5 more",  "Thing 5") == 1
    assert compare_alphanum("14 Name 1", "14   name 3") == -1
    assert compare_alphanum("024 thing next 5", "24 thing next 2") == 1
    # Test comparing by text
    assert compare_alphanum("45 abc", "45 Test") == -1
    assert compare_alphanum("987 banana", "0987   AAA") == 1
    assert compare_alphanum("5 Thing 65 next", "5 thing 65.0 other") == -1
    assert compare_alphanum("5.8 next 4 zzz", " 5.80 next 4 aaa") == 1
    assert compare_alphanum("12 thing", "12 thing next") == -1
    assert compare_alphanum("50 other next", "050 Other") == 1
    # Test comparing that with identical sections
    assert compare_alphanum("AAA", "aaa") == -1
    assert compare_alphanum("1.0", "1") == 1

def test_sort_alphanum():
    """
    Tests the sort_alphanum function.
    """
    lst = ["test 10", "test 1", "test 003", "3.5", "06 Next", "middle"]
    sort = sort_alphanum(lst)
    assert sort == ["3.5", "06 Next", "middle", "test 1", "test 003", "test 10"]

def test_sort_rename():
    """
    Tests the sort_rename function.
    """
    # Create test files
    temp_dir = get_temp_dir()
    unlinked1 = abspath(join(temp_dir, "Unlinked 01.txt"))
    unlinked2 = abspath(join(temp_dir, "Unlinked 10.png"))
    unlinked3 = abspath(join(temp_dir, "Unlinked 120.jpg"))
    create_text_file(unlinked1, "TEXT")
    create_text_file(unlinked2, "TEXT")
    create_text_file(unlinked3, "TEXT")
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
    create_text_file(json1, "JSON")
    create_text_file(json2, "JSON")
    create_text_file(json3, "JSON")
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
    create_text_file(unlinked1, "TEST")
    create_text_file(unlinked2, "TEST")
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
    create_text_file(part1, "Name")
    create_text_file(part2, "Name")
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
