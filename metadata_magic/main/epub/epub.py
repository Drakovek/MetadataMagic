#!/usr/bin/env python3

from argparse import ArgumentParser
from html_string_tools.main.html_string_tools import get_extension, regex_replace
from metadata_magic.main.comic_archive.comic_archive import create_cbz
from metadata_magic.main.comic_archive.comic_archive import get_temp_dir
from metadata_magic.main.comic_archive.comic_xml import generate_info_from_jsons
from metadata_magic.main.rename.sort_rename import sort_alphanum
from metadata_magic.test.temp_file_tools import create_text_file
from metadata_magic.test.temp_file_tools import read_text_file
from os import getcwd, listdir, mkdir
from os.path import abspath, basename, exists, join
from python_print_tools.main.python_print_tools import color_print
from re import sub as resub
from re import findall
from shutil import copy
from typing import List
from xml.etree.ElementTree import indent as xml_indent
from xml.etree.ElementTree import Element, SubElement
from xml.etree.ElementTree import fromstring as xml_from_string
from xml.etree.ElementTree import tostring as xml_to_string

def newline_to_tag(lines:str) -> str:
    """
    Returns a string with number of <br/> tags equal to length of lines.
    <br/> tags are represented as "{{{br}}}" to be replaced in final XHTML.
    
    :param lines: String of new line characters
    :type lines: str, required
    :return: String with a number of <br/> tags
    :rtype: str
    """
    tags = ""
    for i in range(0, len(lines)):
        tags = tags + "{{{br}}}"
    return tags

def format_xhtml(html:str, title:str, indent:bool=True) -> str:
    """
    Creates text for an epub XHTML content file with given html string in the body
    
    :param html: String in HTML format
    :type html: str, required
    :param title: Title to use in the XHTML head
    :type title: str, required
    :param indent: Whether to add indents to the XHTML file, defaults to True
    :type indent: bool, optional
    :return: XHTML text
    :rtype: str
    """
    # Set the base element for the XHTML 
    base = Element("html")
    base.attrib = {"xmlns":"http://www.w3.org/1999/xhtml"}
    # Create the head subelement
    head = SubElement(base, "head")
    title_element = SubElement(head, "title")
    title_element.text = title
    meta = SubElement(head, "meta")
    meta.attrib = {"charset":"UTF-8"}
    link = SubElement(head, "link")
    link.attrib = {"rel":"stylesheet", "href":"style.css"}
    # Parse the given html text and add to body
    final_html = resub("^\\s+|\\s+$|\\n", "", html)
    body = xml_from_string(f"<body>{final_html}</body>")
    base.append(body)
    # Set indents to make the XML more readable
    if indent:
        xml_indent(base, space="   ")
    # Get xml as string
    xml = xml_to_string(base).decode("UTF-8")
    return f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n{xml}"

def create_image_page(image_file, indent:bool=True) -> str:
    """
    Returns a epub formatted XHTML page containing a single full page image.
    
    :param image_file: Path to the image file to include on the page
    :type image_file: str, required
    :param indent: Whether to add indents to the XHTML file, defaults to True
    :type indent: bool, optional
    :return: XHTML text
    :rtype: str
    """
    # Create the image element
    filename = basename(image_file)
    img = Element("img")
    img.attrib = {"class":"image-page", "src":filename, "alt":"Full Page Image"}
    img_string = xml_to_string(img).decode("UTF-8")
    # Create a full page
    return format_xhtml(img_string, filename[:len(filename) - len(get_extension(filename))], indent)

def txt_to_xhtml(txt_file:str, indent:bool=True) -> str:
    """
    Creates text for an epub XHTML content file from a given txt file.
    
    :param txt_file: Path to a txt file.
    :type txt_file: str, required
    :param indent: Whether to add indents to the XHTML file, defaults to True
    :type indent: bool, optional
    :return: XHTML text
    :rtype: str
    """
    # Read text file
    full_path = abspath(txt_file)
    content = read_text_file(full_path)
    # Replace long string of newlines
    content = regex_replace(newline_to_tag, "\\n\\n\\n+", content)
    # Split by new lines
    paragraphs = content.split("\n\n")
    # Create paragraph elements
    body = Element("body")
    for paragraph in paragraphs:
        p_element = SubElement(body, "p")
        p_element.text = paragraph.replace("\n","{{{br}}}")
    # Get xml as string
    xml = xml_to_string(body).decode("UTF-8")
    xml = xml.replace("{{{br}}}", "<br/>")
    xml = resub("^<body>|<\\/body>$", "", xml)
    # Get title
    title_name = basename(txt_file)
    title_name = title_name[:len(title_name) - len(get_extension(title_name))]
    # Return XHTML
    return format_xhtml(xml, title_name, indent)

