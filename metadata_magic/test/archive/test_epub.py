import os
import shutil
import metadata_magic.archive.epub as mm_epub
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive as mm_archive
from os.path import abspath, basename, exists, join
from PIL import Image

def test_get_default_chapters():
    """
    Tests the get_default_chapters function.
    """
    # Test getting the default chapter information.
    temp_dir = mm_file_tools.get_temp_dir()
    sub_dir = abspath(join(temp_dir, "sub"))
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(abspath(join(sub_dir, "sub.txt")), "TEXT")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "[1] 1.txt")), "TEXT")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "[2] 2.html")), "TEXT")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "[3] Thing.png")), "TEXT")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "[4] 4.thing")), "TEXT")
    chapters = mm_epub.get_default_chapters(temp_dir)
    assert len(chapters) == 3
    assert chapters[0]["include"]
    assert chapters[0]["title"] == "1"
    assert len(chapters[0]["files"]) == 1
    assert chapters[0]["files"][0]["id"] == "item0"
    assert basename(chapters[0]["files"][0]["file"]) == "[1] 1.txt"
    assert chapters[1]["include"]
    assert chapters[1]["title"] == "2"
    assert len(chapters[1]["files"]) == 1
    assert chapters[1]["files"][0]["id"] == "item1"
    assert basename(chapters[1]["files"][0]["file"]) == "[2] 2.html"
    assert chapters[2]["include"]
    assert chapters[2]["title"] == "Thing"
    assert len(chapters[2]["files"]) == 1
    assert chapters[2]["files"][0]["id"] == "item2"
    assert basename(chapters[2]["files"][0]["file"]) == "[3] Thing.png"
    # Test getting default chapter information for one text file with a title
    chapters = mm_epub.get_default_chapters(sub_dir, "Title!")
    assert len(chapters) == 1
    assert chapters[0]["include"]
    assert chapters[0]["title"] == "Title!"
    assert chapters[0]["files"][0]["id"] == "item0"
    assert basename(chapters[0]["files"][0]["file"]) == "sub.txt"

def test_add_cover_to_chapters():
    """
    Tests the add cover_to_chapters function
    """
    # Get default chapter information
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "TEXT")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "Thing.html")), "TEXT")
    chapters = mm_epub.get_default_chapters(temp_dir)
    assert len(chapters) == 2
    # Test adding a cover image to the chapter
    metadata = {"title":"Some Title", "writers":"Artist Person"}
    chapters = mm_epub.add_cover_to_chapters(chapters, metadata)
    assert len(chapters) == 3
    assert chapters[0]["include"]
    assert chapters[0]["title"] == "Cover"
    assert len(chapters[0]["files"]) == 1
    assert chapters[0]["files"][0]["id"] == "cover"
    assert basename(chapters[0]["files"][0]["file"]) == "mm_cover_image.jpg"
    assert exists(chapters[0]["files"][0]["file"])
    image = Image.open(chapters[0]["files"][0]["file"])
    assert image.size == (900, 1200)
    assert chapters[1]["include"]
    assert chapters[1]["title"] == "1"
    assert len(chapters[1]["files"]) == 1
    assert chapters[1]["files"][0]["id"] == "item0"
    assert basename(chapters[1]["files"][0]["file"]) == "1.txt"
    assert exists(chapters[1]["files"][0]["file"])
    assert chapters[2]["include"]
    assert chapters[2]["title"] == "Thing"
    assert len(chapters[2]["files"]) == 1
    assert chapters[2]["files"][0]["id"] == "item1"
    assert basename(chapters[2]["files"][0]["file"]) == "Thing.html"
    assert exists(chapters[2]["files"][0]["file"])

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
    # Test get the default chapter information.
    temp_dir = mm_file_tools.get_temp_dir()
    sub_dir = abspath(join(temp_dir, "sub"))
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(abspath(join(sub_dir, "sub.txt")), "TEXT")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "TEXT")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.htm")), "TEXT")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.txt")), "TEXT")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "4.thing")), "TEXT")
    chapters = mm_epub.get_default_chapters(temp_dir)
    # Test getting string from default chapter info
    chapters_string = mm_epub.get_chapters_string(chapters)
    compare = "ENTRY     TITLE    FILES"
    compare = f"{compare}\n------------------------"
    compare = f"{compare}\n001       1        1.txt"
    compare = f"{compare}\n002       2        2.htm"
    compare = f"{compare}\n003       3        3.txt"
    assert chapters_string == compare
    # Test getting string with modified titles
    chapters[0]["title"] = "Cover Image"
    chapters[1]["title"] = "Chapter 01"
    chapters[2]["title"] = "Epilogue"
    chapters_string = mm_epub.get_chapters_string(chapters)
    compare = "ENTRY     TITLE          FILES"
    compare = f"{compare}\n------------------------------"
    compare = f"{compare}\n001       Cover Image    1.txt"
    compare = f"{compare}\n002       Chapter 01     2.htm"
    compare = f"{compare}\n003       Epilogue       3.txt"
    assert chapters_string == compare
    # Test getting string with some non-included chapters
    chapters[1]["include"] = False
    chapters[2]["include"] = False
    chapters_string = mm_epub.get_chapters_string(chapters)
    compare = "ENTRY     TITLE          FILES"
    compare = f"{compare}\n------------------------------"
    compare = f"{compare}\n001       Cover Image    1.txt"
    compare = f"{compare}\n002*      Chapter 01     2.htm"
    compare = f"{compare}\n003*      Epilogue       3.txt"
    assert chapters_string == compare
    # Test getting string with grouped files
    files = chapters[1]["files"]
    files.append({"id":"aaa", "file":"a.png"})
    chapters[1]["files"] = files
    chapters_string = mm_epub.get_chapters_string(chapters)
    compare = "ENTRY     TITLE          FILES       "
    compare = f"{compare}\n-------------------------------------"
    compare = f"{compare}\n001       Cover Image    1.txt       "
    compare = f"{compare}\n002*      Chapter 01     2.htm, a.png"
    compare = f"{compare}\n003*      Epilogue       3.txt       "
    assert chapters_string == compare

