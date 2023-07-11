#!/usr/bin/env python3

from argparse import ArgumentParser
from html_string_tools.main.html_string_tools import get_extension, regex_replace
from lxml.html import fromstring as html_from_string
from lxml.etree import tostring as lxml_to_string
from metadata_magic.main.comic_archive.comic_archive import create_cbz
from metadata_magic.main.file_tools.file_tools import get_temp_dir
from metadata_magic.main.comic_archive.comic_xml import generate_info_from_jsons
from metadata_magic.main.rename.rename_tools import sort_alphanum
from metadata_magic.test.temp_file_tools import create_text_file
from metadata_magic.test.temp_file_tools import read_text_file
from os import getcwd, listdir, mkdir
from os.path import abspath, basename, exists, isdir, join, relpath
from PIL import Image, UnidentifiedImageError
from python_print_tools.main.python_print_tools import color_print
from re import sub as resub
from re import findall
from shutil import copy
from tqdm import tqdm
from typing import List
from xml.etree.ElementTree import indent as xml_indent
from xml.etree.ElementTree import Element, SubElement
from xml.etree.ElementTree import fromstring as xml_from_string
from xml.etree.ElementTree import tostring as xml_to_string
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED

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

def format_xhtml(html:str, title:str, head_tags:List[dict]=[], indent:bool=True) -> str:
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
    meta.attrib = {"charset":"utf-8"}
    # Add given elements to head
    for head_tag in head_tags:
        head_element = SubElement(head, head_tag["type"])
        head_element.attrib = head_tag["params"]
    # Add stylesheet to head
    link = SubElement(head, "link")
    link.attrib = {"rel":"stylesheet", "href":"../style/epubstyle.css", "type":"text/css"}
    # Parse the given html text and add to body
    final_html = resub("^\\s+|\\s+$|\\n", "", html)
    body = xml_from_string(f"<body>{final_html}</body>")
    base.append(body)
    # Set indents to make the XML more readable
    if indent:
        xml_indent(base, space="   ")
    # Get xml as string
    xml = xml_to_string(base).decode("UTF-8")
    return f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n{xml}"

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
    # Load image
    try:
        full_path = abspath(image_file)
        image = Image.open(full_path)
        width, height = image.size
    except (FileNotFoundError, UnidentifiedImageError): return None
    # Create image container
    container = Element("div")
    container.attrib = {"class":"image-page-container"}
    # Create the image element
    filename = basename(full_path)
    title = get_title_from_file(full_path)
    img_element = SubElement(container, "img")
    attributes = {"class":"vertical-image-page", "src":f"../images/{filename}", "alt":title}
    if width > height:
        attributes["class"] = "horizontal-image-page"
    img_element.attrib = attributes
    xml = xml_to_string(container).decode("UTF-8")
    # Add size limited meta tag
    tag = {"type":"meta"}
    tag["params"] = {"content":f"width={width}, height={height}", "name":"viewport"}
    # Return EpubHtml
    return format_xhtml(xml, title, [tag], indent)

def html_to_xhtml(html_file:str, indent:bool=False) -> str:
    """
    Creates text for an epub XHTML content file from a given html file.
    
    :param txt_file: Path to an html file.
    :type txt_file: str, required
    :param indent: Whether to add indents to the XHTML file, defaults to True
    :type indent: bool, optional
    :return: XHTML text
    :rtype: str
    """
    # Read html file
    full_path = abspath(html_file)
    content = read_text_file(full_path)
    print(content)
    # Parse as XML
    root = html_from_string(content)
    # Extract body if necessary
    try:
        body = root.xpath("//body")[0]
        body_text = lxml_to_string(body).decode("UTF-8")
        print(lxml_to_string(root))
        body_text = findall("(?<=^<body>).+(?=<\\/body>$)", body_text)[0]
    except IndexError:
        body_text = lxml_to_string(root).decode("UTF-8")
        inner_text = findall("(?<=^<div>).+(?=<\\/div>$)", body_text)
        if len(inner_text) == 1:
            body_text = inner_text[0]
    # Format html as xml
    body_text = f"<div class=\"text-container\">{body_text}</div>"
    return format_xhtml(body_text, get_title_from_file(full_path), indent=indent)

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
    text_container = Element("div")
    text_container.attrib = {"class":"text-container"}
    for paragraph in paragraphs:
        p_element = SubElement(text_container, "p")
        p_element.text = paragraph.replace("\n","{{{br}}}")
    # Get xml as string
    xml = xml_to_string(text_container).decode("UTF-8")
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
    # Return XHTML
    return format_xhtml(xml, get_title_from_file(full_path), indent=indent)

