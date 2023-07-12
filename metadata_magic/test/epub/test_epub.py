#!/usr/bin/env python3

from os import mkdir, listdir
from os.path import abspath, basename, exists, isdir, join
from metadata_magic.main.file_tools.file_tools import get_temp_dir
from metadata_magic.main.meta_reader import get_empty_metadata
from metadata_magic.main.epub.epub import create_epub
from metadata_magic.main.epub.epub import create_epub_files
from metadata_magic.main.epub.epub import create_image_page
from metadata_magic.main.epub.epub import create_nav_file
from metadata_magic.main.epub.epub import create_ncx_file
from metadata_magic.main.epub.epub import create_manifest
from metadata_magic.main.epub.epub import create_metadata_xml
from metadata_magic.main.epub.epub import create_style_file
from metadata_magic.main.epub.epub import get_title_from_file
from metadata_magic.main.epub.epub import html_to_xhtml
from metadata_magic.main.epub.epub import format_xhtml
from metadata_magic.main.epub.epub import newline_to_tag
from metadata_magic.main.epub.epub import txt_to_xhtml
from metadata_magic.main.rename.rename_tools import sort_alphanum
from metadata_magic.main.file_tools.file_tools import write_text_file, read_text_file
from PIL import Image
from zipfile import ZipFile

def test_newline_to_tag():
    """
    Tests the newline_to_tag function.
    """
    assert newline_to_tag("\n") == "{{{br}}}"
    assert newline_to_tag("\n\n\n") == "{{{br}}}{{{br}}}{{{br}}}"
    assert newline_to_tag("\n\n\n\n\n") == "{{{br}}}{{{br}}}{{{br}}}{{{br}}}{{{br}}}"
    assert newline_to_tag("\n\n") == "{{{br}}}{{{br}}}"

def test_get_title_from_file():
    """
    Tests the get_title_from_file function.
    """
    temp_file = get_temp_dir()
    filename = abspath(join(temp_file, "thing.txt"))
    assert get_title_from_file(filename) == "thing"
    filename = abspath(join(temp_file, "[00] Image  .png"))
    assert get_title_from_file(filename) == "Image"
    filename = abspath(join(temp_file, "[This is a thing] Cover"))
    assert get_title_from_file(filename) == "Cover"
    filename = abspath(join(temp_file, "none"))
    assert get_title_from_file(filename) == "none"

def test_format_xhtml():
    """
    Tests the format_xhtml function.
    """
    # Test single tag
    start = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    head = "<head><title>Title!</title><meta charset=\"utf-8\" />"
    head = f"{head}<link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" /></head>"
    html = "<p>This is a simple test &amp; stuff</p>"
    xhtml = format_xhtml(html, "Title!", indent=False)
    assert xhtml == f"{start}{head}<body><p>This is a simple test &amp; stuff</p></body></html>"
    # Test with multiple tags
    html = "<p>Multiple</p><p>Paragraphs!!!</p>"
    xhtml = format_xhtml(html, "Title!", indent=False)
    assert xhtml == f"{start}{head}<body><p>Multiple</p><p>Paragraphs!!!</p></body></html>"
    # Test with no tags
    head = "<head><title>Title thing.</title><meta charset=\"utf-8\" />"
    head = f"{head}<link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" /></head>"
    html = "This is a thing.<br/><br/>Final thing."
    xhtml = format_xhtml(html, "Title thing.", indent=False)
    assert xhtml == f"{start}{head}<body>This is a thing.<br /><br />Final thing.</body></html>"
    # Test with spaces and newlines
    html = "  <p>  This is a thing!  </p>\n  <div> Another </div> "
    xhtml = format_xhtml(html, "Title thing.", indent=False)
    assert xhtml == f"{start}{head}<body><p>  This is a thing!  </p>  <div> Another </div></body></html>"
    # Test header tags
    html="<p>bleh</p>"
    tags = [{"type":"thing", "params":{"class":"name"}}, {"type":"meta", "params":{"item":"other"}}]
    xhtml = format_xhtml(html, "Name", tags, indent=False)
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\"><head>"
    compare = f"{compare}<title>Name</title><meta charset=\"utf-8\" />"
    compare = f"{compare}<thing class=\"name\" /><meta item=\"other\" />"
    compare = f"{compare}<link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    compare = f"{compare}</head><body><p>bleh</p></body></html>"
    assert xhtml == compare
    # Test adding indent
    html = "<p>These</p><p>Are</p><p>Paragraphs!</p>"
    xhtml = format_xhtml(html, "New", indent=True)
    xml = f"{start}\n"
    xml = f"{xml}   <head>\n"
    xml = f"{xml}      <title>New</title>\n"
    xml = f"{xml}      <meta charset=\"utf-8\" />\n"
    xml = f"{xml}      <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />\n"
    xml = f"{xml}   </head>\n"
    xml = f"{xml}   <body>\n"
    xml = f"{xml}      <p>These</p>\n"
    xml = f"{xml}      <p>Are</p>\n"
    xml = f"{xml}      <p>Paragraphs!</p>\n"
    xml = f"{xml}   </body>\n"
    xml = f"{xml}</html>"
    assert xml == xhtml

