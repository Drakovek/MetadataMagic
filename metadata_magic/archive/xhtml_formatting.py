#!/usr/bin/env python3

import re
import html_string_tools
import metadata_magic.file_tools as mm_file_tools
import lxml.html
import lxml.etree
from xml.etree import ElementTree
from PIL import Image, UnidentifiedImageError
from os.path import basename

def get_title_from_file(file:str) -> str:
    """
    Returns an appropriate title for a given file.
    
    :param file: Path and filename of a file
    :type file: str, required
    :return: Title to use for the file in XHTML header
    :rtype: str
    """
    title = basename(file)
    title = re.sub(r"\.[^\.]{1,6}$", "", title).strip()
    title = re.sub(r"^\[[^\]]+\]\s*|^\([^\)]+\)\s*", "", title)
    return title

def format_xhtml(html:str, title:str) -> str:
    """
    Formats XML text into XHTML text ready to be included in an EPUB file.
    
    :param html: HTML text to format
    :type html: str, required
    :param title: Title to use for the XHTML header
    :type title: str, required
    :return: XHTML formatted text
    :rtype: str
    """  
    # Set the base element for the XHTML 
    base = ElementTree.Element("html")
    base.attrib = {"xmlns":"http://www.w3.org/1999/xhtml"}
    # Create the head SubElement
    head = ElementTree.SubElement(base, "head")
    title_element = ElementTree.SubElement(head, "title")
    title_element.text = title
    meta = ElementTree.SubElement(head, "meta")
    meta.attrib = {"charset":"utf-8"}
    # Remove all unnecessary HTML escape entities
    formatted_html = html_string_tools.html.replace_reserved_in_html(html)
    # Remove newlines
    formatted_html = formatted_html.replace("\n", "").strip()
    # Remove whitespace before closing paragraph and div elenments
    formatted_html = re.sub(r"\s+<\s*\/\s*p\s*>", "</p>", formatted_html)
    formatted_html = re.sub(r"\s+<\s*\/\s*div\s*>", "</div>", formatted_html)
    # Remove whitespace after opening paragraph and div elenments
    formatted_html = "".join(reversed(formatted_html))
    formatted_html = re.sub(r"\s+(?=>[^<]*p\s*<)|\s+(?=>[^<]*vid\s*<)", "", formatted_html)
    # Add centering element to page break lines
    formatted_html = re.sub(r"<\s*(?=[\-*][\s\-*]+>)", "<>retnec/<", formatted_html)
    formatted_html = "".join(reversed(formatted_html))
    formatted_html = re.sub(r">\s*(?=[\-*][\s\-*]+<)", "><center>", formatted_html)
    # Remove paragraph and div elements containing nothing
    formatted_html = re.sub(r"<\s*p[^>]*>\s*<\s*\/\s*p\s*>", "", formatted_html)
    formatted_html = re.sub(r"<\s*div[^>]*>\s*<\s*\/\s*div\s*>", "", formatted_html)
    formatted_html = re.sub(r"<\s*p[^>]*\/\s*>|<\s*div[^>]*\/\s*>", "", formatted_html)
    formatted_html = formatted_html.strip()
    # Add paragraph elements if necessary
    if not formatted_html.startswith("<") and not formatted_html.endswith(">"):
        formatted_html = f"<p>{formatted_html}</p>"
    # Use LXML to clean up tags
    root = lxml.html.fromstring(f"<html><body>{formatted_html}</body></html>")
    formatted_html = lxml.etree.tostring(root).decode("UTF-8")
    formatted_html = re.sub(r"^\s*<\s*html\s*>|<\s*\/\s*html\s*>\s*$", "", formatted_html)
    formatted_html = re.sub(r"^\s*<\s*body\s*>|<\s*\/\s*body\s*>\s*$", "", formatted_html)
    # Convert image to full page SVG element if there is a single image present
    regex = "<div>\\s*<img[^>]+width=\"[0-9]+\"[^>]+height=\"[0-9]+\"[^>]*>\\s*<\\/div>|"
    regex = f"{regex}<div>\\s*<img[^>]+height=\"[0-9]+\"[^>]+width=\"[0-9]+\"[^>]*>\\s*<\\/div>"
    images = re.findall(regex, formatted_html)
    contains_text = len(re.findall(r"<div[^\>]*>(?!.*<img).+<\/div>|<p>|<p\s[^\>]*>", formatted_html)) == 0
    if len(images) == 1 and contains_text:
        # Get the image size
        width = re.findall("(?<=width=\")[0-9]+(?=\")", images[0])[0]
        height = re.findall("(?<=height=\")[0-9]+(?=\")", images[0])[0]
        # Get the image alt tag
        alt = re.findall("(?<=alt=\")[^\"]*(?=\")", images[0])[0]
        # Add the image-page id
        modified_image_tag = re.sub(r"^<div>|</div>$", "", images[0])
        modified_image_tag = re.sub(r"^<img\s+", "<image ", modified_image_tag)
        modified_image_tag = re.sub(r"src=", "xlink:href=", modified_image_tag)
        modified_image_tag = re.sub("\\s*alt=\"[^\"]*\"\\s*", " ", modified_image_tag)
        # Create the svg wrapper
        svg = "<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" "
        svg = f"{svg}width=\"100%\" height=\"100%\" viewBox=\"0 0 {width} {height}\" "
        svg = f"{svg}preserveAspectRatio=\"xMidYMid meet\" version=\"1.1\">"
        modified_image_tag = f"{svg}<title>{alt}</title>{modified_image_tag}</svg>"
        # Create the div wrapper
        modified_image_tag = f"<div id=\"full-image-container\">{modified_image_tag}</div>"
        formatted_html = formatted_html.replace(images[0], modified_image_tag)
        # Register the namespaces
        ElementTree.register_namespace("svgns", "http://www.w3.org/2000/svg")
        ElementTree.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    # Add the CSS stylesheet to the head
    link = ElementTree.SubElement(head, "link")
    link.attrib = {"rel":"stylesheet", "href":"../style/epubstyle.css", "type":"text/css"}
    # Add as body to the main XML tree
    try:
        body = ElementTree.fromstring(f"<body>{formatted_html}</body>")
        base.append(body)
    except ElementTree.ParseError as parse_error:
        character = ord(formatted_html[parse_error.position[0]])
        print(f"XML Parse Error: Character {character}")
        return None
    # Set indents to make the XML more readable
    ElementTree.indent(base, space="    ")
    # Get xml as string
    xml = ElementTree.tostring(base).decode("UTF-8")
    return f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n{xml}"