def create_style_file(file_path:str):
    """
    Creates the default css stylesheet for the epub book.
    
    :param file_path: Path to save the stylesheet to
    :type file_path: str, required
    """
    # Get css style
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
    # Create file
    full_path = abspath(file_path)
    create_text_file(full_path, style)

def create_nav_file(xhtmls:List[str], file_path, indent:bool=True):
    """
    Creates the Table of Contents nav file for the epub file.
    
    :param xhtmls: List of XHTML files to include in the contents
    :type xhtmls: str, required
    :param file_path: Path of the file to save to
    :type file_path: str, required
    :param indent: Whether to add indents to the XHTML file, defaults to True
    :type indent: bool, optional
    """
    # Create base of navigation file
    attributes = {"xmlns":"http://www.w3.org/1999/xhtml"}
    attributes["xmlns:epub"] = "http://www.idpf.org/2007/ops"
    attributes["lang"] = "en"
    attributes["xml:lang"] = "en"
    base = Element("html")
    base.attrib = attributes
    # Create navigation head
    head = SubElement(base, "head")
    meta = SubElement(head, "meta")
    meta.attrib = {"charset":"UTF-8"}
    title = SubElement(head, "title")
    title.text = "Table of Contents"
    # Create navigation body and header
    body = SubElement(base, "body")
    h1 = SubElement(body, "h1")
    h1.text = "Table of Contents"
    # Create nav element
    nav = SubElement(body, "nav")
    nav.attrib = {"epub:type":"toc", "id":"toc"}
    ol = SubElement(nav, "ol")
    # Create entries for each XHTML file
    for xhtml in xhtmls:
        # Get title
        filename = basename(xhtml)
        name = filename[:len(filename) - len(get_extension(filename))]
        # Create list item
        li = SubElement(ol, "li")
        a = SubElement(li, "a")
        a.text = name
        a.attrib = {"href":f"content/{filename}"}
    # Set indents to make the XML more readable
    if indent:
        xml_indent(base, space="   ")
    # Get xml as string
    xml = xml_to_string(base).decode("UTF-8")
    xml = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n{xml}"
    # Write XML
    full_path = abspath(file_path)
    create_text_file(full_path, xml)

def create_manifest(files:List[str]) -> str:
    """
    Create the manifest section for the epub package file.
    Uses all given files, and adds nav file by default.
    
    :param files: List of files to link in the manifest section
    :type files: list[str], required
    :return: Manifest section in xml format
    :rtype: str
    """
    # Create the manifest base
    base = Element("manifest")
    # Add the nav file as item
    nav_item = SubElement(base, "item")
    nav_item.attrib = {"href":"nav.xhtml", "id":"toc", "media-type":"application/xhtml+xml", "properties":"nav"}
    # Add files as items
    for file in files:
        filename = basename(file)
        extension = get_extension(filename)
        file_id = filename[:len(filename) - len(extension)]
        media_type = ""
        # Get the file mimetype
        if extension == ".xhtml":
            media_type = "application/xhtml+xml"
        elif extension == ".css" or extension == ".html" or extension == ".htm":
            media_type = "text/html"
        elif extension == ".jpeg" or extension == ".jpg":
            media_type = "image/jpeg"
        elif extension == ".png":
            media_type = "image/png"
        elif extension == ".svg":
            media_type = "image/svg+xml"
        # Create item
        item = SubElement(base, "item")
        item.attrib = {"href":f"content/{filename}", "id":file_id, "media-type":media_type}
    # Get xml as string
    xml = xml_to_string(base).decode("UTF-8")
    return xml

