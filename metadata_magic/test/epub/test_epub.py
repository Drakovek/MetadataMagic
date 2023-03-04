#!/usr/bin/env python3

from os import mkdir, listdir
from os.path import abspath, basename, exists, isdir, join
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
    # Test with no indents
    temp_dir = get_temp_dir()
    image_file = abspath(join(temp_dir, "[00] Cover.jpg"))
    xml = create_image_page(image_file)
    compare = "<body><img class=\"image-page\" "
    compare = f"{compare}src=\"../images/[00] Cover.jpg\" alt=\"Cover\" /></body>"
    assert xml == compare

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
    xhtml = txt_to_xhtml(text_file)
    assert xhtml == "<body><p>This is a simple sentence!</p></body>"
    # Test multiple paragraphs
    text = "Different paragraphs!\n\nHow cool!"
    create_text_file(text_file, text)
    xhtml = txt_to_xhtml(text_file)
    assert xhtml == "<body><p>Different paragraphs!</p><p>How cool!</p></body>"
    # Test single new line character
    text = "More text!\nAnd This & That..."
    create_text_file(text_file, text)
    xhtml = txt_to_xhtml(text_file)
    assert xhtml == "<body><p>More text!<br/>And This &amp; That...</p></body>"
    # Test new lines and separate paragraphs
    text = "Paragraph\n\nOther\nText!\n\nFinal\nParagraph..."
    create_text_file(text_file, text)
    xhtml = txt_to_xhtml(text_file)
    assert xhtml == "<body><p>Paragraph</p><p>Other<br/>Text!</p><p>Final<br/>Paragraph...</p></body>"
    # Test with more than one two new lines
    text = "Thing\n\n\nOther"
    create_text_file(text_file, text)
    xhtml = txt_to_xhtml(text_file)
    assert xhtml == "<body><p>Thing<br/><br/><br/>Other</p></body>"
    text = "Thing\n\n\nOther\n\nParagraph\n\n\n\nNext"
    create_text_file(text_file, text)
    xhtml = txt_to_xhtml(text_file)
    assert xhtml == "<body><p>Thing<br/><br/><br/>Other</p><p>Paragraph<br/><br/><br/><br/>Next</p></body>"

def test_get_style():
    """
    Tests the create_style_file function()
    """
    style = get_style()
    compare = "body {margin: 14px 14px 14px 14px;"
    compare = f"{compare}font-family: Georgia, serif;font-size:14px;}} "
    compare = f"{compare}.image-page {{"
    compare = f"{compare}display: block;"
    compare = f"{compare}width: 100%;"
    compare = f"{compare}height: auto;"
    compare = f"{compare}margin-left: auto;"
    compare = f"{compare}margin-right: auto;"
    compare = f"{compare}margin-top: auto;"
    compare = f"{compare}margin-bottom: auto;}}"
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
    png = abspath(join(temp_dir, "[00] Cover.png"))
    jpeg = abspath(join(temp_dir, "Image.jpeg"))
    create_text_file(json, "blah")
    create_text_file(text, "Actually important!")
    create_text_file(png, "Not")
    create_text_file(jpeg, "This Though")
    assert exists(json)
    assert exists(text)
    assert exists(png)
    assert exists(jpeg)
    # Get html chapters
    chapters = get_chapters(temp_dir)
    assert len(chapters) == 3
    assert chapters[0].get_name() == "content/[00] Cover.xhtml"
    assert chapters[0].title == "Cover"
    body = "<body><img class=\"image-page\" "
    body = f"{body}src=\"../images/[00] Cover.png\" alt=\"Cover\" /></body>"
    assert chapters[0].content == body
    links = []
    for link in chapters[0].get_links(): links.append(link)
    assert links == [{"href":"../style/epubstyle.css", "rel":"stylesheet", "type":"text/css"}]
    assert chapters[1].get_name() == "content/Image.xhtml"
    assert chapters[1].title == "Image"
    body = "<body><img class=\"image-page\" "
    body = f"{body}src=\"../images/Image.jpeg\" alt=\"Image\" /></body>"
    assert chapters[1].content == body
    assert chapters[2].get_name() == "content/Text.xhtml"
    assert chapters[2].title == "Text"
    body = "<body><p>Actually important!</p></body>"
    assert chapters[2].content == body
    links = []
    for link in chapters[2].get_links(): links.append(link)
    assert links == [{"href":"../style/epubstyle.css", "rel":"stylesheet", "type":"text/css"}]

def test_create_epub():
    # Create test files
    temp_dir = get_temp_dir()
    json = abspath(join(temp_dir, "blah.json"))
    text_page = abspath(join(temp_dir, "Text.txt"))
    cover_image = abspath(join(temp_dir, "00.png"))
    internal_image = abspath(join(temp_dir, "Other.jpeg"))
    create_text_file(json, "Some thing")
    create_text_file(text_page, "This is some text!!!")
    create_text_file(cover_image, "Matter")
    create_text_file(internal_image, "To Me")
    assert exists(json)
    assert exists(text_page)
    assert exists(cover_image)
    assert exists(internal_image)
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
    # Check the contents of the "images" folder
    content_folder = abspath(join(epub_dir, "images"))
    files = sort_alphanum(listdir(content_folder))
    assert files == ["00.png", "Other.jpeg"]
    # Check the contents of the "style" folder
    content_folder = abspath(join(epub_dir, "style"))
    files = sort_alphanum(listdir(content_folder))
    assert files == ["epubstyle.css"]