def test_create_content_files():
    """
    Tests the create_content_files function.
    """
    # Create the default chapters list
    temp_dir = mm_file_tools.get_temp_dir()
    output_dir = mm_file_tools.get_temp_dir("dvk-epub-output")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "[01] 1.txt")), "Here's some text!\n\nAnd More!")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "[02] 2.html")), "<html><body><p>Word<p><p>Things!</p></body></html>")
    image_file = abspath(join(temp_dir, "[03] 3's.jpg"))
    image = Image.new("RGB", size=(500, 500), color="#ff0000")
    image.save(image_file)
    chapters = mm_epub.get_default_chapters(temp_dir)
    # Test creating the content files from the given chapters
    chapters[1]["title"] = "Chapter 2"
    chapters[2]["title"] = "Final's"
    chapters = mm_epub.create_content_files(chapters, output_dir)
    assert len(chapters) == 3
    assert chapters[0]["include"]
    assert chapters[0]["id"] == "item0"
    assert chapters[0]["title"] == "1"
    assert chapters[0]["file"] == "content/[01] 1.xhtml"
    assert chapters[1]["file"] == "content/[02] 2.xhtml"
    assert chapters[2]["file"] == "content/[03] 3's.xhtml"
    assert sorted(os.listdir(output_dir)) == ["content", "images"]
    image_dir = abspath(join(output_dir, "images"))
    assert sorted(os.listdir(image_dir)) == ["image1.jpg"]
    content_dir = abspath(join(output_dir, "content"))
    assert sorted(os.listdir(content_dir)) == ["[01] 1.xhtml", "[02] 2.xhtml", "[03] 3's.xhtml"]
    text = mm_file_tools.read_text_file(abspath(join(content_dir, "[01] 1.xhtml")))
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>1</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>Here's some text!</p>"
    compare = f"{compare}\n        <p>And More!</p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert text == compare
    # Test that HTML based XHTML was created correctly
    text = mm_file_tools.read_text_file(abspath(join(content_dir, "[02] 2.xhtml")))
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Chapter 2</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>Word</p>"
    compare = f"{compare}\n        <p>Things!</p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert text == compare
    # Test that image XHTML was created correctly
    text = mm_file_tools.read_text_file(abspath(join(content_dir, "[03] 3's.xhtml"))) 
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns:svgns=\"http://www.w3.org/2000/svg\" "
    compare = f"{compare}xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Final's</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <div id=\"full-image-container\">"
    compare = f"{compare}\n            <svgns:svg width=\"100%\" height=\"100%\" "
    compare = f"{compare}viewBox=\"0 0 500 500\" preserveAspectRatio=\"xMidYMid meet\" version=\"1.1\">"
    compare = f"{compare}\n                <svgns:title>Final's</svgns:title>"
    compare = f"{compare}\n                <svgns:image xlink:href=\"../images/image1.jpg\" width=\"500\" height=\"500\" />"
    compare = f"{compare}\n            </svgns:svg>"
    compare = f"{compare}\n        </div>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert text == compare
    # Test if chapters are grouped
    temp_dir = mm_file_tools.get_temp_dir()
    chapters = mm_epub.get_default_chapters(temp_dir)
    output_dir = mm_file_tools.get_temp_dir("dvk-epub-output")
    text_file = abspath(join(temp_dir, "A.txt"))
    html_file = abspath(join(temp_dir, "C.html"))
    image_file = abspath(join(temp_dir, "B.jpg"))
    mm_file_tools.write_text_file(text_file, "Some text here!")
    mm_file_tools.write_text_file(html_file, "<html><body><p>Different</p><p>Thing</p></body></html>")
    image = Image.new("RGB", size=(100, 300), color="#ff0000")
    image.save(image_file)
    assert exists(text_file)
    assert exists(html_file)
    assert exists(image_file)
    chapters = mm_epub.get_default_chapters(temp_dir)
    chapters = mm_epub.group_chapters(chapters, [0,1,2])
    chapters[0]["title"] = "Grouped"
    

    chapters = mm_epub.create_content_files(chapters, output_dir)
    assert len(chapters) == 1
    assert chapters[0]["include"]
    assert chapters[0]["id"] == "item0"
    assert chapters[0]["title"] == "Grouped"
    assert chapters[0]["file"] == "content/A.xhtml"
    content_dir = abspath(join(output_dir, "content"))
    assert sorted(os.listdir(content_dir)) == ["A.xhtml"]
    text = mm_file_tools.read_text_file(abspath(join(content_dir, "A.xhtml")))
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Grouped</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>Some text here!</p>"
    compare = f"{compare}\n        <div>"
    compare = f"{compare}\n            <img src=\"../images/image1.jpg\" alt=\"B\" width=\"100\" height=\"300\" />"
    compare = f"{compare}\n        </div>"
    compare = f"{compare}\n        <p>Different</p>"
    compare = f"{compare}\n        <p>Thing</p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert text == compare

def test_copy_original_files():
    """
    Tests the copy_original_files function.
    """
    # Test copying files originating from the given directory
    temp_dir = mm_file_tools.get_temp_dir()
    output_dir = mm_file_tools.get_temp_dir("dvk-epub-output")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.png")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.json")), "BLAH")
    mm_epub.copy_original_files(temp_dir, output_dir)
    assert os.listdir(output_dir) == ["original"]
    original_dir = abspath(join(output_dir, "original"))
    assert sorted(os.listdir(original_dir)) == ["1.txt", "2.png", "3.json"]
    # Test copying files from a designated "original" directory
    output_dir = mm_file_tools.get_temp_dir("dvk-epub-output")
    sub_dir = abspath(join(temp_dir, "Original"))
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(abspath(join(sub_dir, "other.txt")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub_dir, "things.png")), "BLAH")
    mm_epub.copy_original_files(temp_dir, output_dir)
    assert os.listdir(output_dir) == ["original"]
    original_dir = abspath(join(output_dir, "original"))
    assert sorted(os.listdir(original_dir)) == ["other.txt", "things.png"]
    # Test copying files included in subdirectories
    output_dir = mm_file_tools.get_temp_dir("dvk-epub-output")
    sub_dir = abspath(join(sub_dir, "more"))
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(abspath(join(sub_dir, "yet.txt")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub_dir, "more.png")), "BLAH")
    mm_epub.copy_original_files(temp_dir, output_dir)
    assert os.listdir(output_dir) == ["original"]
    original_dir = abspath(join(output_dir, "original"))
    assert sorted(os.listdir(original_dir)) == ["more", "other.txt", "things.png"]
    new_sub = abspath(join(original_dir, "more"))
    assert sorted(os.listdir(new_sub)) == ["more.png", "yet.txt"]
    