def create_metadata_xml(metadata:dict) -> str:
    """
    Creates the metadata section for the epub package file based on given metadata.
    
    :param metadata: Metadata dict, same as given for cbz ComicInfo functions
    :type metadata: dict, required
    :return: Metadata section in xml format
    :rtype: str
    """
    # Create the metadata base
    base = Element("metadata")
    base.attrib = {"xmlns:dc":"http://purl.org/dc/elements/1.1/"}
    # Set the language
    language = SubElement(base, "dc:language")
    language.text = "en"
    # Set the identifier
    identifier = SubElement(base, "dc:identifier")
    if metadata["url"] is not None:
        identifier.text = metadata["url"]
    else:
        identifier.text = metadata["title"].lower()
    # Set the title
    title = SubElement(base, "dc:title")
    title.text = metadata["title"]
    # Add author(s)
    try:
        authors = metadata["writer"].split(",")
    except AttributeError: authors = []
    for i in range(0, len(authors)):
        # Add creator tag
        author_id = "author" + str(i+1)
        creator = SubElement(base, "dc:creator")
        creator.attrib = {"id":author_id}
        creator.text = authors[i]
        # Add role tag
        role = SubElement(base, "meta")
        role.attrib = {"refines":f"#{author_id}", "property":"role", "scheme":"marc:relators"}
        role.text = "aut"
    # Add illustrator(s)
    try:
        illustrators = metadata["artist"].split(",")
    except AttributeError: illustrators = []
    for i in range(0, len(illustrators)):
        # Add creator tag
        illustrator_id = "illustrator" + str(i+1)
        creator = SubElement(base, "dc:creator")
        creator.attrib = {"id":illustrator_id}
        creator.text = illustrators[i]
        # Add role tag
        role = SubElement(base, "meta")
        role.attrib = {"refines":f"#{illustrator_id}", "property":"role", "scheme":"marc:relators"}
        role.text = "ill"
    # Add cover artist(s)
    try:
        covartists = metadata["cover_artist"].split(",")
    except AttributeError: covartists = []
    for i in range(0, len(covartists)):
        # Add creator tag
        cover_id = "covartist" + str(i+1)
        creator = SubElement(base, "dc:creator")
        creator.attrib = {"id":cover_id}
        creator.text = covartists[i]
        # Add role tag
        role = SubElement(base, "meta")
        role.attrib = {"refines":f"#{cover_id}", "property":"role", "scheme":"marc:relators"}
        role.text = "cov"
    # Set the description
    if metadata["description"] is not None:
        description = SubElement(base, "dc:description")
        description.text = metadata["description"]
    # Set the publisher
    if metadata["publisher"] is not None:
        publisher = SubElement(base, "dc:publisher")
        publisher.text = metadata["publisher"]
    # Set the series info
    if metadata["series"] is not None:
        series_title = SubElement(base, "meta")
        series_title.attrib = {"property":"belongs-to-collection", "id":"series-title"}
        series_title.text = metadata["series"]
        collection_type = SubElement(base, "meta")
        collection_type.attrib = {"refines":"series-title", "property":"collection-type"}
        collection_type.text = "series"
        try:
            num = float(metadata["series_number"])
            series_number = SubElement(base, "meta")
            series_number.attrib = {"refines":"series-title", "property":"group-position"}
            series_number.text = metadata["series_number"]
        except (TypeError, ValueError): pass
    # Set the score
    tag_string = metadata["tags"]
    try:
        score = int(metadata["score"])
        if score > -1 and score < 6:
            score_element = SubElement(base, "meta")
            score_element.attrib = {"property":"calibre:rating"}
            score_element.text = str(float(score * 2))
    except (TypeError, ValueError): pass
    # Set the tags
    tag_string = metadata["tags"]
    try:
        # Add score as star rating in tags
        score = int(metadata["score"])
        if score > 0 and score < 6:
            stars = "★"
            while len(stars) < score:
                stars = f"{stars}★"
            if tag_string is None or tag_string == "":
                tag_string = stars
            else:
                tag_string = f"{stars},{tag_string}"
    except (TypeError, ValueError): pass
    try:
        tags = tag_string.split(",")
    except AttributeError: tags = []
    for tag in tags:
        subject = SubElement(base, "dc:subject")
        subject.text = tag
    # Set the date
    date = "0000-00-00T00:00:00+00:00"
    if metadata["date"] is not None:
        date = metadata["date"] + "T00:00:00+00:00"
    modified = SubElement(base, "meta")
    modified.attrib = {"property":"dcterms:modified"}
    modified.text = date
    date_element = SubElement(base, "dc:date")
    date_element.text = date
    # Get xml as string
    xml = xml_to_string(base).decode("UTF-8")
    return xml