def test_create_image_page():
    """
    Tests the create_image_page function.
    """
    # Create image files
    temp_dir = get_temp_dir()
    png_file = abspath(join(temp_dir, "[00] Cover.png"))
    jpg_file = abspath(join(temp_dir, "thing.jpg"))
    png_image = Image.new("RGB", (360, 480), color=(255,0,0))
    jpg_image = Image.new("RGB", (500, 300), color=(0,255,0))
    png_image.save(png_file)
    jpg_image.save(jpg_file)
    assert exists(png_file)
    assert exists(jpg_file)
    # Test with vertical image
    chapter = create_image_page(png_file, False)
    body = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    body = f"{body}<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    body = f"{body}<head><title>Cover</title><meta charset=\"utf-8\" />"
    body = f"{body}<meta content=\"width=360, height=480\" name=\"viewport\" />"
    body = f"{body}<link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    body = f"{body}</head><body><div class=\"image-page-container\">"
    body = f"{body}<img class=\"vertical-image-page\" src=\"../images/[00] Cover.png\" alt=\"Cover\" />"
    body = f"{body}</div></body></html>"
    assert chapter == body
    # Test with horizontal image
    chapter = create_image_page(jpg_file, False)
    body = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    body = f"{body}<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    body = f"{body}<head><title>thing</title><meta charset=\"utf-8\" />"
    body = f"{body}<meta content=\"width=500, height=300\" name=\"viewport\" />"
    body = f"{body}<link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    body = f"{body}</head><body><div class=\"image-page-container\">"
    body = f"{body}<img class=\"horizontal-image-page\" src=\"../images/thing.jpg\" alt=\"thing\" />"
    body = f"{body}</div></body></html>"
    assert chapter == body
    # Test with invalid image file
    text_file = abspath(join(temp_dir, "thing.png"))
    write_text_file(text_file, "Some Text")
    assert exists(text_file)
    assert create_image_page(text_file) is None
    assert create_image_page("/non/existant/thing.png") is None
    # Test with indents
    chapter = create_image_page(jpg_file, True)
    body = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    body = f"{body}<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
    body = f"{body}   <head>\n"
    body = f"{body}      <title>thing</title>\n"
    body = f"{body}      <meta charset=\"utf-8\" />\n"
    body = f"{body}      <meta content=\"width=500, height=300\" name=\"viewport\" />\n"
    body = f"{body}      <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />\n"
    body = f"{body}   </head>\n"
    body = f"{body}   <body>\n"
    body = f"{body}      <div class=\"image-page-container\">\n"
    body = f"{body}         <img class=\"horizontal-image-page\" src=\"../images/thing.jpg\" alt=\"thing\" />\n"
    body = f"{body}      </div>\n"
    body = f"{body}   </body>\n"
    body = f"{body}</html>"
    assert chapter == body

def test_html_to_xhtml():
    """
    Tests the html_to_xml function.
    """
    # Test HTML inside a body
    temp_dir = get_temp_dir()
    html_file = abspath(join(temp_dir, "thing.html"))
    text = "<!DOCTYPE html><html><body><p>This is text!</p><br><p><b>YAY!</b></p></body></html>"
    write_text_file(html_file, text)
    assert exists(html_file)
    contents = html_to_xhtml(html_file, indent=False)
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\"><head>"
    compare = f"{compare}<title>thing</title><meta charset=\"utf-8\" />"
    compare = f"{compare}<link rel=\"stylesheet\" href=\"../style/epubstyle.css\" "
    compare = f"{compare}type=\"text/css\" /></head><body>"
    compare = f"{compare}<div class=\"text-container\"><p>This is text!</p>"
    compare = f"{compare}<br /><p><b>YAY!</b></p></div></body></html>"
    assert contents == compare
    # Test simple HTML with no body
    html_file = abspath(join(temp_dir, "New.htm"))
    text = "<b>A thing</b> and Thing.<hr>Other!"
    write_text_file(html_file, text)
    assert exists(html_file)
    contents = html_to_xhtml(html_file, indent=False)
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}<head><title>New</title><meta charset=\"utf-8\" />"
    compare = f"{compare}<link rel=\"stylesheet\" href=\"../style/epubstyle.css\" "
    compare = f"{compare}type=\"text/css\" /></head><body>"
    compare = f"{compare}<div class=\"text-container\"><b>A thing</b> and Thing."
    compare = f"{compare}<hr />Other!</div></body></html>"
    assert contents == compare
    # Test adding indents
    html_file = abspath(join(temp_dir, "Final.htm"))
    text = "Some Words..."
    write_text_file(html_file, text)
    assert exists(html_file)
    contents = html_to_xhtml(html_file, indent=True)
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
    compare = f"{compare}   <head>\n"
    compare = f"{compare}      <title>Final</title>\n"
    compare = f"{compare}      <meta charset=\"utf-8\" />\n"
    compare = f"{compare}      <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />\n"
    compare = f"{compare}   </head>\n"
    compare = f"{compare}   <body>\n"
    compare = f"{compare}      <div class=\"text-container\">\n"
    compare = f"{compare}         <p>Some Words...</p>\n"
    compare = f"{compare}      </div>\n"
    compare = f"{compare}   </body>\n"
    compare = f"{compare}</html>"
    assert contents == compare