def text_to_xhtml(text:str, replace_reserved:bool=True) -> str:
    """
    Formats text to XHTML, automatically detecting how text should be split into paragraph elements.
    
    :param text: Text to convert into XHTML format
    :type text: str, required
    :param replace_reserved: Whether to escape reserved XHTML reserved charactes.
    :type replace_reserved: bool, optional
    :return: XHTML with text split into paragraphs
    :rtype: str
    """
    # Remove redundant new line characters
    formatted_text = text.replace("\r", "")
    formatted_text = text.replace("\t", "    ")
    # Separate sections into paragraphs
    formatted_text = re.sub(r"\n\s{3,}|(?:\n\s*){2,}", "{{{PPP}}}", formatted_text)
    paragraphs = formatted_text.split("{{{PPP}}}")
    # Format each paragraph
    xhtml = ""
    for paragraph in paragraphs:
        formatted_paragraph = re.sub(r"\s*\n\s*", " ", paragraph)
        formatted_paragraph = formatted_paragraph.strip()
        if replace_reserved:
            formatted_paragraph = html_string_tools.html.replace_reserved_characters(formatted_paragraph, True)
        xhtml = f"{xhtml}<p>{formatted_paragraph}</p>"
    # Return xhtml
    return xhtml

def txt_to_xhtml(txt_file:str) -> str:
    """
    Formats text from a text file to XHTML, automatically detecting how text should be split into paragraph elements.
    
    :param text_file: Text file to convert into XHTML format
    :type text_file: str, required
    :return: XHTML with text split into paragraphs
    :rtype: str
    """
    # Read text from the given txt file
    text = mm_file_tools.read_text_file(txt_file)
    return text_to_xhtml(text)

