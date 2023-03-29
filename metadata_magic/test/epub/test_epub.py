#!/usr/bin/env python3

from ebooklib.epub import EpubHtml
from os import mkdir, listdir
from os.path import abspath, basename, exists, isdir, join
from PIL import Image
from metadata_magic.main.comic_archive.comic_archive import get_temp_dir
from metadata_magic.main.comic_archive.comic_xml import get_empty_metadata
from metadata_magic.main.epub.epub import get_chapters
from metadata_magic.main.epub.epub import get_items
from metadata_magic.main.epub.epub import get_style
from metadata_magic.main.epub.epub import get_title_from_file
from metadata_magic.main.epub.epub import create_epub
from metadata_magic.main.epub.epub import create_image_page
from metadata_magic.main.epub.epub import create_metadata
from metadata_magic.main.epub.epub import newline_to_tag
from metadata_magic.main.epub.epub import txt_to_xhtml
from metadata_magic.main.rename.sort_rename import sort_alphanum
from metadata_magic.test.temp_file_tools import create_text_file, read_text_file
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
    chapter = create_image_page(png_file)
    body = "<body><div class=\"image-page-container\">"
    body = f"{body}<img class=\"vertical-image-page\" "
    body = f"{body}src=\"../images/[00] Cover.png\" alt=\"Cover\" />"
    body = f"{body}</div></body>"
    assert chapter.content == body
    links = []
    for link in chapter.get_links(): links.append(link)
    assert links == [{"href":"../style/epubstyle.css", "rel":"stylesheet", "type":"text/css"}]
    metas = []
    for meta in chapter.get_metas(): metas.append(meta)
    assert metas == [{"content":"width=360, height=480", "name":"viewport"}]
    # Test with horizontal image
    chapter = create_image_page(jpg_file)
    body = "<body><div class=\"image-page-container\">"
    body = f"{body}<img class=\"horizontal-image-page\" src=\"../images/thing.jpg\" alt=\"thing\" />"
    body = f"{body}</div></body>"
    assert chapter.content == body
    links = []
    for link in chapter.get_links(): links.append(link)
    assert links == [{"href":"../style/epubstyle.css", "rel":"stylesheet", "type":"text/css"}]
    metas = []
    for meta in chapter.get_metas(): metas.append(meta)
    assert metas == [{"content":"width=500, height=300", "name":"viewport"}]
    # Test with invalid image file
    text_file = abspath(join(temp_dir, "thing.png"))
    create_text_file(text_file, "Some Text")
    assert exists(text_file)
    assert create_image_page(text_file) is None
    assert create_image_page("/non/existant/thing.png") is None

def test_txt_to_xhtml():
    """
    Tests the txt_to_xhtml function.
    """
    # Test a single paragraph
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "Text.txt"))
    text = "This is a simple sentence!"
    create_text_file(text_file, text)
    assert exists(text_file)
    chapter = txt_to_xhtml(text_file)
    assert isinstance(chapter, EpubHtml)
    body = "<body><div class=\"text-container\">"
    body = f"{body}<p>This is a simple sentence!</p></div></body>"
    assert chapter.content == body
    # Test multiple paragraphs
    text = "Different paragraphs!\n\nHow cool!"
    create_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file)
    assert isinstance(chapter, EpubHtml)
    body = "<body><div class=\"text-container\">"
    body = f"{body}<p>Different paragraphs!</p><p>How cool!</p></div></body>"
    assert chapter.content == body
    # Test single new line character
    text = "More text!\nAnd This & That..."
    create_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file)
    body = "<body><div class=\"text-container\">"
    body = f"{body}<p>More text!<br/>And This &amp; That...</p></div></body>"
    assert chapter.content == body
    # Test new lines and separate paragraphs
    text = "Paragraph\n\nOther\nText!\n\nFinal\nParagraph..."
    create_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file)
    body = "<body><div class=\"text-container\">"
    body = f"{body}<p>Paragraph</p><p>Other<br/>Text!</p>"
    body = f"{body}<p>Final<br/>Paragraph...</p></div></body>"
    assert chapter.content == body
    # Test with more than one two new lines
    text = "Thing\n\n\nOther"
    create_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file)
    body = "<body><div class=\"text-container\"><p>Thing<br/><br/><br/>Other</p></div></body>"
    assert chapter.content == body
    text = "Thing\n\n\nOther\n\nParagraph\n\n\n\nNext"
    create_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file)
    body = "<body><div class=\"text-container\">"
    body = f"{body}<p>Thing<br/><br/><br/>Other</p>"
    body = f"{body}<p>Paragraph<br/><br/><br/><br/>Next</p></div></body>"
    assert chapter.content == body
    # Test removing text stand-ins for HTML tags
    text = "{{i}}Title{{/i}}{{br}}{{b}}Thing{{/b}}"
    create_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file)
    body = "<body><div class=\"text-container\"><p><i>Title</i><br/><b>Thing</b></p></div></body>"
    assert chapter.content == body
    # Remove dangling paragraph tags
    text = "Text  \n\nThing {{br}} {{br}}"
    create_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file)
    body = "<body><div class=\"text-container\"><p>Text</p><p>Thing</p></div></body>"
    assert chapter.content == body
    # Remove dangling italic/bold tags tags
    text = "This is a {{b}}fine{{/b}} sentence."
    create_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file)
    body = "<body><div class=\"text-container\"><p>This is a <b>fine</b> sentence.</p></div></body>"
    assert chapter.content == body
    text = "Some {{b}}words {{/b}} , should {{i}}change{{/i}}  ."
    create_text_file(text_file, text)
    chapter = txt_to_xhtml(text_file)
    body = "<body><div class=\"text-container\"><p>Some <b>words</b>, should <i>change</i>.</p></div></body>"
    assert chapter.content == body

