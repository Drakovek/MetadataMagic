#!/usr/bin/env python3

import os
import shutil
import metadata_magic.rename as mm_rename
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.epub as mm_epub
import metadata_magic.archive.comic_archive as mm_comic_archive
from os.path import abspath, basename, exists, join

def test_get_file_friendly_text():
    """
    Tests the get_file_friendly_text function.
    """
    # Test replacing invalid characters
    assert mm_rename.get_file_friendly_text("**What?!?!") == "What-!-!"
    assert mm_rename.get_file_friendly_text(".This:That") == "This - That"
    assert mm_rename.get_file_friendly_text("Blah...") == "Blah…"
    assert mm_rename.get_file_friendly_text("<\"This/That\\Other\">") == "This-That-Other"
    assert mm_rename.get_file_friendly_text("(A|||B)") == "(A-B)"
    assert mm_rename.get_file_friendly_text("...Mr. Roboto.") == "…Mr. Roboto"
    assert mm_rename.get_file_friendly_text(" This    &    That ") == "This & That"
    assert mm_rename.get_file_friendly_text("thing--stuff  @*-   blah") == "thing-stuff @ blah"
    assert mm_rename.get_file_friendly_text("This..") == "This"
    assert mm_rename.get_file_friendly_text("..Dots.....") == "Dots…"
    assert mm_rename.get_file_friendly_text("Spaced .  .   .") == "Spaced …"
    assert mm_rename.get_file_friendly_text("  This is the end >.<  ") == "This is the end"
    assert mm_rename.get_file_friendly_text(" No, THIS is the end. -.-.. ") == "No, THIS is the end"
    assert mm_rename.get_file_friendly_text("A -> B") == "A to B"
    assert mm_rename.get_file_friendly_text("Thing ----> Other") == "Thing to Other"
    # Test removing hanging hyphens.
    assert mm_rename.get_file_friendly_text("Blah!- Thing") == "Blah! Thing"
    assert mm_rename.get_file_friendly_text("Other23- Item") == "Other23 Item"
    assert mm_rename.get_file_friendly_text("First -!Next") == "First !Next"
    assert mm_rename.get_file_friendly_text("None -Next") == "None Next"
    # Test converting from non-standard latin characters
    assert mm_rename.get_file_friendly_text("ÀÁÂÃÄÅ") == "AAAAAA"
    assert mm_rename.get_file_friendly_text("ÈÉÊË") == "EEEE"
    assert mm_rename.get_file_friendly_text("ÌÍÎÏ") == "IIII"
    assert mm_rename.get_file_friendly_text("ÑÒÓÔÕÖ") == "NOOOOO"
    assert mm_rename.get_file_friendly_text("ÙÚÛÜÝ") == "UUUUY"
    assert mm_rename.get_file_friendly_text("àáâãäå") == "aaaaaa"
    assert mm_rename.get_file_friendly_text("èéêë") == "eeee"
    assert mm_rename.get_file_friendly_text("ìíîï") == "iiii"
    assert mm_rename.get_file_friendly_text("ñòóôõö") == "nooooo"
    assert mm_rename.get_file_friendly_text("ùúûüýÿ") == "uuuuyy"
    # Test getting filename with no length
    assert mm_rename.get_file_friendly_text("") == "0"
    assert mm_rename.get_file_friendly_text("---") == "0"

