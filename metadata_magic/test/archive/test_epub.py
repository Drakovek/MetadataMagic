import os
import metadata_magic.archive.epub as mm_epub
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive as mm_archive
from os.path import abspath, basename, exists, join

def test_format_xhtml():
    """
    Tests the format_xhtml function.
    """
    # Test single paragraph tag
    html = "<p>This is a simple test &amp; stuff</p>"
    xhtml = mm_epub.format_xhtml(html, "Title!")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Title!</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>This is a simple test &amp; stuff</p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    # Test with multiple paragraph tags
    html = "<p>Multiple</p><p>Paragraphs!!!</p>"
    xhtml = mm_epub.format_xhtml(html, "Title!")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Title!</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>Multiple</p>"
    compare = f"{compare}\n        <p>Paragraphs!!!</p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    # Test with no tags
    html = "This is a thing.<br/><br/>Final thing."
    xhtml = mm_epub.format_xhtml(html, "Title thing.")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Title thing.</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>This is a thing.<br />"
    compare = f"{compare}\n            <br />Final thing.</p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    # Test with spaces and newlines
    html = "  <p>  This is a thing!  </p>\n  <div> Another </div> "
    xhtml = mm_epub.format_xhtml(html, "Next Title")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Next Title</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>This is a thing!</p>"
    compare = f"{compare}\n        <div>Another</div>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare

def test_txt_to_xhtml():
    """
    Tests the text_to_xhtml function.
    """
    # Test a single paragraph
    temp_dir = mm_file_tools.get_temp_dir()
    text_file = abspath(join(temp_dir, "Text.txt"))
    text = "This is a simple sentence!"
    mm_file_tools.write_text_file(text_file, text)
    assert exists(text_file)
    xhtml = mm_epub.txt_to_xhtml(text_file, "Title!")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Title!</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>This is a simple sentence!</p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    # Test multiple paragraphs
    text = "Different paragraphs!\n\nHow cool!"
    mm_file_tools.write_text_file(text_file, text)
    xhtml = mm_epub.txt_to_xhtml(text_file, "Thing...")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Thing...</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>Different paragraphs!</p>"
    compare = f"{compare}\n        <p>How cool!</p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    # Test single new line character with HTML escape entities
    text = "More text!\nAnd This & That..."
    mm_file_tools.write_text_file(text_file, text)
    xhtml = mm_epub.txt_to_xhtml(text_file, "Escape")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Escape</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>More text!<br />And This &amp; That...</p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    # Test new lines and separate paragraphs
    text = "Paragraph\n\nOther\nText!\n\nFinal\nParagraph..."
    mm_file_tools.write_text_file(text_file, text)
    xhtml = mm_epub.txt_to_xhtml(text_file, "Both!")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Both!</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>Paragraph</p>"
    compare = f"{compare}\n        <p>Other<br />Text!</p>"
    compare = f"{compare}\n        <p>Final<br />Paragraph...</p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    # Test with more than one two new lines
    text = "Thing\n\n\n\r\n\nOther"
    mm_file_tools.write_text_file(text_file, text)
    xhtml = mm_epub.txt_to_xhtml(text_file, "Multiple")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Multiple</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>Thing</p>"
    compare = f"{compare}\n        <p>Other</p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare

def test_get_title_from_file():
    """
    Tests the get_title_from_file function.
    """
    temp_file = mm_file_tools.get_temp_dir()
    filename = abspath(join(temp_file, "thing.txt"))
    assert mm_epub.get_title_from_file(filename) == "thing"
    filename = abspath(join(temp_file, "[00] Image  .png"))
    assert mm_epub.get_title_from_file(filename) == "Image"
    filename = abspath(join(temp_file, "(This is a thing) Cover"))
    assert mm_epub.get_title_from_file(filename) == "Cover"
    filename = abspath(join(temp_file, "[Not Number) Thing.txt"))
    assert mm_epub.get_title_from_file(filename) == "[Not Number) Thing"
    filename = abspath(join(temp_file, "  1 [2] (3).html"))
    assert mm_epub.get_title_from_file(filename) == "1 [2] (3)"
    filename = abspath(join(temp_file, "none"))
    assert mm_epub.get_title_from_file(filename) == "none"