def test_get_style():
    """
    Tests the create_style_file function()
    """
    style = get_style()
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

def test_create_metadata():
    """
    Tests the create_metadata_xml function.
    """
    # Test setting title for the book
    meta = get_empty_metadata()
    meta["title"] = "This's a title\\'"
    book = create_metadata(meta)
    title = book.get_metadata("DC", "title")
    assert title == [("This's a title\\'", None)]
    identifier = book.get_metadata("DC", "identifier")
    assert identifier == [("this's a title\\'", {"id":"id"})]
    # Test setting identifier in the XML file
    meta = get_empty_metadata()
    meta["url"] = "this/is/a/test"
    meta["title"] = "Title."
    book = create_metadata(meta)
    title = book.get_metadata("DC", "title")
    assert title == [("Title.", None)]
    identifier = book.get_metadata("DC", "identifier")
    assert identifier == [("this/is/a/test", {"id":"id"})]
    # Test that language is set
    language = book.get_metadata("DC", "language")
    assert language == [("en", None)]
    # Test setting description in the XML file
    meta["description"] = "Description of the thing."
    book = create_metadata(meta)
    description = book.get_metadata("DC", "description")
    assert description == [("Description of the thing.", None)]
    meta["description"] = "'Tis this & That's >.<"
    book = create_metadata(meta)
    description = book.get_metadata("DC", "description")
    assert description == [("'Tis this & That's >.<", None)]
    # Test setting writer() in XML file
    meta["description"] = None
    meta["writer"] = "Person!"
    book = create_metadata(meta)
    writers = book.get_metadata("DC", "creator")
    refines = book.get_metadata(None, "meta")
    assert writers == [("Person!", {"id":"author0"})]
    assert refines == [("aut", {"refines":"#author0", "property":"role", "scheme":"marc:relators"})]
    meta["writer"] = "More,People"
    book = create_metadata(meta)
    writers = book.get_metadata("DC", "creator")
    refines = book.get_metadata(None, "meta")
    assert len(writers) == 2
    assert writers[0] == ("More", {"id":"author0"})
    assert writers[1] == ("People", {"id":"author1"})
    assert len(refines) == 2
    assert refines[0] == ("aut", {"refines":"#author0", "property":"role", "scheme":"marc:relators"})
    assert refines[1] == ("aut", {"refines":"#author1", "property":"role", "scheme":"marc:relators"})
    # Test setting cover artist in XML file
    meta["writer"] = None
    meta["cover_artist"] = "Guest"
    book = create_metadata(meta)
    writers = book.get_metadata("DC", "creator")
    refines = book.get_metadata(None, "meta")
    assert writers == [("Guest", {"id":"covartist0"})]
    assert refines == [("cov", {"refines":"#covartist0", "property":"role", "scheme":"marc:relators"})]
    meta["cover_artist"] = "Other,Folks"
    book = create_metadata(meta)
    writers = book.get_metadata("DC", "creator")
    refines = book.get_metadata(None, "meta")
    assert len(writers) == 2
    assert writers[0] == ("Other", {"id":"covartist0"})
    assert writers[1] == ("Folks", {"id":"covartist1"})
    assert len(refines) == 2
    assert refines[0] == ("cov", {"refines":"#covartist0", "property":"role", "scheme":"marc:relators"})
    assert refines[1] == ("cov", {"refines":"#covartist1", "property":"role", "scheme":"marc:relators"})
    # Test setting illustrator in XML file
    meta["cover_artist"] = None
    meta["artist"] = "Bleh"
    book = create_metadata(meta)
    writers = book.get_metadata("DC", "creator")
    refines = book.get_metadata(None, "meta")
    assert writers == [("Bleh", {"id":"illustrator0"})]
    assert refines == [("ill", {"refines":"#illustrator0", "property":"role", "scheme":"marc:relators"})]
    meta["artist"] = "Other,Artist"
    book = create_metadata(meta)
    writers = book.get_metadata("DC", "creator")
    refines = book.get_metadata(None, "meta")
    assert len(writers) == 2
    assert writers[0] == ("Other", {"id":"illustrator0"})
    assert writers[1] == ("Artist", {"id":"illustrator1"})
    assert len(refines) == 2
    assert refines[0] == ("ill", {"refines":"#illustrator0", "property":"role", "scheme":"marc:relators"})
    assert refines[1] == ("ill", {"refines":"#illustrator1", "property":"role", "scheme":"marc:relators"})
    # Test setting publisher in XML file
    meta["artist"] = None
    meta["publisher"] = "Company"
    book = create_metadata(meta)
    publisher = book.get_metadata("DC", "publisher")
    assert publisher == [("Company", None)]
    # Test setting date in the XML file
    meta["publisher"] = None
    meta["date"] = "2023-01-15"
    book = create_metadata(meta)
    date = book.get_metadata("DC", "date")
    assert date == [("2023-01-15T00:00:00+00:00", None)]
    meta["date"] = "2014-12-08"
    book = create_metadata(meta)
    date = book.get_metadata("DC", "date")
    assert date == [("2014-12-08T00:00:00+00:00", None)]
    # Test setting series info in the XML file
    meta["series"] = "Name!!"
    meta["series_number"] = "2.5"
    meta["series_total"] = "5"
    book = create_metadata(meta)
    series = book.get_metadata(None, "meta")
    assert len(series) == 3
    assert series[0] == ("Name!!", {"id":"series-title", "property":"belongs-to-collection"})
    assert series[1] == ("series", {"refines":"#series-title", "property":"collection-type"})
    assert series[2] == ("2.5", {"refines":"#series-title", "property":"group-position"})
    # Test setting invalid series number
    meta["series"] = "New Series"
    meta["series_number"] = "NotNumber"
    book = create_metadata(meta)
    series = book.get_metadata(None, "meta")
    assert len(series) == 2
    assert series[0] == ("New Series", {"id":"series-title", "property":"belongs-to-collection"})
    assert series[1] == ("series", {"refines":"#series-title", "property":"collection-type"})
    # Test setting tags in XML file
    meta["series"] = None
    meta["series_number"] = None
    meta["tags"] = "Some,Tags,&,stuff"
    book = create_metadata(meta)
    tags = book.get_metadata("DC", "subject")
    assert len(tags) == 4
    assert tags[0] == ("Some", None)
    assert tags[1] == ("Tags", None)
    assert tags[2] == ("&", None)
    assert tags[3] == ("stuff", None)
    # Test setting the score in the XML file
    meta["tags"] = None
    meta["score"] = "0"
    book = create_metadata(meta)
    scores = book.get_metadata(None, "meta")
    assert scores == [("0.0", {"property":"calibre:rating"})]
    meta["score"] = "2"
    book = create_metadata(meta)
    scores = book.get_metadata(None, "meta")
    tags = book.get_metadata("DC", "subject")
    assert scores == [("4.0", {"property":"calibre:rating"})]
    assert tags == [("★★", None)]
    meta["score"] = "5"
    book = create_metadata(meta)
    scores = book.get_metadata(None, "meta")
    tags = book.get_metadata("DC", "subject")
    assert scores == [("10.0", {"property":"calibre:rating"})]
    assert tags == [("★★★★★", None)]
    # Test setting invalid score in XML file
    meta["score"] = "Blah"
    book = create_metadata(meta)
    try:
        scores = book.get_metadata(None, "meta")
        assert 1 == 0
    except KeyError: pass
    assert book.get_metadata("DC", "subject") == []
    meta["score"] = "6"
    book = create_metadata(meta)
    try:
        scores = book.get_metadata(None, "meta")
        assert 1 == 0
    except KeyError: pass
    assert book.get_metadata("DC", "subject") == []
    meta["score"] = "-3"
    book = create_metadata(meta)
    try:
        scores = book.get_metadata(None, "meta")
        assert 1 == 0
    except KeyError: pass
    assert book.get_metadata("DC", "subject") == []
    # Test adding score as tags
    meta["tags"] = "These,are,things"
    meta["score"] = "3"
    book = create_metadata(meta)
    scores = book.get_metadata(None, "meta")
    tags = book.get_metadata("DC", "subject")
    assert scores == [("6.0", {"property":"calibre:rating"})]
    assert len(tags) == 4
    assert tags[0] == ("★★★", None)
    assert tags[1] == ("These", None)
    assert tags[2] == ("are", None)
    assert tags[3] == ("things", None)
    meta["score"] = "5"
    meta["tags"] = None
    book = create_metadata(meta)
    scores = book.get_metadata(None, "meta")
    tags = book.get_metadata("DC", "subject")
    assert scores == [("10.0", {"property":"calibre:rating"})]
    assert tags == [("★★★★★", None)]
    meta["score"] = "0"
    book = create_metadata(meta)
    scores = book.get_metadata(None, "meta")
    tags = book.get_metadata("DC", "subject")
    assert scores == [("0.0", {"property":"calibre:rating"})]

