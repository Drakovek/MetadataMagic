import os
import re
import shutil
import html_string_tools
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.comic_xml as mm_comic_xml
import metadata_magic.rename.rename_tools as mm_rename_tools
from xml.etree import ElementTree
from os.path import abspath, basename, exists, isdir, join
from typing import List

def format_xhtml(html:str, title:str) -> str:
    """
    Formats HTML text into XHTML text ready to be included in an EPUB file.
    
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
    # Add the CSS stylesheet to the head
    link = ElementTree.SubElement(head, "link")
    link.attrib = {"rel":"stylesheet", "href":"../style/epubstyle.css", "type":"text/css"}
    # Format the given HTML text
    formatted_html = re.sub(r"^\s+|\s+$|\n", "", html)
    formatted_html = re.sub(r"\s*<p>\s*", "<p>", formatted_html)
    formatted_html = re.sub(r"\s*</p>\s*", "</p>", formatted_html)
    formatted_html = re.sub(r"\s*<div>\s*", "<div>", formatted_html)
    formatted_html = re.sub(r"\s*</div>\s*", "</div>", formatted_html)
    formatted_html = re.sub(r"\s*<p></p>\s*|\s*<p\s*/>\s*", "", formatted_html)
    formatted_html = re.sub(r"\s*<div></div>\s*|\s*<div\s*/>\s*", "", formatted_html)
    if not formatted_html.startswith("<") and not formatted_html.endswith(">"):
        formatted_html = f"<p>{formatted_html}</p>"
    # Add text to the body
    try:
        formatted_html = f"<body>{formatted_html}</body>"
        body = ElementTree.fromstring(formatted_html)
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

def txt_to_xhtml(txt_file:str, title:str) -> str:
    """
    Reads the text in a .txt file and formats it into XHTML for an EPUB file
    
    :param txt_file: Text file to read
    :type text_file: str, required
    :param title: Title to use for the XHTML header
    :type title: str, required
    :return: XHTML formatted text
    :rtype: str
    """
    # Read text from the given txt file
    text = mm_file_tools.read_text_file(txt_file)
    # Remove unnessecary whitespace
    text.replace("\r\n", "\n")
    text.replace("\n\r", "\n")
    text.replace("\r", "")
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"^\s+|\s+$", "", text)
    # Split into paragraphs
    html = ""
    paragraphs = text.split("\n\n")
    for paragraph in paragraphs:
        # Add escape characters
        formatted = paragraph.replace("\n", "{{{{br}}}}")
        formatted = html_string_tools.html.replace_reserved_characters(formatted)
        formatted = formatted.replace("{{{{br}}}}", "<br />")
        html = f"{html}<p>{formatted}</p>"
    html.replace("\r", "")
    # Return with XHTML formatting
    return format_xhtml(html, title)

def get_title_from_file(file:str) -> str:
    """
    Returns an appropriate title for a given file.
    
    :param file: Path and filename of a file
    :type file: str, required
    :return: Title to use for the file in XHTML header
    :rtype: str
    """
    title = basename(file)
    title = re.sub(r"\.[^\.]{1,6}$", "", title)
    title = re.sub(r"^\s+|\s+$", "", title)
    title = re.sub(r"^\[[^\]]+\]\s*|^\([^\)]+\)\s*", "", title)
    return title

def get_default_chapters(directory:str, title:str=None) -> List[dict]:
    """
    Returns a list of default chapter info to use for converting files to an EPUB file.
    Each text file in the given directory is sorted alphabetically, and treated as a chapter in the finished epub.
    Each chapter has a field for the file path ("file"), the chapter title ("title"), and whether to include it in the contents ("include").
    
    :param directory: Directory of files to use for chapters in an EPUB file
    :type directory: str, required
    :param title: Title of the whole ebook used if there is only one chapter, defaults to None
    :type title: str, optional
    :return: List if info for each chapter
    :rtype: List[dict]
    """
    # Find all text files in the given directory
    text_files = mm_file_tools.find_files_of_type(directory, ".txt", include_subdirectories=False)
    text_files = mm_rename_tools.sort_alphanum(text_files)
    # Set default chapter values for each text file
    chapters = []
    for i in range(0, len(text_files)):
        chapter = dict()
        chapter["id"] = f"item{i}"
        chapter["file"] = text_files[i]
        chapter["include"] = True
        chapter["title"] = get_title_from_file(text_files[i])
        chapters.append(chapter)
    # Use a different title, if specified
    if title is not None and len(chapters) == 1:
        chapters[0]["title"] = title
    # Return the default chapters
    return chapters

def create_content_files(chapters:List[dict], output_directory:str) -> List[dict]:
    """
    Creates all the XHTML content files converted from the files provided by the given chapters list.
    Files will be created in a "content" subdirectory in the given output_directory.
    
    :param chapters: Chapter files and info, as returned by get_default_chapters
    :type chapters: List[dict], required
    :param output_directory: Directory in which to create the content files
    :type output_directory: str, required
    :return: List with chapter file info, now with "file" fields pointing to the new XHTML files
    :rtype: List[dict]
    """
    # Create the content folder
    content_dir = abspath(join(output_directory, "content"))
    os.mkdir(content_dir)
    # Convert files to XHTML
    updated_chapters = []
    updated_chapters.extend(chapters)
    for i in range(0, len(updated_chapters)):
        # Get the filename for the XHTML file
        filename = basename(chapters[i]["file"])
        filename = filename[:len(filename) - len(html_string_tools.html.get_extension(filename))]
        xhtml_file = abspath(join(content_dir, f"{filename}.xhtml"))
        # Create the file
        xhtml = txt_to_xhtml(chapters[i]["file"], chapters[i]["title"])
        mm_file_tools.write_text_file(xhtml_file, xhtml)
        updated_chapters[i]["file"] = f"content/{filename}.xhtml"
    return chapters

def copy_original_files(input_directory:str, output_directory:str):
    """
    Copys all original non-converted files to an output directory to be included in the EPUB archive.
    Files will be copied to a directory labeled "original" in the given output directory.
    If an existing "original" directory exists in the given input directory, its contents will be used.
    Otherwise, the full contents of the given input_directory will be copied.
    
    :param input_directory: Directory containing original unconverted files
    :type input_directory: str, required
    :param output_directory: Directory in which to copy files
    :type output_directory: str, required
    """
    # Create the original folder
    original_dir = abspath(join(output_directory, "original"))
    os.mkdir(original_dir)
    # Use user created original files directory, if available
    directory = abspath(join(input_directory, "original"))
    if not exists(directory) or not isdir(directory):
        directory = abspath(join(input_directory, "Original"))
    if not exists(directory) or not isdir(directory):
        directory = abspath(input_directory)
     # Copy all files
    files = os.listdir(directory)
    for file in files:
        full_file = abspath(join(directory, file))
        new_file = abspath(join(original_dir, file))
        if isdir(full_file):
            shutil.copytree(full_file, new_file)
        else:
            shutil.copy(full_file, new_file)

def create_style_file(output_directory:str):
    """
    Creates a CSS style file for the EPUB in a given output directory.
    The file is "epubstyle.css" and created in a "style" subdirectory of the output directory.
    
    :param output_directory: Directory in which to save the style file.
    :type output_directory: str, required
    """
    # Create the style folder
    style_dir = abspath(join(output_directory, "style"))
    os.mkdir(style_dir)
    # Create the style text
    style = ""
    style = f"{style}body{{\n"
    style = f"{style}    margin: 0px 0px 0px 0px;\n"
    style = f"{style}}}"
    # Write style to a CSS file
    style_file = abspath(join(style_dir, "epubstyle.css"))
    mm_file_tools.write_text_file(style_file, style)

def create_nav_file(chapters:List[dict], title:str, output_directory:str):
    """
    Creates the nav.xhtml contents file for the EPUB based on given chapter information
    
    :param chapters: Chapter files and info, as returned by create_content_files.
    :type chapters: List[dict], required
    :param title: Title of the EPUB, for use in the heading and header
    :type title: str, required
    :param output_directory: Directory in which to save the nav.xhtml file
    :type output_directory: str, required
    """
    # Create the base element
    attributes = dict()
    attributes["xmlns"] = "http://www.w3.org/1999/xhtml"
    attributes["xmlns:epub"] = "http://www.idpf.org/2007/ops"
    attributes["lang"] = "en"
    attributes["xml:lang"] = "en"
    base = ElementTree.Element("html")
    base.attrib = attributes
    # Create the head SubElement
    head = ElementTree.SubElement(base, "head")
    title_element = ElementTree.SubElement(head, "title")
    title_element.text = title
    # Create the body and nav elements
    body = ElementTree.SubElement(base, "body")
    nav = ElementTree.SubElement(body, "nav")
    nav.attrib = {"epub:type":"toc", "id":"id", "role":"doc-toc"}
    title_element = ElementTree.SubElement(nav, "h2")
    title_element.text = title
    # Create the list of contents
    ol = ElementTree.SubElement(nav, "ol")
    for chapter in chapters:
        if chapter["include"]:
            li = ElementTree.SubElement(ol, "il")
            a = ElementTree.SubElement(li, "a")
            a.attrib = {"href": chapter["file"]}
            a.text = chapter["title"]
    # Set indents to make the XML more readable
    ElementTree.indent(base, space="    ")
    # Get xml as string
    xml = ElementTree.tostring(base).decode("UTF-8")
    xml = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n{xml}"
    # Write the nav file
    nav_file = abspath(join(output_directory, "nav.xhtml"))
    mm_file_tools.write_text_file(nav_file, xml)

def create_ncx_file(chapters:List[dict], title:str, uid:str, output_directory:str):
    """
    Creates the toc.ncx contents file for the EPUB based on given chapter information
    
    :param chapters: Chapter files and info, as returned by create_content_files.
    :type chapters: List[dict], required
    :param title: Title of the EPUB for use in the document title
    :type title: str, required
    :param uid: Unique identifier for the EPUB for use in the header
    :type uid: str, required
    :param output_directory: Directory in which to save the toc.ncx file
    :type output_directory: str, required
    """
    # Create the base element
    attributes = dict()
    attributes["xmlns"] = "http://www.daisy.org/z3986/2005/ncx/"
    attributes["version"] = "2005-1"
    base = ElementTree.Element("ncx")
    base.attrib = attributes
    # Create the head SubElement
    head = ElementTree.SubElement(base, "head")
    meta = ElementTree.SubElement(head, "meta")
    identifier = uid
    if identifier is None:
        identifier = title
    meta.attrib = {"name":"dtb:uid", "content":identifier}
    meta = ElementTree.SubElement(head, "meta")
    meta.attrib = {"name":"dtb:depth", "content":"1"}
    meta = ElementTree.SubElement(head, "meta")
    meta.attrib = {"name":"dtb:totalPageCount", "content":"0"}
    meta = ElementTree.SubElement(head, "meta")
    meta.attrib = {"name":"dtb:maxPageNumber", "content":"0"}
    # Create the docTitle SubElement
    doc_title = ElementTree.SubElement(base, "docTitle")
    text_element = ElementTree.SubElement(doc_title, "text")
    text_element.text = title
    # Create the list of contents
    nav_map = ElementTree.SubElement(base, "navMap")
    for chapter in chapters:
        if chapter["include"]:
            # Create the navPoint
            nav_point = ElementTree.SubElement(nav_map, "navPoint")
            nav_point.attrib = {"id":chapter["id"]}
            # Create the navLabel
            nav_label = ElementTree.SubElement(nav_point, "navLabel")
            text_element = ElementTree.SubElement(nav_label, "text")
            text_element.text = chapter["title"]
            # Create the nav link
            nav_link = ElementTree.SubElement(nav_point, "content")
            nav_link.attrib = {"src":chapter["file"]}
    # Set indents to make the XML more readable
    ElementTree.indent(base, space="    ")
    # Get xml as string
    xml = ElementTree.tostring(base).decode("UTF-8")
    xml = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n{xml}"
    # Write the ncx file
    nav_file = abspath(join(output_directory, "toc.ncx"))
    mm_file_tools.write_text_file(nav_file, xml)

def get_metadata_xml(metadata:dict) -> str:
    """
    Returns the metadata XML tag for a .opf EPUB contents file based on given metadata.
    
    :param metadata: Metadata dict as returned by meta_reader.py's get_empty_metadata function.
    :type metadata: dict, required
    :return: Metadata in XML format for EPUB
    :rtype: str
    """
    # Create the XML base
    base = ElementTree.Element("metadata")
    meta_attributes = dict()
    meta_attributes["xmlns:dc"] = "http://purl.org/dc/elements/1.1/"
    meta_attributes["xmlns:opf"] = "http://www.idpf.org/2007/opf"
    base.attrib = meta_attributes
    # Set default metadata tags
    language_tag = ElementTree.SubElement(base, "dc:language")
    language_tag.text = "en"
    modified_tag = ElementTree.SubElement(base, "meta")
    modified_tag.attrib = {"property":"dcterms:modified"}
    modified_tag.text = "0000-00-00T00:30:00Z"
    # Set the metadata identifier
    identifier_tag = ElementTree.SubElement(base, "dc:identifier")
    identifier_tag.attrib = {"id":"id"}
    identifier_tag.text = metadata["title"]
    if metadata["url"] is not None:
        identifier_tag.text = metadata["url"]
    # Set the metadata date
    date_tag = ElementTree.SubElement(base, "dc:date")
    date_tag.text = "0000-00-00T00:00:00+00:00"
    if metadata["date"] is not None:
        date_tag.text = metadata["date"] + "T00:00:00+00:00"
    # Set the metadata title
    title_tag = ElementTree.SubElement(base, "dc:title")
    title_tag.text = metadata["title"]
    # Set the metadata description
    if metadata["description"] is not None:
        description_tag = ElementTree.SubElement(base, "dc:description")
        description_tag.text = metadata["description"]
    # Set the metadata writer
    try:
        writers = metadata["writer"].split(",")
    except AttributeError: writers = []
    for i in range(0, len(writers)):
        # Add the creator tag
        creator_id = f"author-{i}"
        creator_tag = ElementTree.SubElement(base, "dc:creator")
        creator_tag.attrib = {"id":creator_id}
        creator_tag.text = writers[i]
        # Add the role tag
        role_tag = ElementTree.SubElement(base, "meta")
        role_tag.attrib = {"refines":creator_id, "property":"role", "scheme":"marc:relators"}
        role_tag.text = "aut"
    # Set the metadata cover artist
    try:
        cover_artists = metadata["cover_artist"].split(",")
    except AttributeError: cover_artists = []
    for i in range(0, len(cover_artists)):
        # Add the creator tag
        creator_id = f"cover-artist-{i}"
        creator_tag = ElementTree.SubElement(base, "dc:creator")
        creator_tag.attrib = {"id":creator_id}
        creator_tag.text = cover_artists[i]
        # Add the role tag
        role_tag = ElementTree.SubElement(base, "meta")
        role_tag.attrib = {"refines":creator_id, "property":"role", "scheme":"marc:relators"}
        role_tag.text = "cov"
    # Set the metadata illustrator
    try:
        illustrators = metadata["artist"].split(",")
    except AttributeError: illustrators = []
    for i in range(0, len(illustrators)):
        # Add the creator tag
        creator_id = f"illustrator-{i}"
        creator_tag = ElementTree.SubElement(base, "dc:creator")
        creator_tag.attrib = {"id":creator_id}
        creator_tag.text = illustrators[i]
        # Add the role tag
        role_tag = ElementTree.SubElement(base, "meta")
        role_tag.attrib = {"refines":creator_id, "property":"role", "scheme":"marc:relators"}
        role_tag.text = "ill"
    # Set the metadata publisher
    if metadata["publisher"] is not None:
        publisher_tag = ElementTree.SubElement(base, "dc:publisher")
        publisher_tag.text = metadata["publisher"]
    # Set the metadata age rating
    if metadata["age_rating"] is not None:
        age_rating_tag = ElementTree.SubElement(base, "meta")
        age_rating_tag.attrib = {"property":"dcterms:audience"}
        age_rating_tag.text = metadata["age_rating"]
    # Set the metadata series
    if metadata["series"] is not None:
        series_title = ElementTree.SubElement(base, "meta")
        series_title.attrib = {"property":"belongs-to-collection", "id":"series-title"}
        series_title.text = metadata["series"]
        collection_type = ElementTree.SubElement(base, "meta")
        collection_type.attrib = {"refines":"series-title", "property":"collection-type"}
        collection_type.text = "series"
        try:
            num = float(metadata["series_number"])
            series_number = ElementTree.SubElement(base, "meta")
            series_number.attrib = {"refines":"series-title", "property":"group-position"}
            series_number.text = metadata["series_number"]
        except (TypeError, ValueError): pass
    # Set the metadata tags
    try:
        tags = metadata["tags"].split(",")
    except AttributeError: tags = []
    for tag in tags:
        tag_tag = ElementTree.SubElement(base, "dc:subject")
        tag_tag.text = tag
    # Set the score
    try:
        score = int(metadata["score"])
        if score > -1 and score < 6:
            score_element = ElementTree.SubElement(base, "meta")
            score_element.attrib = {"property":"calibre:rating"}
            score_element.text = str(float(score * 2))
    except (TypeError, ValueError): pass
    # Set indents to make the XML more readable
    ElementTree.indent(base, space="    ")
    # Return xml as string
    return ElementTree.tostring(base).decode("UTF-8")

def get_manifest_xml(chapters:List[dict]) -> str:
    """
    Creates the manifest section of a content.opf XML file for the EPUB.
    
    :param chapters: Chapter info as returned by create_content_files
    :type chapters: List[dict], required
    :return: XML manifest
    :rtype: str
    """
    # Create the XML base
    base = ElementTree.Element("manifest")
    # Add the XHTML text
    for chapter in chapters:
        attributes = dict()
        attributes["href"] = chapter["file"]
        attributes["id"] = chapter["id"]
        attributes["media-type"] = "application/xhtml+xml"
        chapter_item = ElementTree.SubElement(base, "item")
        chapter_item.attrib = attributes
    # Add the style file
    style_item = ElementTree.SubElement(base, "item")
    style_item.attrib = {"href":"style/epubstyle.css", "id":"epubstyle", "media-type":"text/css"}
    # Add the nav and ncx files
    nav_item = ElementTree.SubElement(base, "item")
    nav_item.attrib = {"href":"nav.xhtml", "id":"nav", "media-type":"application/xhtml+xml", "properties":"nav"}
    ncx_item = ElementTree.SubElement(base, "item")
    ncx_item.attrib = {"href":"toc.ncx", "id":"ncx", "media-type":"application/x-dtbncx+xml"}
    # Set indents to make the XML more readable
    ElementTree.indent(base, space="    ")
    # Return xml as string
    return ElementTree.tostring(base).decode("UTF-8")

def create_content_opf(chapters:List[dict], metadata:dict, output_directory:str):
    """
    Creates the content.opf file for the EPUB containing metadata and spine info.
    
    :param chapters: Chapter info as returned by create_content_files
    :type chapters: List[dict], required
    :param metadata: Metadata dict as returned by meta_reader.py's get_empty_metadata function.
    :type metadata: dict, required
    :param output_directory: Directory in which to write the content.opf file
    :type output_directory: str, required
    """
    # Create the XML base
    base = ElementTree.Element("package")
    package_attributes = dict()
    package_attributes["xmlns"] = "http://www.idpf.org/2007/opf"
    package_attributes["unique-identifier"] = "id"
    package_attributes["version"] = "3.0"
    package_attributes["prefix"] = "http://www.idpf.org/vocab/rendition/#"
    base.attrib = package_attributes
    # Create the metadata tags
    metadata_attributes = dict()
    metadata_attributes["xmlns:dc"] = "http://purl.org/dc/elements/1.1/"
    metadata_attributes["xmlns:opf"] = "http://www.idpf.org/2007/opf"
    metadata_xml = get_metadata_xml(metadata)
    metadata_element = ElementTree.fromstring(metadata_xml)
    metadata_element.attrib = metadata_attributes
    base.append(metadata_element)
    # Create the manifest tags
    manifest_xml = get_manifest_xml(chapters)
    base.append(ElementTree.fromstring(manifest_xml))
    # Create the spine
    spine_element = ElementTree.SubElement(base, "spine")
    spine_element.attrib = {"toc":"ncx"}
    for chapter in chapters:
        itemref = ElementTree.SubElement(spine_element, "itemref")
        itemref.attrib = {"idref":chapter["id"]}
    # Set indents to make the XML more readable
    ElementTree.indent(base, space="    ")
    # Get xml as string
    xml = ElementTree.tostring(base).decode("UTF-8")
    xml = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n{xml}"
    # Write the opf file
    opf_file = abspath(join(output_directory, "content.opf"))
    mm_file_tools.write_text_file(opf_file, xml)

def create_epub(chapters:List[dict], metadata:dict, directory:str) -> str:
    """
    Creates an EPUB file from the files in a directory and a list of given chapters.
    
    :param chapters: Chapter info as returned by create_content_files
    :type chapters: List[dict], required
    :param metadata: Metadata dict as returned by meta_reader.py's get_empty_metadata function.
    :type metadata: dict, required
    :param directory: Directory to get file info from and to save finished EPUB into
    :type directory: str, required
    :return: The path of the created EPUB file
    :rtype: str
    """
    # Create temporary directories for building the epub
    build_directory = mm_file_tools.get_temp_dir("dvk_meta_epub_builder")
    meta_directory = abspath(join(build_directory, "META-INF"))
    epub_directory = abspath(join(build_directory, "EPUB"))
    os.mkdir(meta_directory)
    os.mkdir(epub_directory)
    # Create the meta container xml
    base = ElementTree.Element("container")
    base.attrib = {"xmlns":"urn:oasis:names:tc:opendocument:xmlns:container", "version":"1.0"}
    rootfiles = ElementTree.SubElement(base, "rootfiles")
    rootfile = ElementTree.SubElement(rootfiles, "rootfile")
    rootfile.attrib = {"media-type":"application/oebps-package+xml", "full-path":"EPUB/content.opf"}
    ElementTree.indent(base, space="    ")
    xml = ElementTree.tostring(base).decode("UTF-8")
    xml = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n{xml}"
    container_file = abspath(join(meta_directory, "container.xml"))
    mm_file_tools.write_text_file(container_file, xml)
    # Create the style file
    create_style_file(epub_directory)
    # Copy the original to the EPUB directory
    copy_original_files(directory, epub_directory)
    # Create the content files
    updated_chapters = create_content_files(chapters, epub_directory)
    # Create nav and ncx files
    create_nav_file(updated_chapters, metadata["title"], epub_directory)
    create_ncx_file(updated_chapters, metadata["title"], metadata["url"], epub_directory)
    # Create the content.opf file
    create_content_opf(updated_chapters, metadata, epub_directory)
    # Get the epub file path
    filename = mm_rename_tools.get_available_filename("a.epub", metadata["title"], directory)
    epub_file = abspath(join(directory, filename))
    # Create the epub file
    assert mm_file_tools.create_zip(build_directory, epub_file, 8, "application/epub+zip")
    return epub_file
