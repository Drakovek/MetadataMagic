#!/usr/bin/env python3

import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.xhtml_formatting as mm_xhtml
from os.path import abspath, exists, join
from PIL import Image

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
    compare = f"{compare}\n        <p>This is a thing.<br />"
    compare = f"{compare}\n            <br />Final thing.</p>"
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
    compare = f"{compare}\n        <p>thing <a href=\"a\"> other </a>"
    compare = f"{compare}\n        </p>"
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
    compare = f"{compare}\n        <p />"
    compare = f"{compare}\n        <center>----</center>"
    compare = f"{compare}\n        <div>*SNAP*</div>"
    compare = f"{compare}\n        <div>"
    compare = f"{compare}\n            <center>****</center>"
    compare = f"{compare}\n        </div>"
    compare = f"{compare}\n        <div>"
    compare = f"{compare}\n            <center>*-- -- --*</center>"
    compare = f"{compare}\n        </div>"
    compare = f"{compare}\n        <p />"
    compare = f"{compare}\n        <center>****</center>"
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

def test_text_to_xhtml():
    """
    Tests the text_to_xhtml function.
    """
    # Test a single paragraph
    text = " Just a sentence! "
    assert mm_xhtml.text_to_xhtml(text) == "<p>Just a sentence!</p>"
    # Test combining lines into paragraph
    text = "This is a thing\non multiple \nlines."
    assert mm_xhtml.text_to_xhtml(text) == "<p>This is a thing on multiple lines.</p>"
    text = "What\n\rabout\n\rcarriage\n\rreturns?"
    assert mm_xhtml.text_to_xhtml(text) == "<p>What about carriage returns?</p>"
    # Test paragraphs separated by spaces or tabs
    text = " Some\n text.\n     And more\ntext!  "
    assert mm_xhtml.text_to_xhtml(text) == "<p>Some text.</p><p>And more text!</p>"
    text = "A string \r\n line. \r\n\t And another."
    assert mm_xhtml.text_to_xhtml(text) == "<p>A string line.</p><p>And another.</p>"
    text = "Some\n\tMore\n\tlines\t!"
    assert mm_xhtml.text_to_xhtml(text) == "<p>Some</p><p>More</p><p>lines    !</p>"
    # Test paragraphs separated by new lines
    text = " These. \n\n Are \n\n\n\n Paragraphs!"
    assert mm_xhtml.text_to_xhtml(text) == "<p>These.</p><p>Are</p><p>Paragraphs!</p>"
    text = "One\r\nparagraph.\r\n\r\nSecond\r\nparagraph."
    assert mm_xhtml.text_to_xhtml(text) == "<p>One paragraph.</p><p>Second paragraph.</p>"
    # Test with escape characters
    text = "This & that.\n\n>.>"
    assert mm_xhtml.text_to_xhtml(text) == "<p>This &#38; that.</p><p>&#62;.&#62;</p>"
    # Test with existing html
    text = "This & <i>that.</i>\n\nBlah"
    assert mm_xhtml.text_to_xhtml(text, False) == "<p>This & <i>that.</i></p><p>Blah</p>"

def test_txt_to_xhtml():
    """
    Tests the txt_to_xhtml function.
    """
    # Test a single paragraph
    temp_dir = mm_file_tools.get_temp_dir()
    text_file = abspath(join(temp_dir, "Text.txt"))
    text = "This is a simple sentence!"
    mm_file_tools.write_text_file(text_file, text)
    assert exists(text_file)
    xml = mm_xhtml.txt_to_xhtml(text_file)
    assert xml == "<p>This is a simple sentence!</p>"
    # Test multiple paragraphs
    text = "Different paragraphs!\n\nHow cool!"
    mm_file_tools.write_text_file(text_file, text)
    xml = mm_xhtml.txt_to_xhtml(text_file)
    assert xml == "<p>Different paragraphs!</p><p>How cool!</p>"
    # Test single new line character with HTML escape entities
    text = "More text!\nAnd This & That..."
    mm_file_tools.write_text_file(text_file, text)
    xml = mm_xhtml.txt_to_xhtml(text_file)
    assert xml == "<p>More text! And This &#38; That...</p>"
    # Test new lines and separate paragraphs
    text = "Paragraph\n\nOther\nText!\n\nFinal\nParagraph..."
    mm_file_tools.write_text_file(text_file, text)
    xml = mm_xhtml.txt_to_xhtml(text_file)
    assert xml == "<p>Paragraph</p><p>Other Text!</p><p>Final Paragraph...</p>"
    # Test with more than one two new lines
    text = "Thing\n\n\r\n\r\n\nOther\r"
    mm_file_tools.write_text_file(text_file, text)
    xml = mm_xhtml.txt_to_xhtml(text_file)
    assert xml == "<p>Thing</p><p>Other</p>"