def create_epub_files(directory:str, metadata:dict):
    """
    Creates the nav.xhtml and package.opf files required for an epub archive.
    Saves files in the given directory.
    Searches for files to include in spine and manifest from ./content directory within given directory.
    
    :param directory: Directory in which to save files
    :type directory: str, required
    :param metadata: Metadata to use when creating the file
    :type metadata: dict, required
    """
    # Get list of files in the content directory
    full_directory = abspath(directory)
    content_dir = abspath(join(directory, "content"))
    files = sort_alphanum(listdir(content_dir))
    # Get the manifest and metadata sections
    manifest = create_manifest(files)
    meta_xml = create_metadata_xml(metadata)
    # Get list of just the xhtml files in the content directory
    for i in range(len(files)-1, -1, -1):
        if not get_extension(files[i]) == ".xhtml":
            del files[i]
    # Create nav file
    nav_file = abspath(join(full_directory, "nav.xhtml"))
    create_nav_file(files, nav_file, True)
    # Create the package xml contents
    base = Element("package")
    base.attrib = {"xmlns":"http://www.idpf.org/2007/opf", "unique-identifier":"uid", "version":"3.0"}
    base.append(xml_from_string(meta_xml))
    base.append(xml_from_string(manifest))
    spine = SubElement(base, "spine")
    for file in files:
        # Create spine items
        filename = basename(file)
        file_id = filename[:len(filename) - len(get_extension(filename))]
        itemref = SubElement(spine, "itemref")
        itemref.attrib = {"idref":file_id}
    # Save package xml to file
    xml_indent(base, space="   ")
    xml = xml_to_string(base).decode("UTF-8")
    xml = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n{xml}"
    package_file = abspath(join(full_directory, "package.opf"))
    create_text_file(package_file, xml)

def create_epub(directory:str, metadata:dict) -> str:
    """
    Creates an epub archive from the text and images in a given directory.
    
    :param directory: Directory in which to pull text and images
    :type directory: str, required
    :param metadata: Metadata to use for the epub file
    :type metadata: dict, required
    :return: Path to the newly created epub file
    :rtype: str
    """
    # Get the path of the epub file to create
    input_directory = abspath(directory)
    epub_file = abspath(join(input_directory, basename(input_directory)+".epub"))
    # Create temporary directory to save contents into
    temp_dir = get_temp_dir("dvk-metamagic-epub")
    # Get list of all contents of the given directory
    files = listdir(input_directory)
    for i in range(0, len(files)):
        files[i] = abspath(join(input_directory, files[i]))
    # Copy all files into folder to contain all original unaltered files
    original_folder = abspath(join(temp_dir, "original"))
    mkdir(original_folder)
    for file in files:
        copy(file, abspath(join(original_folder, basename(file))))
    # Create content folder and style sheet
    content_folder = abspath(join(temp_dir, "content"))
    mkdir(content_folder)
    create_style_file(abspath(join(content_folder, "style.css")))
    # Copy all images and convert all text to XHTML for the content folder
    for file in files:
        filename = basename(file)
        extension = get_extension(filename)
        if extension == ".txt":
            # Create text extension
            filename = filename[:len(filename) - len(extension)] + ".xhtml"
            xml = txt_to_xhtml(file, True)
            create_text_file(abspath(join(content_folder, filename)), xml)
        if extension == ".png" or extension == ".jpg" or extension == ".jpeg" or extension == ".svg":
            # Copy image file
            copy(file, abspath(join(content_folder, filename)))
            # Create image page
            filename = filename[:len(filename) - len(extension)] + ".xhtml"
            xml = create_image_page(file)
            create_text_file(abspath(join(content_folder, filename)), xml)
    # Create the package and nav files
    create_epub_files(temp_dir, metadata)
    # Zip files and copy to epub
    cbz = create_cbz(temp_dir)
    copy(cbz, epub_file)
    return epub_file
    