def test_get_available_filename():
    """
    Tests the get_available_filename function.
    """
    # Test getting filename with unacceptable characters.
    temp_dir = mm_file_tools.get_temp_dir()
    assert mm_rename.get_available_filename(["a.txt"], "Name?", temp_dir) == "Name"
    assert mm_rename.get_available_filename(["b.png"], ".dat", temp_dir) == "dat"
    # Test getting filename if desired filename already exists
    text_file = abspath(join(temp_dir, "name.txt"))
    mm_file_tools.write_text_file(text_file, "some text")
    assert exists(text_file)
    assert mm_rename.get_available_filename(["a.txt"], "name", temp_dir) == "name-2"
    # Test if filename exists with a different extension
    assert mm_rename.get_available_filename(["b.png"], "name", temp_dir) == "name"
    # Test if filename alternate filename is also taken
    text_file_2 = abspath(join(temp_dir, "name-2.txt"))
    text_file_3 = abspath(join(temp_dir, "name-3.txt"))
    mm_file_tools.write_text_file(text_file_2, "more")
    mm_file_tools.write_text_file(text_file_3, "text")
    assert exists(text_file_2)
    assert exists(text_file_3)
    assert mm_rename.get_available_filename(["a.txt"], "name", temp_dir) == "name-4"
    # Test checking against multiple file extensions
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "title.txt")), "A")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "title-2.png")), "A")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "title-3.jpg")), "A")
    assert mm_rename.get_available_filename(["a.doc"], "title", temp_dir) == "title"
    assert mm_rename.get_available_filename(["a.txt"], "title", temp_dir) == "title-2"
    assert mm_rename.get_available_filename(["a.txt", "b.png", "c.dvk"], "title", temp_dir) == "title-3"
    assert mm_rename.get_available_filename(["a.txt", "b.png", "c.jpg"], "title", temp_dir) == "title-4"

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
    new_file = mm_rename.rename_file(file, "Name?")
    assert exists(new_file)
    assert abspath(join(new_file, os.pardir)) == temp_dir
    assert basename(new_file) == "Name.txt"
    # Test renaming file to its current name
    file = new_file
    new_file = None
    assert exists(file)
    new_file = mm_rename.rename_file(file, "Name??????????????")
    assert exists(new_file)
    assert file == new_file
    # Test renaming file to name of existing file
    file = abspath(join(temp_dir, "totally_new.txt"))
    mm_file_tools.write_text_file(file, "NEW!")
    assert exists(file)
    new_file = mm_rename.rename_file(file, "Name")
    assert exists(new_file)
    assert abspath(join(new_file, os.pardir)) == temp_dir
    assert basename(new_file) == "Name-2.txt"
    # Test renaming same filename but different extension
    file = abspath(join(temp_dir, "Weeee!.png"))
    mm_file_tools.write_text_file(file, "Not Actually PNG.")
    assert exists(file)
    new_file = mm_rename.rename_file(file, ":Name:")
    assert exists(new_file)
    assert abspath(join(new_file, os.pardir)) == temp_dir
    assert basename(new_file) == "Name.png"
    # Test renaming a third time
    file = abspath(join(temp_dir, "next.txt"))
    mm_file_tools.write_text_file(file, "Next")
    assert exists(file)
    new_file = mm_rename.rename_file(file, ":Name:")
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
    new_file = mm_rename.rename_file(file, "new")
    assert new_file is None

