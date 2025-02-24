#!/usr/bin/env python3

import os
import shutil
import tempfile
import metadata_magic.test as mm_test
import metadata_magic.config as mm_config
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive as mm_archive
import metadata_magic.archive.epub as mm_epub
from os.path import abspath, basename, exists, join
from PIL import Image

def test_get_default_chapters():
    """
    Tests the get_default_chapters function.
    """
    # Test getting default chapters with a single text file.
    simple_dir = abspath(join(mm_test.EPUB_INTERNAL_DIRECTORY, "simple"))
    chapters = mm_epub.get_default_chapters(simple_dir)
    assert len(chapters) == 1
    assert chapters[0]["include"]
    assert chapters[0]["title"] == "text"
    assert len(chapters[0]["files"]) == 1
    assert chapters[0]["files"][0]["id"] == "item0"
    assert basename(chapters[0]["files"][0]["file"]) == "text.txt"
    # Test getting default chapters with multiple text and image files
    multiple_dir = abspath(join(mm_test.EPUB_INTERNAL_DIRECTORY, "multiple"))
    chapters = mm_epub.get_default_chapters(multiple_dir)
    assert len(chapters) == 4
    assert chapters[0]["include"]
    assert chapters[0]["title"] == "Part 1"
    assert len(chapters[0]["files"]) == 1
    assert chapters[0]["files"][0]["id"] == "item0"
    assert basename(chapters[0]["files"][0]["file"]) == "[AA] Part 1.TXT"
    assert chapters[1]["include"]
    assert chapters[1]["title"] == "Image 1"
    assert len(chapters[1]["files"]) == 1
    assert chapters[1]["files"][0]["id"] == "item1"
    assert basename(chapters[1]["files"][0]["file"]) == "[BB] Image 1.PNG"
    assert chapters[2]["include"]
    assert chapters[2]["title"] == "Part 2"
    assert len(chapters[2]["files"]) == 1
    assert chapters[2]["files"][0]["id"] == "item2"
    assert basename(chapters[2]["files"][0]["file"]) == "[CC] Part 2.htm"
    assert chapters[3]["include"]
    assert chapters[3]["title"] == "Image 2"
    assert len(chapters[3]["files"]) == 1
    assert chapters[3]["files"][0]["id"] == "item3"
    assert basename(chapters[3]["files"][0]["file"]) == "[DD] Image 2.jpg"

def test_add_cover_to_chapters():
    """
    Tests the add cover_to_chapters function
    """
    # Test updating chapters and creating content files
    simple_dir = abspath(join(mm_test.EPUB_INTERNAL_DIRECTORY, "simple"))
    chapters = mm_epub.get_default_chapters(simple_dir)
    with tempfile.TemporaryDirectory() as temp_dir:
        metadata = {"title":"Title", "writers":"Artist"}
        chapters = mm_epub.add_cover_to_chapters(chapters, metadata, temp_dir)
        assert len(chapters) == 2
        assert chapters[0]["include"]
        assert chapters[0]["title"] == "Cover"
        assert len(chapters[0]["files"]) == 1
        assert chapters[0]["files"][0]["id"] == "cover"
        assert basename(chapters[0]["files"][0]["file"]) == "cover_image.jpg"
        assert abspath(join(chapters[0]["files"][0]["file"], os.pardir)) == temp_dir
        assert exists(chapters[0]["files"][0]["file"])
        image = Image.open(chapters[0]["files"][0]["file"])
        assert image.size == (900, 1200)
        assert chapters[1]["include"]
        assert chapters[1]["title"] == "text"
        assert len(chapters[1]["files"]) == 1
        assert chapters[1]["files"][0]["id"] == "item0"
        assert basename(chapters[1]["files"][0]["file"]) == "text.txt"
        assert exists(chapters[1]["files"][0]["file"])

def test_group_chapters():
    """
    Tests the group_chapters function.
    """
    # Create test group of chapters
    chapters = []
    chapters.append({"include":False, "title":"Item", "files":[{"id":"item0", "file":"file1.txt"}]})
    chapters.append({"include":True, "title":"Part 2", "files":[{"id":"item1", "file":"file2.png"}]})
    chapters.append({"include":True, "title":"Part 3", "files":[{"id":"item2", "file":"file3.jpg"}]})
    chapters.append({"include":False, "title":"Final", "files":[{"id":"item3", "file":"file4.jpeg"}]})
    # Combine groups of 1
    new_chapters = mm_epub.group_chapters(chapters, [2,0])
    assert len(new_chapters) == 3
    assert new_chapters[0]["include"] is True
    assert new_chapters[0]["title"] == "Item"
    assert new_chapters[0]["files"] == [{"id":"item0", "file":"file1.txt"}, {"id":"item2", "file":"file3.jpg"}]
    assert new_chapters[1] == {"include":True, "title":"Part 2", "files":[{"id":"item1", "file":"file2.png"}]}
    assert new_chapters[2] == {"include":False, "title":"Final", "files":[{"id":"item3", "file":"file4.jpeg"}]}
    # Combine an already combined group
    new_chapters = mm_epub.group_chapters(new_chapters, [2,0,1,0])
    assert len(new_chapters) == 1
    assert new_chapters[0]["include"] is True
    assert new_chapters[0]["title"] == "Item"
    assert len(new_chapters[0]["files"]) == 4
    assert new_chapters[0]["files"][0] == {"id":"item0", "file":"file1.txt"}
    assert new_chapters[0]["files"][1] == {"id":"item1", "file":"file2.png"}
    assert new_chapters[0]["files"][2] == {"id":"item2", "file":"file3.jpg"}
    assert new_chapters[0]["files"][3] == {"id":"item3", "file":"file4.jpeg"}
    # Try combining with just one entry
    new_chapters = mm_epub.group_chapters(chapters, [1,1,1])
    assert len(new_chapters) == 4
    assert new_chapters[0]["include"] is False
    assert new_chapters[0]["title"] == "Item"
    assert new_chapters[0]["files"] == [{"id":"item0", "file":"file1.txt"}]
    assert new_chapters[1]["include"] is True
    assert new_chapters[1]["title"] == "Part 2"
    assert new_chapters[1]["files"] == [{"id":"item1", "file":"file2.png"}]
    assert new_chapters[2]["include"] is True
    assert new_chapters[2]["title"] == "Part 3"
    assert new_chapters[2]["files"] == [{"id":"item2", "file":"file3.jpg"}]
    assert new_chapters[3]["include"] is False
    assert new_chapters[3]["title"] == "Final"
    assert new_chapters[3]["files"] == [{"id":"item3", "file":"file4.jpeg"}]
    # Try combining non-existant entries
    new_chapters = mm_epub.group_chapters(chapters, [-1])
    assert len(new_chapters) == 4
    new_chapters = mm_epub.group_chapters(chapters, [6])
    assert len(new_chapters) == 4
    new_chapters = mm_epub.group_chapters(chapters, [4, 2, 1, -1])
    assert len(new_chapters) == 3
    assert new_chapters[0]["include"] is False
    assert new_chapters[0]["title"] == "Item"
    assert new_chapters[0]["files"] == [{"id":"item0", "file":"file1.txt"}]
    assert new_chapters[1]["include"] is True
    assert new_chapters[1]["title"] == "Part 2"
    assert new_chapters[1]["files"] == [{"id":"item1", "file":"file2.png"}, {"id":"item2", "file":"file3.jpg"}]
    assert new_chapters[2]["include"] is False
    assert new_chapters[2]["title"] == "Final"
    assert new_chapters[2]["files"] == [{"id":"item3", "file":"file4.jpeg"}]