def create_style_file(file_path:str):
    """
    Creates the default css stylesheet for the epub book.
    
    :param file_path: Path to save the stylesheet to
    :type file_path: str, required
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
    # Create file
    full_path = abspath(file_path)
    create_text_file(full_path, style)

def create_nav_file(xhtmls:List[str], file_path:str, title:str, indent:bool=True):
    """
    Creates the Table of Contents nav file for the epub file.
    
    :param xhtmls: List of XHTML files to include in the contents
    :type xhtmls: str, required
    :param file_path: Path of the file to save to
    :type file_path: str, required
    :param title: Title to use for the nav file
    :type title: str, required
    :param indent: Whether to add indents to the XML file, defaults to True
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
    meta.attrib = {"charset":"utf-8"}
    title_element = SubElement(head, "title")
    title_element.text = title
    # Create navigation body and header
    body = SubElement(base, "body")
    h1 = SubElement(body, "h1")
    h1.text = title
    # Create nav element
    nav = SubElement(body, "nav")
    nav.attrib = {"epub:type":"toc", "id":"toc"}
    ol = SubElement(nav, "ol")
    # Create entries for each XHTML file
    for xhtml in xhtmls:
        # Get title
        filename = basename(xhtml)
        name = get_title_from_file(filename)
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
    xml = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n{xml}"
    # Write XML
    full_path = abspath(file_path)
    create_text_file(full_path, xml)

def create_ncx_file(xhtmls:List[str], file_path:str, title:str, uid:str, indent:bool=True):
    """
    Creates the Table of Contents ncx file for the epub file.
    
    :param xhtmls: List of XHTML files to include in the contents
    :type xhtmls: str, required
    :param file_path: Path of the file to save to
    :type file_path: str, required
    :param title: Title to use for the nav file
    :type title: str, required
    :param uid: ID to use for the contents file
    :type uid: str, required
    :param indent: Whether to add indents to the XML file, defaults to True
    :type indent: bool, optional
    """
    # Create base of ncx file
    attributes = {"xmlns":"http://www.daisy.org/z3986/2005/ncx/"}
    attributes["version"] = "2005-1"
    base = Element("ncx")
    base.attrib = attributes
    # Create ncx head
    head = SubElement(base, "head")
    uid_element = SubElement(head, "meta")
    uid_element.attrib = {"content":uid, "name":"dtb:uid"}
    depth = SubElement(head, "meta")
    depth.attrib = {"content":"0", "name":"dtb:depth"}
    pcount = SubElement(head, "meta")
    pcount.attrib = {"content":"0", "name":"dtb:totalPageCount"}
    number = SubElement(head, "meta")
    number.attrib = {"content":"0", "name":"dtb:maxPageNumber"}
    # Create title tag
    title_element = SubElement(base, "docTitle")
    title_text = SubElement(title_element, "text")
    title_text.text = title
    # Create nav map
    nav_map = SubElement(base, "navMap")
    for xhtml in xhtmls:
        nav_point = SubElement(nav_map, "navPoint")
        nav_point.attrib = {"id":get_title_from_file(xhtml) + "-xhtml"}
        nav_label = SubElement(nav_point, "navLabel")
        nav_text = SubElement(nav_label, "text")
        nav_text.text = get_title_from_file(xhtml)
        content = SubElement(nav_point, "content")
        content.text = "content/" + str(basename(xhtml))
    # Set indents to make the XML more readable
    if indent:
        xml_indent(base, space="   ")
    # Get xml as string
    xml = xml_to_string(base).decode("UTF-8")
    xml = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n{xml}"
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
        media_type = ""
        # Get the file mimetype
        if extension == ".xhtml":
            media_type = "application/xhtml+xml"
            attributes = {"href":f"content/{filename}"}
        elif extension == ".jpeg" or extension == ".jpg":
            media_type = "image/jpeg"
            attributes = {"href":f"images/{filename}"}
        elif extension == ".png":
            media_type = "image/png"
            attributes = {"href":f"images/{filename}"}
        elif extension == ".svg":
            media_type = "image/svg+xml"
            attributes = {"href":f"images/{filename}"}
        # Create item
        attributes["id"] = get_title_from_file(filename) + "-" + extension[1:]
        attributes["media-type"] = media_type
        item = SubElement(base, "item")
        item.attrib = attributes
    # Add css file
    css_item = SubElement(base, "item")
    css_item.attrib = {"href":"style/epubstyle.css", "id":"epubstyle-css", "media-type":"text/css"}
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
    content_files = sort_alphanum(listdir(content_dir))
    # Get list of files in the images directory
    image_dir = abspath(join(directory, "images"))
    image_files = sort_alphanum(listdir(image_dir))
    # Get the manifest and metadata sections
    files = []
    files.extend(content_files)
    files.extend(image_files)
    manifest = create_manifest(files)
    meta_xml = create_metadata_xml(metadata)
    # Create nav file
    nav_file = abspath(join(full_directory, "nav.xhtml"))
    create_nav_file(content_files, nav_file, metadata["title"], True)
    # Create ncx file
    uid = metadata["url"]
    if uid is None:
        uid = metadata["title"]
    ncx_file = abspath(join(full_directory, "toc.ncx"))
    create_ncx_file(content_files, ncx_file, metadata["title"], uid, True)
    # Create the content xml contents
    base = Element("package")
    base.attrib = {"xmlns":"http://www.idpf.org/2007/opf", "unique-identifier":"uid", "version":"3.0"}
    base.append(xml_from_string(meta_xml))
    base.append(xml_from_string(manifest))
    spine = SubElement(base, "spine")
    for file in content_files:
        # Create spine items
        itemref = SubElement(spine, "itemref")
        itemref.attrib = {"idref":get_title_from_file(file) + "-xhtml"}
    # Save content xml to file
    xml_indent(base, space="   ")
    xml = xml_to_string(base).decode("UTF-8")
    xml = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n{xml}"
    package_file = abspath(join(full_directory, "content.opf"))
    create_text_file(package_file, xml)

