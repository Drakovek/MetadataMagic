#!/usr/bin/env python3

from os import mkdir, listdir
from os.path import abspath, basename, exists, isdir, join
from metadata_magic.main.comic_archive.comic_archive import get_temp_dir
from metadata_magic.main.comic_archive.comic_xml import get_empty_metadata
from metadata_magic.main.epub.epub import create_epub
from metadata_magic.main.epub.epub import create_epub_files
from metadata_magic.main.epub.epub import create_image_page
from metadata_magic.main.epub.epub import create_nav_file
from metadata_magic.main.epub.epub import create_manifest
from metadata_magic.main.epub.epub import create_metadata_xml
from metadata_magic.main.epub.epub import create_style_file
from metadata_magic.main.epub.epub import format_xhtml
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

def test_format_xhtml():
    """
    Tests the format_xhtml function.
    """
    # Test single tag
    start = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    head = "<head><title>Title!</title><meta charset=\"UTF-8\" />"
    head = f"{head}<link rel=\"stylesheet\" href=\"style.css\" /></head>"
    html = "<p>This is a simple test &amp; stuff</p>"
    xhtml = format_xhtml(html, "Title!", False)
    assert xhtml == f"{start}{head}<body><p>This is a simple test &amp; stuff</p></body></html>"
    # Test with multiple tags
    html = "<p>Multiple</p><p>Paragraphs!!!</p>"
    xhtml = format_xhtml(html, "Title!", False)
    assert xhtml == f"{start}{head}<body><p>Multiple</p><p>Paragraphs!!!</p></body></html>"
    # Test with no tags
    head = "<head><title>Title thing.</title><meta charset=\"UTF-8\" />"
    head = f"{head}<link rel=\"stylesheet\" href=\"style.css\" /></head>"
    html = "This is a thing.<br/><br/>Final thing."
    xhtml = format_xhtml(html, "Title thing.", False)
    assert xhtml == f"{start}{head}<body>This is a thing.<br /><br />Final thing.</body></html>"
    # Test with spaces and newlines
    html = "  <p>  This is a thing!  </p>\n  <div> Another </div> "
    xhtml = format_xhtml(html, "Title thing.", False)
    assert xhtml == f"{start}{head}<body><p>  This is a thing!  </p>  <div> Another </div></body></html>"
    # Test adding indent
    html = "<p>These</p><p>Are</p><p>Paragraphs!</p>"
    xhtml = format_xhtml(html, "New", True)
    xml = f"{start}\n"
    xml = f"{xml}   <head>\n"
    xml = f"{xml}      <title>New</title>\n"
    xml = f"{xml}      <meta charset=\"UTF-8\" />\n"
    xml = f"{xml}      <link rel=\"stylesheet\" href=\"style.css\" />\n"
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
    # Test with no indents
    temp_dir = get_temp_dir()
    image_file = abspath(join(temp_dir, "Cover.jpg"))
    xml = create_image_page(image_file, False)
    compare = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    compare = f"{compare}<head><title>Cover</title><meta charset=\"UTF-8\" />"
    compare = f"{compare}<link rel=\"stylesheet\" href=\"style.css\" />"
    compare = f"{compare}</head><body>"
    compare = f"{compare}<img class=\"image-page\" src=\"Cover.jpg\" alt=\"Full Page Image\" />"
    compare = f"{compare}</body></html>"
    assert xml == compare
    # Test with indents
    image_file = abspath(join(temp_dir, "New.png"))
    xml = create_image_page(image_file, True)
    compare = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
    compare = f"{compare}   <head>\n"
    compare = f"{compare}      <title>New</title>\n"
    compare = f"{compare}      <meta charset=\"UTF-8\" />\n"
    compare = f"{compare}      <link rel=\"stylesheet\" href=\"style.css\" />\n"
    compare = f"{compare}   </head>\n"
    compare = f"{compare}   <body>\n"
    compare = f"{compare}      <img class=\"image-page\" src=\"New.png\" alt=\"Full Page Image\" />\n"
    compare = f"{compare}   </body>\n"
    compare = f"{compare}</html>"
    assert xml == compare

