#!/usr/bin/env python3

from os import pardir
from os.path import abspath, basename, exists, join
from metadata_magic.main.rename.rename_tools import create_filename
from metadata_magic.main.rename.rename_tools import rename_file
from metadata_magic.test.temp_dir import get_temp_dir

def test_create_filename():
    """
    Tests the create_filename function.
    """
    # Test replacing invalid characters
    assert create_filename("**What?!?!") == "What-!-!"
    assert create_filename("This:That") == "This-That"
    assert create_filename("Blah...") == "Blah…"
    assert create_filename("<\"This/That\\Other\">") == "This-That-Other"
    assert create_filename("(A|||B)") == "(A-B)"
    assert create_filename("...Mr. Roboto.") == "…Mr. Roboto"
    assert create_filename(" This    &    That ") == "This & That"
    assert create_filename("thing--stuff  @*-   blah") == "thing-stuff @ blah"
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
    with open(file, "w") as out_file:
        out_file.write("TEST")
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
    with open(file, "w") as out_file:
        out_file.write("NEW!")
    assert exists(file)
    new_file = rename_file(file, "Name")
    assert exists(new_file)
    assert abspath(join(new_file, pardir)) == temp_dir
    assert basename(new_file) == "Name2.txt"
    # Test renaming same filename but different extension
    file = abspath(join(temp_dir, "Weeee!.png"))
    with open(file, "w") as out_file:
        out_file.write("Not Actually PNG.")
    assert exists(file)
    new_file = rename_file(file, ":Name:")
    assert exists(new_file)
    assert abspath(join(new_file, pardir)) == temp_dir
    assert basename(new_file) == "Name.png"
    # Test renaming a third time
    file = abspath(join(temp_dir, "next.txt"))
    with open(file, "w") as out_file:
        out_file.write("Next")
    assert exists(file)
    new_file = rename_file(file, ":Name:")
    assert exists(new_file)
    assert abspath(join(new_file, pardir)) == temp_dir
    assert basename(new_file) == "Name3.txt"
    # Test that renamed files still contain the correct data
    file = abspath(join(temp_dir, "Name.txt"))
    with open (file) as in_file:
        content = in_file.read()
    assert content == "TEST"
    file = abspath(join(temp_dir, "Name2.txt"))
    with open (file) as in_file:
        content = in_file.read()
    assert content == "NEW!"
    file = abspath(join(temp_dir, "Name.png"))
    with open (file) as in_file:
        content = in_file.read()
    assert content == "Not Actually PNG."
    file = abspath(join(temp_dir, "Name3.txt"))
    with open (file) as in_file:
        content = in_file.read()
    assert content == "Next"
    # Test renaming invalid file
    file = abspath(join(temp_dir, "non-existant.txt"))
    new_file = rename_file(file, "new")
    assert new_file is None
    