def test_txt_to_xhtml():
    """
    Tests the txt_to_xhtml function.
    """
    # Test a single paragraph
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "Text.txt"))
    text = "This is a simple sentence!"
    write_text_file(text_file, text)
    assert exists(text_file)
    chapter = txt_to_xhtml(text_file, indent=False)
    head = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    head = f"{head}<html xmlns=\"http://www.w3.org/1999/xhtml\"><head>"
    head = f"{head}<title>Text</title><meta charset=\"utf-8\" />"
    head = f"{head}<link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />"
    head = f"{head}</head>"
    body = f"{head}<body><div class=\"text-container\">"
    body = f"{body}<p>This is a simple sentence!</p></div></body></html>"
    assert chapter == body
    # Test multiple paragraphs
    text = "Different paragraphs!\n\nHow cool!"
    write_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file, False)
    body = f"{head}<body><div class=\"text-container\">"
    body = f"{body}<p>Different paragraphs!</p><p>How cool!</p></div></body></html>"
    assert chapter == body
    # Test single new line character
    text = "More text!\nAnd This & That..."
    write_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file, False)
    body = f"{head}<body><div class=\"text-container\">"
    body = f"{body}<p>More text!<br />And This &amp; That...</p></div></body></html>"
    assert chapter == body
    # Test new lines and separate paragraphs
    text = "Paragraph\n\nOther\nText!\n\nFinal\nParagraph..."
    write_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file, False)
    body = f"{head}<body><div class=\"text-container\">"
    body = f"{body}<p>Paragraph</p><p>Other<br />Text!</p>"
    body = f"{body}<p>Final<br />Paragraph...</p></div></body></html>"
    assert chapter == body
    # Test with more than one two new lines
    text = "Thing\n\n\nOther"
    write_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file, False)
    body = "<body><div class=\"text-container\"><p>Thing<br/><br/><br/>Other</p></div></body>"
    body = f"{head}<body><div class=\"text-container\">"
    body = f"{body}<p>Thing<br /><br /><br />Other</p></div></body></html>"
    assert chapter == body
    text = "Thing\n\n\nOther\n\nParagraph\n\n\n\nNext"
    write_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file, False)
    body = f"{head}<body><div class=\"text-container\">"
    body = f"{body}<p>Thing<br /><br /><br />Other</p>"
    body = f"{body}<p>Paragraph<br /><br /><br /><br />Next</p></div></body></html>"
    assert chapter == body
    # Test removing text stand-ins for HTML tags
    text = "{{i}}Title{{/i}}{{br}}{{b}}Thing{{/b}}"
    write_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file, False)
    body = f"{head}<body><div class=\"text-container\">"
    body = f"{body}<p><i>Title</i><br /><b>Thing</b></p></div></body></html>"
    assert chapter == body
    # Remove dangling paragraph tags
    text = "Text  \n\nThing {{br}} {{br}}"
    write_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file, False)
    body = f"{head}<body><div class=\"text-container\">"
    body = f"{body}<p>Text</p><p>Thing</p></div></body></html>"
    assert chapter == body
    # Remove dangling italic/bold tags tags
    text = "This is a {{b}}fine{{/b}} sentence."
    write_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file, False)
    body = f"{head}<body><div class=\"text-container\">"
    body = f"{body}<p>This is a <b>fine</b> sentence.</p></div></body></html>"
    assert chapter == body
    text = "Some {{b}}words {{/b}} , should {{i}}change{{/i}}  ."
    write_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file, False)
    body = f"{head}<body><div class=\"text-container\">"
    body = f"{body}<p>Some <b>words</b>, should <i>change</i>.</p></div></body></html>"
    assert chapter == body
    # Test with indent
    text = "These are...\n\nwords."
    text_file = abspath(join(temp_dir, "[01] New Thing.txt"))
    write_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file, True)
    body = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    body = f"{body}<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
    body = f"{body}   <head>\n"
    body = f"{body}      <title>New Thing</title>\n"
    body = f"{body}      <meta charset=\"utf-8\" />\n"
    body = f"{body}      <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />\n"
    body = f"{body}   </head>\n"
    body = f"{body}   <body>\n"
    body = f"{body}      <div class=\"text-container\">\n"
    body = f"{body}         <p>These are...</p>\n"
    body = f"{body}         <p>words.</p>\n"
    body = f"{body}      </div>\n"
    body = f"{body}   </body>\n"
    body = f"{body}</html>"
    assert chapter == body

def test_create_style_file():
    """
    Tests the create_style_file function()
    """
    temp_dir = get_temp_dir()
    css_file = abspath(join(temp_dir, "epubstyle.css"))
    assert not exists(css_file)
    create_style_file(css_file)
    assert exists(css_file)
    # Test contents of the css file
    style = read_text_file(css_file)
    compare = "body {\n"
    compare = f"{compare}    margin: 0px 0px 0px 0px;\n"
    compare = f"{compare}}}\n\n"
    compare = f"{compare}.header {{\n"
    compare = f"{compare}    width: 100%;\n"
    compare = f"{compare}    font-size: 2em;\n"
    compare = f"{compare}    line-height: 1.5em;\n"
    compare = f"{compare}}}\n\n"
    compare = f"{compare}.subheader {{\n"
    compare = f"{compare}    width: 100%;\n"
    compare = f"{compare}    font-size: 1.5em;\n"
    compare = f"{compare}    line-height: 1.5em;\n"
    compare = f"{compare}}}\n\n"
    compare = f"{compare}.center {{\n"
    compare = f"{compare}    text-align: center;\n"
    compare = f"{compare}}}\n\n"
    compare = f"{compare}.text-container {{\n"
    compare = f"{compare}    margin: 3em 3em 3em 3em;\n"
    compare = f"{compare}    line-height: 1.5em;\n"
    compare = f"{compare}}}\n\n"
    compare = f"{compare}.vertical-image-page {{\n"
    compare = f"{compare}    display: block;\n"
    compare = f"{compare}    height: 100%;\n"
    compare = f"{compare}    width: auto;\n"
    compare = f"{compare}    margin: auto auto auto auto;\n"
    compare = f"{compare}}}\n\n"
    compare = f"{compare}.horizontal-image-page {{\n"
    compare = f"{compare}    display: block;\n"
    compare = f"{compare}    width: 100%;\n"
    compare = f"{compare}    height: auto;\n"
    compare = f"{compare}    margin: auto auto auto auto;\n"
    compare = f"{compare}}}\n\n"
    compare = f"{compare}.image-page-container {{\n"
    compare = f"{compare}    height: 100vh;\n"
    compare = f"{compare}}}"
    assert style == compare

