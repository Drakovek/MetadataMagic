#!/usr/bin/env python3

import os
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.rename.rename_tools as mm_rename_tools
from os.path import abspath, basename, exists, join

def test_get_section():
    """
    Tests the get_section_function.
    """
    # Test getting number sections
    assert mm_rename_tools.get_section("12") == "12"
    assert mm_rename_tools.get_section("123 Thing!") == "123"
    assert mm_rename_tools.get_section("1.25Words") == "1.25"
    assert mm_rename_tools.get_section("1,000 Next") == "1,000"
    assert mm_rename_tools.get_section("1,523.26!Numbers") == "1,523.26"
    # Test getting non-number sections
    assert mm_rename_tools.get_section("Just text.") == "Just text."
    assert mm_rename_tools.get_section("Text, then Numbers.137") == "Text, then Numbers."
    # Test getting section from string that has none
    assert mm_rename_tools.get_section("") == ""

def test_compare_sections():
    """
    Tests the compare_sections function.
    """
    # Test comparing just numbers
    assert mm_rename_tools.compare_sections("25", "0025") == 0
    assert mm_rename_tools.compare_sections("1,000", "1000") == 0
    assert mm_rename_tools.compare_sections("2", "2.000") == 0
    assert mm_rename_tools.compare_sections("2", "3") == -1
    assert mm_rename_tools.compare_sections("54", "023") == 1
    assert mm_rename_tools.compare_sections("1,200", "1250") == -1
    assert mm_rename_tools.compare_sections("3,500", "3,000") == 1
    assert mm_rename_tools.compare_sections("0105.3", "105.38") == -1
    assert mm_rename_tools.compare_sections("1.5", "1.25") == 1
    # Test comparing just text
    assert mm_rename_tools.compare_sections("text", "text") == 0
    assert mm_rename_tools.compare_sections("abc", "def") == -1
    assert mm_rename_tools.compare_sections("test", "blah") == 1
    assert mm_rename_tools.compare_sections("un", "unfinished") == -1
    assert mm_rename_tools.compare_sections("ending", "end") == 1
    # Test comparing text and numbers
    assert mm_rename_tools.compare_sections("43", "text") == -1
    assert mm_rename_tools.compare_sections("other", "5.8") == 1
    # Test with missing sections
    assert mm_rename_tools.compare_sections("", "540") == -1
    assert mm_rename_tools.compare_sections("0", "") == 1
    assert mm_rename_tools.compare_sections("", "word") == -1
    assert mm_rename_tools.compare_sections("other", "")

def test_compare_alphanum():
    """
    Tests the compare_alphanum function.
    """
    # Test identical strings
    assert mm_rename_tools.compare_alphanum("", "") == 0
    assert mm_rename_tools.compare_alphanum("23 test", "23 test") == 0
    # Test comparing by number
    assert mm_rename_tools.compare_alphanum("Test 4", "  test 10") == -1
    assert mm_rename_tools.compare_alphanum("  Thing 34.5 more",  "Thing 5") == 1
    assert mm_rename_tools.compare_alphanum("14 Name 1", "14   name 3") == -1
    assert mm_rename_tools.compare_alphanum("024 thing next 5", "24 thing next 2") == 1
    # Test comparing by text
    assert mm_rename_tools.compare_alphanum("45 abc", "45 Test") == -1
    assert mm_rename_tools.compare_alphanum("987 banana", "0987   AAA") == 1
    assert mm_rename_tools.compare_alphanum("5 Thing 65 next", "5 thing 65.0 other") == -1
    assert mm_rename_tools.compare_alphanum("5.8 next 4 zzz", " 5.80 next 4 aaa") == 1
    assert mm_rename_tools.compare_alphanum("12 thing", "12 thing next") == -1
    assert mm_rename_tools.compare_alphanum("50 other next", "050 Other") == 1
    # Test comparing that with identical sections
    assert mm_rename_tools.compare_alphanum("AAA", "aaa") == -1
    assert mm_rename_tools.compare_alphanum("1.0", "1") == 1

def test_sort_alphanum():
    """
    Tests the sort_alphanum function.
    """
    lst = ["test 10", "test 1", "test 003", "3.5", "06 Next", "middle"]
    sort = mm_rename_tools.sort_alphanum(lst)
    assert sort == ["3.5", "06 Next", "middle", "test 1", "test 003", "test 10"]