def test_separate_chapters():
    """
    Tests the separate_chapters function.
    """
    # Create test group of chapters
    chapters = []
    chapters.append({"include":False, "title":"Item", "files":[{"id":"item0", "file":"[00] a.txt"}]})
    files = [{"id":"item1", "file":"[01] B.png"}, {"id":"item3", "file":"[3] file.jpg"}]
    chapters.append({"include":False, "title":"Part 2", "files":files})
    files = [{"id":"item2", "file":"[02] Z.png"}, {"id":"item4", "file":"[4] E.jpg"}, {"id":"item5", "file":"[5] D.jpg"}]
    chapters.append({"include":False, "title":"Final", "files":files})
    # Test ungrouping a chapter with two files
    new_chapters = mm_epub.separate_chapters(chapters, 1)
    assert len(new_chapters) == 4
    assert new_chapters[0]["include"] is False
    assert new_chapters[0]["title"] == "Item"
    assert new_chapters[0]["files"] == [{"id":"item0", "file":"[00] a.txt"}]
    assert new_chapters[1]["include"] is True
    assert new_chapters[1]["title"] == "B"
    assert new_chapters[1]["files"] == [{"id":"item1", "file":"[01] B.png"}]
    assert new_chapters[2]["include"] is False
    assert new_chapters[2]["title"] == "Final"
    assert len(new_chapters[2]["files"]) == 3
    assert new_chapters[2]["files"][0] == {"id":"item2", "file":"[02] Z.png"}
    assert new_chapters[2]["files"][1] == {"id":"item4", "file":"[4] E.jpg"}
    assert new_chapters[2]["files"][2] == {"id":"item5", "file":"[5] D.jpg"}
    assert new_chapters[3]["include"] is True
    assert new_chapters[3]["title"] == "file"
    assert new_chapters[3]["files"] == [{"id":"item3", "file":"[3] file.jpg"}]
    # Test ungrouping a chapter with more than two files
    new_chapters = mm_epub.separate_chapters(chapters, 2)
    assert len(new_chapters) == 5
    assert new_chapters[0]["include"] is False
    assert new_chapters[0]["title"] == "Item"
    assert new_chapters[0]["files"] == [{"id":"item0", "file":"[00] a.txt"}]
    assert new_chapters[1]["include"] is False
    assert new_chapters[1]["title"] == "Part 2"
    assert len(new_chapters[1]["files"]) == 2
    assert new_chapters[1]["files"][0] == {"id":"item1", "file":"[01] B.png"}
    assert new_chapters[1]["files"][1] == {"id":"item3", "file":"[3] file.jpg"}
    assert new_chapters[2]["include"] is True
    assert new_chapters[2]["title"] == "Z"
    assert new_chapters[2]["files"] == [{"id":"item2", "file":"[02] Z.png"}]
    assert new_chapters[3]["include"] is True
    assert new_chapters[3]["title"] == "E"
    assert new_chapters[3]["files"] == [{"id":"item4", "file":"[4] E.jpg"}]
    assert new_chapters[4]["include"] is True
    assert new_chapters[4]["title"] == "D"
    assert new_chapters[4]["files"] == [{"id":"item5", "file":"[5] D.jpg"}]
    # Test ungrouping a chapter with only one file
    new_chapters = mm_epub.separate_chapters(chapters, 0)
    assert len(new_chapters) == 3
    assert new_chapters[0]["include"] is False
    assert new_chapters[0]["title"] == "Item"
    assert new_chapters[0]["files"] == [{"id":"item0", "file":"[00] a.txt"}]
    assert new_chapters[1]["include"] is False
    assert new_chapters[1]["title"] == "Part 2"
    assert len(new_chapters[1]["files"]) == 2
    assert new_chapters[1]["files"][0] == {"id":"item1", "file":"[01] B.png"}
    assert new_chapters[1]["files"][1] == {"id":"item3", "file":"[3] file.jpg"}
    assert new_chapters[2]["include"] is False
    assert new_chapters[2]["title"] == "Final"
    assert len(new_chapters[2]["files"]) == 3
    assert new_chapters[2]["files"][0] == {"id":"item2", "file":"[02] Z.png"}
    assert new_chapters[2]["files"][1] == {"id":"item4", "file":"[4] E.jpg"}
    assert new_chapters[2]["files"][2] == {"id":"item5", "file":"[5] D.jpg"}
    # Test ungrouping a chapter at in invalid index
    new_chapters = mm_epub.separate_chapters(chapters, -1)
    assert len(new_chapters) == 3
    new_chapters = mm_epub.separate_chapters(chapters, 5)
    assert len(new_chapters) == 3
    assert new_chapters[0]["include"] is False
    assert new_chapters[0]["title"] == "Item"
    assert new_chapters[0]["files"] == [{"id":"item0", "file":"[00] a.txt"}]
    assert new_chapters[1]["include"] is False
    assert new_chapters[1]["title"] == "Part 2"
    assert len(new_chapters[1]["files"]) == 2
    assert new_chapters[1]["files"][0] == {"id":"item1", "file":"[01] B.png"}
    assert new_chapters[1]["files"][1] == {"id":"item3", "file":"[3] file.jpg"}
    assert new_chapters[2]["include"] is False
    assert new_chapters[2]["title"] == "Final"
    assert len(new_chapters[2]["files"]) == 3
    assert new_chapters[2]["files"][0] == {"id":"item2", "file":"[02] Z.png"}
    assert new_chapters[2]["files"][1] == {"id":"item4", "file":"[4] E.jpg"}
    assert new_chapters[2]["files"][2] == {"id":"item5", "file":"[5] D.jpg"}

def test_get_chapters_string():
    """
    Tests the get_chapters_string.
    """
    # Test getting the string from default chapter information
    multiple_dir = abspath(join(mm_test.EPUB_INTERNAL_DIRECTORY, "multiple"))
    chapters = mm_epub.get_default_chapters(multiple_dir)
    chapters_string = mm_epub.get_chapters_string(chapters)
    compare = "ENTRY     TITLE      FILES           "
    compare = f"{compare}\n-------------------------------------"
    compare = f"{compare}\n001       Part 1     [AA] Part 1.TXT "
    compare = f"{compare}\n002       Image 1    [BB] Image 1.PNG"
    compare = f"{compare}\n003       Part 2     [CC] Part 2.htm "
    compare = f"{compare}\n004       Image 2    [DD] Image 2.jpg"
    assert chapters_string == compare
    # Test getting chapter string with modified chapter titles
    chapters[0]["title"] = "Intro"
    chapters[1]["title"] = "Cover"
    chapters[2]["title"] = "Story"
    chapters[3]["title"] = "Epilogue"
    chapters_string = mm_epub.get_chapters_string(chapters)
    compare = "ENTRY     TITLE       FILES           "
    compare = f"{compare}\n--------------------------------------"
    compare = f"{compare}\n001       Intro       [AA] Part 1.TXT "
    compare = f"{compare}\n002       Cover       [BB] Image 1.PNG"
    compare = f"{compare}\n003       Story       [CC] Part 2.htm "
    compare = f"{compare}\n004       Epilogue    [DD] Image 2.jpg"
    assert chapters_string == compare
    # Test getting chapter string when not all chapters are included
    chapters[1]["include"] = False
    chapters[2]["include"] = False
    chapters_string = mm_epub.get_chapters_string(chapters)
    compare = "ENTRY     TITLE       FILES           "
    compare = f"{compare}\n--------------------------------------"
    compare = f"{compare}\n001       Intro       [AA] Part 1.TXT "
    compare = f"{compare}\n002*      Cover       [BB] Image 1.PNG"
    compare = f"{compare}\n003*      Story       [CC] Part 2.htm "
    compare = f"{compare}\n004       Epilogue    [DD] Image 2.jpg"
    assert chapters_string == compare
    # Test getting chapter string if some of the chapters are grouped
    chapters = mm_epub.get_default_chapters(multiple_dir)
    chapters = mm_epub.group_chapters(chapters, [0,1])
    chapters = mm_epub.group_chapters(chapters, [1,2])
    chapters[1]["include"] = False
    chapters_string = mm_epub.get_chapters_string(chapters)
    print(chapters_string)
    compare = "ENTRY     TITLE     FILES                            "
    compare = f"{compare}\n-----------------------------------------------------"
    compare = f"{compare}\n001       Part 1    [AA] Part 1.TXT, [BB] Image 1.PNG"
    compare = f"{compare}\n002*      Part 2    [CC] Part 2.htm, [DD] Image 2.jpg"
    assert chapters_string == compare