def test_get_string_from_metadata():
    """
    Tests the get_string_from_metadata function
    """
    # Test getting string with no formatting
    assert mm_rename.get_string_from_metadata({"name":"thing"}, "Blah") == "Blah"
    # Test getting string with some metadata keys
    metadata = {"title":"This is a title", "artist":"Person", "thing":"Other"}
    assert mm_rename.get_string_from_metadata(metadata, "{title}") == "This is a title"
    assert mm_rename.get_string_from_metadata(metadata, "{thing}_{title}") == "Other_This is a title"
    assert mm_rename.get_string_from_metadata(metadata, "[{thing}] ({artist})") == "[Other] (Person)"    
    # Test getting string with non-existant keys
    assert mm_rename.get_string_from_metadata(metadata, "{blah}") is None
    assert mm_rename.get_string_from_metadata(metadata, "{other} {title}  ") is None
    assert mm_rename.get_string_from_metadata(metadata, "{a}{b}{c}{thing}{e}{f}") is None
    # Test getting string with existing JSON data
    metadata = {"title":"Name", "original":{"number":5, "other":"Final"}}
    assert mm_rename.get_string_from_metadata(metadata, "[{number}] {title}") == "[5] Name"
    assert mm_rename.get_string_from_metadata(metadata, "{title} - {other}") == "Name - Final"
    # Test with series info
    metadata = {"series_number":"15", "series_total":"20"}
    assert mm_rename.get_string_from_metadata(metadata, "[{series_number}] AAA") == "[15] AAA"
    metadata = {"series_number":"1", "series_total":"20"}
    assert mm_rename.get_string_from_metadata(metadata, "[{series_number}] AAA") == "[01] AAA"
    metadata = {"series_number":"1.00", "series_total":"15"}
    assert mm_rename.get_string_from_metadata(metadata, "[{series_number}] AAA") == "[01] AAA"
    metadata = {"series_number":"1.5", "series_total":"1.0"}
    assert mm_rename.get_string_from_metadata(metadata, "[{series_number}] AAA") == "[01.5] AAA"
    metadata = {"series_number":"12.0", "series_total":None}
    assert mm_rename.get_string_from_metadata(metadata, "[{series_number}] AAA") == "[12] AAA"
    metadata = {"series_number":"1", "series_total":"1.0"}
    assert mm_rename.get_string_from_metadata(metadata, "[{series_number}] AAA") is None
    metadata = {"series_number":"1.0", "series_total":"1"}
    assert mm_rename.get_string_from_metadata(metadata, "[{series_number}] AAA") is None
    metadata = {"series_number":"A", "series_total":"20"}
    assert mm_rename.get_string_from_metadata(metadata, "[{series_number}] AAA") is None
    metadata = {"series_number":"20", "series_total":"A"}
    assert mm_rename.get_string_from_metadata(metadata, "[{series_number}] AAA") is None
    metadata = {"series_number":"20"}
    assert mm_rename.get_string_from_metadata(metadata, "[{series_number}] AAA") is None
    # Test getting string with empty keys
    metadata["id"] = None
    assert mm_rename.get_string_from_metadata(metadata, "{id}") is None
    assert mm_rename.get_string_from_metadata(metadata, "{id} Thing") is None
    