def test_get_items():
    """
    Tests the get_items function.
    """
    # Create test files
    temp_dir = get_temp_dir()
    json = abspath(join(temp_dir, "Text.json"))
    text = abspath(join(temp_dir, "Text.txt"))
    png = abspath(join(temp_dir, "[00] Cover.png"))
    jpeg = abspath(join(temp_dir, "Image.jpeg"))
    create_text_file(json, "Not")
    create_text_file(text, "Really")
    create_text_file(png, "That")
    create_text_file(jpeg, "Important")
    assert exists(json)
    assert exists(text)
    assert exists(png)
    assert exists(jpeg)
    # Get EpubItems
    items = get_items(temp_dir)
    assert len(items) == 7
    assert items[0].get_name() == "images/[00] Cover.png"
    assert items[0].get_id() == "Cover"
    assert items[0].get_content() == b"That"
    assert items[1].get_name() == "original/[00] Cover.png"
    assert items[1].get_id() == "[00] Cover-png"
    assert items[2].get_name() == "images/Image.jpeg"
    assert items[2].get_id() == "Image"
    assert items[3].get_name() == "original/Image.jpeg"
    assert items[3].get_id() == "Image-jpeg"
    assert items[4].get_name() == "original/Text.json"
    assert items[4].get_id() == "Text-json"
    assert items[5].get_name() == "original/Text.txt"
    assert items[5].get_id() == "Text-txt"
    assert items[6].get_name() == "style/epubstyle.css"
    assert items[6].get_id() == "epubstyle"
    assert items[6].get_content() == get_style()