def test_create_content_files():
    """
    Tests the create_content_files function.
    """
    # Test updating chapters and creating content files
    multiple_dir = abspath(join(mm_test.EPUB_INTERNAL_DIRECTORY, "multiple"))
    chapters = mm_epub.get_default_chapters(multiple_dir)
    with tempfile.TemporaryDirectory() as temp_dir:
        chapters[1]["title"] = "Vertical"
        chapters[2]["title"] = "Chapter 2"
        chapters = mm_epub.create_content_files(chapters, temp_dir)
        assert len(chapters) == 4
        assert chapters[0]["include"]
        assert chapters[0]["id"] == "item0"
        assert chapters[0]["title"] == "Part 1"
        assert chapters[1]["title"] == "Vertical"
        assert chapters[2]["title"] == "Chapter 2"
        assert chapters[3]["title"] == "Image 2"
        assert chapters[0]["file"] == "content/[AA] Part 1.xhtml"
        assert chapters[1]["file"] == "content/[BB] Image 1.xhtml"
        assert chapters[2]["file"] == "content/[CC] Part 2.xhtml"
        assert chapters[3]["file"] == "content/[DD] Image 2.xhtml"
        # Test that the files were created
        assert sorted(os.listdir(temp_dir)) == ["content", "images"]
        image_dir = abspath(join(temp_dir, "images"))
        assert sorted(os.listdir(image_dir)) == ["image1.PNG", "image2.jpg"]
        content_dir = abspath(join(temp_dir, "content"))
        files = sorted(os.listdir(content_dir))
        assert len(files) == 4
        assert  files[0] == "[AA] Part 1.xhtml"
        assert  files[1] == "[BB] Image 1.xhtml"
        assert  files[2] == "[CC] Part 2.xhtml"
        assert  files[3] == "[DD] Image 2.xhtml"
        # Test the XHTML generated from plain text
        contents = mm_file_tools.read_text_file(abspath(join(content_dir, "[AA] Part 1.xhtml")))
        compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
        compare = f"{compare}\n    <head>"
        compare = f"{compare}\n        <title>Part 1</title>"
        compare = f"{compare}\n        <meta charset=\"utf-8\" />"
        compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
        compare = f"{compare}\n    </head>"
        compare = f"{compare}\n    <body>"
        compare = f"{compare}\n        <p>This is line 1.</p>"
        compare = f"{compare}\n        <p>&amp; This is line 2!</p>"
        compare = f"{compare}\n    </body>"
        compare = f"{compare}\n</html>"
        assert contents == compare
        # Test the XHTML generated from HTML
        contents = mm_file_tools.read_text_file(abspath(join(content_dir, "[CC] Part 2.xhtml")))
        compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
        compare = f"{compare}\n    <head>"
        compare = f"{compare}\n        <title>Chapter 2</title>"
        compare = f"{compare}\n        <meta charset=\"utf-8\" />"
        compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
        compare = f"{compare}\n    </head>"
        compare = f"{compare}\n    <body>"
        compare = f"{compare}\n        <p>This is paragraph 1</p>"
        compare = f"{compare}\n        <p>&amp; this is paragraph 2!</p>"
        compare = f"{compare}\n    </body>"
        compare = f"{compare}\n</html>"
        assert contents == compare
        # Test the XHTML generated from images
        contents = mm_file_tools.read_text_file(abspath(join(content_dir, "[BB] Image 1.xhtml")))
        compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<html xmlns:svgns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns=\"http://www.w3.org/1999/xhtml\">"
        compare = f"{compare}\n    <head>"
        compare = f"{compare}\n        <title>Vertical</title>"
        compare = f"{compare}\n        <meta charset=\"utf-8\" />"
        compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
        compare = f"{compare}\n    </head>"
        compare = f"{compare}\n    <body>"
        compare = f"{compare}\n        <div id=\"full-image-container\">"
        compare = f"{compare}\n            <svgns:svg width=\"100%\" height=\"100%\" viewBox=\"0 0 20 100\" preserveAspectRatio=\"xMidYMid meet\" version=\"1.1\">"
        compare = f"{compare}\n                <svgns:title>Vertical</svgns:title>"
        compare = f"{compare}\n                <svgns:image xlink:href=\"../images/image1.PNG\" width=\"20\" height=\"100\" />"
        compare = f"{compare}\n            </svgns:svg>"
        compare = f"{compare}\n        </div>"
        compare = f"{compare}\n    </body>"
        compare = f"{compare}\n</html>"
        assert contents == compare
        contents = mm_file_tools.read_text_file(abspath(join(content_dir, "[DD] Image 2.xhtml")))
        compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<html xmlns:svgns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns=\"http://www.w3.org/1999/xhtml\">"
        compare = f"{compare}\n    <head>"
        compare = f"{compare}\n        <title>Image 2</title>"
        compare = f"{compare}\n        <meta charset=\"utf-8\" />"
        compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
        compare = f"{compare}\n    </head>"
        compare = f"{compare}\n    <body>"
        compare = f"{compare}\n        <div id=\"full-image-container\">"
        compare = f"{compare}\n            <svgns:svg width=\"100%\" height=\"100%\" viewBox=\"0 0 200 30\" preserveAspectRatio=\"xMidYMid meet\" version=\"1.1\">"
        compare = f"{compare}\n                <svgns:title>Image 2</svgns:title>"
        compare = f"{compare}\n                <svgns:image xlink:href=\"../images/image2.jpg\" width=\"200\" height=\"30\" />"
        compare = f"{compare}\n            </svgns:svg>"
        compare = f"{compare}\n        </div>"
        compare = f"{compare}\n    </body>"
        compare = f"{compare}\n</html>"
        assert contents == compare
    # Test creating content files while chapters are grouped
    multiple_dir = abspath(join(mm_test.EPUB_INTERNAL_DIRECTORY, "multiple"))
    chapters = mm_epub.get_default_chapters(multiple_dir)
    chapters = mm_epub.group_chapters(chapters, [0,1,2,3])
    with tempfile.TemporaryDirectory() as temp_dir:
        chapters[0]["title"] = "Grouped"
        chapters = mm_epub.create_content_files(chapters, temp_dir)
        assert len(chapters) == 1
        assert chapters[0]["include"]
        assert chapters[0]["id"] == "item0"
        assert chapters[0]["title"] == "Grouped"
        assert chapters[0]["file"] == "content/[AA] Part 1.xhtml"
        # Test that the files were created
        assert sorted(os.listdir(temp_dir)) == ["content", "images"]
        image_dir = abspath(join(temp_dir, "images"))
        assert sorted(os.listdir(image_dir)) == ["image1.PNG", "image2.jpg"]
        content_dir = abspath(join(temp_dir, "content"))
        assert os.listdir(content_dir) == ["[AA] Part 1.xhtml"]
        # Test the XHTML from combined sources
        contents = mm_file_tools.read_text_file(abspath(join(content_dir, "[AA] Part 1.xhtml")))
        compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
        compare = f"{compare}\n    <head>"
        compare = f"{compare}\n        <title>Grouped</title>"
        compare = f"{compare}\n        <meta charset=\"utf-8\" />"
        compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
        compare = f"{compare}\n    </head>"
        compare = f"{compare}\n    <body>"
        compare = f"{compare}\n        <p>This is line 1.</p>"
        compare = f"{compare}\n        <p>&amp; This is line 2!</p>"
        compare = f"{compare}\n        <div>"
        compare = f"{compare}\n            <img src=\"../images/image1.PNG\" alt=\"Image 1\" width=\"20\" height=\"100\" />"
        compare = f"{compare}\n        </div>"
        compare = f"{compare}\n        <p>This is paragraph 1</p>"
        compare = f"{compare}\n        <p>&amp; this is paragraph 2!</p>"
        compare = f"{compare}\n        <div>"
        compare = f"{compare}\n            <img src=\"../images/image2.jpg\" alt=\"Image 2\" width=\"200\" height=\"30\" />"
        compare = f"{compare}\n        </div>"
        compare = f"{compare}\n    </body>"
        compare = f"{compare}\n</html>"
        assert contents == compare

def test_copy_original_files():
    """
    Tests the copy_original_files function.
    """
    # Test copying all files from a directory to the given directory, including subdirectories
    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = abspath(join(mm_test.EPUB_INTERNAL_DIRECTORY, "multiple"))
        mm_epub.copy_original_files(base_dir, temp_dir)
        assert os.listdir(temp_dir) == ["original"]
        original_dir = abspath(join(temp_dir, "original"))
        files = sorted(os.listdir(original_dir))
        assert len(files) == 10
        assert files[0] == ".test"
        assert files[1] == "[AA] Part 1.TXT"
        assert files[2] == "[AA] Part 1.json"
        assert files[3] == "[BB] Image 1.PNG"
        assert files[4] == "[BB] Image 1.json"
        assert files[5] == "[CC] Part 2.htm"
        assert files[6] == "[CC] Part 2.json"
        assert files[7] == "[DD] Image 2.jpg"
        assert files[8] == "[DD] Image 2.json"
        assert files[9] == "ignore"
        assert os.listdir(abspath(join(original_dir, "ignore"))) == ["sub.txt"]
    # Test copying all files from a designated directory labeled as "original"
    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = abspath(join(mm_test.EPUB_INTERNAL_DIRECTORY, "simple"))
        mm_epub.copy_original_files(base_dir, temp_dir)
        assert os.listdir(temp_dir) == ["original"]
        assert os.listdir(abspath(join(temp_dir, "original"))) == ["Original.pdf"]
    