def test_create_nav_file():
    """
    Tests the create_nav_file function.
    """
    # Test creating nav file
    xhtmls = []
    temp_dir = get_temp_dir()
    xhtmls.append(abspath(join(temp_dir, "[00] Cover.xhtml")))
    xhtmls.append(abspath(join(temp_dir, "Chapter 1.xhtml")))
    xhtmls.append(abspath(join(temp_dir, "Chapter 2.xhtml")))
    xhtmls.append(abspath(join(temp_dir, "Epilogues.xhtml")))
    nav_file = abspath(join(temp_dir, "nav.xhtml"))
    assert not exists(nav_file)
    create_nav_file(xhtmls, nav_file, "Name of thing!", False)
    assert exists(nav_file)
    content = read_text_file(nav_file)
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:epub=\"http://www.idpf.org/2007/ops\" lang=\"en\" xml:lang=\"en\">"
    compare = f"{compare}<head><meta charset=\"utf-8\" /><title>Name of thing!</title></head>"
    compare = f"{compare}<body><h1>Name of thing!</h1><nav epub:type=\"toc\" id=\"toc\">"
    compare = f"{compare}<ol><li><a href=\"content/[00] Cover.xhtml\">Cover</a></li>"
    compare = f"{compare}<li><a href=\"content/Chapter 1.xhtml\">Chapter 1</a></li>"
    compare = f"{compare}<li><a href=\"content/Chapter 2.xhtml\">Chapter 2</a></li>"
    compare = f"{compare}<li><a href=\"content/Epilogues.xhtml\">Epilogues</a></li>"
    compare = f"{compare}</ol></nav></body></html>"
    assert content == compare
    # Test creating nav file with indents
    xhtmls = [abspath(join(temp_dir, "[3] Cover.xhtml"))]
    create_nav_file(xhtmls, nav_file, "Other thing", True)
    content = read_text_file(nav_file)
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:epub=\"http://www.idpf.org/2007/ops\" lang=\"en\" xml:lang=\"en\">\n"
    compare = f"{compare}   <head>\n"
    compare = f"{compare}      <meta charset=\"utf-8\" />\n"
    compare = f"{compare}      <title>Other thing</title>\n"
    compare = f"{compare}   </head>\n"
    compare = f"{compare}   <body>\n"
    compare = f"{compare}      <h1>Other thing</h1>\n"
    compare = f"{compare}      <nav epub:type=\"toc\" id=\"toc\">\n"
    compare = f"{compare}         <ol>\n"
    compare = f"{compare}            <li>\n"
    compare = f"{compare}               <a href=\"content/[3] Cover.xhtml\">Cover</a>\n"
    compare = f"{compare}            </li>\n"
    compare = f"{compare}         </ol>\n"
    compare = f"{compare}      </nav>\n"
    compare = f"{compare}   </body>\n"
    compare = f"{compare}</html>"
    assert content == compare

def test_create_ncx_file():
    """
    Tests the create_ncx_file function.
    """
    # Test creating ncx file
    xhtmls = []
    temp_dir = get_temp_dir()
    xhtmls.append(abspath(join(temp_dir, "[00] Cover.xhtml")))
    xhtmls.append(abspath(join(temp_dir, "Chapter 1.xhtml")))
    xhtmls.append(abspath(join(temp_dir, "Chapter 2.xhtml")))
    xhtmls.append(abspath(join(temp_dir, "Epilogues.xhtml")))
    ncx_file = abspath(join(temp_dir, "toc.ncx"))
    assert not exists(ncx_file)
    create_ncx_file(xhtmls, ncx_file, "Name of thing!", "UNIQUE-id", False)
    assert exists(ncx_file)
    content = read_text_file(ncx_file)
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    compare = f"{compare}<ncx xmlns=\"http://www.daisy.org/z3986/2005/ncx/\" version=\"2005-1\">"
    compare = f"{compare}<head><meta content=\"UNIQUE-id\" name=\"dtb:uid\" />"
    compare = f"{compare}<meta content=\"0\" name=\"dtb:depth\" />"
    compare = f"{compare}<meta content=\"0\" name=\"dtb:totalPageCount\" />"
    compare = f"{compare}<meta content=\"0\" name=\"dtb:maxPageNumber\" /></head>"
    compare = f"{compare}<docTitle><text>Name of thing!</text></docTitle><navMap>"
    compare = f"{compare}<navPoint id=\"Cover-xhtml\"><navLabel><text>Cover</text></navLabel>"
    compare = f"{compare}<content>content/[00] Cover.xhtml</content></navPoint>"
    compare = f"{compare}<navPoint id=\"Chapter 1-xhtml\"><navLabel><text>Chapter 1</text></navLabel>"
    compare = f"{compare}<content>content/Chapter 1.xhtml</content></navPoint>"
    compare = f"{compare}<navPoint id=\"Chapter 2-xhtml\"><navLabel><text>Chapter 2</text></navLabel>"
    compare = f"{compare}<content>content/Chapter 2.xhtml</content></navPoint>"
    compare = f"{compare}<navPoint id=\"Epilogues-xhtml\"><navLabel><text>Epilogues</text></navLabel>"
    compare = f"{compare}<content>content/Epilogues.xhtml</content></navPoint></navMap></ncx>"
    assert content == compare
    # Test creating ncx file with indents
    xhtmls = [abspath(join(temp_dir, "[3] Cover.xhtml"))]
    create_ncx_file(xhtmls, ncx_file, "Other thing", "new-uid", True)
    content = read_text_file(ncx_file)
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    compare = f"{compare}<ncx xmlns=\"http://www.daisy.org/z3986/2005/ncx/\" version=\"2005-1\">\n"
    compare = f"{compare}   <head>\n"
    compare = f"{compare}      <meta content=\"new-uid\" name=\"dtb:uid\" />\n"
    compare = f"{compare}      <meta content=\"0\" name=\"dtb:depth\" />\n"
    compare = f"{compare}      <meta content=\"0\" name=\"dtb:totalPageCount\" />\n"
    compare = f"{compare}      <meta content=\"0\" name=\"dtb:maxPageNumber\" />\n"
    compare = f"{compare}   </head>\n"
    compare = f"{compare}   <docTitle>\n"
    compare = f"{compare}      <text>Other thing</text>\n"
    compare = f"{compare}   </docTitle>\n"
    compare = f"{compare}   <navMap>\n"
    compare = f"{compare}      <navPoint id=\"Cover-xhtml\">\n"
    compare = f"{compare}         <navLabel>\n"
    compare = f"{compare}            <text>Cover</text>\n"
    compare = f"{compare}         </navLabel>\n"
    compare = f"{compare}         <content>content/[3] Cover.xhtml</content>\n"
    compare = f"{compare}      </navPoint>\n"
    compare = f"{compare}   </navMap>\n"
    compare = f"{compare}</ncx>"
    assert content == compare

