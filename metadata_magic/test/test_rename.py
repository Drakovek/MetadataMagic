#!/usr/bin/env python3

import os
import shutil
import tempfile
import metadata_magic.test as mm_test
import metadata_magic.config as mm_config
import metadata_magic.rename as mm_rename
import metadata_magic.file_tools as mm_file_tools
from os.path import abspath, basename, join

def test_get_file_friendly_text():
    """
    Tests the get_file_friendly_text function.
    """
    # Test replacing invalid characters
    assert mm_rename.get_file_friendly_text(r"A < B > C") == "A - B - C"
    assert mm_rename.get_file_friendly_text(r'1 " 2 " 3') == "1 - 2 - 3"
    assert mm_rename.get_file_friendly_text(r"A\B/C | 123") == "A-B-C - 123"
    assert mm_rename.get_file_friendly_text(r"a*b?c") == "a-b-c"
    assert mm_rename.get_file_friendly_text(r"abcd..") == "abcd"
    assert mm_rename.get_file_friendly_text(r"abcd . .") == "abcd"
    assert mm_rename.get_file_friendly_text("ABCDE") == "ABCDE"
    # Test removing reserved file names
    assert mm_rename.get_file_friendly_text(r"CON") == "0"
    assert mm_rename.get_file_friendly_text(r"prn") == "0"
    assert mm_rename.get_file_friendly_text(r"AUX") == "0"
    assert mm_rename.get_file_friendly_text(r"nul") == "0"
    assert mm_rename.get_file_friendly_text(r"com1") == "0"
    assert mm_rename.get_file_friendly_text(r"COM2") == "0"
    assert mm_rename.get_file_friendly_text(r"com5") == "0"
    assert mm_rename.get_file_friendly_text(r"lpt1") == "0"
    assert mm_rename.get_file_friendly_text(r"LPT5") == "0"
    assert mm_rename.get_file_friendly_text(r"CONTENT") == "CONTENT"
    assert mm_rename.get_file_friendly_text(r"aprn") == "aprn"
    assert mm_rename.get_file_friendly_text(r"com6") == "com6"
    assert mm_rename.get_file_friendly_text(r"LPT6") == "LPT6"
    assert mm_rename.get_file_friendly_text(r"LPT0") == "LPT0"
    # Test replacing different types of whitespace and hyphens
    assert mm_rename.get_file_friendly_text(r"A－B⎼C") == "A-B-C"
    assert mm_rename.get_file_friendly_text("1\n2\t3") == "1 2 3"
    # Test replacing multiple hyphens or whitespace
    assert mm_rename.get_file_friendly_text(r"A-----B") == "A-B"
    assert mm_rename.get_file_friendly_text(r"1     2") == "1 2"
    assert mm_rename.get_file_friendly_text(r"a -  -?   -   b") == "a - b"
    assert mm_rename.get_file_friendly_text(r"A- -*-   -Z") == "A-Z"
    # Test replacing special structures
    assert mm_rename.get_file_friendly_text(r"A:B") == "A - B"
    assert mm_rename.get_file_friendly_text(r"abc...") == "abc…"
    assert mm_rename.get_file_friendly_text(r"123.  . .  . ") == "123…"
    assert mm_rename.get_file_friendly_text(r". . . A . . . . . .") == "… A … …"
    assert mm_rename.get_file_friendly_text(r"A -> B") == "A to B"
    assert mm_rename.get_file_friendly_text(r"B --－－-> C") == "B to C"
    assert mm_rename.get_file_friendly_text(r"1->3") == "1-3"
    # Test removing hanging hyphens
    assert mm_rename.get_file_friendly_text(r"A- B") == "A B"
    assert mm_rename.get_file_friendly_text(r"C -D") == "C D"
    assert mm_rename.get_file_friendly_text(r"a? z") == "a z"
    assert mm_rename.get_file_friendly_text(r"A *Z") == "A Z"
    # Test removing whitespace and hyphens from ends of string
    assert mm_rename.get_file_friendly_text(r"   ABC    ") == "ABC"
    assert mm_rename.get_file_friendly_text(r"- - 123 - -") == "123"
    assert mm_rename.get_file_friendly_text(r" ?? az * * ") == "az"
    # Test replacing diacritic characters in ASCII only mode
    assert mm_rename.get_file_friendly_text("Áéíóú") == "Áéíóú"
    assert mm_rename.get_file_friendly_text("ÀÁÂÃÄÅ", True) == "AAAAAA"
    assert mm_rename.get_file_friendly_text("ÈÉÊË", True) == "EEEE"
    assert mm_rename.get_file_friendly_text("ÌÍÎÏ", True) == "IIII"
    assert mm_rename.get_file_friendly_text("ÑŃÒÓÔÕÖ", True) == "NNOOOOO"
    assert mm_rename.get_file_friendly_text("ÙÚÛÜÝŸ", True) == "UUUUYY"
    assert mm_rename.get_file_friendly_text("àáâãäå", True) == "aaaaaa"
    assert mm_rename.get_file_friendly_text("èéêë", True) == "eeee"
    assert mm_rename.get_file_friendly_text("ìíîï", True) == "iiii"
    assert mm_rename.get_file_friendly_text("ńñòóôõö", True) == "nnooooo"
    assert mm_rename.get_file_friendly_text("ùúûüýÿ", True) == "uuuuyy"
    # Test non-ASCII characters are removed in ASCII only mode
    assert mm_rename.get_file_friendly_text("$.AAA☺") == "$.AAA☺"
    assert mm_rename.get_file_friendly_text("$.☺abz", True) == "abz"
    assert mm_rename.get_file_friendly_text("[A] @;`^{} (Z)", True) == "[A] - (Z)"
    assert mm_rename.get_file_friendly_text("0 % % % 9!", True) == "0 - 9!"
    # Test if the final filename has no length
    assert mm_rename.get_file_friendly_text("@#$%^&*-=", True) == "0"
    assert mm_rename.get_file_friendly_text("---") == "0"
    assert mm_rename.get_file_friendly_text("   ") == "0"
    assert mm_rename.get_file_friendly_text("") == "0"
    assert mm_rename.get_file_friendly_text(None) == "0"