def test_create_filename():
    """
    Tests the create_filename function.
    """
    # Test replacing invalid characters
    assert mm_rename_tools.create_filename("**What?!?!") == "What-!-!"
    assert mm_rename_tools.create_filename(".This:That") == "This - That"
    assert mm_rename_tools.create_filename("Blah...") == "Blah…"
    assert mm_rename_tools.create_filename("<\"This/That\\Other\">") == "This-That-Other"
    assert mm_rename_tools.create_filename("(A|||B)") == "(A-B)"
    assert mm_rename_tools.create_filename("...Mr. Roboto.") == "…Mr. Roboto"
    assert mm_rename_tools.create_filename(" This    &    That ") == "This & That"
    assert mm_rename_tools.create_filename("thing--stuff  @*-   blah") == "thing-stuff @ blah"
    assert mm_rename_tools.create_filename("This..") == "This"
    assert mm_rename_tools.create_filename("..Dots.....") == "Dots…"
    assert mm_rename_tools.create_filename("Spaced .  .   .") == "Spaced …"
    assert mm_rename_tools.create_filename("  This is the end >.<  ") == "This is the end"
    assert mm_rename_tools.create_filename(" No, THIS is the end. -.-.. ") == "No, THIS is the end"
    assert mm_rename_tools.create_filename("A -> B") == "A to B"
    assert mm_rename_tools.create_filename("Thing ----> Other") == "Thing to Other"
    # Test removing hanging hyphens.
    assert mm_rename_tools.create_filename("Blah!- Thing") == "Blah! Thing"
    assert mm_rename_tools.create_filename("Other23- Item") == "Other23 Item"
    assert mm_rename_tools.create_filename("First -!Next") == "First !Next"
    assert mm_rename_tools.create_filename("None -Next") == "None Next"
    # Test converting from non-standard latin characters
    assert mm_rename_tools.create_filename("ÀÁÂÃÄÅ") == "AAAAAA"
    assert mm_rename_tools.create_filename("ÈÉÊË") == "EEEE"
    assert mm_rename_tools.create_filename("ÌÍÎÏ") == "IIII"
    assert mm_rename_tools.create_filename("ÑÒÓÔÕÖ") == "NOOOOO"
    assert mm_rename_tools.create_filename("ÙÚÛÜÝ") == "UUUUY"
    assert mm_rename_tools.create_filename("àáâãäå") == "aaaaaa"
    assert mm_rename_tools.create_filename("èéêë") == "eeee"
    assert mm_rename_tools.create_filename("ìíîï") == "iiii"
    assert mm_rename_tools.create_filename("ñòóôõö") == "nooooo"
    assert mm_rename_tools.create_filename("ùúûüýÿ") == "uuuuyy"
    # Test getting filename with no length
    assert mm_rename_tools.create_filename("") == "0"
    assert mm_rename_tools.create_filename("---") == "0"

def test_get_available_filename():
    """
    Tests the get_available_filename function.
    """
    # Test getting filename with unacceptable characters.
    temp_dir = mm_file_tools.get_temp_dir()
    assert mm_rename_tools.get_available_filename("a.txt", "Name?", temp_dir) == "Name.txt"
    assert mm_rename_tools.get_available_filename("b.png", ".dat", temp_dir) == "dat.png"
    # Test getting filename if desired filename already exists
    text_file = abspath(join(temp_dir, "name.txt"))
    mm_file_tools.write_text_file(text_file, "some text")
    assert exists(text_file)
    assert mm_rename_tools.get_available_filename("a.txt", "name", temp_dir) == "name-2.txt"
    # Test if filename exists with a different extension
    assert mm_rename_tools.get_available_filename("b.png", "name", temp_dir) == "name.png"
    # Test if filename alternate filename is also taken
    text_file_2 = abspath(join(temp_dir, "name-2.txt"))
    text_file_3 = abspath(join(temp_dir, "name-3.txt"))
    mm_file_tools.write_text_file(text_file_2, "more")
    mm_file_tools.write_text_file(text_file_3, "text")
    assert exists(text_file_2)
    assert exists(text_file_3)
    assert mm_rename_tools.get_available_filename("a.txt", "name", temp_dir) == "name-4.txt"

def test_rename_file():
    """
    Tests the rename_file function.
    """
    # Create test file
    temp_dir = mm_file_tools.get_temp_dir()
    file = abspath(join(temp_dir, "file.txt"))
    mm_file_tools.write_text_file(file, "TEST")
    assert exists(file)
    # Test renaming file
    new_file = mm_rename_tools.rename_file(file, "Name?")
    assert exists(new_file)
    assert abspath(join(new_file, os.pardir)) == temp_dir
    assert basename(new_file) == "Name.txt"
    # Test renaming file to its current name
    file = new_file
    new_file = None
    assert exists(file)
    new_file = mm_rename_tools.rename_file(file, "Name??????????????")
    assert exists(new_file)
    assert file == new_file
    # Test renaming file to name of existing file
    file = abspath(join(temp_dir, "totally_new.txt"))
    mm_file_tools.write_text_file(file, "NEW!")
    assert exists(file)
    new_file = mm_rename_tools.rename_file(file, "Name")
    assert exists(new_file)
    assert abspath(join(new_file, os.pardir)) == temp_dir
    assert basename(new_file) == "Name-2.txt"
    # Test renaming same filename but different extension
    file = abspath(join(temp_dir, "Weeee!.png"))
    mm_file_tools.write_text_file(file, "Not Actually PNG.")
    assert exists(file)
    new_file = mm_rename_tools.rename_file(file, ":Name:")
    assert exists(new_file)
    assert abspath(join(new_file, os.pardir)) == temp_dir
    assert basename(new_file) == "Name.png"
    # Test renaming a third time
    file = abspath(join(temp_dir, "next.txt"))
    mm_file_tools.write_text_file(file, "Next")
    assert exists(file)
    new_file = mm_rename_tools.rename_file(file, ":Name:")
    assert exists(new_file)
    assert abspath(join(new_file, os.pardir)) == temp_dir
    assert basename(new_file) == "Name-3.txt"
    # Test that renamed files still contain the correct data
    file = abspath(join(temp_dir, "Name.txt"))
    assert mm_file_tools.read_text_file(file) == "TEST"
    file = abspath(join(temp_dir, "Name-2.txt"))
    assert mm_file_tools.read_text_file(file) == "NEW!"
    file = abspath(join(temp_dir, "Name.png"))
    assert mm_file_tools.read_text_file(file) == "Not Actually PNG."
    file = abspath(join(temp_dir, "Name-3.txt"))
    assert mm_file_tools.read_text_file(file) == "Next"
    # Test renaming invalid file
    file = abspath(join(temp_dir, "non-existant.txt"))
    new_file = mm_rename_tools.rename_file(file, "new")
    assert new_file is None