def test_create_manifest():
    """
    Tests the create_manifest function.
    """
    files = []
    temp_dir = get_temp_dir()
    files.append(abspath(join(temp_dir, "[03] Cover.xhtml")))
    files.append(abspath(join(temp_dir, "Picture.png")))
    files.append(abspath(join(temp_dir, "[02] Jpeg!.jpg")))
    files.append(abspath(join(temp_dir, "Thing.svg")))
    manifest = create_manifest(files)
    compare = "<manifest>"
    compare = f"{compare}<item href=\"nav.xhtml\" id=\"toc\" media-type=\"application/xhtml+xml\" properties=\"nav\" />"
    compare = f"{compare}<item href=\"content/[03] Cover.xhtml\" id=\"Cover-xhtml\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}<item href=\"images/Picture.png\" id=\"Picture-png\" media-type=\"image/png\" />"
    compare = f"{compare}<item href=\"images/[02] Jpeg!.jpg\" id=\"Jpeg!-jpg\" media-type=\"image/jpeg\" />"
    compare = f"{compare}<item href=\"images/Thing.svg\" id=\"Thing-svg\" media-type=\"image/svg+xml\" />"
    compare = f"{compare}<item href=\"style/epubstyle.css\" id=\"epubstyle-css\" media-type=\"text/css\" />"
    compare = f"{compare}</manifest>"
    assert manifest == compare