def test_get_available_filename():
    """
    Tests the get_available_filename function.
    """
    # Test getting a filename with invalid characters
    pair_dir = mm_test.PAIR_DIRECTORY
    assert mm_rename.get_available_filename("a.txt", "Name?", pair_dir) == "Name"
    assert mm_rename.get_available_filename(["a.txt"], ".Náme.", pair_dir) == ".Náme"
    assert mm_rename.get_available_filename("a.txt", ".Náme.", pair_dir, True) == "Name"
    # Test getting the filename if the desired filename already exists
    assert mm_rename.get_available_filename("a.txt", "páir", pair_dir, True) == "pair-2"
    assert mm_rename.get_available_filename(["a.TXT", "a.jpg"], "pair", pair_dir) == "pair-3"
    # Test if filename exists with filename but different capitalization
    image_dir = mm_test.PAIR_IMAGE_DIRECTORY
    assert mm_rename.get_available_filename(".jpg", "Long", image_dir) == "Long-2"
    # Test if the filename exists, but with a different extension
    assert mm_rename.get_available_filename(".txt", "bare", image_dir) == "bare"
    assert mm_rename.get_available_filename([".txt", ".jpg"], "AAA", image_dir) == "AAA"
    # Test with invalid directory
    assert mm_rename.get_available_filename(".txt", "bare", "/non/existant/dir/") is None

