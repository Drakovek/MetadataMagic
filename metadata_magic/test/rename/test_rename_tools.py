#!/usr/bin/env python3

from os import pardir
from os.path import abspath, basename, exists, join
from metadata_magic.main.file_tools.file_tools import get_temp_dir
from metadata_magic.main.rename.rename_tools import get_section
from metadata_magic.main.rename.rename_tools import compare_sections
from metadata_magic.main.rename.rename_tools import compare_alphanum
from metadata_magic.main.rename.rename_tools import sort_alphanum
from metadata_magic.main.rename.rename_tools import create_filename
from metadata_magic.main.rename.rename_tools import rename_file
from metadata_magic.test.temp_file_tools import create_json_file
from metadata_magic.test.temp_file_tools import create_text_file
from metadata_magic.test.temp_file_tools import read_text_file

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

def test_create_filename():
    """
    Tests the create_filename function.
    """
    # Test replacing invalid characters
    assert create_filename("**What?!?!") == "What-!-!"
    assert create_filename("This:That") == "This - That"
    assert create_filename("Blah...") == "Blah…"
    assert create_filename("<\"This/That\\Other\">") == "This-That-Other"
    assert create_filename("(A|||B)") == "(A-B)"
    assert create_filename("...Mr. Roboto.") == "…Mr. Roboto"
    assert create_filename(" This    &    That ") == "This & That"
    assert create_filename("thing--stuff  @*-   blah") == "thing-stuff @ blah"
    assert create_filename("This..") == "This"
    assert create_filename("Dots.....") == "Dots…"
    assert create_filename("Spaced .  .   .") == "Spaced …"
    assert create_filename("  This is the end >.<  ") == "This is the end"
    assert create_filename(" No, THIS is the end. -.-.. ") == "No, THIS is the end"
    # Test removing hanging hyphens.
    assert create_filename("Blah!- Thing") == "Blah! Thing"
    assert create_filename("Other23- Item") == "Other23 Item"
    assert create_filename("First -!Next") == "First !Next"
    assert create_filename("None -Next") == "None Next"
    # Test converting from non-standard latin characters
    assert create_filename("ÀÁÂÃÄÅ") == "AAAAAA"
    assert create_filename("ÈÉÊË") == "EEEE"
    assert create_filename("ÌÍÎÏ") == "IIII"
    assert create_filename("ÑÒÓÔÕÖ") == "NOOOOO"
    assert create_filename("ÙÚÛÜÝ") == "UUUUY"
    assert create_filename("àáâãäå") == "aaaaaa"
    assert create_filename("èéêë") == "eeee"
    assert create_filename("ìíîï") == "iiii"
    assert create_filename("ñòóôõö") == "nooooo"
    assert create_filename("ùúûüýÿ") == "uuuuyy"
    # Test getting filename with no length
    assert create_filename("") == "0"
    assert create_filename("---") == "0"

def test_rename_file():
    """
    Tests the rename_file function.
    """
    # Create test file
    temp_dir = get_temp_dir()
    file = abspath(join(temp_dir, "file.txt"))
    create_text_file(file, "TEST")
    assert exists(file)
    # Test renaming file
    new_file = rename_file(file, "Name?")
    assert exists(new_file)
    assert abspath(join(new_file, pardir)) == temp_dir
    assert basename(new_file) == "Name.txt"
    # Test renaming file to its current name
    file = new_file
    new_file = None
    assert exists(file)
    new_file = rename_file(file, "Name??????????????")
    assert exists(new_file)
    assert file == new_file
    # Test renaming file to name of existing file
    file = abspath(join(temp_dir, "totally_new.txt"))
    create_text_file(file, "NEW!")
    assert exists(file)
    new_file = rename_file(file, "Name")
    assert exists(new_file)
    assert abspath(join(new_file, pardir)) == temp_dir
    assert basename(new_file) == "Name-2.txt"
    # Test renaming same filename but different extension
    file = abspath(join(temp_dir, "Weeee!.png"))
    create_text_file(file, "Not Actually PNG.")
    assert exists(file)
    new_file = rename_file(file, ":Name:")
    assert exists(new_file)
    assert abspath(join(new_file, pardir)) == temp_dir
    assert basename(new_file) == "Name.png"
    # Test renaming a third time
    file = abspath(join(temp_dir, "next.txt"))
    create_text_file(file, "Next")
    assert exists(file)
    new_file = rename_file(file, ":Name:")
    assert exists(new_file)
    assert abspath(join(new_file, pardir)) == temp_dir
    assert basename(new_file) == "Name-3.txt"
    # Test that renamed files still contain the correct data
    file = abspath(join(temp_dir, "Name.txt"))
    assert read_text_file(file) == "TEST"
    file = abspath(join(temp_dir, "Name-2.txt"))
    assert read_text_file(file) == "NEW!"
    file = abspath(join(temp_dir, "Name.png"))
    assert read_text_file(file) == "Not Actually PNG."
    file = abspath(join(temp_dir, "Name-3.txt"))
    assert read_text_file(file) == "Next"
    # Test renaming invalid file
    file = abspath(join(temp_dir, "non-existant.txt"))
    new_file = rename_file(file, "new")
    assert new_file is None