def test_txt_to_xhtml():
    """
    Tests the txt_to_xhtml function.
    """
    # Test a single paragraph
    start = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    head = "<head><title>Text</title><meta charset=\"UTF-8\" />"
    head = f"{head}<link rel=\"stylesheet\" href=\"style.css\" /></head>"
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "Text.txt"))
    text = "This is a simple sentence!"
    create_text_file(text_file, text)
    assert exists(text_file)
    xhtml = txt_to_xhtml(text_file, False)
    assert xhtml == f"{start}{head}<body><p>This is a simple sentence!</p></body></html>"
    # Test multiple paragraphs
    text = "Different paragraphs!\n\nHow cool!"
    create_text_file(text_file, text)
    xhtml = txt_to_xhtml(text_file, False)
    assert xhtml == f"{start}{head}<body><p>Different paragraphs!</p><p>How cool!</p></body></html>"
    # Test single new line character
    text = "More text!\nAnd This & That..."
    create_text_file(text_file, text)
    xhtml = txt_to_xhtml(text_file, False)
    assert xhtml == f"{start}{head}<body><p>More text!<br />And This &amp; That...</p></body></html>"
    # Test new lines and separate paragraphs
    text = "Paragraph\n\nOther\nText!\n\nFinal\nParagraph..."
    create_text_file(text_file, text)
    xhtml = txt_to_xhtml(text_file, False)
    assert xhtml == f"{start}{head}<body><p>Paragraph</p><p>Other<br />Text!</p><p>Final<br />Paragraph...</p></body></html>"
    # Test with more than one two new lines
    text = "Thing\n\n\nOther"
    create_text_file(text_file, text)
    xhtml = txt_to_xhtml(text_file, False)
    assert xhtml == f"{start}{head}<body><p>Thing<br /><br /><br />Other</p></body></html>"
    text = "Thing\n\n\nOther\n\nParagraph\n\n\n\nNext"
    create_text_file(text_file, text)
    xhtml = txt_to_xhtml(text_file, False)
    assert xhtml == f"{start}{head}<body><p>Thing<br /><br /><br />Other</p><p>Paragraph<br /><br /><br /><br />Next</p></body></html>"
    # Test adding indents
    new_file = abspath(join(temp_dir, "Different Title!.txt"))
    text = "Final\n\nText\nThing!"
    create_text_file(new_file, text)
    xhtml = txt_to_xhtml(new_file, True)
    xml = f"{start}\n"
    xml = f"{xml}   <head>\n"
    xml = f"{xml}      <title>Different Title!</title>\n"
    xml = f"{xml}      <meta charset=\"UTF-8\" />\n"
    xml = f"{xml}      <link rel=\"stylesheet\" href=\"style.css\" />\n"
    xml = f"{xml}   </head>\n"
    xml = f"{xml}   <body>\n"
    xml = f"{xml}      <p>Final</p>\n"
    xml = f"{xml}      <p>Text<br />Thing!</p>\n"
    xml = f"{xml}   </body>\n"
    xml = f"{xml}</html>"
    assert xhtml == xml

def test_create_style_file():
    """
    Tests the create_style_file function()
    """
    temp_dir = get_temp_dir()
    css_file = abspath(join(temp_dir, "style.css"))
    assert not exists(css_file)
    create_style_file(css_file)
    assert exists(css_file)
    # Test contents of the css file
    content = read_text_file(css_file)
    style = "body {margin: 0px 0px 0px 0px;}"
    style = style + "\n\n.image-page {\n"
    style = style + "   display: block;\n"
    style = style + "   width: 100%;\n"
    style = style + "   height: auto;\n"
    style = style + "   max-height: 500px;\n"
    style = style + "   max-width: 500px;"
    style = style + "   margin: 0;\n"
    style = style + "   position: absolute;\n"
    style = style + "   top: 50%;\n"
    style = style + "   left: 50%;\n"
    style = style + "   transform: translate(-50%, -50%);\n}"
    assert content == style