def zip_epub(directory:str, epub_file):
    try:
        # Get list of files in the directory
        full_directory = abspath(directory)
        files = listdir(full_directory)
        for i in range(0, len(files)):
            files[i] = abspath(join(full_directory, files[i]))
        # Expand list of files to include subdirectories
        for file in files:
            if isdir(file):
                sub_files = listdir(file)
                for i in range(0, len(sub_files)):
                    files.append(abspath(join(file, sub_files[i])))
        # Create empty epub file
        with ZipFile(epub_file, "w", compression=ZIP_DEFLATED, compresslevel=8) as out_file:
            out_file.writestr('mimetype', 'application/epub+zip', compress_type=ZIP_STORED)
        assert exists(epub_file)
        # Write contents of directory to epub file
        for file in tqdm(files):
            relative = relpath(file, full_directory)
            with ZipFile(epub_file, "a", compression=ZIP_DEFLATED, compresslevel=8) as out_file:
                if not isdir(file):
                    out_file.write(file, relative, compress_type=ZIP_DEFLATED, compresslevel=8)
        # Return the path of the written epub archive
        return epub_file
    except FileNotFoundError:
        return None

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
    # Create container
    meta_dir = abspath(join(temp_dir, "META-INF"))
    mkdir(meta_dir)
    base = Element("container")
    base.attrib = {"xmlns":"urn:oasis:names:tc:opendocument:xmlns:container", "version":"1.0"}
    rootfiles = SubElement(base, "rootfiles")
    rootfile = SubElement(rootfiles, "rootfile")
    rootfile.attrib = {"media-type":"application/oebps-package+xml", "full-path":"EPUB/content.opf"}
    xml_indent(base, space="   ")
    xml = xml_to_string(base).decode("UTF-8")
    xml = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n{xml}"
    container_file = abspath(join(meta_dir, "container.xml"))
    create_text_file(container_file, xml)
    # Get list of all contents of the given directory
    files = listdir(input_directory)
    for i in range(0, len(files)):
        files[i] = abspath(join(input_directory, files[i]))
    # Copy all files into folder to contain all original unaltered files
    epub_folder = abspath(join(temp_dir, "EPUB"))
    mkdir(epub_folder)
    original_folder = abspath(join(epub_folder, "original"))
    mkdir(original_folder)
    for file in files:
        copy(file, abspath(join(original_folder, basename(file))))
    # Create style sheet
    style_folder = abspath(join(epub_folder, "style"))
    mkdir(style_folder)
    create_style_file(abspath(join(style_folder, "epubstyle.css")))
    # Copy all images and convert all text to XHTML for the content folder
    content_folder = abspath(join(epub_folder, "content"))
    mkdir(content_folder)
    image_folder = abspath(join(epub_folder, "images"))
    mkdir(image_folder)
    for file in files:
        filename = basename(file)
        extension = get_extension(filename)
        if extension == ".txt":
            # Create text extension
            filename = filename[:len(filename) - len(extension)] + ".xhtml"
            xml = txt_to_xhtml(file, True)
            create_text_file(abspath(join(content_folder, filename)), xml)
        if extension == ".html" or extension == ".htm" or extension == ".xhtml":
            # Create text extension
            filename = filename[:len(filename) - len(extension)] + ".xhtml"
            xml = html_to_xhtml(file, True)
            create_text_file(abspath(join(content_folder, filename)), xml)
        if extension == ".png" or extension == ".jpg" or extension == ".jpeg" or extension == ".svg":
            # Copy image file
            copy(file, abspath(join(image_folder, filename)))
            # Create image page
            filename = filename[:len(filename) - len(extension)] + ".xhtml"
            xml = create_image_page(file)
            create_text_file(abspath(join(content_folder, filename)), xml)
    # Create the package and nav files
    create_epub_files(epub_folder, metadata)
    # Zip files and copy to epub
    zip_epub(temp_dir, epub_file)
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