def test_get_default_chapters():
    """
    Tests the get_default_chapters function.
    """
    # Test getting the default chapter information.
    temp_dir = mm_file_tools.get_temp_dir()
    sub_dir = abspath(join(temp_dir, "sub"))
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(abspath(join(sub_dir, "sub.txt")), "TEXT")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "TEXT")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.txt")), "TEXT")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.txt")), "TEXT")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "4.thing")), "TEXT")
    chapters = mm_epub.get_default_chapters(temp_dir)
    assert len(chapters) == 3
    assert chapters[0]["id"] == "item0"
    assert chapters[0]["include"]
    assert chapters[0]["title"] == "1"
    assert basename(chapters[0]["file"]) == "1.txt"
    assert chapters[1]["id"] == "item1"
    assert chapters[1]["include"]
    assert chapters[1]["title"] == "2"
    assert basename(chapters[1]["file"]) == "2.txt"
    assert chapters[2]["id"] == "item2"
    assert chapters[2]["include"]
    assert chapters[2]["title"] == "3"
    assert basename(chapters[2]["file"]) == "3.txt"
    # Test getting default chapter information for one text file with a title
    chapters = mm_epub.get_default_chapters(sub_dir, "Title!")
    assert len(chapters) == 1
    assert chapters[0]["id"] == "item0"
    assert chapters[0]["include"]
    assert chapters[0]["title"] == "Title!"
    assert basename(chapters[0]["file"]) == "sub.txt"

def test_create_content_files():
    """
    Tests the create_content_files function.
    """
    # Create the default chapters list
    temp_dir = mm_file_tools.get_temp_dir()
    output_dir = mm_file_tools.get_temp_dir("dvk-epub-output")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "Here's some text!")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.txt")), "And")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.txt")), "Stuff")
    chapters = mm_epub.get_default_chapters(temp_dir)
    # Test creating the content files from the given chapters
    chapters = mm_epub.create_content_files(chapters, output_dir)
    assert len(chapters) == 3
    assert chapters[0]["include"]
    assert chapters[0]["id"] == "item0"
    assert chapters[0]["title"] == "1"
    assert chapters[0]["file"] == "content/1.xhtml"
    assert chapters[1]["file"] == "content/2.xhtml"
    assert chapters[2]["file"] == "content/3.xhtml"
    content_dir = abspath(join(output_dir, "content"))
    assert sorted(os.listdir(content_dir)) == ["1.xhtml", "2.xhtml", "3.xhtml"]
    text = mm_file_tools.read_text_file(abspath(join(content_dir, "1.xhtml")))
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>1</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>Here's some text!</p>"
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
    compare = f"{compare}body{{\n"
    compare = f"{compare}    margin: 0px 0px 0px 0px;\n"
    compare = f"{compare}}}"
    assert style == compare