def test_rename_file():
    """
    Tests the rename_file function.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test file
        file = abspath(join(temp_dir, "file.txt"))
        mm_file_tools.write_text_file(file, "test text")
        # Test renaming file
        file = mm_rename.rename_file(file, "Náme?")
        assert abspath(join(file, os.pardir)) == temp_dir
        assert basename(file) == "Náme.txt"
        # Test renaming file with only ASCII characters allowed
        file = mm_rename.rename_file(file, ".Náme", True)
        assert abspath(join(file, os.pardir)) == temp_dir
        assert basename(file) == "Name.txt"
        # Test renaming file to its current name
        file = mm_rename.rename_file(file, "Name??????????????")
        assert basename(file) == "Name.txt"
        # Test renaming file to name of existing file
        file = abspath(join(temp_dir, "new.txt"))
        mm_file_tools.write_text_file(file, "new text")
        file = mm_rename.rename_file(file, "Name")
        assert basename(file) == "Name-2.txt"
        assert sorted(os.listdir(temp_dir)) == ["Name-2.txt", "Name.txt"]
        # Test renaming same filename but different extension
        file = abspath(join(temp_dir, "Image.png"))
        mm_file_tools.write_text_file(file, "image text")
        file = mm_rename.rename_file(file, ":Name:")
        assert basename(file) == "Name.png"
        # Test that renamed files still contain the correct data
        assert sorted(os.listdir(temp_dir)) == ["Name-2.txt", "Name.png", "Name.txt"]
        file = abspath(join(temp_dir, "Name.txt"))
        assert mm_file_tools.read_text_file(file) == "test text"
        file = abspath(join(temp_dir, "Name-2.txt"))
        assert mm_file_tools.read_text_file(file) == "new text"
        file = abspath(join(temp_dir, "Name.png"))
        assert mm_file_tools.read_text_file(file) == "image text"
        # Test renaming invalid file
        file = abspath(join(temp_dir, "non-existant"))
        assert mm_rename.rename_file(file, "new") is None
        assert mm_rename.rename_file("/non/existant/file", "new") is None
    
def test_rename_media_archives():
    """
    Tests the rename_media_archives function.
    """
    # Test renaming cbz archives
    config = mm_config.get_config([])
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_dir = abspath(join(temp_dir, "cbz_dir"))
        shutil.copytree(mm_test.ARCHIVE_CBZ_DIRECTORY, cbz_dir)
        mm_rename.rename_archives(cbz_dir, "{title}")
        assert sorted(os.listdir(cbz_dir)) == ["Cómic.CBZ", "Internal.CBZ", "No Page.cbz", "empty.cbz"]
        # Test that files aren't renamed if already correct
        mm_rename.rename_archives(cbz_dir, "{title}")
        assert sorted(os.listdir(cbz_dir)) == ["Cómic.CBZ", "Internal.CBZ", "No Page.cbz", "empty.cbz"]
        # Test with different keys
        mm_rename.rename_archives(cbz_dir, "[{date}]")
        assert sorted(os.listdir(cbz_dir)) == ["Internal.CBZ", "[2012-12-21].CBZ", "[2023-04-13].cbz", "empty.cbz"]
    # Test renaming epub archives
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_dir = abspath(join(temp_dir, "epub_dir"))
        shutil.copytree(mm_test.ARCHIVE_EPUB_DIRECTORY, epub_dir)
        mm_rename.rename_archives(epub_dir, "{title}")
        assert sorted(os.listdir(epub_dir)) == ["Básic EPUB.epub", "Long Book.EPUB", "small.epub"]
        # Test that files aren't renamed if already correct
        mm_rename.rename_archives(epub_dir, "{title}")
        assert sorted(os.listdir(epub_dir)) == ["Básic EPUB.epub", "Long Book.EPUB", "small.epub"]
        # Test with different keys
        mm_rename.rename_archives(epub_dir, "[{writers}]")
        assert sorted(os.listdir(epub_dir)) == ["[Author].EPUB", "[Multiple,Writers].epub", "[Writer].epub"]
    # Test renaming archives with an invalid key/empty filename
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_dir = abspath(join(temp_dir, "cbz_dir"))
        shutil.copytree(mm_test.ARCHIVE_CBZ_DIRECTORY, cbz_dir)
        mm_rename.rename_archives(cbz_dir, "{unused}")
        assert sorted(os.listdir(cbz_dir)) == ["NoPage.cbz", "SubInfo.CBZ", "basic.CBZ", "empty.cbz"]
    # Test renaming archives while only allowing basic ASCII characters
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_dir = abspath(join(temp_dir, "cbz_dir"))
        shutil.copytree(mm_test.ARCHIVE_CBZ_DIRECTORY, cbz_dir)
        mm_rename.rename_archives(cbz_dir, "{title}", True)
        assert sorted(os.listdir(cbz_dir)) == ["Comic.CBZ", "Internal.CBZ", "No Page.cbz", "empty.cbz"]

def test_rename_json_pairs():
    """
    Tests the rename_json_pairs function.
    """
    # Test renaming JSON pairs
    config = mm_config.get_config([])
    with tempfile.TemporaryDirectory() as temp_dir:
        text_dir = abspath(join(temp_dir, "text"))
        image_dir = abspath(join(temp_dir, "image"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, text_dir)
        shutil.copytree(mm_test.PAIR_IMAGE_DIRECTORY, image_dir)
        mm_rename.rename_json_pairs(temp_dir, "{title}", config)
        assert sorted(os.listdir(text_dir)) == ["HTML.htm", "HTML.json", "TXT.JSON", "TXT.TXT"]
        assert sorted(os.listdir(image_dir)) == [".empty", "LRG.json", "LRG.webp", "LÑG.JPG", "LÑG.JSON", "Émpty.json", "Émpty.png"]
        # Test that files aren't renamed if not necessary
        mm_rename.rename_json_pairs(temp_dir, "{title}", config)
        assert sorted(os.listdir(text_dir)) == ["HTML.htm", "HTML.json", "TXT.JSON", "TXT.TXT"]
        assert sorted(os.listdir(image_dir)) == [".empty", "LRG.json", "LRG.webp", "LÑG.JPG", "LÑG.JSON", "Émpty.json", "Émpty.png"]
    # Test with multiple keys
    with tempfile.TemporaryDirectory() as temp_dir:
        text_dir = abspath(join(temp_dir, "text"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, text_dir)
        mm_rename.rename_json_pairs(text_dir, "{unused}-{writers}", config)
        assert sorted(os.listdir(text_dir)) == ["1-AAA.htm", "1-AAA.json", "2-BBB.JSON", "2-BBB.TXT"]
    # Test if JSON filename already exists
    with tempfile.TemporaryDirectory() as temp_dir:
        text_dir = abspath(join(temp_dir, "text"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, text_dir)
        mm_file_tools.write_text_file(abspath(join(text_dir, "2.json")), "A")
        mm_rename.rename_json_pairs(text_dir, "{unused}", config)
        assert sorted(os.listdir(text_dir)) == ["1.htm", "1.json", "2-2.JSON", "2-2.TXT", "2.json"]
    # Test if media filename already exists
    with tempfile.TemporaryDirectory() as temp_dir:
        text_dir = abspath(join(temp_dir, "text"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, text_dir)
        mm_file_tools.write_text_file(abspath(join(text_dir, "1.htm")), "A")
        mm_rename.rename_json_pairs(text_dir, "{unused}", config)
        assert sorted(os.listdir(text_dir)) == ["1-2.htm", "1-2.json", "1.htm", "2.JSON", "2.TXT"]
    # Test with an invalid filename template
    with tempfile.TemporaryDirectory() as temp_dir:
        text_dir = abspath(join(temp_dir, "text"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, text_dir)
        mm_rename.rename_json_pairs(text_dir, "{NONE}", config)
        assert sorted(os.listdir(text_dir)) == ["text 02.TXT", "text 02.txt.JSON", "text 1.htm", "text 1.json"]
    # Test renaming while only allowing basic ASCII characters
    with tempfile.TemporaryDirectory() as temp_dir:
        text_dir = abspath(join(temp_dir, "text"))
        image_dir = abspath(join(temp_dir, "image"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, text_dir)
        shutil.copytree(mm_test.PAIR_IMAGE_DIRECTORY, image_dir)
        mm_rename.rename_json_pairs(temp_dir, "{title}", config, True)
        assert sorted(os.listdir(text_dir)) == ["HTML.htm", "HTML.json", "TXT.JSON", "TXT.TXT"]
        assert sorted(os.listdir(image_dir)) == [".empty", "Empty.json", "Empty.png", "LNG.JPG", "LNG.JSON", "LRG.json", "LRG.webp"]

def test_sort_rename():
    """
    Tests the sort_rename function.
    """
    # Test sorting unlinked files
    with tempfile.TemporaryDirectory() as temp_dir:
        file_dir = abspath(join(temp_dir, "copy"))
        shutil.copytree(mm_test.BASIC_TEXT_DIRECTORY, file_dir)
        mm_rename.sort_rename(file_dir, "A [###]")
        assert sorted(os.listdir(file_dir)) == ["A [001].TXT", "A [002].txt", "A [003].txt"]
    # Test sorting JSON-media pairs
    with tempfile.TemporaryDirectory() as temp_dir:
        file_dir = abspath(join(temp_dir, "copy"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, file_dir)
        mm_rename.sort_rename(file_dir, "B#")
        assert sorted(os.listdir(file_dir)) == ["B1.htm", "B1.json", "B2.JSON", "B2.TXT"]
        # Test that files aren't renamed if unnecessary
        mm_rename.sort_rename(file_dir, "B#")
        assert sorted(os.listdir(file_dir)) == ["B1.htm", "B1.json", "B2.JSON", "B2.TXT"]
    # Test sorting a combination of JSON-media pairs and unlinked files
    with tempfile.TemporaryDirectory() as temp_dir:
        file_dir = abspath(join(temp_dir, "copy"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, file_dir)
        mm_file_tools.write_text_file(abspath(join(file_dir, "text.txt")), "A")
        mm_rename.sort_rename(file_dir, "#")
        assert sorted(os.listdir(file_dir)) == ["1.htm", "1.json", "2.JSON", "2.TXT", "3.txt"]
    # Test Using a different starting index
    with tempfile.TemporaryDirectory() as temp_dir:
        file_dir = abspath(join(temp_dir, "copy"))
        shutil.copytree(mm_test.BASIC_TEXT_DIRECTORY, file_dir)
        mm_rename.sort_rename(file_dir, "[##]", 42)
        assert sorted(os.listdir(file_dir)) == ["[42].TXT", "[43].txt", "[44].txt"]
        # Test that subdirectories are not affected
        mm_rename.sort_rename(temp_dir, "NONE [#####]", 500)
        assert sorted(os.listdir(file_dir)) == ["[42].TXT", "[43].txt", "[44].txt"]
    # Test limiting to a certain file pattern
    with tempfile.TemporaryDirectory() as temp_dir:
        file_dir = abspath(join(temp_dir, "copy"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, file_dir)
        mm_file_tools.write_text_file(abspath(join(file_dir, "text.txt")), "A")
        mm_rename.sort_rename(file_dir, "#", file_pattern=r"\.txt$")
        assert sorted(os.listdir(file_dir)) == ["1.JSON", "1.TXT", "2.txt", "text 1.htm", "text 1.json"]
        mm_rename.sort_rename(file_dir, "A!", file_pattern=r"2")
        assert sorted(os.listdir(file_dir)) == ["1.JSON", "1.TXT", "A!.txt", "text 1.htm", "text 1.json"]
    # Test renaming a single file
    with tempfile.TemporaryDirectory() as temp_dir:
        mm_file_tools.write_text_file(abspath(join(temp_dir, "AAA.png")), "AAA")
        mm_rename.sort_rename(temp_dir, "Title", 500)
        assert sorted(os.listdir(temp_dir)) == ["Title [500].png"]
        mm_rename.sort_rename(temp_dir, "Title")
        assert sorted(os.listdir(temp_dir)) == ["Title.png"]
        mm_rename.sort_rename(temp_dir, "#")
        assert sorted(os.listdir(temp_dir)) == ["1.png"]