def test_create_metadata_xml():
    """
    Tests the create_metadata_xml function.
    """
    # Test setting title in the XML file
    start = "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\"><dc:language>en</dc:language>"
    end = "<meta property=\"dcterms:modified\">0000-00-00T00:00:00+00:00</meta>"
    end = f"{end}<dc:date>0000-00-00T00:00:00+00:00</dc:date></metadata>"
    meta = get_empty_metadata()
    meta["title"] = "This's a title\\'"
    xml = create_metadata_xml(meta)
    compare = f"{start}<dc:identifier>this's a title\\'</dc:identifier>"
    compare = f"{compare}<dc:title>This's a title\\'</dc:title>{end}"
    assert xml == compare
    # Test setting identifier in the XML file
    base_meta = get_empty_metadata()
    base_meta["url"] = "this/is/a/test"
    base_meta["title"] = "Title."
    start = f"{start}<dc:identifier>this/is/a/test</dc:identifier>"
    start = f"{start}<dc:title>Title.</dc:title>"
    xml = create_metadata_xml(base_meta)
    assert xml == f"{start}{end}"
    # Test setting description in the XML file
    meta = base_meta
    meta["description"] = "Description of the thing."
    xml = create_metadata_xml(meta)
    assert xml == f"{start}<dc:description>Description of the thing.</dc:description>{end}"
    meta["description"] = "'Tis this & That's >.<"
    xml = create_metadata_xml(meta)
    assert xml == f"{start}<dc:description>'Tis this &amp; That's &gt;.&lt;</dc:description>{end}"
    # Test setting writer() in XML file
    meta["description"] = None
    meta["writer"] = "Person!"
    xml = create_metadata_xml(meta)
    compare = f"{start}<dc:creator id=\"author1\">Person!</dc:creator>"
    compare = f"{compare}<meta refines=\"#author1\" property=\"role\" scheme=\"marc:relators\">aut</meta>"
    assert xml == f"{compare}{end}"
    meta["writer"] = "More,People"
    xml = create_metadata_xml(meta)
    compare = f"{start}<dc:creator id=\"author1\">More</dc:creator>"
    compare = f"{compare}<meta refines=\"#author1\" property=\"role\" scheme=\"marc:relators\">aut</meta>"
    compare = f"{compare}<dc:creator id=\"author2\">People</dc:creator>"
    compare = f"{compare}<meta refines=\"#author2\" property=\"role\" scheme=\"marc:relators\">aut</meta>"
    assert xml == f"{compare}{end}"
    # Test setting cover artist in XML file
    meta["writer"] = None
    meta["cover_artist"] = "Guest"
    xml = create_metadata_xml(meta)
    compare = f"{start}<dc:creator id=\"covartist1\">Guest</dc:creator>"
    compare = f"{compare}<meta refines=\"#covartist1\" property=\"role\" scheme=\"marc:relators\">cov</meta>"
    assert xml == f"{compare}{end}"
    meta["cover_artist"] = "Other,Folks"
    xml = create_metadata_xml(meta)
    compare = f"{start}<dc:creator id=\"covartist1\">Other</dc:creator>"
    compare = f"{compare}<meta refines=\"#covartist1\" property=\"role\" scheme=\"marc:relators\">cov</meta>"
    compare = f"{compare}<dc:creator id=\"covartist2\">Folks</dc:creator>"
    compare = f"{compare}<meta refines=\"#covartist2\" property=\"role\" scheme=\"marc:relators\">cov</meta>"
    assert xml == f"{compare}{end}"
    # Test setting illustrator in XML file
    meta["cover_artist"] = None
    meta["artist"] = "Bleh"
    xml = create_metadata_xml(meta)
    compare = f"{start}<dc:creator id=\"illustrator1\">Bleh</dc:creator>"
    compare = f"{compare}<meta refines=\"#illustrator1\" property=\"role\" scheme=\"marc:relators\">ill</meta>"
    assert xml == f"{compare}{end}"
    meta["artist"] = "Other,Artist"
    xml = create_metadata_xml(meta)
    compare = f"{start}<dc:creator id=\"illustrator1\">Other</dc:creator>"
    compare = f"{compare}<meta refines=\"#illustrator1\" property=\"role\" scheme=\"marc:relators\">ill</meta>"
    compare = f"{compare}<dc:creator id=\"illustrator2\">Artist</dc:creator>"
    compare = f"{compare}<meta refines=\"#illustrator2\" property=\"role\" scheme=\"marc:relators\">ill</meta>"
    assert xml == f"{compare}{end}"
    # Test setting publisher in XML file
    meta["artist"] = None
    meta["publisher"] = "Company"
    xml = create_metadata_xml(meta)
    compare = f"{start}<dc:publisher>Company</dc:publisher>{end}"
    assert xml == compare
    # Test setting date in the XML file
    meta["publisher"] = None
    meta["date"] = "2023-01-15"
    xml = create_metadata_xml(meta)
    end = "<meta property=\"dcterms:modified\">2023-01-15T00:00:00+00:00</meta>"
    end = f"{end}<dc:date>2023-01-15T00:00:00+00:00</dc:date></metadata>"
    assert xml == f"{start}{end}"
    meta["date"] = "2014-12-08"
    xml = create_metadata_xml(meta)
    end = "<meta property=\"dcterms:modified\">2014-12-08T00:00:00+00:00</meta>"
    end = f"{end}<dc:date>2014-12-08T00:00:00+00:00</dc:date></metadata>"
    assert xml == f"{start}{end}"
    # Test setting series info in the XML file
    meta["series"] = "Name!!"
    meta["series_number"] = "2.5"
    meta["series_total"] = "5"
    xml = create_metadata_xml(meta)
    compare = f"{start}<meta property=\"belongs-to-collection\" id=\"series-title\">Name!!</meta>"
    compare = f"{compare}<meta refines=\"series-title\" property=\"collection-type\">series</meta>"
    compare = f"{compare}<meta refines=\"series-title\" property=\"group-position\">2.5</meta>{end}"
    assert xml == compare
    # Test setting invalid series number
    meta["series_number"] = "NotNumber"
    xml = create_metadata_xml(meta)
    compare = f"{start}<meta property=\"belongs-to-collection\" id=\"series-title\">Name!!</meta>"
    compare = f"{compare}<meta refines=\"series-title\" property=\"collection-type\">series</meta>{end}"
    assert xml == compare
    # Test setting tags in XML file
    meta["series"] = None
    meta["series_number"] = None
    meta["tags"] = "Some,Tags,&,stuff"
    xml = create_metadata_xml(meta)
    compare = f"{start}<dc:subject>Some</dc:subject>"
    compare = f"{compare}<dc:subject>Tags</dc:subject>"
    compare = f"{compare}<dc:subject>&amp;</dc:subject>"
    compare = f"{compare}<dc:subject>stuff</dc:subject>{end}"
    assert xml == compare
    # Test setting the score in the XML file
    meta["tags"] = None
    meta["score"] = "0"
    xml = create_metadata_xml(meta)
    assert xml == f"{start}<meta property=\"calibre:rating\">0.0</meta>{end}"
    meta["score"] = "2"
    xml = create_metadata_xml(meta)
    compare = f"{start}<meta property=\"calibre:rating\">4.0</meta>"
    compare = f"{compare}<dc:subject>&#9733;&#9733;</dc:subject>{end}"
    assert xml == compare
    meta["score"] = "5"
    xml = create_metadata_xml(meta)
    compare = f"{start}<meta property=\"calibre:rating\">10.0</meta>"
    compare = f"{compare}<dc:subject>&#9733;&#9733;&#9733;&#9733;&#9733;</dc:subject>{end}"
    assert xml == compare
    # Test setting invalid score in XML file
    meta["score"] = "Blah"
    xml = create_metadata_xml(meta)
    assert xml == f"{start}{end}"
    meta["score"] = "6"
    xml = create_metadata_xml(meta)
    assert xml == f"{start}{end}"
    meta["score"] = "-3"
    xml = create_metadata_xml(meta)
    assert xml == f"{start}{end}"
    # Test adding score as tags
    meta["tags"] = "These,are,things"
    meta["score"] = "3"
    xml = create_metadata_xml(meta)
    compare = f"{start}<meta property=\"calibre:rating\">6.0</meta>"
    compare = f"{compare}<dc:subject>&#9733;&#9733;&#9733;</dc:subject>"
    compare = f"{compare}<dc:subject>These</dc:subject>"
    compare = f"{compare}<dc:subject>are</dc:subject>"
    compare = f"{compare}<dc:subject>things</dc:subject>{end}"
    assert xml == compare
    meta["score"] = "5"
    meta["tags"] = None
    xml = create_metadata_xml(meta)
    compare = f"{start}<meta property=\"calibre:rating\">10.0</meta>"
    compare = f"{compare}<dc:subject>&#9733;&#9733;&#9733;&#9733;&#9733;</dc:subject>{end}"
    assert xml == compare
    meta["score"] = "0"
    xml = create_metadata_xml(meta)
    assert xml == f"{start}<meta property=\"calibre:rating\">0.0</meta>{end}"