def test_create_style_file():
    """
    Tests the create_style_file function.
    """
    temp_dir = mm_file_tools.get_temp_dir()
    mm_epub.create_style_file(temp_dir)
    assert os.listdir(temp_dir) == ["style"]
    sub_dir = abspath(join(temp_dir, "style"))
    assert os.listdir(sub_dir) == ["epubstyle.css"]
    style_file = abspath(join(sub_dir, "epubstyle.css"))
    style = mm_file_tools.read_text_file(style_file)
    compare = ""
    compare = f"{compare}img {{"
    compare = f"{compare}\n    display: block;"
    compare = f"{compare}\n    max-width: 100%;"
    compare = f"{compare}\n    max-height: 100%;"
    compare = f"{compare}\n    text-align: center;"
    compare = f"{compare}\n    margin-left: auto;"
    compare = f"{compare}\n    margin-right: auto;"
    compare = f"{compare}\n}}\n\n"
    compare = f"{compare}#full-image-container {{"
    compare = f"{compare}\n    width: 100%;"
    compare = f"{compare}\n    height: 100%;"
    compare = f"{compare}\n    margin: 0;"
    compare = f"{compare}\n    padding: 0;"
    compare = f"{compare}\n    page-break-after: always;"
    compare = f"{compare}\n}}\n\n"
    compare = f"{compare}center {{"
    compare = f"{compare}\n    text-align: center;"
    compare = f"{compare}\n}}"
    assert style == compare

def test_create_nav_file():
    """
    Test the create_nav_file function.
    """
    # Create content files to list in the contents
    temp_dir = mm_file_tools.get_temp_dir()
    output_dir = mm_file_tools.get_temp_dir("dvk-epub-output")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "Here's some text!")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.htm")), "And")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.txt")), "Stuff")
    chapters = mm_epub.get_default_chapters(temp_dir)
    chapters = mm_epub.create_content_files(chapters, output_dir)
    # Test creating the nav file
    mm_epub.create_nav_file(chapters, "Title!", output_dir)
    assert sorted(os.listdir(output_dir)) == ["content", "images", "nav.xhtml"]
    nav_file = abspath(join(output_dir, "nav.xhtml"))
    nav_contents = mm_file_tools.read_text_file(nav_file)
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\" "
    compare = f"{compare}xmlns:epub=\"http://www.idpf.org/2007/ops\" lang=\"en\" xml:lang=\"en\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Title!</title>"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <nav epub:type=\"toc\" id=\"id\" role=\"doc-toc\">"
    compare = f"{compare}\n            <h2>Title!</h2>"
    compare = f"{compare}\n            <ol>"
    compare = f"{compare}\n                <il>"
    compare = f"{compare}\n                    <a href=\"content/1.xhtml\">1</a>"
    compare = f"{compare}\n                </il>"
    compare = f"{compare}\n                <il>"
    compare = f"{compare}\n                    <a href=\"content/2.xhtml\">2</a>"
    compare = f"{compare}\n                </il>"
    compare = f"{compare}\n                <il>"
    compare = f"{compare}\n                    <a href=\"content/3.xhtml\">3</a>"
    compare = f"{compare}\n                </il>"
    compare = f"{compare}\n            </ol>"
    compare = f"{compare}\n        </nav>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert nav_contents == compare
    # Test not including chapters
    chapters[0]["title"] = "Cover"
    chapters[1]["include"] = False
    chapters[2]["title"] = "Chapter 2"
    mm_epub.create_nav_file(chapters, "Not the Same", output_dir)
    assert sorted(os.listdir(output_dir)) == ["content", "images", "nav.xhtml"]
    nav_file = abspath(join(output_dir, "nav.xhtml"))
    nav_contents = mm_file_tools.read_text_file(nav_file)
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\" "
    compare = f"{compare}xmlns:epub=\"http://www.idpf.org/2007/ops\" lang=\"en\" xml:lang=\"en\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Not the Same</title>"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <nav epub:type=\"toc\" id=\"id\" role=\"doc-toc\">"
    compare = f"{compare}\n            <h2>Not the Same</h2>"
    compare = f"{compare}\n            <ol>"
    compare = f"{compare}\n                <il>"
    compare = f"{compare}\n                    <a href=\"content/1.xhtml\">Cover</a>"
    compare = f"{compare}\n                </il>"
    compare = f"{compare}\n                <il>"
    compare = f"{compare}\n                    <a href=\"content/3.xhtml\">Chapter 2</a>"
    compare = f"{compare}\n                </il>"
    compare = f"{compare}\n            </ol>"
    compare = f"{compare}\n        </nav>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert nav_contents == compare