def test_create_style_file():
    """
    Tests the create_style_file function.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        mm_epub.create_style_file(temp_dir)
        assert os.listdir(temp_dir) == ["style"]
        sub_dir = abspath(join(temp_dir, "style"))
        assert os.listdir(sub_dir) == ["epubstyle.css"]
        style_file = abspath(join(sub_dir, "epubstyle.css"))
        style = mm_file_tools.read_text_file(style_file)
        compare = ""
        compare = f"{compare}img "+ "{"
        compare = f"{compare}\n    display: block;"
        compare = f"{compare}\n    max-width: 100%;"
        compare = f"{compare}\n    max-height: 100%;"
        compare = f"{compare}\n    text-align: center;"
        compare = f"{compare}\n    margin-left: auto;"
        compare = f"{compare}\n    margin-right: auto;"
        compare = f"{compare}\n}}\n\n"
        compare = f"{compare}#full-image-container " + "{"
        compare = f"{compare}\n    width: 100%;"
        compare = f"{compare}\n    height: 100%;"
        compare = f"{compare}\n    margin: 0;"
        compare = f"{compare}\n    padding: 0;"
        compare = f"{compare}\n    page-break-after: always;"
        compare = f"{compare}\n}}\n\n"
        compare = f"{compare}center " + "{"
        compare = f"{compare}\n    text-align: center;"
        compare = f"{compare}\n" + "}"
        assert style == compare

def test_create_nav_file():
    """
    Test the create_nav_file function.
    """
    # Test Creating a nav file
    multiple_dir = abspath(join(mm_test.EPUB_INTERNAL_DIRECTORY, "multiple"))
    chapters = mm_epub.get_default_chapters(multiple_dir)
    with tempfile.TemporaryDirectory() as temp_dir:
        chapters = mm_epub.create_content_files(chapters, temp_dir)
        mm_epub.create_nav_file(chapters, "Title!", temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["content", "images", "nav.xhtml"]
        nav_file = abspath(join(temp_dir, "nav.xhtml"))
        contents = mm_file_tools.read_text_file(nav_file)
        compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:epub=\"http://www.idpf.org/2007/ops\" lang=\"en\" xml:lang=\"en\">"
        compare = f"{compare}\n    <head>"
        compare = f"{compare}\n        <title>Title!</title>"
        compare = f"{compare}\n    </head>"
        compare = f"{compare}\n    <body>"
        compare = f"{compare}\n        <nav epub:type=\"toc\" id=\"id\" role=\"doc-toc\">"
        compare = f"{compare}\n            <h2>Title!</h2>"
        compare = f"{compare}\n            <ol>"
        compare = f"{compare}\n                <il>"
        compare = f"{compare}\n                    <a href=\"content/[AA] Part 1.xhtml\">Part 1</a>"
        compare = f"{compare}\n                </il>"
        compare = f"{compare}\n                <il>"
        compare = f"{compare}\n                    <a href=\"content/[BB] Image 1.xhtml\">Image 1</a>"
        compare = f"{compare}\n                </il>"
        compare = f"{compare}\n                <il>"
        compare = f"{compare}\n                    <a href=\"content/[CC] Part 2.xhtml\">Part 2</a>"
        compare = f"{compare}\n                </il>"
        compare = f"{compare}\n                <il>"
        compare = f"{compare}\n                    <a href=\"content/[DD] Image 2.xhtml\">Image 2</a>"
        compare = f"{compare}\n                </il>"
        compare = f"{compare}\n            </ol>"
        compare = f"{compare}\n        </nav>"
        compare = f"{compare}\n    </body>"
        compare = f"{compare}\n</html>"
        assert contents == compare
    # Test if not all chapters are listed as included
    chapters = mm_epub.get_default_chapters(multiple_dir)
    with tempfile.TemporaryDirectory() as temp_dir:
        chapters = mm_epub.create_content_files(chapters, temp_dir)
        chapters[0]["title"] = "Start"
        chapters[1]["include"] = False
        chapters[2]["include"] = False
        mm_epub.create_nav_file(chapters, "Grouped", temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["content", "images", "nav.xhtml"]
        nav_file = abspath(join(temp_dir, "nav.xhtml"))
        contents = mm_file_tools.read_text_file(nav_file)
        compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:epub=\"http://www.idpf.org/2007/ops\" lang=\"en\" xml:lang=\"en\">"
        compare = f"{compare}\n    <head>"
        compare = f"{compare}\n        <title>Grouped</title>"
        compare = f"{compare}\n    </head>"
        compare = f"{compare}\n    <body>"
        compare = f"{compare}\n        <nav epub:type=\"toc\" id=\"id\" role=\"doc-toc\">"
        compare = f"{compare}\n            <h2>Grouped</h2>"
        compare = f"{compare}\n            <ol>"
        compare = f"{compare}\n                <il>"
        compare = f"{compare}\n                    <a href=\"content/[AA] Part 1.xhtml\">Start</a>"
        compare = f"{compare}\n                </il>"
        compare = f"{compare}\n                <il>"
        compare = f"{compare}\n                    <a href=\"content/[DD] Image 2.xhtml\">Image 2</a>"
        compare = f"{compare}\n                </il>"
        compare = f"{compare}\n            </ol>"
        compare = f"{compare}\n        </nav>"
        compare = f"{compare}\n    </body>"
        compare = f"{compare}\n</html>"
        assert contents == compare

def test_create_ncx_file():
    """
    Tests the create_ncx_file function.
    """
    # Test Creating a nav file
    multiple_dir = abspath(join(mm_test.EPUB_INTERNAL_DIRECTORY, "multiple"))
    chapters = mm_epub.get_default_chapters(multiple_dir)
    with tempfile.TemporaryDirectory() as temp_dir:
        chapters = mm_epub.create_content_files(chapters, temp_dir)
        mm_epub.create_ncx_file(chapters, "Title!", "/page/url/", temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["content", "images", "toc.ncx"]
        ncx_file = abspath(join(temp_dir, "toc.ncx"))
        contents = mm_file_tools.read_text_file(ncx_file)
        compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<ncx xmlns=\"http://www.daisy.org/z3986/2005/ncx/\" version=\"2005-1\">"
        compare = f"{compare}\n    <head>"
        compare = f"{compare}\n        <meta name=\"dtb:uid\" content=\"/page/url/\" />"
        compare = f"{compare}\n        <meta name=\"dtb:depth\" content=\"1\" />"
        compare = f"{compare}\n        <meta name=\"dtb:totalPageCount\" content=\"0\" />"
        compare = f"{compare}\n        <meta name=\"dtb:maxPageNumber\" content=\"0\" />"
        compare = f"{compare}\n    </head>"
        compare = f"{compare}\n    <docTitle>"
        compare = f"{compare}\n        <text>Title!</text>"
        compare = f"{compare}\n    </docTitle>"
        compare = f"{compare}\n    <navMap>"
        compare = f"{compare}\n        <navPoint id=\"item0\">"
        compare = f"{compare}\n            <navLabel>"
        compare = f"{compare}\n                <text>Part 1</text>"
        compare = f"{compare}\n            </navLabel>"
        compare = f"{compare}\n            <content src=\"content/[AA] Part 1.xhtml\" />"
        compare = f"{compare}\n        </navPoint>"
        compare = f"{compare}\n        <navPoint id=\"item1\">"
        compare = f"{compare}\n            <navLabel>"
        compare = f"{compare}\n                <text>Image 1</text>"
        compare = f"{compare}\n            </navLabel>"
        compare = f"{compare}\n            <content src=\"content/[BB] Image 1.xhtml\" />"
        compare = f"{compare}\n        </navPoint>"
        compare = f"{compare}\n        <navPoint id=\"item2\">"
        compare = f"{compare}\n            <navLabel>"
        compare = f"{compare}\n                <text>Part 2</text>"
        compare = f"{compare}\n            </navLabel>"
        compare = f"{compare}\n            <content src=\"content/[CC] Part 2.xhtml\" />"
        compare = f"{compare}\n        </navPoint>"
        compare = f"{compare}\n        <navPoint id=\"item3\">"
        compare = f"{compare}\n            <navLabel>"
        compare = f"{compare}\n                <text>Image 2</text>"
        compare = f"{compare}\n            </navLabel>"
        compare = f"{compare}\n            <content src=\"content/[DD] Image 2.xhtml\" />"
        compare = f"{compare}\n        </navPoint>"
        compare = f"{compare}\n    </navMap>"
        compare = f"{compare}\n</ncx>"
        assert contents == compare
    # Test if not all chapters are listed as included
    chapters = mm_epub.get_default_chapters(multiple_dir)
    with tempfile.TemporaryDirectory() as temp_dir:
        chapters = mm_epub.create_content_files(chapters, temp_dir)
        chapters[0]["title"] = "Start"
        chapters[1]["include"] = False
        chapters[2]["include"] = False
        mm_epub.create_ncx_file(chapters, "Group", "/other/", temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["content", "images", "toc.ncx"]
        ncx_file = abspath(join(temp_dir, "toc.ncx"))
        contents = mm_file_tools.read_text_file(ncx_file)
        compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<ncx xmlns=\"http://www.daisy.org/z3986/2005/ncx/\" version=\"2005-1\">"
        compare = f"{compare}\n    <head>"
        compare = f"{compare}\n        <meta name=\"dtb:uid\" content=\"/other/\" />"
        compare = f"{compare}\n        <meta name=\"dtb:depth\" content=\"1\" />"
        compare = f"{compare}\n        <meta name=\"dtb:totalPageCount\" content=\"0\" />"
        compare = f"{compare}\n        <meta name=\"dtb:maxPageNumber\" content=\"0\" />"
        compare = f"{compare}\n    </head>"
        compare = f"{compare}\n    <docTitle>"
        compare = f"{compare}\n        <text>Group</text>"
        compare = f"{compare}\n    </docTitle>"
        compare = f"{compare}\n    <navMap>"
        compare = f"{compare}\n        <navPoint id=\"item0\">"
        compare = f"{compare}\n            <navLabel>"
        compare = f"{compare}\n                <text>Start</text>"
        compare = f"{compare}\n            </navLabel>"
        compare = f"{compare}\n            <content src=\"content/[AA] Part 1.xhtml\" />"
        compare = f"{compare}\n        </navPoint>"
        compare = f"{compare}\n        <navPoint id=\"item3\">"
        compare = f"{compare}\n            <navLabel>"
        compare = f"{compare}\n                <text>Image 2</text>"
        compare = f"{compare}\n            </navLabel>"
        compare = f"{compare}\n            <content src=\"content/[DD] Image 2.xhtml\" />"
        compare = f"{compare}\n        </navPoint>"
        compare = f"{compare}\n    </navMap>"
        compare = f"{compare}\n</ncx>"
        assert contents == compare

def test_get_metadata_xml():
    """
    Tests the get_metadata_xml function.
    """
    # Test title metadata
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "This's a title!\\'"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">This's a title!\\'</dc:identifier>"
    compare = f"{compare}\n    <dc:date>0000-00-00T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>This's a title!\\'</dc:title>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test url metadata
    metadata["title"] = None
    metadata["url"] = "this/is/a/test"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
    compare = f"{compare}\n    <dc:date>0000-00-00T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title />"
    compare = f"{compare}\n    <dc:source>this/is/a/test</dc:source>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test date metadata
    metadata["title"] = "Title."
    metadata["date"] = "2023-01-15"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:source>this/is/a/test</dc:source>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test description metadata
    metadata["description"] = "This & That"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:source>this/is/a/test</dc:source>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test writer metadata
    metadata["writers"] = ["Person!"]
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:source>this/is/a/test</dc:source>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:creator id=\"author-0\">Person!</dc:creator>"
    compare = f"{compare}\n    <meta refines=\"author-0\" property=\"role\" scheme=\"marc:relators\">aut</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    metadata["url"] = None
    metadata["writers"] = ["Multiple", "People"]
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:creator id=\"author-0\">Multiple</dc:creator>"
    compare = f"{compare}\n    <meta refines=\"author-0\" property=\"role\" scheme=\"marc:relators\">aut</meta>"
    compare = f"{compare}\n    <dc:creator id=\"author-1\">People</dc:creator>"
    compare = f"{compare}\n    <meta refines=\"author-1\" property=\"role\" scheme=\"marc:relators\">aut</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test cover artist metadata
    metadata["writers"] = None
    metadata["cover_artists"] = ["Guest"]
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:creator id=\"cover-artist-0\">Guest</dc:creator>"
    compare = f"{compare}\n    <meta refines=\"cover-artist-0\" property=\"role\" scheme=\"marc:relators\">cov</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    metadata["writer"] = None
    metadata["cover_artists"] = ["Other", "Folks"]
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:creator id=\"cover-artist-0\">Other</dc:creator>"
    compare = f"{compare}\n    <meta refines=\"cover-artist-0\" property=\"role\" scheme=\"marc:relators\">cov</meta>"
    compare = f"{compare}\n    <dc:creator id=\"cover-artist-1\">Folks</dc:creator>"
    compare = f"{compare}\n    <meta refines=\"cover-artist-1\" property=\"role\" scheme=\"marc:relators\">cov</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test illustrator metadata
    metadata["cover_artists"] = None
    metadata["artists"] = ["New Person"]
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:creator id=\"illustrator-0\">New Person</dc:creator>"
    compare = f"{compare}\n    <meta refines=\"illustrator-0\" property=\"role\" scheme=\"marc:relators\">ill</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    metadata["artists"] = ["Other", "Name"]
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:creator id=\"illustrator-0\">Other</dc:creator>"
    compare = f"{compare}\n    <meta refines=\"illustrator-0\" property=\"role\" scheme=\"marc:relators\">ill</meta>"
    compare = f"{compare}\n    <dc:creator id=\"illustrator-1\">Name</dc:creator>"
    compare = f"{compare}\n    <meta refines=\"illustrator-1\" property=\"role\" scheme=\"marc:relators\">ill</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test publisher metadata
    metadata["artists"] = None
    metadata["publisher"] = "Company"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:publisher>Company</dc:publisher>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test series metadata
    metadata["series"] = "Name!!"
    metadata["series_number"] = "2.5"
    metadata["series_total"] = "5"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:publisher>Company</dc:publisher>"
    compare = f"{compare}\n    <meta property=\"belongs-to-collection\" id=\"series-title\">Name!!</meta>"
    compare = f"{compare}\n    <meta refines=\"series-title\" property=\"collection-type\">series</meta>"
    compare = f"{compare}\n    <meta refines=\"series-title\" property=\"group-position\">2.5</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test series metadata with invalid series number
    metadata["series_number"] = "NotNumber"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:publisher>Company</dc:publisher>"
    compare = f"{compare}\n    <meta property=\"belongs-to-collection\" id=\"series-title\">Name!!</meta>"
    compare = f"{compare}\n    <meta refines=\"series-title\" property=\"collection-type\">series</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test metadata tags
    metadata["series"] = None
    metadata["series_number"] = None
    metadata["tags"] = ["Some", "Tags", "&", "stuff"]
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:publisher>Company</dc:publisher>"
    compare = f"{compare}\n    <dc:subject>Some</dc:subject>"
    compare = f"{compare}\n    <dc:subject>Tags</dc:subject>"
    compare = f"{compare}\n    <dc:subject>&amp;</dc:subject>"
    compare = f"{compare}\n    <dc:subject>stuff</dc:subject>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test metadata age rating
    metadata["tags"] = None
    metadata["age_rating"] = "Everyone"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:publisher>Company</dc:publisher>"
    compare = f"{compare}\n    <meta property=\"dcterms:audience\">Everyone</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test metadata score w/ star tags
    metadata["score"] = "0"
    metadata["age_rating"] = None
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:publisher>Company</dc:publisher>"
    compare = f"{compare}\n    <meta property=\"calibre:rating\">0.0</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    metadata["score"] = "5"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:publisher>Company</dc:publisher>"
    compare = f"{compare}\n    <dc:subject>&#9733;&#9733;&#9733;&#9733;&#9733;</dc:subject>"
    compare = f"{compare}\n    <meta property=\"calibre:rating\">10.0</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    metadata["score"] = "3"
    metadata["tags"] = ["Some", "tags"]
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:publisher>Company</dc:publisher>"
    compare = f"{compare}\n    <dc:subject>&#9733;&#9733;&#9733;</dc:subject>"
    compare = f"{compare}\n    <dc:subject>Some</dc:subject>"
    compare = f"{compare}\n    <dc:subject>tags</dc:subject>"
    compare = f"{compare}\n    <meta property=\"calibre:rating\">6.0</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test metadata score if the score is invalid
    metadata["tags"] = []
    metadata["score"] = "Not Number"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:publisher>Company</dc:publisher>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    metadata["score"] = "6"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:publisher>Company</dc:publisher>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    metadata["score"] = "-2"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:publisher>Company</dc:publisher>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test adding metadata for a cover image
    xml = mm_epub.get_metadata_xml(metadata, "image1")
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:publisher>Company</dc:publisher>"
    compare = f"{compare}\n    <meta name=\"cover\" content=\"image1\" />"
    compare = f"{compare}\n</metadata>"
    assert xml == compare

def test_get_manifest_xml():
    """
    Tests the get_manifest_xml function.
    """
    # Test creating a manifest xml section
    multiple_dir = abspath(join(mm_test.EPUB_INTERNAL_DIRECTORY, "multiple"))
    chapters = mm_epub.get_default_chapters(multiple_dir)
    with tempfile.TemporaryDirectory() as temp_dir:
        chapters = mm_epub.create_content_files(chapters, temp_dir)
        xml = mm_epub.get_manifest_xml(chapters, temp_dir)
        compare = "<manifest>"
        compare = f"{compare}\n    <item href=\"content/[AA] Part 1.xhtml\" id=\"item0\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n    <item href=\"content/[BB] Image 1.xhtml\" id=\"item1\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n    <item href=\"content/[CC] Part 2.xhtml\" id=\"item2\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n    <item href=\"content/[DD] Image 2.xhtml\" id=\"item3\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n    <item href=\"images/image1.PNG\" id=\"image1\" media-type=\"image/png\" />"
        compare = f"{compare}\n    <item href=\"images/image2.jpg\" id=\"image2\" media-type=\"image/jpeg\" />"
        compare = f"{compare}\n    <item href=\"style/epubstyle.css\" id=\"epubstyle\" media-type=\"text/css\" />"
        compare = f"{compare}\n    <item href=\"nav.xhtml\" id=\"nav\" media-type=\"application/xhtml+xml\" properties=\"nav\" />"
        compare = f"{compare}\n    <item href=\"toc.ncx\" id=\"ncx\" media-type=\"application/x-dtbncx+xml\" />"
        compare = f"{compare}\n</manifest>"
        assert xml == compare

def test_create_content_opf():
    """
    Tests the create_content_opf function.
    """
    # Test creating an opf file
    multiple_dir = abspath(join(mm_test.EPUB_INTERNAL_DIRECTORY, "multiple"))
    chapters = mm_epub.get_default_chapters(multiple_dir)
    with tempfile.TemporaryDirectory() as temp_dir:
        chapters = mm_epub.create_content_files(chapters, temp_dir)
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "Thing!"
        mm_epub.create_content_opf(chapters, metadata, temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["content", "content.opf", "images"]
        opf_file = abspath(join(temp_dir, "content.opf"))
        contents = mm_file_tools.read_text_file(opf_file)
        compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<package xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns=\"http://www.idpf.org/2007/opf\" unique-identifier=\"id\" version=\"3.0\" prefix=\"http://www.idpf.org/vocab/rendition/#\">"
        compare = f"{compare}\n    <metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
        compare = f"{compare}\n        <dc:language>en</dc:language>"
        compare = f"{compare}\n        <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
        compare = f"{compare}\n        <dc:identifier id=\"id\">Thing!</dc:identifier>"
        compare = f"{compare}\n        <dc:date>0000-00-00T00:00:00+00:00</dc:date>"
        compare = f"{compare}\n        <dc:title>Thing!</dc:title>"
        compare = f"{compare}\n        <meta name=\"cover\" content=\"image1\" />"
        compare = f"{compare}\n    </metadata>"
        compare = f"{compare}\n    <manifest>"
        compare = f"{compare}\n        <item href=\"content/[AA] Part 1.xhtml\" id=\"item0\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n        <item href=\"content/[BB] Image 1.xhtml\" id=\"item1\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n        <item href=\"content/[CC] Part 2.xhtml\" id=\"item2\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n        <item href=\"content/[DD] Image 2.xhtml\" id=\"item3\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n        <item href=\"images/image1.PNG\" id=\"image1\" media-type=\"image/png\" />"
        compare = f"{compare}\n        <item href=\"images/image2.jpg\" id=\"image2\" media-type=\"image/jpeg\" />"
        compare = f"{compare}\n        <item href=\"style/epubstyle.css\" id=\"epubstyle\" media-type=\"text/css\" />"
        compare = f"{compare}\n        <item href=\"nav.xhtml\" id=\"nav\" media-type=\"application/xhtml+xml\" properties=\"nav\" />"
        compare = f"{compare}\n        <item href=\"toc.ncx\" id=\"ncx\" media-type=\"application/x-dtbncx+xml\" />"
        compare = f"{compare}\n    </manifest>"
        compare = f"{compare}\n    <spine toc=\"ncx\">"
        compare = f"{compare}\n        <itemref idref=\"item0\" />"
        compare = f"{compare}\n        <itemref idref=\"item1\" />"
        compare = f"{compare}\n        <itemref idref=\"item2\" />"
        compare = f"{compare}\n        <itemref idref=\"item3\" />"
        compare = f"{compare}\n    </spine>"
        compare = f"{compare}\n</package>"
        assert contents == compare

def test_create_epub():
    """
    Tests the create_epub function.
    """
    # Create an EPUB file
    multiple_dir = abspath(join(mm_test.EPUB_INTERNAL_DIRECTORY, "multiple"))
    with tempfile.TemporaryDirectory() as temp_dir:
        copy_dir = abspath(join(temp_dir, "copy"))
        shutil.copytree(multiple_dir, copy_dir)
        chapters = mm_epub.get_default_chapters(copy_dir)
        chapters = mm_epub.group_chapters(chapters, [2,3])
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "Generated"
        epub_file = mm_epub.create_epub(chapters, metadata, copy_dir)
        assert exists(epub_file)
        assert basename(epub_file) == "Generated.epub"
        assert abspath(join(epub_file, os.pardir)) == abspath(copy_dir)
        # Extract the epub file to see contents
        extract_dir = abspath(join(temp_dir, "extracted"))
        os.mkdir(extract_dir)
        assert mm_file_tools.extract_zip(epub_file, extract_dir)
        assert sorted(os.listdir(extract_dir)) == ["EPUB", "META-INF", "mimetype"]
        # Check the mimetype contents
        assert mm_file_tools.read_text_file(abspath(join(extract_dir, "mimetype"))) == "application/epub+zip"
        # Check the contents of the meta folder
        meta_directory = abspath(join(extract_dir, "META-INF"))
        assert sorted(os.listdir(meta_directory)) == ["container.xml"]
        container = mm_file_tools.read_text_file(abspath(join(meta_directory, "container.xml")))
        compare = ""
        compare = f"{compare}<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<container xmlns=\"urn:oasis:names:tc:opendocument:xmlns:container\" version=\"1.0\">"
        compare = f"{compare}\n    <rootfiles>"
        compare = f"{compare}\n        <rootfile media-type=\"application/oebps-package+xml\" full-path=\"EPUB/content.opf\" />"
        compare = f"{compare}\n    </rootfiles>"
        compare = f"{compare}\n</container>"
        assert container == compare
        # Check the contents of the epub folder
        epub_directory = abspath(join(extract_dir, "EPUB"))
        assert sorted(os.listdir(epub_directory)) == ["content", "content.opf", "images", "nav.xhtml", "original", "style", "toc.ncx"]
        # Check the contents of the content folder
        content_directory = abspath(join(epub_directory, "content"))
        assert sorted(os.listdir(content_directory)) == ["[AA] Part 1.xhtml", "[BB] Image 1.xhtml", "[CC] Part 2.xhtml"]
        # Check the contents of the original directory
        original_directory = abspath(join(epub_directory, "original"))
        original_files = sorted(os.listdir(original_directory))
        assert len(original_files) == 9
        assert original_files[0] == "[AA] Part 1.TXT"
        assert original_files[1] == "[AA] Part 1.json"
        assert original_files[2] == "[BB] Image 1.PNG"
        assert original_files[3] == "[BB] Image 1.json"
        assert original_files[4] == "[CC] Part 2.htm"
        assert original_files[5] == "[CC] Part 2.json"
        assert original_files[6] == "[DD] Image 2.jpg"
        assert original_files[7] == "[DD] Image 2.json"
        assert original_files[8] == "ignore"
        # Check the contents of the style directory
        style_directory = abspath(join(epub_directory, "style"))
        assert sorted(os.listdir(style_directory)) == ["epubstyle.css"]
        # Check the contents of the images directory
        style_directory = abspath(join(epub_directory, "images"))
        assert sorted(os.listdir(style_directory)) == ["image1.PNG", "image2.jpg"]
        # Check the contents of the content.opf file
        content = mm_file_tools.read_text_file(abspath(join(epub_directory, "content.opf")))
        compare = ""
        compare = f"{compare}<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<package xmlns:dc=\"http://purl.org/dc/elements/1.1/\" "
        compare = f"{compare}xmlns=\"http://www.idpf.org/2007/opf\" unique-identifier=\"id\" "
        compare = f"{compare}version=\"3.0\" prefix=\"http://www.idpf.org/vocab/rendition/#\">"
        compare = f"{compare}\n    <metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
        compare = f"{compare}\n        <dc:language>en</dc:language>"
        compare = f"{compare}\n        <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
        compare = f"{compare}\n        <dc:identifier id=\"id\">Generated</dc:identifier>"
        compare = f"{compare}\n        <dc:date>0000-00-00T00:00:00+00:00</dc:date>"
        compare = f"{compare}\n        <dc:title>Generated</dc:title>"
        compare = f"{compare}\n        <meta name=\"cover\" content=\"image1\" />"
        compare = f"{compare}\n    </metadata>"
        compare = f"{compare}\n    <manifest>"
        compare = f"{compare}\n        <item href=\"content/[AA] Part 1.xhtml\" id=\"item0\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n        <item href=\"content/[BB] Image 1.xhtml\" id=\"item1\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n        <item href=\"content/[CC] Part 2.xhtml\" id=\"item2\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n        <item href=\"images/image1.PNG\" id=\"image1\" media-type=\"image/png\" />"
        compare = f"{compare}\n        <item href=\"images/image2.jpg\" id=\"image2\" media-type=\"image/jpeg\" />"
        compare = f"{compare}\n        <item href=\"style/epubstyle.css\" id=\"epubstyle\" media-type=\"text/css\" />"
        compare = f"{compare}\n        <item href=\"nav.xhtml\" id=\"nav\" media-type=\"application/xhtml+xml\" properties=\"nav\" />"
        compare = f"{compare}\n        <item href=\"toc.ncx\" id=\"ncx\" media-type=\"application/x-dtbncx+xml\" />"
        compare = f"{compare}\n    </manifest>"
        compare = f"{compare}\n    <spine toc=\"ncx\">"
        compare = f"{compare}\n        <itemref idref=\"item0\" />"
        compare = f"{compare}\n        <itemref idref=\"item1\" />"
        compare = f"{compare}\n        <itemref idref=\"item2\" />"
        compare = f"{compare}\n    </spine>"
        compare = f"{compare}\n</package>"
        assert content == compare

def test_create_epub_from_description():
    """
    Tests the create_epub_from_description function.
    """
    # Create an EPUB file from the description of an image-JSON pair
    config = mm_config.get_config([])
    image_file = abspath(join(mm_test.PAIR_IMAGE_DIRECTORY, "long.JPG"))
    json_file = abspath(join(mm_test.PAIR_IMAGE_DIRECTORY, "long.JSON"))
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Description"
    metadata["writers"] = ["Person"]
    metadata["url"] = "/some/page"
    metadata["description"] = "Not text"
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_file = mm_epub.create_epub_from_description(json_file, image_file, metadata, temp_dir, config)
        assert basename(epub_file) == "Description.epub"
        assert abspath(join(epub_file, os.pardir)) == temp_dir
        assert exists(epub_file)
        # Extract the epub file to see contents
        extract_dir = abspath(join(temp_dir, "extracted"))
        os.mkdir(extract_dir)
        assert mm_file_tools.extract_zip(epub_file, extract_dir)
        assert sorted(os.listdir(extract_dir)) == ["EPUB", "META-INF", "mimetype"]
        # Check the mimetype contents
        assert mm_file_tools.read_text_file(abspath(join(extract_dir, "mimetype"))) == "application/epub+zip"
        # Check the contents of the META-INF directory
        meta_directory = abspath(join(extract_dir, "META-INF"))
        assert sorted(os.listdir(meta_directory)) == ["container.xml"]
        container = mm_file_tools.read_text_file(abspath(join(meta_directory, "container.xml")))
        compare = ""
        compare = f"{compare}<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<container xmlns=\"urn:oasis:names:tc:opendocument:xmlns:container\" version=\"1.0\">"
        compare = f"{compare}\n    <rootfiles>"
        compare = f"{compare}\n        <rootfile media-type=\"application/oebps-package+xml\" full-path=\"EPUB/content.opf\" />"
        compare = f"{compare}\n    </rootfiles>"
        compare = f"{compare}\n</container>"
        assert container == compare
        # Check the contents of the epub directory
        epub_directory = abspath(join(extract_dir, "EPUB"))
        assert sorted(os.listdir(epub_directory)) == ["content", "content.opf", "images", "nav.xhtml", "original", "style", "toc.ncx"]
        # Check the contents of the content folder
        content_directory = abspath(join(epub_directory, "content"))
        assert sorted(os.listdir(content_directory)) == ["back_cover_image.xhtml", "cover_image.xhtml", "long.xhtml"]
        # Check the contents of the original directory
        original_directory = abspath(join(epub_directory, "original"))
        assert sorted(os.listdir(original_directory)) == ["long.JPG", "long.JSON"]
        # Check the contents of the style directory
        style_directory = abspath(join(epub_directory, "style"))
        assert sorted(os.listdir(style_directory)) == ["epubstyle.css"]
        # Check the contents of the images directory
        style_directory = abspath(join(epub_directory, "images"))
        assert sorted(os.listdir(style_directory)) == ["image1.JPG"]
        # Check the contents of the content.opf file
        content = mm_file_tools.read_text_file(abspath(join(epub_directory, "content.opf")))
        compare = ""
        compare = f"{compare}<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<package xmlns:dc=\"http://purl.org/dc/elements/1.1/\" "
        compare = f"{compare}xmlns=\"http://www.idpf.org/2007/opf\" unique-identifier=\"id\" "
        compare = f"{compare}version=\"3.0\" prefix=\"http://www.idpf.org/vocab/rendition/#\">"
        compare = f"{compare}\n    <metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
        compare = f"{compare}\n        <dc:language>en</dc:language>"
        compare = f"{compare}\n        <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
        compare = f"{compare}\n        <dc:identifier id=\"id\">/some/page</dc:identifier>"
        compare = f"{compare}\n        <dc:date>0000-00-00T00:00:00+00:00</dc:date>"
        compare = f"{compare}\n        <dc:title>Description</dc:title>"
        compare = f"{compare}\n        <dc:source>/some/page</dc:source>"
        compare = f"{compare}\n        <dc:description>Not text</dc:description>"
        compare = f"{compare}\n        <dc:creator id=\"author-0\">Person</dc:creator>"
        compare = f"{compare}\n        <meta refines=\"author-0\" property=\"role\" scheme=\"marc:relators\">aut</meta>"
        compare = f"{compare}\n        <meta name=\"cover\" content=\"image1\" />"
        compare = f"{compare}\n    </metadata>"
        compare = f"{compare}\n    <manifest>"
        compare = f"{compare}\n        <item href=\"content/cover_image.xhtml\" id=\"item_cover\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n        <item href=\"content/long.xhtml\" id=\"item_text\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n        <item href=\"content/back_cover_image.xhtml\" id=\"back_cover\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n        <item href=\"images/image1.JPG\" id=\"image1\" media-type=\"image/jpeg\" />"
        compare = f"{compare}\n        <item href=\"style/epubstyle.css\" id=\"epubstyle\" media-type=\"text/css\" />"
        compare = f"{compare}\n        <item href=\"nav.xhtml\" id=\"nav\" media-type=\"application/xhtml+xml\" properties=\"nav\" />"
        compare = f"{compare}\n        <item href=\"toc.ncx\" id=\"ncx\" media-type=\"application/x-dtbncx+xml\" />"
        compare = f"{compare}\n    </manifest>"
        compare = f"{compare}\n    <spine toc=\"ncx\">"
        compare = f"{compare}\n        <itemref idref=\"item_cover\" />"
        compare = f"{compare}\n        <itemref idref=\"item_text\" />"
        compare = f"{compare}\n        <itemref idref=\"back_cover\" />"
        compare = f"{compare}\n    </spine>"
        compare = f"{compare}\n</package>"
        assert content == compare
        # Check the contents of the XHTML generated from the description
        content = mm_file_tools.read_text_file(abspath(join(content_directory, "long.xhtml")))
        compare = ""
        compare = f"{compare}<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
        compare = f"{compare}\n    <head>"
        compare = f"{compare}\n        <title>Description</title>"
        compare = f"{compare}\n        <meta charset=\"utf-8\" />"
        compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
        compare = f"{compare}\n    </head>"
        compare = f"{compare}\n    <body>"
        compare = f"{compare}\n        <p>Lorem ipsum odor amet, consectetuer adipiscing elit. "
        compare = f"{compare}Malesuada magna libero vestibulum habitant lobortis laoreet. Lectus mus fermentum "
        compare = f"{compare}maximus mattis in vel viverra eleifend. Suscipit pulvinar montes aenean, molestie "
        compare = f"{compare}hendrerit neque. Per semper feugiat et velit eu ante fringilla cursus conubia! Ornare "
        compare = f"{compare}fames enim tempus; mattis luctus elit vel suspendisse.</p>"
        compare = f"{compare}\n        <p>Auctor neque tortor dolor lacus mus quisque massa leo. Porta vehicula "
        compare = f"{compare}sagittis cras penatibus tortor litora. Et efficitur leo consequat platea; consectetur "
        compare = f"{compare}ad vel. Hac himenaeos curae cubilia nec tempor. Commodo et eros nam primis sem congue. "
        compare = f"{compare}Tortor suscipit amet platea himenaeos consequat consectetur cras sodales. Mus maximus "
        compare = f"{compare}tempus faucibus commodo tortor eleifend dis. Praesent enim odio nec ornare ante senectus mus.</p>"
        compare = f"{compare}\n        <p>Vivamus lacinia luctus dapibus suspendisse habitasse, felis non at. Rutrum "
        compare = f"{compare}habitasse malesuada vulputate fringilla felis pretium mauris. Potenti vel integer lacus lectus, "
        compare = f"{compare}class conubia senectus. Et nisl feugiat dignissim iaculis ligula amet finibus condimentum "
        compare = f"{compare}conubia. Tempor mauris laoreet est, adipiscing nisi neque commodo curae porta. Cubilia amet "
        compare = f"{compare}vivamus pellentesque fermentum ligula etiam dolor nam. Massa eros metus urna sodales egestas "
        compare = f"{compare}dictum. Sagittis morbi orci viverra eros elementum arcu. Ullamcorper velit hendrerit class "
        compare = f"{compare}class dolor convallis dapibus?</p>"
        compare = f"{compare}\n    </body>"
        compare = f"{compare}\n</html>"
        assert content == compare

def test_get_info_from_epub():
    """
    Tests the get_info_from_epub function.
    """
    # Test getting metadata info from a EPUB file
    epub_file = abspath(join(mm_test.ARCHIVE_EPUB_DIRECTORY, "basic.epub"))
    metadata = mm_epub.get_info_from_epub(epub_file)
    assert metadata["title"] == "Básic EPUB"
    assert metadata["series"] == "Books"
    assert metadata["series_number"] == "0.5"
    assert metadata["series_total"] is None
    assert metadata["description"] == "Simple Description"
    assert metadata["date"] == "2020-01-01"
    assert metadata["writers"] == ["Multiple", "Writers"]
    assert metadata["artists"] == ["Different", "Artists"]
    assert metadata["cover_artists"] == ["Cover", "Artists"]
    assert metadata["publisher"] == "BookCo"
    assert metadata["tags"] == ["This", "&", "That"]
    assert metadata["url"] == "/placeholder/"
    assert metadata["age_rating"] == "Everyone"
    assert metadata["score"] == "4"
    assert metadata["page_count"] == "1"
    assert metadata["cover_id"] is None
    # Test getting metadata from EPUB with higher page count and less metadata
    epub_file = abspath(join(mm_test.ARCHIVE_EPUB_DIRECTORY, "long.EPUB"))
    metadata = mm_epub.get_info_from_epub(epub_file)
    assert metadata["title"] == "Long Book"
    assert metadata["series"] is None
    assert metadata["series_number"] is None
    assert metadata["series_total"] is None
    assert metadata["description"].startswith("Lorem ipsum odor amet, consectetuer adipiscing")
    assert metadata["date"] == "2012-01-20"
    assert metadata["writers"] == ["Author"]
    assert metadata["artists"] == ["Single Artist"]
    assert metadata["cover_artists"] == ["Cover"]
    assert metadata["publisher"] is None
    assert metadata["tags"] == ["One Tag"]
    assert metadata["url"] is None
    assert metadata["age_rating"] == "Unknown"
    assert metadata["score"] is None
    assert metadata["page_count"] == "3"
    assert metadata["cover_id"] == "image1"
    # Test getting metadata from EPUB with no title
    epub_file = abspath(join(mm_test.ARCHIVE_EPUB_DIRECTORY, "small.epub"))
    metadata = mm_epub.get_info_from_epub(epub_file)
    assert metadata["title"] is None
    assert metadata["series"] is None
    assert metadata["series_number"] is None
    assert metadata["series_total"] is None
    assert metadata["description"] == "Small Cover"
    assert metadata["date"] is None
    assert metadata["writers"] == ["Writer"]
    assert metadata["artists"] is None
    assert metadata["cover_artists"] is None
    assert metadata["publisher"] is None
    assert metadata["tags"] is None
    assert metadata["url"] is None
    assert metadata["age_rating"] is None
    assert metadata["score"] is None
    assert metadata["page_count"] == "1"
    assert metadata["cover_id"] == "image1"
    # Test getting info from a non-epub file
    cbz_file = abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "basic.cbz"))
    assert mm_epub.get_info_from_epub(cbz_file) == mm_archive.get_empty_metadata()
    text_file = abspath(join(mm_test.BASIC_TEXT_DIRECTORY, "unicode.txt"))
    assert mm_epub.get_info_from_epub(text_file) == mm_archive.get_empty_metadata()

def test_update_epub_info():
    """
    Tests the update_epub_info function.
    """
    # Test updating EPUB metadata while leaving cover intact
    base_file = abspath(join(mm_test.ARCHIVE_EPUB_DIRECTORY, "small.epub"))
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_file = abspath(join(temp_dir, "small.epub"))
        shutil.copy(base_file, epub_file)
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "New Title"
        metadata["artists"] = ["Other", "People"]
        metadata["cover_id"] = "image1"
        mm_epub.update_epub_info(epub_file, metadata)
        # Check that EPUB structure is intact
        assert mm_file_tools.extract_zip(epub_file, temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["EPUB", "META-INF", "mimetype", "small.epub"]
        epub_dir = abspath(join(temp_dir, "EPUB"))
        assert sorted(os.listdir(epub_dir)) == ["content", "content.opf", "images", "nav.xhtml", "original", "style", "toc.ncx"]
        content_dir = abspath(join(epub_dir, "content"))
        assert sorted(os.listdir(content_dir)) == ["Text.xhtml", "cover_image.xhtml"]
        image_dir = abspath(join(epub_dir, "images"))
        assert sorted(os.listdir(image_dir)) == ["image1.jpg"]
        # Check that the cover image hasn't been changed
        assert os.stat(abspath(join(image_dir, "image1.jpg"))).st_size == 1196
        contents = mm_file_tools.read_text_file(abspath(join(content_dir, "cover_image.xhtml")))
        compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<html xmlns:svgns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns=\"http://www.w3.org/1999/xhtml\">"
        compare = f"{compare}\n    <head>"
        compare = f"{compare}\n        <title>Cover</title>"
        compare = f"{compare}\n        <meta charset=\"utf-8\" />"
        compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
        compare = f"{compare}\n    </head>"
        compare = f"{compare}\n    <body>"
        compare = f"{compare}\n        <div id=\"full-image-container\">"
        compare = f"{compare}\n            <svgns:svg width=\"100%\" height=\"100%\" viewBox=\"0 0 100 150\" preserveAspectRatio=\"xMidYMid meet\" version=\"1.1\">"
        compare = f"{compare}\n                <svgns:title>Cover</svgns:title>"
        compare = f"{compare}\n                <svgns:image xlink:href=\"../images/image1.jpg\" width=\"100\" height=\"150\" />"
        compare = f"{compare}\n            </svgns:svg>"
        compare = f"{compare}\n        </div>"
        compare = f"{compare}\n    </body>"
        compare = f"{compare}\n</html>"
        assert contents == compare
        # Test that the metadata has been updated
        contents = mm_file_tools.read_text_file(abspath(join(epub_dir, "content.opf")))
        compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<package xmlns=\"http://www.idpf.org/2007/opf\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\" unique-identifier=\"id\" version=\"3.0\" prefix=\"http://www.idpf.org/vocab/rendition/#\">"
        compare = f"{compare}\n    <metadata>"
        compare = f"{compare}\n        <dc:language>en</dc:language>"
        compare = f"{compare}\n        <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
        compare = f"{compare}\n        <dc:identifier id=\"id\">New Title</dc:identifier>"
        compare = f"{compare}\n        <dc:date>0000-00-00T00:00:00+00:00</dc:date>"
        compare = f"{compare}\n        <dc:title>New Title</dc:title>"
        compare = f"{compare}\n        <dc:creator id=\"illustrator-0\">Other</dc:creator>"
        compare = f"{compare}\n        <meta refines=\"illustrator-0\" property=\"role\" scheme=\"marc:relators\">ill</meta>"
        compare = f"{compare}\n        <dc:creator id=\"illustrator-1\">People</dc:creator>"
        compare = f"{compare}\n        <meta refines=\"illustrator-1\" property=\"role\" scheme=\"marc:relators\">ill</meta>"
        compare = f"{compare}\n        <meta name=\"cover\" content=\"image1\" />"
        compare = f"{compare}\n    </metadata>"
        compare = f"{compare}\n    <manifest>"
        compare = f"{compare}\n        <item href=\"content/cover_image.xhtml\" id=\"cover\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n        <item href=\"content/Text.xhtml\" id=\"item0\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n        <item href=\"images/image1.jpg\" id=\"image1\" media-type=\"image/jpeg\" />"
        compare = f"{compare}\n        <item href=\"style/epubstyle.css\" id=\"epubstyle\" media-type=\"text/css\" />"
        compare = f"{compare}\n        <item href=\"nav.xhtml\" id=\"nav\" media-type=\"application/xhtml+xml\" properties=\"nav\" />"
        compare = f"{compare}\n        <item href=\"toc.ncx\" id=\"ncx\" media-type=\"application/x-dtbncx+xml\" />"
        compare = f"{compare}\n    </manifest>"
        compare = f"{compare}\n    <spine toc=\"ncx\">"
        compare = f"{compare}\n        <itemref idref=\"cover\" />"
        compare = f"{compare}\n        <itemref idref=\"item0\" />"
        compare = f"{compare}\n    </spine>"
        compare = f"{compare}\n</package>"
        assert contents == compare
    # Test updating EPUB metadata and cover image
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_file = abspath(join(temp_dir, "small.epub"))
        shutil.copy(base_file, epub_file)
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "New Cover"
        metadata["writers"] = ["Person"]
        metadata["cover_id"] = "image1"
        mm_epub.update_epub_info(epub_file, metadata, update_cover=True)
        # Check that EPUB structure is intact
        assert mm_file_tools.extract_zip(epub_file, temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["EPUB", "META-INF", "mimetype", "small.epub"]
        epub_dir = abspath(join(temp_dir, "EPUB"))
        assert sorted(os.listdir(epub_dir)) == ["content", "content.opf", "images", "nav.xhtml", "original", "style", "toc.ncx"]
        content_dir = abspath(join(epub_dir, "content"))
        assert sorted(os.listdir(content_dir)) == ["Text.xhtml", "cover_image.xhtml"]
        image_dir = abspath(join(epub_dir, "images"))
        assert sorted(os.listdir(image_dir)) == ["image1.jpg"]
        # Check that the cover image has been updated
        assert os.stat(abspath(join(image_dir, "image1.jpg"))).st_size > 5000
        contents = mm_file_tools.read_text_file(abspath(join(content_dir, "cover_image.xhtml")))
        compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<html xmlns:svgns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns=\"http://www.w3.org/1999/xhtml\">"
        compare = f"{compare}\n    <head>"
        compare = f"{compare}\n        <title>Cover</title>"
        compare = f"{compare}\n        <meta charset=\"utf-8\" />"
        compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
        compare = f"{compare}\n    </head>"
        compare = f"{compare}\n    <body>"
        compare = f"{compare}\n        <div id=\"full-image-container\">"
        compare = f"{compare}\n            <svgns:svg width=\"100%\" height=\"100%\" viewBox=\"0 0 900 1200\" preserveAspectRatio=\"xMidYMid meet\" version=\"1.1\">"
        compare = f"{compare}\n                <svgns:title>Cover</svgns:title>"
        compare = f"{compare}\n                <svgns:image xlink:href=\"../images/image1.jpg\" width=\"900\" height=\"1200\" />"
        compare = f"{compare}\n            </svgns:svg>"
        compare = f"{compare}\n        </div>"
        compare = f"{compare}\n    </body>"
        compare = f"{compare}\n</html>"
        assert contents == compare
        # Test that the metadata has been updated
        contents = mm_file_tools.read_text_file(abspath(join(epub_dir, "content.opf")))
        compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<package xmlns=\"http://www.idpf.org/2007/opf\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\" unique-identifier=\"id\" version=\"3.0\" prefix=\"http://www.idpf.org/vocab/rendition/#\">"
        compare = f"{compare}\n    <metadata>"
        compare = f"{compare}\n        <dc:language>en</dc:language>"
        compare = f"{compare}\n        <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
        compare = f"{compare}\n        <dc:identifier id=\"id\">New Cover</dc:identifier>"
        compare = f"{compare}\n        <dc:date>0000-00-00T00:00:00+00:00</dc:date>"
        compare = f"{compare}\n        <dc:title>New Cover</dc:title>"
        compare = f"{compare}\n        <dc:creator id=\"author-0\">Person</dc:creator>"
        compare = f"{compare}\n        <meta refines=\"author-0\" property=\"role\" scheme=\"marc:relators\">aut</meta>"
        compare = f"{compare}\n        <meta name=\"cover\" content=\"image1\" />"
        compare = f"{compare}\n    </metadata>"
        compare = f"{compare}\n    <manifest>"
        compare = f"{compare}\n        <item href=\"content/cover_image.xhtml\" id=\"cover\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n        <item href=\"content/Text.xhtml\" id=\"item0\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n        <item href=\"images/image1.jpg\" id=\"image1\" media-type=\"image/jpeg\" />"
        compare = f"{compare}\n        <item href=\"style/epubstyle.css\" id=\"epubstyle\" media-type=\"text/css\" />"
        compare = f"{compare}\n        <item href=\"nav.xhtml\" id=\"nav\" media-type=\"application/xhtml+xml\" properties=\"nav\" />"
        compare = f"{compare}\n        <item href=\"toc.ncx\" id=\"ncx\" media-type=\"application/x-dtbncx+xml\" />"
        compare = f"{compare}\n    </manifest>"
        compare = f"{compare}\n    <spine toc=\"ncx\">"
        compare = f"{compare}\n        <itemref idref=\"cover\" />"
        compare = f"{compare}\n        <itemref idref=\"item0\" />"
        compare = f"{compare}\n    </spine>"
        compare = f"{compare}\n</package>"
        assert contents == compare
    # Test attempting to update EPUB cover image when no cover image is present
    base_file = abspath(join(mm_test.ARCHIVE_EPUB_DIRECTORY, "basic.epub"))
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_file = abspath(join(temp_dir, "basic.epub"))
        shutil.copy(base_file, epub_file)
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "No Cover"
        metadata["tags"] = ["Multiple", "Tags"]
        metadata["cover_id"] = None
        mm_epub.update_epub_info(epub_file, metadata, update_cover=True)
        # Check that EPUB structure is intact
        assert mm_file_tools.extract_zip(epub_file, temp_dir)
        assert sorted(os.listdir(temp_dir)) == ["EPUB", "META-INF", "basic.epub", "mimetype"]
        epub_dir = abspath(join(temp_dir, "EPUB"))
        assert sorted(os.listdir(epub_dir)) == ["content", "content.opf", "images", "nav.xhtml", "original", "style", "toc.ncx"]
        content_dir = abspath(join(epub_dir, "content"))
        assert os.listdir(content_dir) == ["text.xhtml"]
        image_dir = abspath(join(epub_dir, "images"))
        assert os.listdir(image_dir) == []
        # Test that the metadata has been updated
        contents = mm_file_tools.read_text_file(abspath(join(epub_dir, "content.opf")))
        compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        compare = f"{compare}\n<package xmlns=\"http://www.idpf.org/2007/opf\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\" unique-identifier=\"id\" version=\"3.0\" prefix=\"http://www.idpf.org/vocab/rendition/#\">"
        compare = f"{compare}\n    <metadata>"
        compare = f"{compare}\n        <dc:language>en</dc:language>"
        compare = f"{compare}\n        <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
        compare = f"{compare}\n        <dc:identifier id=\"id\">No Cover</dc:identifier>"
        compare = f"{compare}\n        <dc:date>0000-00-00T00:00:00+00:00</dc:date>"
        compare = f"{compare}\n        <dc:title>No Cover</dc:title>"
        compare = f"{compare}\n        <dc:subject>Multiple</dc:subject>"
        compare = f"{compare}\n        <dc:subject>Tags</dc:subject>"
        compare = f"{compare}\n    </metadata>"
        compare = f"{compare}\n    <manifest>"
        compare = f"{compare}\n        <item href=\"content/text.xhtml\" id=\"item0\" media-type=\"application/xhtml+xml\" />"
        compare = f"{compare}\n        <item href=\"style/epubstyle.css\" id=\"epubstyle\" media-type=\"text/css\" />"
        compare = f"{compare}\n        <item href=\"nav.xhtml\" id=\"nav\" media-type=\"application/xhtml+xml\" properties=\"nav\" />"
        compare = f"{compare}\n        <item href=\"toc.ncx\" id=\"ncx\" media-type=\"application/x-dtbncx+xml\" />"
        compare = f"{compare}\n    </manifest>"
        compare = f"{compare}\n    <spine toc=\"ncx\">"
        compare = f"{compare}\n        <itemref idref=\"item0\" />"
        compare = f"{compare}\n    </spine>"
        compare = f"{compare}\n</package>"
        assert contents == compare
    # Test that file isn't overwritten if using the exact same metadata
    base_file = abspath(join(mm_test.ARCHIVE_EPUB_DIRECTORY, "basic.epub"))
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_file = abspath(join(temp_dir, "basic.epub"))
        shutil.copy(base_file, epub_file)
        assert os.stat(epub_file).st_size == 3359
        metadata = mm_epub.get_info_from_epub(epub_file)
        metadata["page_count"] = "136"
        mm_epub.update_epub_info(epub_file, metadata)
        assert os.stat(epub_file).st_size == 3359
        # Test that file will be overwritten even with the same metadata, if specified
        metadata = mm_epub.get_info_from_epub(epub_file)
        mm_epub.update_epub_info(epub_file, metadata, always_overwrite=True)
        assert os.stat(epub_file).st_size == 3336
        assert metadata == mm_epub.get_info_from_epub(epub_file)
