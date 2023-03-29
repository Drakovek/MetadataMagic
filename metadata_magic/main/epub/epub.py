#!/usr/bin/env python3

from argparse import ArgumentParser
from ebooklib.epub import EpubBook, EpubHtml, EpubItem, EpubNav, EpubNcx, Link, Section, write_epub
from html_string_tools.main.html_string_tools import get_extension, regex_replace
from metadata_magic.main.comic_archive.comic_archive import create_cbz
from metadata_magic.main.comic_archive.comic_archive import get_temp_dir
from metadata_magic.main.comic_archive.comic_xml import generate_info_from_jsons
from metadata_magic.main.rename.sort_rename import sort_alphanum
from metadata_magic.test.temp_file_tools import create_text_file
from metadata_magic.test.temp_file_tools import read_text_file
from os import getcwd, listdir, mkdir
from os.path import abspath, basename, exists, join
from PIL import Image, UnidentifiedImageError
from python_print_tools.main.python_print_tools import color_print
from re import sub as resub
from re import findall
from shutil import copy
from typing import List
from xml.etree.ElementTree import indent as xml_indent
from xml.etree.ElementTree import Element, SubElement
from xml.etree.ElementTree import fromstring as xml_from_string
from xml.etree.ElementTree import tostring as xml_to_string

class DvkEpubHtml(EpubHtml):
    def __init__(self, uid=None, file_name='', media_type='', content=None, title='',
                 lang=None, direction=None, media_overlay=None, media_duration=None):
        super().__init__(uid, file_name, media_type, content, title,
                 lang, direction, media_overlay, media_duration)
        self.metas = []
    
    def get_content(self, default=None):
        # Get the default content
        original_xml = super().get_content(default).decode("UTF-8")
        original_xml = resub("\\s*<\\?xml[^>]*>\\s*", "", original_xml)
        original_xml = resub("\\s*<!DOCTYPE[^>]*>\\s*", "", original_xml)
        original_xml = resub("\\s*<html[^>]*>", "<html>", original_xml)
        # Parse xml
        base = xml_from_string(original_xml)
        attributes = {"xmlns":"http://www.w3.org/1999/xhtml"}
        attributes["xmlns:epub"] = "http://www.idpf.org/2007/ops"
        attributes["epub:prefix"] = "z3998: http://www.daisy.org/z3998/2012/vocab/structure/#"
        attributes["lang"] = "en"
        attributes["xml:lang"] = "en"
        base.attrib = attributes
        # Add meta tags
        myhead = base.find("head")
        for meta in self.metas:
            meta_el = SubElement(myhead, "meta")
            meta_el.attrib = meta
        # Return the xml
        xml_indent(base, space="   ")
        xml = xml_to_string(base).decode("UTF-8")
        xml = f"<?xml version='1.0' encoding='utf-8'?>\n<!DOCTYPE html>\n{xml}"
        return xml.encode("UTF-8")

    def add_meta(self, **kwgs):
        self.metas.append(kwgs)

    def get_metas(self):
        return (meta for meta in self.metas)

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

def get_title_from_file(file:str) -> str:
    """
    Gets an id/title for a file from the filename.

    :param file: File path or file name
    :type file: str, required
    :return: ID/title
    :rtype: str
    """
    regex = "^\\s*\\[[^\\]]+\\]\\s*|\\s*\\.[^\\.]{1,5}$"
    title = resub(regex, "", basename(file))
    return title

def create_image_page(image_file) -> str:
    """
    Returns a epub formatted XHTML page containing a single full page image.
    
    :param image_file: Path to the image file to include on the page
    :type image_file: str, required
    :param indent: Whether to add indents to the XHTML file, defaults to True
    :type indent: bool, optional
    :return: XHTML text
    :rtype: str
    """
    # Load image
    try:
        full_path = abspath(image_file)
        image = Image.open(full_path)
        width, height = image.size
    except (FileNotFoundError, UnidentifiedImageError): return None
    # Create image container
    base = Element("body")
    container = SubElement(base, "div")
    container.attrib = {"class":"image-page-container"}
    # Create the image element
    filename = basename(full_path)
    title = get_title_from_file(full_path)
    img_element = SubElement(container, "img")
    attributes = {"class":"vertical-image-page", "src":f"../images/{filename}", "alt":title}
    if width > height:
        attributes["class"] = "horizontal-image-page"
    img_element.attrib = attributes
    xml = xml_to_string(base).decode("UTF-8")
    # Create DvkEpubHtml
    filename = filename[:len(filename) - len(get_extension(filename))]
    chapter = DvkEpubHtml(title=title, file_name=f"content/{filename}.xhtml", lang='en')
    chapter.set_content(xml)
    chapter.add_link(href="../style/epubstyle.css", rel="stylesheet", type="text/css")
    # Add size limiting meta tag
    chapter.add_meta(content=f"width={width}, height={height}", name="viewport")
    # Return EpubHtml
    return chapter