def test_create_ncx_file():
    """
    Tests the create_ncx_file function.
    """
    # Create content files to list in the contents
    temp_dir = mm_file_tools.get_temp_dir()
    output_dir = mm_file_tools.get_temp_dir("dvk-epub-output")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "Here's some text!")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.html")), "And")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.txt")), "Stuff")
    chapters = mm_epub.get_default_chapters(temp_dir)
    chapters = mm_epub.create_content_files(chapters, output_dir)
    # Test creating the nav file
    mm_epub.create_ncx_file(chapters, "Title!", "/page/url/", output_dir)
    assert sorted(os.listdir(output_dir)) == ["content", "images", "toc.ncx"]
    ncx_file = abspath(join(output_dir, "toc.ncx"))
    ncx_contents = mm_file_tools.read_text_file(ncx_file)
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
    compare = f"{compare}\n                <text>1</text>"
    compare = f"{compare}\n            </navLabel>"
    compare = f"{compare}\n            <content src=\"content/1.xhtml\" />"
    compare = f"{compare}\n        </navPoint>"
    compare = f"{compare}\n        <navPoint id=\"item1\">"
    compare = f"{compare}\n            <navLabel>"
    compare = f"{compare}\n                <text>2</text>"
    compare = f"{compare}\n            </navLabel>"
    compare = f"{compare}\n            <content src=\"content/2.xhtml\" />"
    compare = f"{compare}\n        </navPoint>"
    compare = f"{compare}\n        <navPoint id=\"item2\">"
    compare = f"{compare}\n            <navLabel>"
    compare = f"{compare}\n                <text>3</text>"
    compare = f"{compare}\n            </navLabel>"
    compare = f"{compare}\n            <content src=\"content/3.xhtml\" />"
    compare = f"{compare}\n        </navPoint>"
    compare = f"{compare}\n    </navMap>"
    compare = f"{compare}\n</ncx>"
    assert ncx_contents == compare
    # Test not including chapters
    chapters[0]["title"] = "Cover"
    chapters[1]["include"] = False
    chapters[2]["title"] = "Chapter 2"
    mm_epub.create_ncx_file(chapters, "Not the Same", None, output_dir)
    assert sorted(os.listdir(output_dir)) == ["content", "images", "toc.ncx"]
    ncx_file = abspath(join(output_dir, "toc.ncx"))
    ncx_contents = mm_file_tools.read_text_file(ncx_file)
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<ncx xmlns=\"http://www.daisy.org/z3986/2005/ncx/\" version=\"2005-1\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <meta name=\"dtb:uid\" content=\"Not the Same\" />"
    compare = f"{compare}\n        <meta name=\"dtb:depth\" content=\"1\" />"
    compare = f"{compare}\n        <meta name=\"dtb:totalPageCount\" content=\"0\" />"
    compare = f"{compare}\n        <meta name=\"dtb:maxPageNumber\" content=\"0\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <docTitle>"
    compare = f"{compare}\n        <text>Not the Same</text>"
    compare = f"{compare}\n    </docTitle>"
    compare = f"{compare}\n    <navMap>"
    compare = f"{compare}\n        <navPoint id=\"item0\">"
    compare = f"{compare}\n            <navLabel>"
    compare = f"{compare}\n                <text>Cover</text>"
    compare = f"{compare}\n            </navLabel>"
    compare = f"{compare}\n            <content src=\"content/1.xhtml\" />"
    compare = f"{compare}\n        </navPoint>"
    compare = f"{compare}\n        <navPoint id=\"item2\">"
    compare = f"{compare}\n            <navLabel>"
    compare = f"{compare}\n                <text>Chapter 2</text>"
    compare = f"{compare}\n            </navLabel>"
    compare = f"{compare}\n            <content src=\"content/3.xhtml\" />"
    compare = f"{compare}\n        </navPoint>"
    compare = f"{compare}\n    </navMap>"
    compare = f"{compare}\n</ncx>"
    assert ncx_contents == compare

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
    metadata["title"] = "Title."
    metadata["url"] = "this/is/a/test"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
    compare = f"{compare}\n    <dc:date>0000-00-00T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:source>this/is/a/test</dc:source>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test date metadata
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
    metadata["writers"] = "Person!"
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
    metadata["writers"] = "Multiple,People"
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
    metadata["cover_artists"] = "Guest"
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
    metadata["cover_artists"] = "Other,Folks"
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
    metadata["artists"] = "Bleh"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:creator id=\"illustrator-0\">Bleh</dc:creator>"
    compare = f"{compare}\n    <meta refines=\"illustrator-0\" property=\"role\" scheme=\"marc:relators\">ill</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    metadata["artists"] = "Other,Name"
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
    metadata["tags"] = "Some,Tags,&,stuff"
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
    # Test metadata score
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
    compare = f"{compare}\n    <meta property=\"calibre:rating\">10.0</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    metadata["score"] = "3"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">Title.</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:publisher>Company</dc:publisher>"
    compare = f"{compare}\n    <meta property=\"calibre:rating\">6.0</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test metadata score if the score is invalid
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
    # Create content files
    temp_dir = mm_file_tools.get_temp_dir()
    output_dir = mm_file_tools.get_temp_dir("dvk-epub-output")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "Here's some text!")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.txt")), "And")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.html")), "Stuff")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "4.png")), "Image")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "5.jpeg")), "Image2")
    chapters = mm_epub.get_default_chapters(temp_dir)
    chapters = mm_epub.create_content_files(chapters, output_dir)
    # Get manifest xml
    xml = mm_epub.get_manifest_xml(chapters, output_dir)
    compare = ""
    compare = f"{compare}<manifest>"
    compare = f"{compare}\n    <item href=\"content/1.xhtml\" id=\"item0\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n    <item href=\"content/2.xhtml\" id=\"item1\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n    <item href=\"content/3.xhtml\" id=\"item2\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n    <item href=\"content/4.xhtml\" id=\"item3\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n    <item href=\"content/5.xhtml\" id=\"item4\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n    <item href=\"images/image1.png\" id=\"image1\" media-type=\"image/png\" />"
    compare = f"{compare}\n    <item href=\"images/image2.jpeg\" id=\"image2\" media-type=\"image/jpeg\" />"
    compare = f"{compare}\n    <item href=\"style/epubstyle.css\" id=\"epubstyle\" media-type=\"text/css\" />"
    compare = f"{compare}\n    <item href=\"nav.xhtml\" id=\"nav\" media-type=\"application/xhtml+xml\" properties=\"nav\" />"
    compare = f"{compare}\n    <item href=\"toc.ncx\" id=\"ncx\" media-type=\"application/x-dtbncx+xml\" />"
    compare = f"{compare}\n</manifest>"
    assert xml == compare

def test_create_content_opf():
    """
    Tests the create_content_opf function.
    """
    # Create content files
    temp_dir = mm_file_tools.get_temp_dir()
    output_dir = mm_file_tools.get_temp_dir("dvk-epub-output")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "Here's some text!")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.html")), "And")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.jpg")), "Stuff")
    chapters = mm_epub.get_default_chapters(temp_dir)
    chapters = mm_epub.create_content_files(chapters, output_dir)
    # Test creating the opf file
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Thing!"
    mm_epub.create_content_opf(chapters, metadata, output_dir)
    assert sorted(os.listdir(output_dir)) == ["content", "content.opf", "images"]
    opf_file = abspath(join(output_dir, "content.opf"))
    opf_contents = mm_file_tools.read_text_file(opf_file)
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<package xmlns:dc=\"http://purl.org/dc/elements/1.1/\" "
    compare = f"{compare}xmlns=\"http://www.idpf.org/2007/opf\" unique-identifier=\"id\" "
    compare = f"{compare}version=\"3.0\" prefix=\"http://www.idpf.org/vocab/rendition/#\">"
    compare = f"{compare}\n    <metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n        <dc:language>en</dc:language>"
    compare = f"{compare}\n        <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n        <dc:identifier id=\"id\">Thing!</dc:identifier>"
    compare = f"{compare}\n        <dc:date>0000-00-00T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n        <dc:title>Thing!</dc:title>"
    compare = f"{compare}\n        <meta name=\"cover\" content=\"image1\" />"
    compare = f"{compare}\n    </metadata>"
    compare = f"{compare}\n    <manifest>"
    compare = f"{compare}\n        <item href=\"content/1.xhtml\" id=\"item0\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n        <item href=\"content/2.xhtml\" id=\"item1\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n        <item href=\"content/3.xhtml\" id=\"item2\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n        <item href=\"images/image1.jpg\" id=\"image1\" media-type=\"image/jpeg\" />"
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
    assert opf_contents == compare