def test_rename_media_archives():
    """
    Tests the rename_media_archives function.
    """
    # Create test archives
    temp_dir = mm_file_tools.get_temp_dir()
    build_dir = mm_file_tools.get_temp_dir("dvk_test_builder")
    sub_dir = abspath(join(temp_dir, "sub"))
    os.mkdir(sub_dir)
    media_file = abspath(join(build_dir, "image.png"))
    mm_file_tools.write_text_file(media_file, "AAA")
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "CBZ Root"
    metadata["artists"] = "Person"
    cbz_file = mm_comic_archive.create_cbz(build_dir, "CBZ1", metadata=metadata)
    shutil.copy(cbz_file, temp_dir)
    os.remove(cbz_file)
    metadata["title"] = "Part 2"
    metadata["artists"] = "Person"
    cbz_file = mm_comic_archive.create_cbz(build_dir, "CBZ2", metadata=metadata)
    shutil.copy(cbz_file, temp_dir)
    os.remove(cbz_file)
    metadata["title"] = "CBZ Deep"
    metadata["artists"] = "Artist"
    cbz_file = mm_comic_archive.create_cbz(build_dir, "CBZ3", metadata=metadata)
    shutil.copy(cbz_file, sub_dir)
    build_dir = mm_file_tools.get_temp_dir("dvk_test_builder")
    text_file = abspath(join(build_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "Text")
    metadata["title"] = "EPUB Root"
    metadata["artists"] = "Writer"
    chapters = mm_epub.get_default_chapters(build_dir)
    epub_file = mm_epub.create_epub(chapters, metadata, build_dir)
    shutil.copy(epub_file, temp_dir)
    os.remove(epub_file)
    metadata["title"] = "EPUB Sub"
    metadata["artists"] = "Final"
    chapters = mm_epub.get_default_chapters(build_dir)
    epub_file = mm_epub.create_epub(chapters, metadata, build_dir)
    shutil.copy(epub_file, sub_dir)
    assert sorted(os.listdir(temp_dir)) == ["CBZ1.cbz", "CBZ2.cbz", "EPUB Root.epub", "sub"]
    assert sorted(os.listdir(sub_dir)) == ["CBZ3.cbz", "EPUB Sub.epub"]
    # Test renaming archives to their titles 
    mm_rename.rename_archives(temp_dir, "{title}")
    assert sorted(os.listdir(temp_dir)) == ["CBZ Root.cbz", "EPUB Root.epub", "Part 2.cbz", "sub"]
    assert sorted(os.listdir(sub_dir)) == ["CBZ Deep.cbz", "EPUB Sub.epub"]
    # Test with additional keys
    mm_rename.rename_archives(temp_dir, "[{artists}] {title}")
    assert sorted(os.listdir(temp_dir)) == ["[Person] CBZ Root.cbz", "[Person] Part 2.cbz", "[Writer] EPUB Root.epub", "sub"]
    assert sorted(os.listdir(sub_dir)) == ["[Artist] CBZ Deep.cbz", "[Final] EPUB Sub.epub"]
    # Test if archive filename already exists
    duplicate_cbz = abspath(join(sub_dir, "CBZ Deep.cbz"))
    duplicate_epub = abspath(join(sub_dir, "EPUB Sub.epub"))
    mm_file_tools.write_text_file(duplicate_cbz, "TEXT")
    mm_file_tools.write_text_file(duplicate_epub, "TEXT")
    mm_rename.rename_archives(temp_dir, "{title}")
    assert sorted(os.listdir(temp_dir)) == ["CBZ Root.cbz", "EPUB Root.epub", "Part 2.cbz", "sub"]
    assert sorted(os.listdir(sub_dir)) == ["CBZ Deep-2.cbz", "CBZ Deep.cbz", "EPUB Sub-2.epub", "EPUB Sub.epub"]
    mm_rename.rename_archives(temp_dir, "{artists}")
    assert sorted(os.listdir(temp_dir)) == ["Person-2.cbz", "Person.cbz", "Writer.epub", "sub"]
    assert sorted(os.listdir(sub_dir)) == ["Artist.cbz", "CBZ Deep.cbz", "EPUB Sub.epub", "Final.epub"]

def test_rename_json_pairs():
    """
    Tests the rename_json_pairs function.
    """
    # Create test files
    temp_dir = mm_file_tools.get_temp_dir()
    sub_dir = abspath(join(temp_dir, "sub"))
    os.mkdir(sub_dir)
    text_file = abspath(join(temp_dir, "textA.txt"))
    mm_file_tools.write_text_file(text_file, "TEXT")
    json_file = abspath(join(temp_dir, "textA.json"))
    mm_file_tools.write_json_file(json_file, {"title":"Title A!", "artist":"Artist"})
    text_file = abspath(join(temp_dir, "textB.txt"))
    mm_file_tools.write_text_file(text_file, "TEXT")
    json_file = abspath(join(temp_dir, "textB.json"))
    mm_file_tools.write_json_file(json_file, {"title":"Other", "artist":"Name"})
    text_file = abspath(join(sub_dir, "textC.txt"))
    mm_file_tools.write_text_file(text_file, "TEXT")
    json_file = abspath(join(sub_dir, "textC.json"))
    mm_file_tools.write_json_file(json_file, {"title":"Final", "artist":"New"})
    text_file = abspath(join(sub_dir, "unrelated.txt"))
    mm_file_tools.write_text_file(text_file, "TEXT")
    assert sorted(os.listdir(temp_dir)) == ["sub", "textA.json", "textA.txt", "textB.json", "textB.txt"]
    assert sorted(os.listdir(sub_dir)) == ["textC.json", "textC.txt", "unrelated.txt"]
    # Test renaming JSON pairs
    mm_rename.rename_json_pairs(temp_dir, "{title}")
    assert sorted(os.listdir(temp_dir)) == ["Other.json", "Other.txt", "Title A!.json", "Title A!.txt", "sub"]
    assert sorted(os.listdir(sub_dir)) == ["Final.json", "Final.txt", "unrelated.txt"]
    # Test that files aren't renamed if not necessary
    mm_rename.rename_json_pairs(temp_dir, "{title}")
    assert sorted(os.listdir(temp_dir)) == ["Other.json", "Other.txt", "Title A!.json", "Title A!.txt", "sub"]
    assert sorted(os.listdir(sub_dir)) == ["Final.json", "Final.txt", "unrelated.txt"]
    # Test with additional keys
    mm_rename.rename_json_pairs(temp_dir, "{title} ({writers})")
    assert sorted(os.listdir(temp_dir)) == ["Other (Name).json", "Other (Name).txt", "Title A! (Artist).json", "Title A! (Artist).txt", "sub"]
    assert sorted(os.listdir(sub_dir)) == ["Final (New).json", "Final (New).txt", "unrelated.txt"]
    # Test renaming if JSON filename already exists
    duplicate_json = abspath(join(sub_dir, "Final A.json"))
    mm_file_tools.write_json_file(duplicate_json, "NOT ACTUAL JSON")
    mm_rename.rename_json_pairs(temp_dir, "{title} A")
    assert sorted(os.listdir(temp_dir)) == ["Other A.json", "Other A.txt", "Title A! A.json", "Title A! A.txt", "sub"]
    assert sorted(os.listdir(sub_dir)) == ["Final A-2.json", "Final A-2.txt", "Final A.json", "unrelated.txt"]
    # Test renaming if media filename already exists
    duplicate_media = abspath(join(temp_dir, "Other B.txt"))
    mm_file_tools.write_json_file(duplicate_media, "Text")
    mm_rename.rename_json_pairs(temp_dir, "{title} B")
    assert sorted(os.listdir(temp_dir)) == ["Other B-2.json", "Other B-2.txt", "Other B.txt", "Title A! B.json", "Title A! B.txt", "sub"]
    assert sorted(os.listdir(sub_dir)) == ["Final A.json", "Final B.json", "Final B.txt", "unrelated.txt"]
    # Test renaming pair with invalid JSON metadata
    json_file = abspath(join(sub_dir, "Final C.json"))
    mm_file_tools.write_json_file(json_file, "NOT ACTUAL JSON")
    media_file = abspath(join(sub_dir, "Final C.png"))
    mm_file_tools.write_json_file(media_file, "Text")
    mm_rename.rename_json_pairs(temp_dir, "{title} C")
    assert sorted(os.listdir(temp_dir)) == ["Other B.txt", "Other C.json", "Other C.txt", "Title A! C.json", "Title A! C.txt", "sub"]
    assert sorted(os.listdir(sub_dir)) == ["Final A.json", "Final C-2.json", "Final C-2.txt", "Final C.json", "Final C.png", "unrelated.txt"]

def test_sort_rename():
    """
    Tests the sort_rename function.
    """
    # Test sorting unlinked files
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "A.txt")), "A")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "B.png")), "B")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "C.jpg")), "C")
    mm_rename.sort_rename(temp_dir, "Title [###]")
    assert sorted(os.listdir(temp_dir)) == ["Title [001].txt", "Title [002].png", "Title [003].jpg"]
    # Test sorting JSON pairs
    mm_file_tools.write_text_file(abspath(join(temp_dir, "Title [001].json")), "A")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "Title [002].json")), "B")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "Title [003].json")), "C")
    mm_rename.sort_rename(temp_dir, "New - ##")
    files = sorted(os.listdir(temp_dir))
    assert len(files) == 6
    assert basename(files[0]) == "New - 01.json"
    assert basename(files[1]) == "New - 01.txt"
    assert basename(files[2]) == "New - 02.json"
    assert basename(files[3]) == "New - 02.png"
    assert basename(files[4]) == "New - 03.jpg"
    assert basename(files[5]) == "New - 03.json"
    # Test sorting combination of JSON pairs and unlinked files
    mm_file_tools.write_text_file(abspath(join(temp_dir, "Unlinked.json")), "A")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "Thing.png")), "A")
    mm_rename.sort_rename(temp_dir, "New")
    files = sorted(os.listdir(temp_dir))
    assert len(files) == 8
    assert basename(files[0]) == "New [01].json"
    assert basename(files[1]) == "New [01].txt"
    assert basename(files[2]) == "New [02].json"
    assert basename(files[3]) == "New [02].png"
    assert basename(files[4]) == "New [03].jpg"
    assert basename(files[5]) == "New [03].json"
    assert basename(files[6]) == "New [04].png"
    assert basename(files[7]) == "New [05].json"
    # Test sorting files with a different starting index
    mm_rename.sort_rename(temp_dir, "AAA (###)", 23)
    files = sorted(os.listdir(temp_dir))
    assert len(files) == 8
    assert basename(files[0]) == "AAA (023).json"
    assert basename(files[1]) == "AAA (023).txt"
    assert basename(files[2]) == "AAA (024).json"
    assert basename(files[3]) == "AAA (024).png"
    assert basename(files[4]) == "AAA (025).jpg"
    assert basename(files[5]) == "AAA (025).json"
    assert basename(files[6]) == "AAA (026).png"
    assert basename(files[7]) == "AAA (027).json"
    # Test that files in subdirectories aren't effected
    sub_dir = abspath(join(temp_dir, "subdir"))
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(abspath(join(sub_dir, "File.png")), "A")
    mm_file_tools.write_text_file(abspath(join(sub_dir, "File.json")), "B")
    mm_file_tools.write_text_file(abspath(join(sub_dir, "Other.jpg")), "C")
    mm_rename.sort_rename(temp_dir, "##", 0)
    files = sorted(os.listdir(temp_dir))
    assert len(files) == 9
    assert basename(files[0]) == "00.json"
    assert basename(files[1]) == "00.txt"
    assert basename(files[2]) == "01.json"
    assert basename(files[3]) == "01.png"
    assert basename(files[4]) == "02.jpg"
    assert basename(files[5]) == "02.json"
    assert basename(files[6]) == "03.png"
    assert basename(files[7]) == "04.json"
    assert basename(files[8]) == "subdir"
    assert sorted(os.listdir(sub_dir)) == ["File.json", "File.png", "Other.jpg"]
    # Test that files aren't renamed if unnecessary
    mm_rename.sort_rename(temp_dir, "##", 0)
    files = sorted(os.listdir(temp_dir))
    assert len(files) == 9
    assert basename(files[0]) == "00.json"
    assert basename(files[1]) == "00.txt"
    assert basename(files[2]) == "01.json"
    assert basename(files[3]) == "01.png"
    assert basename(files[4]) == "02.jpg"
    assert basename(files[5]) == "02.json"
    assert basename(files[6]) == "03.png"
    assert basename(files[7]) == "04.json"
    assert basename(files[8]) == "subdir"
    # Test renaming a single file
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "File.png")), "A")
    mm_rename.sort_rename(temp_dir, "New File")
    assert os.listdir(temp_dir) == ["New File.png"]
    mm_rename.sort_rename(temp_dir, "New ##")
    assert os.listdir(temp_dir) == ["New 01.png"]
    mm_rename.sort_rename(temp_dir, "Other", 5)
    assert os.listdir(temp_dir) == ["Other [05].png"]