def test_get_chapters():
    """
    Tests the get_chapters function.
    """
    # Create test files
    temp_dir = get_temp_dir()
    json = abspath(join(temp_dir, "Text.json"))
    text = abspath(join(temp_dir, "Text.txt"))
    png_file = abspath(join(temp_dir, "[00] Cover.png"))
    jpg_file = abspath(join(temp_dir, "Image.jpeg"))
    invalid = abspath(join(temp_dir, "invalid.png"))
    create_text_file(json, "blah")
    create_text_file(text, "Actually important!")
    create_text_file(invalid, "THING")
    png_image = Image.new("RGB", (100, 200), color=(255,0,0))
    jpg_image = Image.new("RGB", (500, 300), color=(0,255,0))
    png_image.save(png_file)
    jpg_image.save(jpg_file)
    assert exists(json)
    assert exists(text)
    assert exists(png_file)
    assert exists(jpg_file)
    assert exists(invalid)
    # Get html chapters
    chapters = get_chapters(temp_dir)
    assert len(chapters) == 3
    assert chapters[0].get_name() == "content/[00] Cover.xhtml"
    assert chapters[0].title == "Cover"
    body = "<body><div class=\"image-page-container\">"
    body = f"{body}<img class=\"vertical-image-page\" "
    body = f"{body}src=\"../images/[00] Cover.png\" alt=\"Cover\" /></div></body>"
    assert chapters[0].content == body
    links = []
    for link in chapters[0].get_links(): links.append(link)
    assert links == [{"href":"../style/epubstyle.css", "rel":"stylesheet", "type":"text/css"}]
    metas = []
    for meta in chapters[0].get_metas(): metas.append(meta)
    assert metas == [{'content': 'width=100, height=200', 'name': 'viewport'}]
    assert chapters[1].get_name() == "content/Image.xhtml"
    assert chapters[1].title == "Image"
    body = "<body><div class=\"image-page-container\">"
    body = f"{body}<img class=\"horizontal-image-page\" src=\"../images/Image.jpeg\" "
    body = f"{body}alt=\"Image\" /></div></body>"
    assert chapters[1].content == body
    metas = []
    for meta in chapters[1].get_metas(): metas.append(meta)
    assert metas == [{'content': 'width=500, height=300', 'name': 'viewport'}]
    assert chapters[2].get_name() == "content/Text.xhtml"
    assert chapters[2].title == "Text"
    body = "<body><div class=\"text-container\"><p>Actually important!</p></div></body>"
    assert chapters[2].content == body
    links = []
    for link in chapters[2].get_links(): links.append(link)
    assert links == [{"href":"../style/epubstyle.css", "rel":"stylesheet", "type":"text/css"}]