def html_to_xhtml(html_file:str) -> str:
    """
    Formats text from an HTML file to XHTML.
    Restructures paragraph elements if necessary.
    
    :param html_file: HTML file to convert into XHTML format
    :type html_file: str, required
    :return: XHTML with text split into paragraphs
    :rtype: str
    """
    # Read text from the HTML file
    text = mm_file_tools.read_text_file(html_file)
    # Remove all carriage returns
    for i in range(len(text)-1, -1, -1):
        if ord(text[i]) == 13:
            text = text[:i] + text[i+1:]
    # Parse the HTML text
    root = lxml.html.fromstring(text)
    # Get internal html tag
    delete_encapsulation = False
    try:
        html = root.xpath("//html")[0]
        root = html
        delete_encapsulation = True
    except IndexError: pass
    # Get internal body tag
    try:
        body = root.xpath("//body")[0]
        root = body
        delete_encapsulation = True
    except IndexError: pass
    # Get text block (Deviantart formatted html)
    try:
        text_class = root.xpath("//div[@class='text']")[0]
        root = text_class
        delete_encapsulation = True
    except IndexError: pass
    # Get text from the root
    content = lxml.etree.tostring(root).decode("UTF-8")
    # Delete encapsulation
    if delete_encapsulation:
        content = re.sub(r"^<[^>]*>|<\s*\/[^>]*>$", "", content)
    # Delete javascript tags
    content = re.sub(r"<\s*script[^>]*>[^<]*<\s*\/\s*script\s*>|<\s*script\s*\/\s*>", "", content)
    # Reformat text in <pre> elements
    for pre in re.findall(r"<pre>[\S\s]*<\/pre>", content):
        new_pre = text_to_xhtml(re.sub(r"^<pre>|<\/pre>$", "", pre), False)
        content = re.sub(r"<pre>[\S\s]*<\/pre>", new_pre, content, count=1)
    # Reformat if there are no individual paragraph elements
    if len(re.findall(r"<\/p>", content)) == 1 and len(re.findall(r"<br\s*\/>", content)) > 0:
        content = re.sub(r"\n", "", content)
        content = re.sub(r"^<p>|<\/p>$", "", content)
        content = re.sub(r"\s*<br\s*\/>\s*", "\n", content)
        content = text_to_xhtml(content, False)
    # Replace escape characters
    content = content.strip().replace("\n", "")
    content = html_string_tools.html.replace_reserved_in_html(content, True)
    # Return in XML format
    return content

def image_to_xhtml(image_file:str, alt_string:str=None) -> str:
    """
    Creates an XHTML svg and img container to reference a given image for use in an EPUB file.
    
    :param image_file: Image file to reference
    :type image_file: str, required
    :param alt_string: Text to use for the alt value for the image tag, defaults to None
    :type alt_string:, str, optional
    :return: XML formatted text
    :rtype: str
    """
    # Get the image path
    image_path = basename(image_file)
    image_path = f"../images/{image_path}"
    # Get the alt tag
    title = alt_string
    if alt_string is None:
        title = get_title_from_file(image_file)
    # Get the size of the image
    try:
        image = Image.open(image_file)
        width, height = image.size
    except UnidentifiedImageError:
        return ""
    # Construct the xml
    return f"<div><img src=\"{image_path}\" alt=\"{title}\" width=\"{width}\" height=\"{height}\" /></div>"