def test_create_epub():
    """
    Tests the create_epub function.
    """
    # Create content files
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "Here's some text!")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.html")), "And")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.pdf")), "Stuff")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "a.png")), "image")
    chapters = mm_epub.get_default_chapters(temp_dir)
    # Create the epub file
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Name"
    epub_file = mm_epub.create_epub(chapters, metadata, temp_dir)
    assert exists(epub_file)
    assert basename(epub_file) == "Name.epub"
    # Extract the epub file to see contents
    extracted = abspath(join(temp_dir, "extracted"))
    os.mkdir(extracted)
    assert mm_file_tools.extract_zip(epub_file, extracted)
    assert sorted(os.listdir(extracted)) == ["EPUB", "META-INF", "mimetype"]
    # Check the mimetype contents
    assert mm_file_tools.read_text_file(abspath(join(extracted, "mimetype"))) == "application/epub+zip"
    # Check the contents of the meta folder
    meta_directory = abspath(join(extracted, "META-INF"))
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
    epub_directory = abspath(join(extracted, "EPUB"))
    assert sorted(os.listdir(epub_directory)) == ["content", "content.opf", "images", "nav.xhtml", "original", "style", "toc.ncx"]
    # Check the contents of the content folder
    content_directory = abspath(join(epub_directory, "content"))
    assert sorted(os.listdir(content_directory)) == ["1.xhtml", "2.xhtml", "a.xhtml"]
    # Check the contents of the original directory
    original_directory = abspath(join(epub_directory, "original"))
    assert sorted(os.listdir(original_directory)) == ["1.txt", "2.html", "3.pdf", "a.png"]
    # Check the contents of the style directory
    style_directory = abspath(join(epub_directory, "style"))
    assert sorted(os.listdir(style_directory)) == ["epubstyle.css"]
    # Check the contents of the images directory
    style_directory = abspath(join(epub_directory, "images"))
    assert sorted(os.listdir(style_directory)) == ["image1.png"]
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
    compare = f"{compare}\n        <dc:identifier id=\"id\">Name</dc:identifier>"
    compare = f"{compare}\n        <dc:date>0000-00-00T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n        <dc:title>Name</dc:title>"
    compare = f"{compare}\n        <meta name=\"cover\" content=\"image1\" />"
    compare = f"{compare}\n    </metadata>"
    compare = f"{compare}\n    <manifest>"
    compare = f"{compare}\n        <item href=\"content/1.xhtml\" id=\"item0\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n        <item href=\"content/2.xhtml\" id=\"item1\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n        <item href=\"content/a.xhtml\" id=\"item2\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n        <item href=\"images/image1.png\" id=\"image1\" media-type=\"image/png\" />"
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
    # Create base files
    temp_dir = mm_file_tools.get_temp_dir()
    json_file = abspath(join(temp_dir, "test.json"))
    image_file = abspath(join(temp_dir, "test.png"))
    image = Image.new("RGB", size=(100, 100), color="#ff0000")
    image.save(image_file)
    summary = "These are<br/>\n\rall lines.<br/><br/>And<br/>such."
    mm_file_tools.write_json_file(json_file, {"title":"doesn't matter","caption":summary})
    assert exists(json_file)
    assert exists(image_file)
    # Create the epub file
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "This is a Title"
    metadata["writers"] = "Person"
    metadata["url"] = "/thing/"
    metadata["date"] = "2021-01-01"
    metadata["description"] = "Something Else"
    epub_file = mm_epub.create_epub_from_description(json_file, image_file, metadata, temp_dir)
    assert basename(epub_file) == "This is a Title.epub"
    assert abspath(join(epub_file, os.pardir)) == temp_dir
    assert exists(epub_file)
    # Extract the epub file to see contents
    extracted = abspath(join(temp_dir, "extracted"))
    os.mkdir(extracted)
    assert mm_file_tools.extract_zip(epub_file, extracted)
    assert sorted(os.listdir(extracted)) == ["EPUB", "META-INF", "mimetype"]
    # Check the mimetype contents
    assert mm_file_tools.read_text_file(abspath(join(extracted, "mimetype"))) == "application/epub+zip"
    # Check the contents of the meta folder
    meta_directory = abspath(join(extracted, "META-INF"))
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
    epub_directory = abspath(join(extracted, "EPUB"))
    assert sorted(os.listdir(epub_directory)) == ["content", "content.opf", "images", "nav.xhtml", "original", "style", "toc.ncx"]
    # Check the contents of the content folder
    content_directory = abspath(join(epub_directory, "content"))
    assert sorted(os.listdir(content_directory)) == ["dvk-cover.xhtml", "test.xhtml"]
    # Check the contents of the original directory
    original_directory = abspath(join(epub_directory, "original"))
    assert sorted(os.listdir(original_directory)) == ["test.json", "test.png"]
    # Check the contents of the style directory
    style_directory = abspath(join(epub_directory, "style"))
    assert sorted(os.listdir(style_directory)) == ["epubstyle.css"]
    # Check the contents of the images directory
    style_directory = abspath(join(epub_directory, "images"))
    assert sorted(os.listdir(style_directory)) == ["image1.png"]
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
    compare = f"{compare}\n        <dc:identifier id=\"id\">/thing/</dc:identifier>"
    compare = f"{compare}\n        <dc:date>2021-01-01T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n        <dc:title>This is a Title</dc:title>"
    compare = f"{compare}\n        <dc:source>/thing/</dc:source>"
    compare = f"{compare}\n        <dc:description>Something Else</dc:description>"
    compare = f"{compare}\n        <dc:creator id=\"author-0\">Person</dc:creator>"
    compare = f"{compare}\n        <meta refines=\"author-0\" property=\"role\" scheme=\"marc:relators\">aut</meta>"
    compare = f"{compare}\n        <meta name=\"cover\" content=\"image1\" />"
    compare = f"{compare}\n    </metadata>"
    compare = f"{compare}\n    <manifest>"
    compare = f"{compare}\n        <item href=\"content/dvk-cover.xhtml\" id=\"item_cover\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n        <item href=\"content/test.xhtml\" id=\"item_text\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n        <item href=\"images/image1.png\" id=\"image1\" media-type=\"image/png\" />"
    compare = f"{compare}\n        <item href=\"style/epubstyle.css\" id=\"epubstyle\" media-type=\"text/css\" />"
    compare = f"{compare}\n        <item href=\"nav.xhtml\" id=\"nav\" media-type=\"application/xhtml+xml\" properties=\"nav\" />"
    compare = f"{compare}\n        <item href=\"toc.ncx\" id=\"ncx\" media-type=\"application/x-dtbncx+xml\" />"
    compare = f"{compare}\n    </manifest>"
    compare = f"{compare}\n    <spine toc=\"ncx\">"
    compare = f"{compare}\n        <itemref idref=\"item_cover\" />"
    compare = f"{compare}\n        <itemref idref=\"item_text\" />"
    compare = f"{compare}\n    </spine>"
    compare = f"{compare}\n</package>"
    assert content == compare
    # Check the contents of the generated XHTML
    content = mm_file_tools.read_text_file(abspath(join(content_directory, "test.xhtml")))
    compare = ""
    compare = f"{compare}<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>This is a Title</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>These are all lines.</p>"
    compare = f"{compare}\n        <p>And such.</p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert content == compare
    # Check the contents of the cover XHTML
    content = mm_file_tools.read_text_file(abspath(join(content_directory, "dvk-cover.xhtml")))
    compare = ""
    compare = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns:svgns=\"http://www.w3.org/2000/svg\" "
    compare = f"{compare}xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Cover</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <div id=\"full-image-container\">"
    compare = f"{compare}\n            <svgns:svg width=\"100%\" height=\"100%\" viewBox=\"0 0 100 100\" "
    compare = f"{compare}preserveAspectRatio=\"xMidYMid meet\" version=\"1.1\">"
    compare = f"{compare}\n            <svgns:title>Cover</svgns:title>"
    compare = f"{compare}\n            <svgns:image xlink:href=\"../images/image1.png\" width=\"100\" height=\"100\" />"
    compare = f"{compare}\n            </svgns:svg>"
    compare = f"{compare}\n        </div>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"