def test_create_epub_files():
    """
    Tests the create_epub_files function.
    """
    # Create test files
    temp_dir = get_temp_dir()
    content = abspath(join(temp_dir, "content"))
    images = abspath(join(temp_dir, "images"))
    mkdir(content)
    mkdir(images)
    assert isdir(content) and exists(content)
    cover_page = abspath(join(content, "[00] Cover.xhtml"))
    chapter_page = abspath(join(content, "[01] Chapter1.xhtml"))
    cover_image = abspath(join(images, "cover.png"))
    internal_image = abspath(join(images, "other.jpeg"))
    write_text_file(cover_page, "Doesn't")
    write_text_file(chapter_page, "Really")
    write_text_file(cover_image, "Matter")
    write_text_file(internal_image, "To Me")
    assert exists(cover_page)
    assert exists(chapter_page)
    assert exists(cover_image)
    assert exists(internal_image)
    # Create content file
    metadata = get_empty_metadata()
    metadata["title"] = "Experimental Title"
    metadata["url"] = "thing/page/"
    metadata["date"] = "2020-04-02"
    nav_file = abspath(join(temp_dir, "nav.xhtml"))
    ncx_file = abspath(join(temp_dir, "toc.ncx"))
    content_file = abspath(join(temp_dir, "content.opf"))
    create_epub_files(temp_dir, metadata)
    # Test that nav file is correct
    assert exists(nav_file)
    contents = read_text_file(nav_file)
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\" "
    compare = f"{compare}xmlns:epub=\"http://www.idpf.org/2007/ops\" lang=\"en\" xml:lang=\"en\">\n"
    compare = f"{compare}   <head>\n"
    compare = f"{compare}      <meta charset=\"utf-8\" />\n"
    compare = f"{compare}      <title>Experimental Title</title>\n"
    compare = f"{compare}   </head>\n"
    compare = f"{compare}   <body>\n"
    compare = f"{compare}      <h1>Experimental Title</h1>\n"
    compare = f"{compare}      <nav epub:type=\"toc\" id=\"toc\">\n"
    compare = f"{compare}         <ol>\n"
    compare = f"{compare}            <li>\n"
    compare = f"{compare}               <a href=\"content/[00] Cover.xhtml\">Cover</a>\n"
    compare = f"{compare}            </li>\n"
    compare = f"{compare}            <li>\n"
    compare = f"{compare}               <a href=\"content/[01] Chapter1.xhtml\">Chapter1</a>\n"
    compare = f"{compare}            </li>\n"
    compare = f"{compare}         </ol>\n"
    compare = f"{compare}      </nav>\n"
    compare = f"{compare}   </body>\n"
    compare = f"{compare}</html>"
    assert contents == compare
    # Test that ncx file is correct
    assert exists(ncx_file)
    contents = read_text_file(ncx_file)
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    compare = f"{compare}<ncx xmlns=\"http://www.daisy.org/z3986/2005/ncx/\" version=\"2005-1\">\n"
    compare = f"{compare}   <head>\n"
    compare = f"{compare}      <meta content=\"thing/page/\" name=\"dtb:uid\" />\n"
    compare = f"{compare}      <meta content=\"0\" name=\"dtb:depth\" />\n"
    compare = f"{compare}      <meta content=\"0\" name=\"dtb:totalPageCount\" />\n"
    compare = f"{compare}      <meta content=\"0\" name=\"dtb:maxPageNumber\" />\n"
    compare = f"{compare}   </head>\n"
    compare = f"{compare}   <docTitle>\n"
    compare = f"{compare}      <text>Experimental Title</text>\n"
    compare = f"{compare}   </docTitle>\n"
    compare = f"{compare}   <navMap>\n"
    compare = f"{compare}      <navPoint id=\"Cover-xhtml\">\n"
    compare = f"{compare}         <navLabel>\n"
    compare = f"{compare}            <text>Cover</text>\n"
    compare = f"{compare}         </navLabel>\n"
    compare = f"{compare}         <content>content/[00] Cover.xhtml</content>\n"
    compare = f"{compare}      </navPoint>\n"
    compare = f"{compare}      <navPoint id=\"Chapter1-xhtml\">\n"
    compare = f"{compare}         <navLabel>\n"
    compare = f"{compare}            <text>Chapter1</text>\n"
    compare = f"{compare}         </navLabel>\n"
    compare = f"{compare}         <content>content/[01] Chapter1.xhtml</content>\n"
    compare = f"{compare}      </navPoint>\n"
    compare = f"{compare}   </navMap>\n"
    compare = f"{compare}</ncx>"
    assert contents == compare
    # Test that package file is correct
    assert exists(content_file)
    contents = read_text_file(content_file)
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    compare = f"{compare}<package xmlns:dc=\"http://purl.org/dc/elements/1.1/\" "
    compare = f"{compare}xmlns=\"http://www.idpf.org/2007/opf\" unique-identifier=\"uid\" version=\"3.0\">\n"
    compare = f"{compare}   <metadata>\n"
    compare = f"{compare}      <dc:language>en</dc:language>\n"
    compare = f"{compare}      <dc:identifier>thing/page/</dc:identifier>\n"
    compare = f"{compare}      <dc:title>Experimental Title</dc:title>\n"
    compare = f"{compare}      <meta property=\"dcterms:modified\">2020-04-02T00:00:00+00:00</meta>\n"
    compare = f"{compare}      <dc:date>2020-04-02T00:00:00+00:00</dc:date>\n"
    compare = f"{compare}   </metadata>\n"
    compare = f"{compare}   <manifest>\n"
    compare = f"{compare}      <item href=\"nav.xhtml\" id=\"toc\" media-type=\"application/xhtml+xml\" properties=\"nav\" />\n"
    compare = f"{compare}      <item href=\"content/[00] Cover.xhtml\" id=\"Cover-xhtml\" media-type=\"application/xhtml+xml\" />\n"
    compare = f"{compare}      <item href=\"content/[01] Chapter1.xhtml\" id=\"Chapter1-xhtml\" media-type=\"application/xhtml+xml\" />\n"
    compare = f"{compare}      <item href=\"images/cover.png\" id=\"cover-png\" media-type=\"image/png\" />\n"
    compare = f"{compare}      <item href=\"images/other.jpeg\" id=\"other-jpeg\" media-type=\"image/jpeg\" />\n"
    compare = f"{compare}      <item href=\"style/epubstyle.css\" id=\"epubstyle-css\" media-type=\"text/css\" />\n"
    compare = f"{compare}   </manifest>\n"
    compare = f"{compare}   <spine>\n"
    compare = f"{compare}      <itemref idref=\"Cover-xhtml\" />\n"
    compare = f"{compare}      <itemref idref=\"Chapter1-xhtml\" />\n"
    compare = f"{compare}   </spine>\n"
    compare = f"{compare}</package>"
    assert contents == compare

