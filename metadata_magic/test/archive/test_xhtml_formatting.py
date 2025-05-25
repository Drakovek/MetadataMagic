#!/usr/bin/env python3

import tempfile
import metadata_magic.test as mm_test
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.xhtml_formatting as mm_xhtml
from os.path import abspath, exists, join

def test_format_xhtml():
    """
    Tests the format_xhtml function.
    """
    # Test single paragraph tag
    html = "<p>This is a simple test &amp; stuff</p>"
    xhtml = mm_xhtml.format_xhtml(html, "Title!")
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
    xhtml = mm_xhtml.format_xhtml(html, "Title!")
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
    xhtml = mm_xhtml.format_xhtml(html, "Title thing.")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Title thing.</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>This is a thing.<br /><br />Final thing.</p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    # Test with spaces and newlines
    html = "  <p>  This is a thing!  </p>\n  <div> Another </div>"
    html = f"{html}<p class='thing'>  Next  < / p> <div id='1'> Final < / div>  "
    html = f"{html}<p> thing <a href='a'> other </a> </p>"
    xhtml = mm_xhtml.format_xhtml(html, "Next Title")
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
    compare = f"{compare}\n        <p class=\"thing\">Next</p>"
    compare = f"{compare}\n        <div id=\"1\">Final</div>"
    compare = f"{compare}\n        <p>thing <a href=\"a\"> other </a></p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    # Test Removing non-breaking space characters
    html = "  <p> &nbsp; Thing &nbsp;&nbsp; </p>\n  &nbsp;<div id='blah'> Another &nbsp;</div> "
    xhtml = mm_xhtml.format_xhtml(html, "Non-breaking")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Non-breaking</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>Thing</p>"
    compare = f"{compare}\n        <div id=\"blah\">Another</div>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    # Test removing extraneous paragraph and div tags
    html = "<p/><div/><p/><p>This is fine</p> <p> </p> <div> </div> <div>Blah</div> <p class='thing'>\n"
    html = f"{html}</p> <div id='other'> </div> <p /> <div /> <p class='a' /> <div id='final' />"
    xhtml = mm_xhtml.format_xhtml(html, "Remove Space")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Remove Space</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>This is fine</p>"
    compare = f"{compare}\n        <div>Blah</div>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    # Test centering lines consisting entirely of hyphens or astericks
    html = "<p>A-Z</p><p> ---- </p><div>*SNAP*</div><div> **** </div><div>*-- -- --*</div><p>****</p>"
    xhtml = mm_xhtml.format_xhtml(html, "Lines")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Lines</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>A-Z</p>"
    compare = f"{compare}\n        <p><center>----</center></p>"
    compare = f"{compare}\n        <div>*SNAP*</div>"
    compare = f"{compare}\n        <div>"
    compare = f"{compare}\n            <center>****</center>"
    compare = f"{compare}\n        </div>"
    compare = f"{compare}\n        <div>"
    compare = f"{compare}\n            <center>*-- -- --*</center>"
    compare = f"{compare}\n        </div>"
    compare = f"{compare}\n        <p><center>****</center></p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    # Test hyphen or asterix between tags
    html = "<a>Thing</a> - <a href='other'>Other</a> * <a>Last</a>"
    xhtml = mm_xhtml.format_xhtml(html, "Lines")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Lines</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <a>Thing</a> - <a href=\"other\">Other</a> * <a>Last</a>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    # Test altering image wrapper for a single image
    html = "<div><img src=\"../images/thing's.jpg\" alt=\"thing's\" width=\"600\" height=\"800\"/></div>"
    xhtml = mm_xhtml.format_xhtml(html, "Single's Image")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns:svgns=\"http://www.w3.org/2000/svg\" "
    compare = f"{compare}xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Single's Image</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <div id=\"full-image-container\">"
    compare = f"{compare}\n            <svgns:svg width=\"100%\" height=\"100%\" "
    compare = f"{compare}viewBox=\"0 0 600 800\" preserveAspectRatio=\"xMidYMid meet\" version=\"1.1\">"
    compare = f"{compare}\n                <svgns:title>thing's</svgns:title>"
    compare = f"{compare}\n                <svgns:image xlink:href=\"../images/thing's.jpg\" width=\"600\" height=\"800\" />"
    compare = f"{compare}\n            </svgns:svg>"
    compare = f"{compare}\n        </div>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    # Test that the image wrapper is not altered if there is text alongside the image
    html = f"<div class='blah'>Some words!</div>{html}<div id='A'>And such</div>"
    xhtml = mm_xhtml.format_xhtml(html, "Single's Image")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Single's Image</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <div class=\"blah\">Some words!</div>"
    compare = f"{compare}\n        <div>"
    compare = f"{compare}\n            <img src=\"../images/thing's.jpg\" alt=\"thing's\" width=\"600\" height=\"800\" />"
    compare = f"{compare}\n        </div>"
    compare = f"{compare}\n        <div id=\"A\">And such</div>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    html = "<div><img src=\"../images/new.png\" alt=\"Other\" width=\"200\" height=\"200\"/></div>"
    html = f"<p>Some words!</p>{html}<p>And such</p>"
    xhtml = mm_xhtml.format_xhtml(html, "Single's Image")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Single's Image</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <p>Some words!</p>"
    compare = f"{compare}\n        <div>"
    compare = f"{compare}\n            <img src=\"../images/new.png\" alt=\"Other\" width=\"200\" height=\"200\" />"
    compare = f"{compare}\n        </div>"
    compare = f"{compare}\n        <p>And such</p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare 
    html = "<div><img src=\"../images/thing.jpg\" alt=\"thing\" width=\"600\" height=\"800\"/></div>"
    html = f"{html}<p id='other'>Something Else</p>"
    xhtml = mm_xhtml.format_xhtml(html, "Single's")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Single's</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <div>"
    compare = f"{compare}\n            <img src=\"../images/thing.jpg\" alt=\"thing\" width=\"600\" height=\"800\" />"
    compare = f"{compare}\n        </div>"
    compare = f"{compare}\n        <p id=\"other\">Something Else</p>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare
    # Test that image wrapper is not altered with multiple image files
    html = "<div><img src=\"../images/thing.jpg\" alt=\"thing\" width=\"600\" height=\"800\"/></div>"
    html = f"{html}<div><img src=\"../images/other.jpg\" alt=\"other\" width=\"1200\" height=\"750\"/></div>"
    xhtml = mm_xhtml.format_xhtml(html, "Single Image")
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    compare = f"{compare}\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}\n    <head>"
    compare = f"{compare}\n        <title>Single Image</title>"
    compare = f"{compare}\n        <meta charset=\"utf-8\" />"
    compare = f"{compare}\n        <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}\n    </head>"
    compare = f"{compare}\n    <body>"
    compare = f"{compare}\n        <div>"
    compare = f"{compare}\n            <img src=\"../images/thing.jpg\" alt=\"thing\" width=\"600\" height=\"800\" />"
    compare = f"{compare}\n        </div>"
    compare = f"{compare}\n        <div>"
    compare = f"{compare}\n            <img src=\"../images/other.jpg\" alt=\"other\" width=\"1200\" height=\"750\" />"
    compare = f"{compare}\n        </div>"
    compare = f"{compare}\n    </body>"
    compare = f"{compare}\n</html>"
    assert xhtml == compare