def test_get_info_from_epub():
    """
    Tests the get_info_from_epub function.
    """
    # Create content files
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "Here's some text!")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.txt")), "And")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.pdf")), "Stuff")
    chapters = mm_epub.get_default_chapters(temp_dir)
    metadata = mm_archive.get_empty_metadata()
    # Test Getting the title
    metadata["title"] = "This is a title!\\'"
    epub_file = mm_epub.create_epub(chapters, metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "This is a title!\\'"
    assert read_meta["url"] is None
    assert read_meta["description"] is None
    # Test getting the URL
    os.remove(epub_file)
    metadata["title"] = "New Title"
    metadata["url"] = "https://www.notrealsite"
    epub_file = mm_epub.create_epub(mm_epub.get_default_chapters(temp_dir), metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "New Title"
    assert read_meta["url"] == "https://www.notrealsite"
    assert read_meta["date"] is None
    assert read_meta["description"] is None
    # Test getting the date
    os.remove(epub_file)
    metadata["url"] = "http://www.alsofake"
    metadata["date"] = "2012-12-21"
    epub_file = mm_epub.create_epub(mm_epub.get_default_chapters(temp_dir), metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "New Title"
    assert read_meta["url"] == "http://www.alsofake"
    assert read_meta["date"] == "2012-12-21"
    assert read_meta["description"] is None
    # Test getting the description
    os.remove(epub_file)
    metadata["url"] = "www.alsofake"
    metadata["date"] = "2012-12-21"
    metadata["description"] = "This & That."
    epub_file = mm_epub.create_epub(mm_epub.get_default_chapters(temp_dir), metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "New Title"
    assert read_meta["url"] == "www.alsofake"
    assert read_meta["date"] == "2012-12-21"
    assert read_meta["description"] == "This & That."
    assert read_meta["writers"] is None
    assert read_meta["artists"] is None
    assert read_meta["cover_artists"] is None
    # Test getting writers and artists
    os.remove(epub_file)
    metadata["artists"] = "Some,Artist,Folks"
    metadata["writers"] = "The,Author"
    metadata["cover_artists"] = "Last,People"
    epub_file = mm_epub.create_epub(mm_epub.get_default_chapters(temp_dir), metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "New Title"
    assert read_meta["url"] == "www.alsofake"
    assert read_meta["date"] == "2012-12-21"
    assert read_meta["description"] == "This & That."
    assert read_meta["writers"] == "The,Author"
    assert read_meta["artists"] == "Some,Artist,Folks"
    assert read_meta["cover_artists"] == "Last,People"
    assert read_meta["publisher"] is None
    # Test getting the publisher
    os.remove(epub_file)
    metadata["publisher"] = "Book People"
    epub_file = mm_epub.create_epub(mm_epub.get_default_chapters(temp_dir), metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "New Title"
    assert read_meta["url"] == "www.alsofake"
    assert read_meta["date"] == "2012-12-21"
    assert read_meta["description"] == "This & That."
    assert read_meta["publisher"] == "Book People"
    assert read_meta["series"] is None
    assert read_meta["series_number"] is None
    assert read_meta["series_total"] is None
    # Test getting series metadata
    os.remove(epub_file)
    metadata["series"] = "The EPUB Chronicles."
    metadata["series_number"] = "3.5"
    epub_file = mm_epub.create_epub(mm_epub.get_default_chapters(temp_dir), metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "New Title"
    assert read_meta["url"] == "www.alsofake"
    assert read_meta["date"] == "2012-12-21"
    assert read_meta["description"] == "This & That."
    assert read_meta["publisher"] == "Book People"
    assert read_meta["series"] == "The EPUB Chronicles."
    assert read_meta["series_number"] == "3.5"
    assert read_meta["series_total"] is None
    assert read_meta["tags"] is None
    # Test getting the tags
    os.remove(epub_file)
    metadata["tags"] = "Some,Tags,&,Stuff"
    epub_file = mm_epub.create_epub(mm_epub.get_default_chapters(temp_dir), metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "New Title"
    assert read_meta["tags"] == "Some,Tags,&,Stuff"
    assert read_meta["age_rating"] is None
    # Test getting the age rating
    os.remove(epub_file)
    metadata["age_rating"] = "Teen"
    epub_file = mm_epub.create_epub(mm_epub.get_default_chapters(temp_dir), metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "New Title"
    assert read_meta["tags"] == "Some,Tags,&,Stuff"
    assert read_meta["age_rating"] == "Teen"
    assert read_meta["score"] is None
    # Test getting the score
    os.remove(epub_file)
    metadata["score"] = "3"
    epub_file = mm_epub.create_epub(mm_epub.get_default_chapters(temp_dir), metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "New Title"
    assert read_meta["tags"] == "Some,Tags,&,Stuff"
    assert read_meta["age_rating"] == "Teen"
    assert read_meta["score"] == "3"
    metadata["score"] = "1"
    epub_file = mm_epub.create_epub(mm_epub.get_default_chapters(temp_dir), metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "New Title"
    assert read_meta["tags"] == "Some,Tags,&,Stuff"
    assert read_meta["age_rating"] == "Teen"
    assert read_meta["score"] == "1"
    metadata["score"] = "5"
    epub_file = mm_epub.create_epub(mm_epub.get_default_chapters(temp_dir), metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "New Title"
    assert read_meta["tags"] == "Some,Tags,&,Stuff"
    assert read_meta["age_rating"] == "Teen"
    assert read_meta["score"] == "5"
    metadata["score"] = "0"
    epub_file = mm_epub.create_epub(mm_epub.get_default_chapters(temp_dir), metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "New Title"
    assert read_meta["tags"] == "Some,Tags,&,Stuff"
    assert read_meta["age_rating"] == "Teen"
    assert read_meta["score"] == "0"
    # Test getting score that is invalid
    metadata["score"] = "6"
    epub_file = mm_epub.create_epub(mm_epub.get_default_chapters(temp_dir), metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "New Title"
    assert read_meta["tags"] == "Some,Tags,&,Stuff"
    assert read_meta["age_rating"] == "Teen"
    assert read_meta["score"] is None
    assert read_meta["cover_id"] is None
    # Test getting the cover id from the epub file
    chapters = mm_epub.add_cover_to_chapters(mm_epub.get_default_chapters(temp_dir), metadata)
    epub_file = mm_epub.create_epub(chapters, metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "New Title"
    assert read_meta["tags"] == "Some,Tags,&,Stuff"
    assert read_meta["age_rating"] == "Teen"
    assert read_meta["score"] is None
    assert read_meta["cover_id"] == "image1"
    # Test getting info from a non-epub file
    temp_dir = mm_file_tools.get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "Text")
    read_meta = mm_epub.get_info_from_epub(text_file)
    assert read_meta == mm_archive.get_empty_metadata()
    zip_file = abspath(join(temp_dir, "not_epub.zip"))
    mm_file_tools.create_zip(temp_dir, zip_file)
    read_meta = mm_epub.get_info_from_epub(zip_file)
    assert read_meta == mm_archive.get_empty_metadata()

def test_update_epub_info():
    """
    Tests the update_epub_info function.
    """
    # Create content files
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "Here's some text!")
    image = Image.new("RGB", size=(100, 100), color="#ff0000")
    image.save(abspath(join(temp_dir, "2.png")))
    chapters = mm_epub.get_default_chapters(temp_dir)
    # Create the epub file
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Name"
    epub_file = mm_epub.create_epub(chapters, metadata, temp_dir)
    assert exists(epub_file)
    assert basename(epub_file) == "Name.epub"
    # Get the epub info
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "Name"
    assert read_meta["artists"] is None
    assert read_meta["description"] is None
    # Update the epub info
    metadata["cover_id"] = None
    metadata["title"] = "New Name!"
    metadata["writers"] = "Person"
    metadata["artists"] = "Another"
    metadata["description"] = "Some text!!"
    mm_epub.update_epub_info(epub_file, metadata, update_cover=True)
    read_meta = mm_epub.get_info_from_epub(epub_file)
    assert read_meta["title"] == "New Name!"
    assert read_meta["writers"] == "Person"
    assert read_meta["artists"] == "Another"
    assert read_meta["description"] == "Some text!!"
    # Extract the epub file to see contents
    extracted = abspath(join(temp_dir, "extracted"))
    os.mkdir(extracted)
    assert mm_file_tools.extract_zip(epub_file, extracted)
    assert sorted(os.listdir(extracted)) == ["EPUB", "META-INF", "mimetype"]
    # Check that contents are still correct
    assert mm_file_tools.read_text_file(abspath(join(extracted, "mimetype"))) == "application/epub+zip"
    epub_directory = abspath(join(extracted, "EPUB"))
    contents = ["content", "content.opf", "images", "nav.xhtml", "original", "style", "toc.ncx"]
    assert sorted(os.listdir(epub_directory)) == contents
    assert sorted(os.listdir(abspath(join(epub_directory, "content")))) == ["1.xhtml", "2.xhtml"]
    assert sorted(os.listdir(abspath(join(epub_directory, "original")))) == ["1.txt", "2.png"]
    assert sorted(os.listdir(abspath(join(epub_directory, "style")))) == ["epubstyle.css"]
    image_dir = abspath(join(epub_directory, "images"))
    assert sorted(os.listdir(image_dir)) == ["image1.png"]
    # Test than non-cover_image is unaltered
    extracted_image = Image.open(abspath(join(image_dir, "image1.png")))
    assert extracted_image.size == (100, 100)
    # Create an epub file
    os.remove(epub_file)
    shutil.rmtree(extracted)
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "N"
    metadata["writer"] = "N"
    chapters = mm_epub.get_default_chapters(temp_dir)
    chapters = mm_epub.add_cover_to_chapters(chapters, metadata)
    epub_file = mm_epub.create_epub(chapters, metadata, temp_dir)
    extracted = abspath(join(temp_dir, "extracted"))
    os.mkdir(extracted)
    assert mm_file_tools.extract_zip(epub_file, extracted)
    epub_dir = abspath(join(extracted, "EPUB"))
    image_dir = abspath(join(epub_dir, "images"))
    assert sorted(os.listdir(image_dir)) == ["image1.jpg", "image2.png"]
    extracted_image = Image.open(abspath(join(image_dir, "image2.png")))
    assert extracted_image.size == (100, 100)
    cover_image = Image.open(abspath(join(image_dir, "image1.jpg")))
    assert cover_image.size == (900, 1200)
    cover_size = os.stat(abspath(join(image_dir, "image1.jpg"))).st_size
    # Test that cover image is not altered if not specified
    shutil.rmtree(extracted)
    metadata["cover_id"] = "image1"
    metadata["title"] = "Something else!"
    metadata["writers"] = "Something"
    mm_epub.update_epub_info(epub_file, metadata, update_cover=False)
    assert mm_epub.get_info_from_epub(epub_file)["title"] == "Something else!"
    extracted = abspath(join(temp_dir, "extracted"))
    os.mkdir(extracted)
    assert mm_file_tools.extract_zip(epub_file, extracted)
    epub_dir = abspath(join(extracted, "EPUB"))
    image_dir = abspath(join(epub_dir, "images"))
    assert sorted(os.listdir(image_dir)) == ["image1.jpg", "image2.png"]
    extracted_image = Image.open(abspath(join(image_dir, "image2.png")))
    assert extracted_image.size == (100, 100)
    cover_image = Image.open(abspath(join(image_dir, "image1.jpg")))
    assert cover_image.size == (900, 1200)
    assert os.stat(abspath(join(image_dir, "image1.jpg"))).st_size == cover_size
    content = mm_file_tools.read_text_file(abspath(join(epub_dir, "content.opf")))
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<package xmlns=\"http://www.idpf.org/2007/opf\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\" unique-identifier=\"id\" version=\"3.0\" prefix=\"http://www.idpf.org/vocab/rendition/#\">"
    compare = f"{compare}\n    <metadata>"
    compare = f"{compare}\n        <dc:language>en</dc:language>"
    compare = f"{compare}\n        <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n        <dc:identifier id=\"id\">Something else!</dc:identifier>"
    compare = f"{compare}\n        <dc:date>0000-00-00T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n        <dc:title>Something else!</dc:title>"
    compare = f"{compare}\n        <dc:creator id=\"author-0\">Something</dc:creator>"
    compare = f"{compare}\n        <meta refines=\"author-0\" property=\"role\" scheme=\"marc:relators\">aut</meta>"
    compare = f"{compare}\n        <meta name=\"cover\" content=\"image1\" />"
    compare = f"{compare}\n    </metadata>"
    compare = f"{compare}\n    <manifest>"
    compare = f"{compare}\n        <item href=\"content/mm_cover_image.xhtml\" id=\"cover\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n        <item href=\"content/1.xhtml\" id=\"item0\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n        <item href=\"content/2.xhtml\" id=\"item1\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n        <item href=\"images/image1.jpg\" id=\"image1\" media-type=\"image/jpeg\" />"
    compare = f"{compare}\n        <item href=\"images/image2.png\" id=\"image2\" media-type=\"image/png\" />"
    compare = f"{compare}\n        <item href=\"style/epubstyle.css\" id=\"epubstyle\" media-type=\"text/css\" />"
    compare = f"{compare}\n        <item href=\"nav.xhtml\" id=\"nav\" media-type=\"application/xhtml+xml\" properties=\"nav\" />"
    compare = f"{compare}\n        <item href=\"toc.ncx\" id=\"ncx\" media-type=\"application/x-dtbncx+xml\" />"
    compare = f"{compare}\n    </manifest>"
    compare = f"{compare}\n    <spine toc=\"ncx\">"
    compare = f"{compare}\n        <itemref idref=\"cover\" />"
    compare = f"{compare}\n        <itemref idref=\"item0\" />"
    compare = f"{compare}\n        <itemref idref=\"item1\" />"
    compare = f"{compare}\n    </spine>"
    compare = f"{compare}\n</package>"
    assert content == compare
    # Test updating the epub
    shutil.rmtree(extracted)
    metadata["title"] = "Another Title of Sorts"
    metadata["writer"] = "Something"
    mm_epub.update_epub_info(epub_file, metadata, update_cover=True)
    assert mm_epub.get_info_from_epub(epub_file)["title"] == "Another Title of Sorts"
    extracted = abspath(join(temp_dir, "extracted"))
    os.mkdir(extracted)
    assert mm_file_tools.extract_zip(epub_file, extracted)
    image_dir = abspath(join(extracted, "EPUB"))
    image_dir = abspath(join(image_dir, "images"))
    assert sorted(os.listdir(image_dir)) == ["image1.jpg", "image2.png"]
    extracted_image = Image.open(abspath(join(image_dir, "image2.png")))
    assert extracted_image.size == (100, 100)
    cover_image = Image.open(abspath(join(image_dir, "image1.jpg")))
    assert cover_image.size == (900, 1200)
    assert not os.stat(abspath(join(image_dir, "image1.jpg"))).st_size == cover_size
    # Test updating a non-epub file
    temp_dir = mm_file_tools.get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "This is text!")
    mm_epub.update_epub_info(text_file, metadata)
    assert mm_file_tools.read_text_file(text_file) == "This is text!"
    zip_file = abspath(join(temp_dir, "not_epub.zip"))
    mm_file_tools.create_zip(temp_dir, zip_file)
    mm_epub.update_epub_info(zip_file, metadata)
    extract_dir = abspath(join(temp_dir, "extract"))
    os.mkdir(extract_dir)
    assert mm_file_tools.extract_zip(zip_file, extract_dir)
    assert sorted(os.listdir(extract_dir)) == ["text.txt"]
    assert mm_file_tools.read_text_file(abspath(join(extract_dir, "text.txt"))) == "This is text!"