def test_create_nav_file():
    # Test creating nav file
    xhtmls = []
    temp_dir = get_temp_dir()
    xhtmls.append(abspath(join(temp_dir, "Cover.xhtml")))
    xhtmls.append(abspath(join(temp_dir, "Chapter 1.xhtml")))
    xhtmls.append(abspath(join(temp_dir, "Chapter 2.xhtml")))
    xhtmls.append(abspath(join(temp_dir, "Epilogues.xhtml")))
    nav_file = abspath(join(temp_dir, "nav.xhtml"))
    assert not exists(nav_file)
    create_nav_file(xhtmls, nav_file, False)
    assert exists(nav_file)
    content = read_text_file(nav_file)
    compare = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:epub=\"http://www.idpf.org/2007/ops\" lang=\"en\" xml:lang=\"en\">"
    compare = f"{compare}<head><meta charset=\"UTF-8\" /><title>Table of Contents</title></head>"
    compare = f"{compare}<body><h1>Table of Contents</h1><nav epub:type=\"toc\" id=\"toc\">"
    compare = f"{compare}<ol><li><a href=\"content/Cover.xhtml\">Cover</a></li>"
    compare = f"{compare}<li><a href=\"content/Chapter 1.xhtml\">Chapter 1</a></li>"
    compare = f"{compare}<li><a href=\"content/Chapter 2.xhtml\">Chapter 2</a></li>"
    compare = f"{compare}<li><a href=\"content/Epilogues.xhtml\">Epilogues</a></li>"
    compare = f"{compare}</ol></nav></body></html>"
    assert content == compare
    # Test creating nav file with indents
    xhtmls = [abspath(join(temp_dir, "Cover.xhtml"))]
    create_nav_file(xhtmls, nav_file, True)
    content = read_text_file(nav_file)
    compare = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:epub=\"http://www.idpf.org/2007/ops\" lang=\"en\" xml:lang=\"en\">\n"
    compare = f"{compare}   <head>\n"
    compare = f"{compare}      <meta charset=\"UTF-8\" />\n"
    compare = f"{compare}      <title>Table of Contents</title>\n"
    compare = f"{compare}   </head>\n"
    compare = f"{compare}   <body>\n"
    compare = f"{compare}      <h1>Table of Contents</h1>\n"
    compare = f"{compare}      <nav epub:type=\"toc\" id=\"toc\">\n"
    compare = f"{compare}         <ol>\n"
    compare = f"{compare}            <li>\n"
    compare = f"{compare}               <a href=\"content/Cover.xhtml\">Cover</a>\n"
    compare = f"{compare}            </li>\n"
    compare = f"{compare}         </ol>\n"
    compare = f"{compare}      </nav>\n"
    compare = f"{compare}   </body>\n"
    compare = f"{compare}</html>"
    assert content == compare