def test_create_epub():
    """
    Tests the create_epub function.
    """
    # Create test files
    temp_dir = get_temp_dir()
    json = abspath(join(temp_dir, "blah.json"))
    text_page = abspath(join(temp_dir, "Text.txt"))
    html_page = abspath(join(temp_dir, "Html.htm"))
    cover_file = abspath(join(temp_dir, "[00] Cover.png"))
    internal_file = abspath(join(temp_dir, "Other.jpeg"))
    write_text_file(json, "Some thing")
    write_text_file(html_page, "<p>Some things</p>")
    write_text_file(text_page, "This is some text!!!")
    cover_image = Image.new("RGB", (100, 200), color=(255,0,0))
    internal_image = Image.new("RGB", (500, 300), color=(0,255,0))
    cover_image.save(cover_file)
    internal_image.save(internal_file)
    assert exists(json)
    assert exists(text_page)
    assert exists(html_page)
    assert exists(cover_file)
    assert exists(internal_file)
    # Attempt to create an epub archive
    metadata = get_empty_metadata()
    metadata["title"] = "New Title."
    epub = create_epub(temp_dir, metadata)
    assert exists(epub)
    assert basename(epub) == "dvk_meta_magic.epub"
    # Extract epub and check its contents
    extract_dir = abspath(join(temp_dir, "ext"))
    mkdir(extract_dir)
    with ZipFile(epub, mode="r") as file:
        file.extractall(path=extract_dir)
    files = sort_alphanum(listdir(extract_dir))
    assert files == ["EPUB", "META-INF", "mimetype"]
    # Check the contents of the EPUB folder
    epub_dir = abspath(join(extract_dir, "EPUB"))
    files = sort_alphanum(listdir(epub_dir))
    assert files == ["content", "content.opf", "images", "nav.xhtml", "original", "style", "toc.ncx"]
    # Check the contents of the "original" folder
    original_folder = abspath(join(epub_dir, "original"))
    files = sort_alphanum(listdir(original_folder))
    assert files == ["[00] Cover.png", "blah.json", "Html.htm", "Other.jpeg", "Text.txt"]
    # Check the contents of the "content" folder
    content_folder = abspath(join(epub_dir, "content"))
    files = sort_alphanum(listdir(content_folder))
    assert files == ["[00] Cover.xhtml", "Html.xhtml", "Other.xhtml", "Text.xhtml"]
    # Check the contents of the cover image xhtml
    xml = read_text_file(abspath(join(content_folder, "[00] Cover.xhtml")))
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
    compare = f"{compare}   <head>\n"
    compare = f"{compare}      <title>Cover</title>\n"
    compare = f"{compare}      <meta charset=\"utf-8\" />\n"
    compare = f"{compare}      <meta content=\"width=100, height=200\" name=\"viewport\" />\n"
    compare = f"{compare}      <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />\n"
    compare = f"{compare}   </head>\n"
    compare = f"{compare}   <body>\n"
    compare = f"{compare}      <div class=\"image-page-container\">\n"
    compare = f"{compare}         <img class=\"vertical-image-page\" src=\"../images/[00] Cover.png\" alt=\"Cover\" />\n"
    compare = f"{compare}      </div>\n"
    compare = f"{compare}   </body>\n"
    compare = f"{compare}</html>"
    assert xml == compare
    # Check the contents of the other image xhtml
    xml = read_text_file(abspath(join(content_folder, "Other.xhtml")))
    compare = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
    compare = f"{compare}   <head>\n"
    compare = f"{compare}      <title>Other</title>\n"
    compare = f"{compare}      <meta charset=\"utf-8\" />\n"
    compare = f"{compare}      <meta content=\"width=500, height=300\" name=\"viewport\" />\n"
    compare = f"{compare}      <link rel=\"stylesheet\" href=\"../style/epubstyle.css\" type=\"text/css\" />\n"
    compare = f"{compare}   </head>\n"
    compare = f"{compare}   <body>\n"
    compare = f"{compare}      <div class=\"image-page-container\">\n"
    compare = f"{compare}         <img class=\"horizontal-image-page\" src=\"../images/Other.jpeg\" alt=\"Other\" />\n"
    compare = f"{compare}      </div>\n"
    compare = f"{compare}   </body>\n"
    compare = f"{compare}</html>"
    assert xml == compare
    # Check the contents of the "images" folder
    content_folder = abspath(join(epub_dir, "images"))
    files = sort_alphanum(listdir(content_folder))
    assert files == ["[00] Cover.png", "Other.jpeg"]
    # Check the contents of the "style" folder
    content_folder = abspath(join(epub_dir, "style"))
    files = sort_alphanum(listdir(content_folder))
    assert files == ["epubstyle.css"]