def test_create_nav_file():
    """
    Test the create_nav_file function.
    """
    # Create content files to list in the contents
    temp_dir = mm_file_tools.get_temp_dir()
    output_dir = mm_file_tools.get_temp_dir("dvk-epub-output")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "Here's some text!")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.txt")), "And")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.txt")), "Stuff")
    chapters = mm_epub.get_default_chapters(temp_dir)
    chapters = mm_epub.create_content_files(chapters, output_dir)
    # Test creating the nav file
    mm_epub.create_nav_file(chapters, "Title!", output_dir)
    assert sorted(os.listdir(output_dir)) == ["content", "nav.xhtml"]
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
    assert sorted(os.listdir(output_dir)) == ["content", "nav.xhtml"]
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
    # Create content files to list in the contents
    temp_dir = mm_file_tools.get_temp_dir()
    output_dir = mm_file_tools.get_temp_dir("dvk-epub-output")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "Here's some text!")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.txt")), "And")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.txt")), "Stuff")
    chapters = mm_epub.get_default_chapters(temp_dir)
    chapters = mm_epub.create_content_files(chapters, output_dir)
    # Test creating the nav file
    mm_epub.create_ncx_file(chapters, "Title!", "/page/url/", output_dir)
    assert sorted(os.listdir(output_dir)) == ["content", "toc.ncx"]
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
    assert sorted(os.listdir(output_dir)) == ["content", "toc.ncx"]
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
    # Test identifier metadata
    metadata["title"] = "Title."
    metadata["url"] = "this/is/a/test"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
    compare = f"{compare}\n    <dc:date>0000-00-00T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
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
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    # Test writer metadata
    metadata["writer"] = "Person!"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:creator id=\"author-0\">Person!</dc:creator>"
    compare = f"{compare}\n    <meta refines=\"author-0\" property=\"role\" scheme=\"marc:relators\">aut</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    metadata["writer"] = "Multiple,People"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
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
    metadata["writer"] = None
    metadata["cover_artist"] = "Guest"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:creator id=\"cover-artist-0\">Guest</dc:creator>"
    compare = f"{compare}\n    <meta refines=\"cover-artist-0\" property=\"role\" scheme=\"marc:relators\">cov</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    metadata["writer"] = None
    metadata["cover_artist"] = "Other,Folks"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
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
    metadata["cover_artist"] = None
    metadata["artist"] = "Bleh"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:creator id=\"illustrator-0\">Bleh</dc:creator>"
    compare = f"{compare}\n    <meta refines=\"illustrator-0\" property=\"role\" scheme=\"marc:relators\">ill</meta>"
    compare = f"{compare}\n</metadata>"
    assert xml == compare
    metadata["artist"] = "Other,Name"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
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
    metadata["artist"] = None
    metadata["publisher"] = "Company"
    xml = mm_epub.get_metadata_xml(metadata)
    compare = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"
    compare = f"{compare}\n    <dc:language>en</dc:language>"
    compare = f"{compare}\n    <meta property=\"dcterms:modified\">0000-00-00T00:30:00Z</meta>"
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
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
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
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
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
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
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
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
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
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
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
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
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
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
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
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
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
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
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
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
    compare = f"{compare}\n    <dc:identifier id=\"id\">this/is/a/test</dc:identifier>"
    compare = f"{compare}\n    <dc:date>2023-01-15T00:00:00+00:00</dc:date>"
    compare = f"{compare}\n    <dc:title>Title.</dc:title>"
    compare = f"{compare}\n    <dc:description>This &amp; That</dc:description>"
    compare = f"{compare}\n    <dc:publisher>Company</dc:publisher>"
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
    chapters = mm_epub.get_default_chapters(temp_dir)
    chapters = mm_epub.create_content_files(chapters, output_dir)
    # Get manifest xml
    xml = mm_epub.get_manifest_xml(chapters)
    compare = ""
    compare = f"{compare}<manifest>"
    compare = f"{compare}\n    <item href=\"content/1.xhtml\" id=\"item0\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n    <item href=\"content/2.xhtml\" id=\"item1\" media-type=\"application/xhtml+xml\" />"
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
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.txt")), "And")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.txt")), "Stuff")
    chapters = mm_epub.get_default_chapters(temp_dir)
    chapters = mm_epub.create_content_files(chapters, output_dir)
    # Test creating the opf file
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Thing!"
    mm_epub.create_content_opf(chapters, metadata, output_dir)
    assert sorted(os.listdir(output_dir)) == ["content", "content.opf"]
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
    compare = f"{compare}\n    </metadata>"
    compare = f"{compare}\n    <manifest>"
    compare = f"{compare}\n        <item href=\"content/1.xhtml\" id=\"item0\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n        <item href=\"content/2.xhtml\" id=\"item1\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n        <item href=\"content/3.xhtml\" id=\"item2\" media-type=\"application/xhtml+xml\" />"
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
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.txt")), "And")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.pdf")), "Stuff")
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
    assert sorted(os.listdir(epub_directory)) == ["content", "content.opf", "nav.xhtml", "original", "style", "toc.ncx"]
    # Check the contents of the content folder
    content_directory = abspath(join(epub_directory, "content"))
    assert sorted(os.listdir(content_directory)) == ["1.xhtml", "2.xhtml"]
    # Check the contents of the original directory
    original_directory = abspath(join(epub_directory, "original"))
    assert sorted(os.listdir(original_directory)) == ["1.txt", "2.txt", "3.pdf"]
    # Check the contents of the style directory
    style_directory = abspath(join(epub_directory, "style"))
    assert sorted(os.listdir(style_directory)) == ["epubstyle.css"]
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
    compare = f"{compare}\n    </metadata>"
    compare = f"{compare}\n    <manifest>"
    compare = f"{compare}\n        <item href=\"content/1.xhtml\" id=\"item0\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n        <item href=\"content/2.xhtml\" id=\"item1\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}\n        <item href=\"style/epubstyle.css\" id=\"epubstyle\" media-type=\"text/css\" />"
    compare = f"{compare}\n        <item href=\"nav.xhtml\" id=\"nav\" media-type=\"application/xhtml+xml\" properties=\"nav\" />"
    compare = f"{compare}\n        <item href=\"toc.ncx\" id=\"ncx\" media-type=\"application/x-dtbncx+xml\" />"
    compare = f"{compare}\n    </manifest>"
    compare = f"{compare}\n    <spine toc=\"ncx\">"
    compare = f"{compare}\n        <itemref idref=\"item0\" />"
    compare = f"{compare}\n        <itemref idref=\"item1\" />"
    compare = f"{compare}\n    </spine>"
    compare = f"{compare}\n</package>"
    assert content == compare