def test_html_to_xml():
    """
    Tests the html_to_xhtml function.
    """
    # Test with no formatting.
    temp_dir = mm_file_tools.get_temp_dir()
    html_file = abspath(join(temp_dir, "HTML.html"))
    text = "<p>This is a simple sentence!</p>"
    mm_file_tools.write_text_file(html_file, text)
    assert exists(html_file)
    xml = mm_xhtml.html_to_xhtml(html_file)
    assert xml == "<p>This is a simple sentence!</p>"
    # Test with multiple paragraphs
    text = "<html><p>Some text.</p><p>&amp; More!</p></html>"
    mm_file_tools.write_text_file(html_file, text)
    xml = mm_xhtml.html_to_xhtml(html_file)
    assert xml == "<p>Some text.</p><p>&#38; More!</p>"
    # Test with a body
    text = "<!DOCTYPE html>\n<html>\n<body>\n<p>New.</p>\n<p>Words</p>\n<body>\n</html>"
    mm_file_tools.write_text_file(html_file, text)
    xml = mm_xhtml.html_to_xhtml(html_file)
    assert xml == "<p>New.</p><p>Words</p>"
    # Test with newlines and no formatting
    text = "This is a test.\n\r\r\n\nHopefully nothing added."
    mm_file_tools.write_text_file(html_file, text)
    xml = mm_xhtml.html_to_xhtml(html_file)
    assert xml == "<p>This is a test.Hopefully nothing added.</p>"
    # Test with DeviantArt formatting
    text = "<!DOCTYPE html><html><head>Not at all relevant</head><body>"
    text = f"{text}<div class='blah'>Random metadata and stuff.</div><span>Other things</span>"
    text = f"{text}<div  class='text'><p>This is the real stuff.</p><p>Right<br>Here.</p>"
    text = f"{text}<script type'thing'>Blah</script><p>More.<p></div>"
    text = f"{text}</body></html>"
    mm_file_tools.write_text_file(html_file, text)
    xml = mm_xhtml.html_to_xhtml(html_file)
    assert xml == "<p>This is the real stuff.</p><p>Right<br/>Here.</p><p>More.</p><p/>"
    # Test with text in a <pre> element
    text = "<html><body><p>Thing</p><pre>    This &\nthat!\n    <b>Another!</b></pre></body></html>"
    mm_file_tools.write_text_file(html_file, text)
    xml = mm_xhtml.html_to_xhtml(html_file)
    assert xml == "<p>Thing</p><p>This &#38; that!</p><p><b>Another!</b></p>"
    # Test if HTML contains only line breaks and no proper <p> or <div> containers
    text = "No<br/>\r\n     Paragraphs.<br/> <br/> Just<br/>breaks."
    mm_file_tools.write_text_file(html_file, text)
    xml = mm_xhtml.html_to_xhtml(html_file)
    assert xml == "<p>No Paragraphs.</p><p>Just breaks.</p>"

def test_image_to_xml():
    """
    Tests the image_to_xhtml function.
    """
    # Test getting image as XML
    temp_dir = mm_file_tools.get_temp_dir()
    image_file = abspath(join(temp_dir, "image.png"))
    image = Image.new("RGB", size=(600, 800), color="#ff0000")
    image.save(image_file)
    assert exists(image_file)
    xml = mm_xhtml.image_to_xhtml(image_file)
    assert xml == "<div><img src=\"../images/image.png\" alt=\"image\" width=\"600\" height=\"800\" /></div>"
    # Different dimensions and an alt tag
    image_file = abspath(join(temp_dir, "[01] Other's.jpg"))
    image = Image.new("RGB", size=(350, 200), color="#ff0000")
    image.save(image_file)
    assert exists(image_file)
    xml = mm_xhtml.image_to_xhtml(image_file, "Some Name")
    assert xml == "<div><img src=\"../images/[01] Other's.jpg\" alt=\"Some Name\" width=\"350\" height=\"200\" /></div>"
    # Test with a non-image file
    image_file = abspath(join(temp_dir, "notimage.jpg"))
    mm_file_tools.write_text_file(image_file, "not an image")
    assert mm_xhtml.image_to_xhtml(image_file) == ""

def test_get_title_from_file():
    """
    Tests the get_title_from_file function.
    """
    temp_file = mm_file_tools.get_temp_dir()
    filename = abspath(join(temp_file, "thing.txt"))
    assert mm_xhtml.get_title_from_file(filename) == "thing"
    filename = abspath(join(temp_file, "[00] Image  .png"))
    assert mm_xhtml.get_title_from_file(filename) == "Image"
    filename = abspath(join(temp_file, "(This is a thing) Cover"))
    assert mm_xhtml.get_title_from_file(filename) == "Cover"
    filename = abspath(join(temp_file, "[Not Number) Thing.txt"))
    assert mm_xhtml.get_title_from_file(filename) == "[Not Number) Thing"
    filename = abspath(join(temp_file, "  1 [2] (3).html"))
    assert mm_xhtml.get_title_from_file(filename) == "1 [2] (3)"
    filename = abspath(join(temp_file, "none"))
    assert mm_xhtml.get_title_from_file(filename) == "none"