def test_clean_html():
    """
    Tests the clean_html function
    """
    # Test formatting HTML with basic HTML structure with head & body
    html_file = abspath(join(mm_test.BASIC_HTML_DIRECTORY, "basic.html"))
    xml = mm_xhtml.clean_html(html_file, add_smart_quotes=False)
    assert xml == "<p>This text is basic.</p><p><hr /></p><p>More Text</p>"
    # Test formatting individual paragraph elements, as necessary
    html_file = abspath(join(mm_test.BASIC_HTML_DIRECTORY, "badformat.html"))
    xml = mm_xhtml.clean_html(html_file, add_smart_quotes=False)
    compare = "<p>This is all a <i>single</i> paragraph!</p>"
    compare = f"{compare}<p>This is a separate paragraph.</p>"
    compare = f"{compare}<p>Badly <i>formatted</i> paragraph.</p>"
    compare = f"{compare}<p>This should be <b>separate!</b></p>"
    compare = f"{compare}<p>This is fine as one</p>"
    assert xml == compare
    # Test getting html in the DeviantArt liturature format
    html_file = abspath(join(mm_test.BASIC_HTML_DIRECTORY, "deviantart.htm"))
    xml = mm_xhtml.clean_html(html_file, add_smart_quotes=False)
    assert xml == "<p>This is the real stuff.</p><p>Right Here.</p><p>More.</p>"
    # Test formatting text that is not HTML
    html_file = abspath(join(mm_test.BASIC_TEXT_DIRECTORY, "unicode.txt"))
    xml = mm_xhtml.clean_html(html_file, add_smart_quotes=False)
    assert xml == "<p>This is ünicode.</p>"
    # Test adding smart quotes
    html_file = abspath(join(mm_test.BASIC_HTML_DIRECTORY, "unformatted.html"))
    xml = mm_xhtml.clean_html(html_file, add_smart_quotes=True)
    assert xml == "<p>“This is text”</p><p>‘This is more text’</p>"