def test_create_epub():
    # Create test files
    temp_dir = get_temp_dir()
    json = abspath(join(temp_dir, "blah.json"))
    text_page = abspath(join(temp_dir, "Text.txt"))
    cover_file = abspath(join(temp_dir, "00.png"))
    internal_file = abspath(join(temp_dir, "Other.jpeg"))
    create_text_file(json, "Some thing")
    create_text_file(text_page, "This is some text!!!")
    cover_image = Image.new("RGB", (100, 200), color=(255,0,0))
    internal_image = Image.new("RGB", (500, 300), color=(0,255,0))
    cover_image.save(cover_file)
    internal_image.save(internal_file)
    assert exists(json)
    assert exists(text_page)
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
    assert files == ["00.png", "blah.json", "Other.jpeg", "Text.txt"]
    # Check the contents of the "content" folder
    content_folder = abspath(join(epub_dir, "content"))
    files = sort_alphanum(listdir(content_folder))
    assert files == ["00.xhtml", "Other.xhtml", "Text.xhtml"]
    # Check the contents of the cover image xhtml
    xml = read_text_file(abspath(join(content_folder, "00.xhtml")))
    compare = "<?xml version='1.0' encoding='utf-8'?>\n"
    compare = f"{compare}<!DOCTYPE html>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\" "
    compare = f"{compare}xmlns:epub=\"http://www.idpf.org/2007/ops\" "
    compare = f"{compare}epub:prefix=\"z3998: http://www.daisy.org/z3998/2012/vocab/structure/#\" "
    compare = f"{compare}lang=\"en\" xml:lang=\"en\">\n"
    compare = f"{compare}   <head>\n"
    compare = f"{compare}      <title>00</title>\n"
    compare = f"{compare}      <link href=\"../style/epubstyle.css\" rel=\"stylesheet\" type=\"text/css\" />\n"
    compare = f"{compare}      <meta content=\"width=100, height=200\" name=\"viewport\" />\n"
    compare = f"{compare}   </head>\n"
    compare = f"{compare}   <body>\n"
    compare = f"{compare}      <div class=\"image-page-container\">\n"
    compare = f"{compare}         <img class=\"vertical-image-page\" src=\"../images/00.png\" alt=\"00\" />\n"
    compare = f"{compare}      </div>\n"
    compare = f"{compare}   </body>\n"
    compare = f"{compare}</html>"
    assert xml == compare
    # Check the contents of the other image xhtml
    xml = read_text_file(abspath(join(content_folder, "Other.xhtml")))
    compare = "<?xml version='1.0' encoding='utf-8'?>\n"
    compare = f"{compare}<!DOCTYPE html>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\" "
    compare = f"{compare}xmlns:epub=\"http://www.idpf.org/2007/ops\" "
    compare = f"{compare}epub:prefix=\"z3998: http://www.daisy.org/z3998/2012/vocab/structure/#\" "
    compare = f"{compare}lang=\"en\" xml:lang=\"en\">\n"
    compare = f"{compare}   <head>\n"
    compare = f"{compare}      <title>Other</title>\n"
    compare = f"{compare}      <link href=\"../style/epubstyle.css\" rel=\"stylesheet\" type=\"text/css\" />\n"
    compare = f"{compare}      <meta content=\"width=500, height=300\" name=\"viewport\" />\n"
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
    assert files == ["00.png", "Other.jpeg"]
    # Check the contents of the "style" folder
    content_folder = abspath(join(epub_dir, "style"))
    files = sort_alphanum(listdir(content_folder))
    assert files == ["epubstyle.css"]