def test_create_manifest():
    """
    Tests the create_manifest function.
    """
    files = []
    temp_dir = get_temp_dir()
    files.append(abspath(join(temp_dir, "Cover.xhtml")))
    files.append(abspath(join(temp_dir, "Picture.png")))
    files.append(abspath(join(temp_dir, "Jpeg!.jpg")))
    files.append(abspath(join(temp_dir, "Thing.svg")))
    manifest = create_manifest(files)
    compare = "<manifest>"
    compare = f"{compare}<item href=\"nav.xhtml\" id=\"toc\" media-type=\"application/xhtml+xml\" properties=\"nav\" />"
    compare = f"{compare}<item href=\"content/Cover.xhtml\" id=\"Cover\" media-type=\"application/xhtml+xml\" />"
    compare = f"{compare}<item href=\"content/Picture.png\" id=\"Picture\" media-type=\"image/png\" />"
    compare = f"{compare}<item href=\"content/Jpeg!.jpg\" id=\"Jpeg!\" media-type=\"image/jpeg\" />"
    compare = f"{compare}<item href=\"content/Thing.svg\" id=\"Thing\" media-type=\"image/svg+xml\" /></manifest>"
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
    mkdir(content)
    assert isdir(content) and exists(content)
    cover_page = abspath(join(content, "00-Cover.xhtml"))
    chapter_page = abspath(join(content, "01-Chapter1.xhtml"))
    cover_image = abspath(join(content, "cover.png"))
    internal_image = abspath(join(content, "other.jpeg"))
    create_text_file(cover_page, "Doesn't")
    create_text_file(chapter_page, "Really")
    create_text_file(cover_image, "Matter")
    create_text_file(internal_image, "To Me")
    assert exists(cover_page)
    assert exists(chapter_page)
    assert exists(cover_image)
    assert exists(internal_image)
    # Create package file
    metadata = get_empty_metadata()
    metadata["title"] = "Some title!"
    nav_file = abspath(join(temp_dir, "nav.xhtml"))
    package_file = abspath(join(temp_dir, "package.opf"))
    create_epub_files(temp_dir, metadata)
    # Test that nav file is correct
    assert exists(nav_file)
    contents = read_text_file(nav_file)
    compare = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    compare = f"{compare}<html xmlns=\"http://www.w3.org/1999/xhtml\" "
    compare = f"{compare}xmlns:epub=\"http://www.idpf.org/2007/ops\" lang=\"en\" xml:lang=\"en\">\n"
    compare = f"{compare}   <head>\n"
    compare = f"{compare}      <meta charset=\"UTF-8\" />\n"
    compare = f"{compare}      <title>Table of Contents</title>\n"
    compare = f"{compare}   </head>\n"
    compare = f"{compare}   <body>\n"
    compare = f"{compare}      <h1>Table of Contents</h1>\n"
    compare = f"{compare}      <nav epub:type=\"toc\" id=\"toc\">\n"
    compare = f"{compare}         <ol>\n"
    compare = f"{compare}            <li>\n"
    compare = f"{compare}               <a href=\"content/00-Cover.xhtml\">00-Cover</a>\n"
    compare = f"{compare}            </li>\n"
    compare = f"{compare}            <li>\n"
    compare = f"{compare}               <a href=\"content/01-Chapter1.xhtml\">01-Chapter1</a>\n"
    compare = f"{compare}            </li>\n"
    compare = f"{compare}         </ol>\n"
    compare = f"{compare}      </nav>\n"
    compare = f"{compare}   </body>\n"
    compare = f"{compare}</html>"
    assert contents == compare
    # Test that package file is correct
    assert exists(package_file)
    contents = read_text_file(package_file)
    compare = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    compare = f"{compare}<package xmlns:dc=\"http://purl.org/dc/elements/1.1/\" "
    compare = f"{compare}xmlns=\"http://www.idpf.org/2007/opf\" unique-identifier=\"uid\" version=\"3.0\">\n"
    compare = f"{compare}   <metadata>\n"
    compare = f"{compare}      <dc:language>en</dc:language>\n"
    compare = f"{compare}      <dc:identifier>some title!</dc:identifier>\n"
    compare = f"{compare}      <dc:title>Some title!</dc:title>\n"
    compare = f"{compare}      <meta property=\"dcterms:modified\">0000-00-00T00:00:00+00:00</meta>\n"
    compare = f"{compare}      <dc:date>0000-00-00T00:00:00+00:00</dc:date>\n"
    compare = f"{compare}   </metadata>\n"
    compare = f"{compare}   <manifest>\n"
    compare = f"{compare}      <item href=\"nav.xhtml\" id=\"toc\" media-type=\"application/xhtml+xml\" properties=\"nav\" />\n"
    compare = f"{compare}      <item href=\"content/00-Cover.xhtml\" id=\"00-Cover\" media-type=\"application/xhtml+xml\" />\n"
    compare = f"{compare}      <item href=\"content/01-Chapter1.xhtml\" id=\"01-Chapter1\" media-type=\"application/xhtml+xml\" />\n"
    compare = f"{compare}      <item href=\"content/cover.png\" id=\"cover\" media-type=\"image/png\" />\n"
    compare = f"{compare}      <item href=\"content/other.jpeg\" id=\"other\" media-type=\"image/jpeg\" />\n"
    compare = f"{compare}   </manifest>\n"
    compare = f"{compare}   <spine>\n"
    compare = f"{compare}      <itemref idref=\"00-Cover\" />\n"
    compare = f"{compare}      <itemref idref=\"01-Chapter1\" />\n"
    compare = f"{compare}   </spine>\n"
    compare = f"{compare}</package>"
    assert contents == compare

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
    assert files == ["content", "nav.xhtml", "original", "package.opf"]
    # Check the contents of the "original" folder
    original_folder = abspath(join(extract_dir, "original"))
    new_files = sort_alphanum(listdir(original_folder))
    assert new_files == ["00.png", "blah.json", "Other.jpeg", "Text.txt"]
    # Check the contents of the "content" folder
    content_folder = abspath(join(extract_dir, "content"))
    new_files = sort_alphanum(listdir(content_folder))
    assert new_files == ["00.png", "00.xhtml", "Other.jpeg", "Other.xhtml", "style.css", "Text.xhtml"]