def test_image_to_xml():
    """
    Tests the image_to_xhtml function.
    """
    # Test getting an image as XML with no alt tag
    image_file = abspath(join(mm_test.PAIR_IMAGE_DIRECTORY, "bare.png"))
    xml = mm_xhtml.image_to_xhtml(image_file)
    assert xml == "<div><img src=\"../images/bare.png\" alt=\"bare\" width=\"300\" height=\"200\" /></div>"
    # Test getting an image as XML with an alt tag
    image_file = abspath(join(mm_test.PAIR_IMAGE_DIRECTORY, "long.JPG"))
    xml = mm_xhtml.image_to_xhtml(image_file, "[00] AAA'A")
    assert xml == "<div><img src=\"../images/long.JPG\" alt=\"[00] AAA'A\" width=\"50\" height=\"250\" /></div>"
    # Test loading a non-image file
    image_file = abspath(join(mm_test.PAIR_IMAGE_DIRECTORY, "long.JSON"))
    assert mm_xhtml.image_to_xhtml(image_file, "BBB") == ""

def test_get_title_from_file():
    """
    Tests the get_title_from_file function.
    """
    temp_dir = abspath(tempfile.gettempdir())
    filename = abspath(join(temp_dir, "thing.txt"))
    assert mm_xhtml.get_title_from_file(filename) == "thing"
    filename = abspath(join(temp_dir, "[00] Image  .png"))
    assert mm_xhtml.get_title_from_file(filename) == "Image"
    filename = abspath(join(temp_dir, "(This is a thing) Cover"))
    assert mm_xhtml.get_title_from_file(filename) == "Cover"
    filename = abspath(join(temp_dir, "[Not Number) Thing.txt"))
    assert mm_xhtml.get_title_from_file(filename) == "[Not Number) Thing"
    filename = abspath(join(temp_dir, "  1 [2] (3).html"))
    assert mm_xhtml.get_title_from_file(filename) == "1 [2] (3)"
    filename = abspath(join(temp_dir, "none"))
    assert mm_xhtml.get_title_from_file(filename) == "none"

def test_get_word_count_from_html():
    """
    Tests the get_word_count_from_html function.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test with low word count
        html_file = abspath(join(temp_dir, "text.html"))
        mm_file_tools.write_text_file(html_file, "<p>Some words.</p>")
        assert mm_xhtml.get_word_count_from_html(html_file) == 2
        mm_file_tools.write_text_file(html_file, "<p>Some <i>more</i> <a href='b'>words.</a></p>")
        assert mm_xhtml.get_word_count_from_html(html_file) == 3
        mm_file_tools.write_text_file(html_file, "<p class='a'>Something else entirely.</p>")
        assert mm_xhtml.get_word_count_from_html(html_file) == 3
        mm_file_tools.write_text_file(html_file, "<p>A</p><div>blah<div><p>B C D</p>")
        assert mm_xhtml.get_word_count_from_html(html_file) == 4
        # Test with high word count
        paragraph = "AAA " * 50
        paragraph = f"<p>{paragraph}</p>"
        html = f"<ol>Thing</ol>{paragraph}{paragraph}{paragraph}"
        mm_file_tools.write_text_file(html_file, html)
        assert mm_xhtml.get_word_count_from_html(html_file) == 150
        # Test with non-ascii characters
        mm_file_tools.write_text_file(html_file, "<p>Thís shóuldn't bréak.</p>")
        assert mm_xhtml.get_word_count_from_html(html_file) == 3
        # Test with no words
        mm_file_tools.write_text_file(html_file, "<html><div>nothing here</div></html>")
        assert mm_xhtml.get_word_count_from_html(html_file) == 0
        mm_file_tools.write_text_file(html_file, "Not HTML text.")
        assert mm_xhtml.get_word_count_from_html(html_file) == 0