def txt_to_xhtml(txt_file:str) -> str:
    """
    Creates text for an epub XHTML content file from a given txt file.
    
    :param txt_file: Path to a txt file.
    :type txt_file: str, required
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
    text_container = SubElement(body, "div")
    text_container.attrib = {"class":"text-container"}
    for paragraph in paragraphs:
        p_element = SubElement(text_container, "p")
        p_element.text = paragraph.replace("\n","{{{br}}}")
    # Get xml as string
    xml = xml_to_string(body).decode("UTF-8")
    # Remove misformatted tags
    xml = xml.replace("{{{br}}}", "<br/>")
    xml = xml.replace("{{br}}", "<br/>")
    xml = xml.replace("{{i}}", "<i>")
    xml = xml.replace("{{/i}}", "</i>")
    xml = xml.replace("{{b}}", "<b>")
    xml = xml.replace("{{/b}}", "</b>")
    xml = resub("(<br\\/>|\\s)*<\\/p?>", "</p>", xml)
    xml = resub("<\\/i>\\s+(?=[,.?!])", "</i>", xml)
    xml = resub("<\\/b>\\s+(?=[,.?!])", "</b>", xml)
    xml = resub("\\s+<\\/i>", "</i>", xml)
    xml = resub("\\s+<\\/b>", "</b>", xml)
    # Get the title for the file
    title = get_title_from_file(full_path)
    filename = basename(full_path)
    filename = filename[:len(filename) - len(get_extension(full_path))]
    # Create EpubHtml
    chapter = EpubHtml(title=title, file_name=f"content/{filename}.xhtml", lang='en')
    chapter.set_content(xml)
    chapter.add_link(href="../style/epubstyle.css", rel="stylesheet", type="text/css")
    # Return the EpubHtml
    return chapter

def get_style() -> str:
    """
    Creates the default css stylesheet for the epub book.
    
    :return: CSS style sheet 
    :rtype: str
    """
    # Body Style
    style = ""
    style = f"{style}body {{\n"
    style = f"{style}    margin: 0px 0px 0px 0px;\n"
    style = f"{style}}}\n\n"
    # Header style
    style = f"{style}.header {{\n"
    style = f"{style}    width: 100%;\n"
    style = f"{style}    font-size: 2em;\n"
    style = f"{style}    line-height: 1.5em;\n"
    style = f"{style}}}\n\n"
    # Subheader style
    style = f"{style}.subheader {{\n"
    style = f"{style}    width: 100%;\n"
    style = f"{style}    font-size: 1.5em;\n"
    style = f"{style}    line-height: 1.5em;\n"
    style = f"{style}}}\n\n"
    # Center style
    style = f"{style}.center {{\n"
    style = f"{style}    text-align: center;\n"
    style = f"{style}}}\n\n"
    # Text Container
    style = f"{style}.text-container {{\n"
    style = f"{style}    margin: 3em 3em 3em 3em;\n"
    style = f"{style}    line-height: 1.5em;\n"
    style = f"{style}}}\n\n"
    # Vertical Image Page
    style = f"{style}.vertical-image-page {{\n"
    style = f"{style}    display: block;\n"
    style = f"{style}    height: 100%;\n"
    style = f"{style}    width: auto;\n"
    style = f"{style}    margin: auto auto auto auto;\n"
    style = f"{style}}}\n\n"
    # Horizontal Image Page
    style = f"{style}.horizontal-image-page {{\n"
    style = f"{style}    display: block;\n"
    style = f"{style}    width: 100%;\n"
    style = f"{style}    height: auto;\n"
    style = f"{style}    margin: auto auto auto auto;\n"
    style = f"{style}}}\n\n"
    # Image Page Container
    style = f"{style}.image-page-container {{\n"
    style = f"{style}    height: 100vh;\n"
    style = f"{style}}}"
    # Return style
    return style

def create_metadata(metadata:dict) -> EpubBook:
    """
    Creates an EpubBook object with the given metadata.
    Metadata is the same as used for the get_comic_xml function.

    :param metadata: Metadata dictionary
    :type metadata: dict, required
    :return: EpubBook object containing metadata
    :rtype: EpubBook
    """
    # Create book
    book = EpubBook()
    # Set the language
    book.set_language("en")
    # Set the identifier
    if metadata["url"] is not None:
        book.set_identifier(metadata["url"])
    else:
        book.set_identifier(metadata["title"].lower())
    # Set the title
    book.set_title(metadata["title"])
    # Set the description
    if metadata["description"] is not None:
        book.add_metadata("DC", "description", metadata["description"])
    # Add Authors
    try:
        authors = metadata["writer"].split(",")
    except AttributeError: authors = []
    for i in range(0, len(authors)):
        book.add_author(authors[i], role="aut", uid=f"author{i}")
    # Add Illustrator(s)
    try:
        illustrators = metadata["artist"].split(",")
    except AttributeError: illustrators = []
    for i in range(0, len(illustrators)):
        book.add_author(illustrators[i], role="ill", uid=f"illustrator{i}")
    # Add Cover Artist(s)
    try:
        covartists = metadata["cover_artist"].split(",")
    except AttributeError: covartists = []
    for i in range(0, len(covartists)):
        book.add_author(covartists[i], role="cov", uid=f"covartist{i}")
    # Add publisher
    if metadata["publisher"] is not None:
        book.add_metadata("DC", "publisher", metadata["publisher"])
    # Add date
    if metadata["date"] is not None:
        book.add_metadata("DC", "date", metadata["date"] + "T00:00:00+00:00")
    # Set the score
    try:
        score = int(metadata["score"])
        if score > -1 and score < 6:
            book.add_metadata(None, "meta", str(float(score * 2)), {"property":"calibre:rating"})
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
        book.add_metadata("DC", "subject", tag)
    # Add series info
    if metadata["series"] is not None:
        attribs = {"property":"belongs-to-collection", "id":"series-title"}
        book.add_metadata(None, "meta", metadata["series"], attribs)
        attribs = {"refines":"#series-title", "property":"collection-type"}
        book.add_metadata(None, "meta", "series", attribs)
        try:
            num = float(metadata["series_number"])
            attribs = {"refines":"#series-title", "property":"group-position"}
            book.add_metadata(None, "meta", metadata["series_number"], attribs)
        except (TypeError, ValueError): pass
    # Return ebook with metadata
    return book

def get_items(directory:str) -> List[EpubItem]:
    """
    Creates a list of items to include in epub based on files in a given directory.

    :param directory: Directory to search for files within
    :type directory: str, required
    :return: List of EpubItems
    :rtype: list[EpubItem]
    """
    # Get list of files in directory
    full_directory = abspath(directory)
    files = sort_alphanum(listdir(full_directory))
    # Run through files
    items = []
    for file in files:
        # Read file
        full_file = abspath(join(full_directory, file))
        with open(full_file, "rb") as infile:
            contents = infile.read()
        # Create item
        item = EpubItem(uid=basename(full_file).replace(".","-"),
                    file_name="original/"+basename(full_file),
                    content=contents)
        # Copy image
        if item.get_type() == 1:
            title = get_title_from_file(full_file)
            image = EpubItem(uid=title,
                        file_name="images/"+basename(full_file),
                        content=contents)
            items.append(image)
        items.append(item)
    # Add style file
    css = EpubItem(uid="epubstyle",
                file_name="style/epubstyle.css",
                media_type="text/css",
                content=get_style())
    items.append(css)
    # Return items
    return items

def get_chapters(directory:str) -> List[EpubHtml]:
    """
    Returns a list of EpubHtml objects for each chapter of the epub.
    Creates XHTML chapter files for each text file and image in a given directory.

    :param directory: Directory to search for files within
    :type directory: str, required
    :return: List of EpubHtml objects for each chapter
    :rtype: list[EpubHtml]
    """
    # Get list of files in directory
    full_directory = abspath(directory)
    files = sort_alphanum(listdir(full_directory))
    # Run through files
    chapters = []
    for file in files:
        # Get the XML body
        xml = None
        full_file = abspath(join(full_directory, file))
        extension = get_extension(full_file)
        if extension == ".txt":
            chapter = txt_to_xhtml(full_file)
            chapters.append(chapter)
            continue
        if extension == ".jpg" or extension == ".jpeg" or extension == ".png":
            chapter = create_image_page(full_file)
            if chapter is not None:
                chapters.append(chapter)
    # Return chapters
    return chapters

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
    full_directory = abspath(directory)
    epub_file = abspath(join(full_directory, basename(full_directory) + ".epub"))
    # Get book from metadata
    book = create_metadata(metadata)
    # Get XHTMLs and base content    
    chapters = get_chapters(full_directory)
    items = get_items(full_directory)
    # Add items to the book
    for chapter in chapters:
        book.add_item(chapter)
    for item in items:
        book.add_item(item)
    # Add spine and table of contents
    book.spine = chapters
    book.toc = chapters
    book.add_item(EpubNcx())
    book.add_item(EpubNav())
    # Write book
    write_epub(epub_file, book)
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