def user_create_epub(path:str,
                rp_description:bool=False,
                rp_date:bool=False,
                rp_artists:bool=False,
                rp_publisher:bool=False,
                rp_url:bool=False,
                rp_tags:bool=False,
                rp_score:bool=False):
    """
    Creates an epub file using the files in a directory and metadata from the user.
    
    :param path: Directory with files to archive
    :type path: str, required
    :param rp_description: Whether to replace the description from gathered metadata, defaults to False
    :type rp_description: bool, optional
    :param rp_date: Whether to replace the date from gathered metadata, defaults to False
    :type rp_date: bool, optional
    :param rp_artists: Whether to replace the artists/writers from gathered metadata, defaults to False
    :type rp_artists: bool, optional
    :param rp_publisher: Whether to replace the publisher from gathered metadata, defaults to False
    :type rp_publiser: bool, optional
    :param rp_url: Whether to replace the URL from gathered metadata, defaults to False
    :type rp_url: bool, optional
    :param rp_tags: Whether to replace the tags from gathered metadata, defaults to False
    :type rp_tags: bool, optional
    :param rp_score: Whether to replace the score from gathered metadata, defaults to False
    :type rp_score: bool, optional
    """
    # Get default metadata
    full_path = abspath(path)
    try:
        metadata = generate_info_from_jsons(full_path)
    except FileNotFoundError: metadata = get_empty_metadata()
    # Remove metadata fields the user wishes to replace
    if rp_description:
        metadata["description"] = None
    if rp_date:
        metadata["date"] = None
    if rp_artists:
        metadata["artist"] = None
        metadata["writer"] = None
        metadata["cover_artist"] = None
    if rp_publisher:
        metadata["publisher"] = None
    if rp_url:
        metadata["url"] = None
    if rp_tags:
        metadata["tags"] = None
    # Get the title
    title = metadata["title"]
    if title is None:
        metadata["title"] = str(input("Title: "))
    else:
        title = str(input(f"Title (Default is \"{title}\"): "))
        if not title == "":
            metadata["title"] = title
    # Get the description
    if metadata["description"] is None:
        description = str(input("Description: "))
        if not description == "":
            metadata["description"] = description
    # Get the date
    if metadata["date"] is None:
        date = ""
        regex = "(19[7-9][0-9]|2[0-1][0-9]{2})\\-(0[1-9]|1[0-2])\\-(0[1-9]|[1-2][0-9]|3[0-1])"
        while len(findall(regex, date)) == 0:
            date = str(input("Date (YYYY-MM-DD): "))
        metadata["date"] = date
    # Get the Writer
    if metadata["writer"] is None:
        writer = str(input(f"Writer: "))
        if not writer == "":
            metadata["writer"] = writer
    # Get the Illustrator
    artist = metadata["artist"]
    if artist is None:
        artist = str(input("Illustrator: "))
        if not artist == "":
            metadata["artist"] = artist
    # Get the Cover Artist
    if metadata["cover_artist"] is None:
        cover = str(input(f"Cover Artist: "))
        if not cover == "":
            metadata["cover_artist"] = cover
    # Get the Publisher
    if metadata["publisher"] is None:
        publisher = str(input("Publisher: "))
        if not publisher == "":
            metadata["publisher"] = publisher
    # Get the URL
    if metadata["url"] is None:
        url = str(input("URL: "))
        if not url == "":
            metadata["url"] = url
    # Get tags
    if metadata["tags"] is None:
        url = str(input("Tags: "))
        if not url == "":
            metadata["tags"] = resub("\\s*,\\s*", ",", url)
    # Get score
    if rp_score:
        score = str(input("Score (Range 0-5): "))
        if not score == "":
            metadata["score"] = score
    # Create/Update .cbz
    create_epub(full_path, metadata)

def main():
    """
    Sets up the parser for creating an epub file.
    """
    # Set up argument parser
    parser = ArgumentParser()
    parser.add_argument(
            "path",
            help="Path to directory for creating epub.",
            nargs="?",
            type=str,
            default=str(getcwd()))
    parser.add_argument(
            "-s",
            "--summary",
            help="Use user summary instead of summary in metadata.",
            action="store_true")
    parser.add_argument(
            "-d",
            "--date",
            help="Use user date instead of date in metadata.",
            action="store_true")
    parser.add_argument(
            "-a",
            "--artists",
            help="Use user artists instead of artists in metadata.",
            action="store_true")
    parser.add_argument(
            "-p",
            "--publisher",
            help="Use user publisher instead of publisher in metadata.",
            action="store_true")
    parser.add_argument(
            "-u",
            "--url",
            help="Use user URL instead of URL in metadata.",
            action="store_true")
    parser.add_argument(
            "-t",
            "--tags",
            help="Use user tags instead of tags in metadata.",
            action="store_true")
    parser.add_argument(
            "-g",
            "--grade",
            help="Use user grade/score instead of score in metadata.",
            action="store_true")
    args = parser.parse_args()
    # Check that directory is valid
    path = abspath(args.path)
    if not exists(path):
        color_print("Invalid path.", "red")
    else:
        # Create the epub
        user_create_epub(path,
                rp_description=args.summary,
                rp_date=args.date,
                rp_artists=args.artists,
                rp_publisher=args.publisher,
                rp_url=args.url,
                rp_tags=args.tags,
                rp_score=args.grade)
            
if __name__ == "__main__":
    main()
