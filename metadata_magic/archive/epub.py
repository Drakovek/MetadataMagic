import os
import re
import math
import shutil
import html_string_tools
import python_print_tools.printer
import metadata_magic.sort as mm_sort
import metadata_magic.rename as mm_rename
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.comic_xml as mm_comic_xml
import metadata_magic.archive.xhtml_formatting as mm_xhtml
import metadata_magic.meta_reader as mm_meta_reader
from xml.etree import ElementTree
from os.path import abspath, basename, exists, isdir, join
from typing import List

def get_default_chapters(directory:str, title:str=None) -> List[dict]:
    """
    Returns a list of default chapter info to use for converting files to an EPUB file.
    Each text file in the given directory is sorted alphabetically, and treated as a chapter in the finished epub.
    Each chapter has a field for the file path ("file"), the chapter title ("title"), and whether to include it in the contents ("include").
    
    :param directory: Directory of files to use for chapters in an EPUB file
    :type directory: str, required
    :param title: Title of the whole ebook used if there is only one chapter, defaults to None
    :type title: str, optional
    :return: List of info for each chapter
    :rtype: List[dict]
    """
    # Find all media files in the given directory
    file_types = [".txt", ".html", ".htm", ".png", ".jpeg", ".jpg", ".bmp", ".tiff"]
    media_files = mm_file_tools.find_files_of_type(directory, file_types, include_subdirectories=False)
    media_files = mm_sort.sort_alphanum(media_files)
    # Set default chapter values for each text file
    chapters = []
    for i in range(0, len(media_files)):
        # Set the info for the full chapter
        chapter = dict()
        chapter["include"] = True
        chapter["title"] = mm_xhtml.get_title_from_file(media_files[i])
        # Set the info for the individual files
        file_info = dict()
        file_info["id"] = f"item{i}"
        file_info["file"] = media_files[i]
        chapter["files"] = [file_info]
        # Add to the chapter list
        chapters.append(chapter)
    # Use a different title, if specified
    if title is not None and len(chapters) == 1:
        chapters[0]["title"] = title
    # Return the default chapters
    return chapters

def add_cover_to_chapters(chapters:List[dict], metadata:dict) -> List[dict]:
    """
    Adds information for a cover image to a list of chapter information.
    
    :param chapters: List of chapters as returned by get_default_chapters
    :type chapters: List[dict], required
    :param metadata: Metadata dict as returned by meta_reader.py's get_empty_metadata function.
    :type metadata: dict, required
    :return: List of chapter information with cover image added to the beginning
    :rtype: List[dict]
    """
    # Create new chapters list
    new_chapters = []
    new_chapters.extend(chapters)
    # Create a cover image
    cover_directory = mm_file_tools.get_temp_dir("dvk_cover_gen")
    cover_file = abspath(join(cover_directory, "mm_cover_image.jpg"))
    cover_image = mm_archive.get_cover_image(metadata["title"], metadata["writers"], uppercase=True)
    cover_image = cover_image.convert("RGB")
    cover_image.save(cover_file, quality=95)
    # Create a cover image chapter entry
    entry = dict()
    entry["include"] = True
    entry["title"] = "Cover"
    entry["files"] = [{"id":"cover", "file":cover_file}]
    # Add the entry to the chapters
    new_chapters.insert(0, entry)
    # Return the new chapters
    return new_chapters

def group_chapters(chapters:List[dict], group:List[int]) -> List[dict]:
    """
    Groups the files of the given chapters into one new chapter.

    :param chapters: List of chapters as returned by get_default_chapters
    :type chapters: List[dict], required
    :param group: List of indexes of the entries to group together
    :type group: List[int], required
    :return: New list of chapters with the given entries grouped
    :rtype: List[dict]
    """
    # Remove out of range items in the group list
    sorted_group = list(set(group))
    sorted_group = sorted(sorted_group)
    for i in range(len(sorted_group)-1,-1,-1):
        if sorted_group[i] < 0 or sorted_group[i] > (len(chapters)-1):
            del sorted_group[i]
    # Get the title and include key
    try:
        title = chapters[sorted_group[0]]["title"]
        grouped_entry = {"title":title, "include":True}
    except IndexError: return chapters
    # Get a list of all the files
    files = []
    updated_chapters = []
    updated_chapters.extend(chapters)
    for i in range(len(sorted_group)-1, -1, -1):
        files.extend(chapters[sorted_group[i]]["files"])
        del updated_chapters[sorted_group[i]]
    # Add the grouped entry
    grouped_entry["files"] = mm_sort.sort_dictionaries_alphanum(files, "file")
    updated_chapters.append(grouped_entry)
    updated_chapters = mm_sort.sort_dictionaries_alphanum(updated_chapters, ["files",0,"file"])
    # Return the updated chapters
    return updated_chapters

def separate_chapters(chapters:List[dict], chapter_num:str) -> List[dict]:
    """
    Separates the files of a given grouped chapter into separate chapters.

    :param chapters: List of chapters as returned by get_default_chapters
    :type chapters: List[dict], required
    :param chapter_num: The chapter with files to separate into different chapters
    :type chapter_num: int, required 
    :return: New list of chapters with the given entry separated into multiple chapters
    :rtype: List[dict]
    """
    # Return the existing chapters if separating is unneccessary
    try:
        if chapter_num < 0 or len(chapters[chapter_num]["files"]) == 1:
            return chapters
    except IndexError: return chapters
    # Get the new chapters
    new_chapters = []
    new_chapters.extend(chapters)
    for file in chapters[chapter_num]["files"]:
        new_chapter = {"include":True, "title":mm_xhtml.get_title_from_file(file["file"])}
        new_chapter["files"] = [{"id":file["id"], "file":file["file"]}]
        new_chapters.append(new_chapter)
    # Delete the old grouped chapter
    del new_chapters[chapter_num]
    # Sort the list of chapters
    new_chapters = mm_sort.sort_dictionaries_alphanum(new_chapters, ["files",0,"file"])
    # Return the new chapters
    return new_chapters

def get_chapters_string(chapters:List[dict]) -> str:
    """
    Returns a human-readable string block representing the given list of chapters.
    
    :param chapters: Chapter files and info, as returned by get_default_chapters
    :type chapters: List[dict], required
    :return: Human-readable string representation of the given chapter data
    :rtype: str
    """
    # Get the length of the block of characters for each field
    files_length = 5
    title_length = 5
    entry_length = 10
    basenames = []
    for chapter in chapters:
        # Get the length of the file list
        filename = ""
        for file in chapter["files"]:
            filename = filename + basename(file["file"]) + ", "
        filename = re.sub(r",\s*$", "", filename)
        basenames.append(filename)
        # Set the length of the block
        if len(filename) > files_length:
            files_length = len(filename)
        if len(chapter["title"]) > title_length:
            title_length = len(chapter["title"])
    title_length += 4
    # Set the chapters string header
    total_length = entry_length + title_length + files_length
    chapters_string = "-" * total_length
    chapters_string = f"{{:<{files_length}}}\n{chapters_string}".format("FILES")
    chapters_string = f"{{:<{title_length}}}{chapters_string}".format("TITLE")
    chapters_string = f"{{:<{entry_length}}}{chapters_string}".format("ENTRY")
    # Get a string for each chapter entry
    for i in range(0, len(chapters)):
        # Get the entry value
        entry_string = str(i+1).zfill(3)
        if not chapters[i]["include"]:
            entry_string = f"{entry_string}*"
        chapter_string = f"{{:<{entry_length}}}".format(entry_string)
        # Get the title value
        chapter_string = f"{chapter_string}{{:<{title_length}}}".format(chapters[i]["title"])
        # Get the file value
        chapter_string = f"{chapter_string}{{:<{files_length}}}".format(basenames[i])
        # Add to the overall chapters string
        chapters_string = f"{chapters_string}\n{chapter_string}"
    # Return the chapters string
    return chapters_string

def get_chapters_from_user(directory:str, metadata:dict) -> List[dict]:
    """
    Returns a list of chapter information for use when converting files into an EPUB file.
    Initial chapter info is gatherd from the get_default_chapters function, then the user is prompted to modify fields.
    The user can choose to modify chapter titles and whether to include the chapter in the table of contents.
    
    :param directory: Directory of files to use for chapters in an EPUB file
    :type directory: str, required
    :param metadata: Metadata dict as returned by meta_reader.py's get_empty_metadata function.
    :type metadata: dict, required
    :return: List of info for each chapter
    :rtype: List[dict]
    """
    chapters = get_default_chapters(directory, metadata["title"])
    while True:
        # Clear the console
        python_print_tools.printer.clear_console()
        # Print the chapters
        print(get_chapters_string(chapters))
        # Print extra instructions
        print("\n* - Not Included in Table of Contents\n")
        print("OPTIONS:")
        print("T - Edit Chapter Title")
        print("C - Toggle Inclusion in Contents")
        print("G - Group Files")
        print("S - Separate Files")
        print("W - Commit Changes\n")
        # Get the user response
        response = input("Command: ").lower()
        if response == "w":
            break
        # Edit the title
        if response == "t":
            try:
                entry_num = int(input("Entry Number: ")) -1
                chapters[entry_num]["title"] = input("Title: ")
            except (IndexError, ValueError): pass
        # Toggle the include flag
        if response == "c":
            try:
                entry_num = int(input("Entry Number: ")) -1
                chapters[entry_num]["include"] = not chapters[entry_num]["include"]
            except (IndexError, ValueError): pass
        # Separate files
        if response == "s":
            try:
                entry_num = int(input("Entry Number: ")) -1
                chapters = separate_chapters(chapters, entry_num)
            except ValueError: pass
        # Group files
        if response == "g":
            try:
                response = input("Entry Numbers (Separate with \",\"): ")
                entry_nums = re.sub(r"\s*,\s*", ",", response).split(",")
                for i in range(0, len(entry_nums)):
                    entry_nums[i] = int(entry_nums[i])-1
                chapters = group_chapters(chapters, entry_nums)
            except ValueError:pass
    # Ask whether to add a cover image
    if input("Generate Cover Image? (Y/[N]): ").lower() == "y":
        chapters = add_cover_to_chapters(chapters, metadata)
    # Return the chapters
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
    # Create the content and images folders
    content_dir = abspath(join(output_directory, "content"))
    image_dir = abspath(join(output_directory, "images"))
    os.mkdir(content_dir)
    os.mkdir(image_dir)
    # Convert files to XHTML
    updated_chapters = []
    updated_chapters.extend(chapters)
    image_num = 1
    for i in range(0, len(updated_chapters)):
        # Get the filename for the XHTML file
        title = chapters[i]["title"]
        filename = basename(chapters[i]["files"][0]["file"])
        filename = filename[:len(filename) - len(html_string_tools.html.get_extension(filename))]
        xhtml_file = abspath(join(content_dir, f"{filename}.xhtml"))
        # Convert all the files for the chapter into XML
        chapter_xml = ""
        for file in chapters[i]["files"]:
            # Get the file extension
            extension = html_string_tools.html.get_extension(file["file"])
            # Convert based on the appropriate format
            if extension == ".txt":
                xml = mm_xhtml.txt_to_xhtml(file["file"])
            elif extension == ".html" or extension == ".htm":
                xml = mm_xhtml.html_to_xhtml(file["file"])
            else:
                # Copy image to the image folder with new name
                extension = html_string_tools.html.get_extension(file["file"])
                new_image = abspath(join(image_dir, f"image{image_num}{extension}"))
                shutil.copy(file["file"], new_image)
                image_num += 1
                # Get the image xml file
                image_alt = title
                if len(chapters[i]["files"]) > 1:
                    image_alt = mm_xhtml.get_title_from_file(file["file"])
                xml = mm_xhtml.image_to_xhtml(new_image, image_alt)
            # Append to the chapter xml
            chapter_xml = f"{chapter_xml}{xml}"
        # Write with proper XHTML formatting
        mm_file_tools.write_text_file(xhtml_file, mm_xhtml.format_xhtml(chapter_xml, title))
        # Update info for the chapter
        updated_chapters[i]["id"] = updated_chapters[i]["files"][0]["id"]
        updated_chapters[i]["file"] = f"content/{filename}.xhtml"
        updated_chapters[i].pop("files")
    return updated_chapters

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
    style = f"{style}img {{"
    style = f"{style}\n    display: block;"
    style = f"{style}\n    max-width: 100%;"
    style = f"{style}\n    max-height: 100%;"
    style = f"{style}\n    text-align: center;"
    style = f"{style}\n    margin-left: auto;"
    style = f"{style}\n    margin-right: auto;"
    style = f"{style}\n}}\n\n"
    style = f"{style}#full-image-container {{"
    style = f"{style}\n    width: 100%;"
    style = f"{style}\n    height: 100%;"
    style = f"{style}\n    margin: 0;"
    style = f"{style}\n    padding: 0;"
    style = f"{style}\n    page-break-after: always;"
    style = f"{style}\n}}\n\n"
    style = f"{style}center {{"
    style = f"{style}\n    text-align: center;"
    style = f"{style}\n}}"
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

def get_metadata_xml(metadata:dict, cover_id:str=None) -> str:
    """
    Returns the metadata XML tag for a .opf EPUB contents file based on given metadata.
    
    :param metadata: Metadata dict as returned by meta_reader.py's get_empty_metadata function.
    :type metadata: dict, required
    :param cover_id: ID for a cover image, defaults to None
    :type cover_id: str, optional
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
    # Create the metadata identifier
    identifier_tag = ElementTree.SubElement(base, "dc:identifier")
    identifier_tag.attrib = {"id":"id"}
    # Set the metadata date
    date_tag = ElementTree.SubElement(base, "dc:date")
    date_tag.text = "0000-00-00T00:00:00+00:00"
    if metadata["date"] is not None:
        date_tag.text = metadata["date"] + "T00:00:00+00:00"
    # Set the metadata title
    title_tag = ElementTree.SubElement(base, "dc:title")
    title_tag.text = metadata["title"]
    identifier_tag.text = metadata["title"]
    # Set the metadata source url
    if metadata["url"] is not None:
        url_tag = ElementTree.SubElement(base, "dc:source")
        url_tag.text = metadata["url"]
        identifier_tag.text = metadata["url"]
    # Set the metadata description
    if metadata["description"] is not None:
        description_tag = ElementTree.SubElement(base, "dc:description")
        description_tag.text = metadata["description"]
    # Set the metadata writer
    try:
        writers = metadata["writers"].split(",")
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
        cover_artists = metadata["cover_artists"].split(",")
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
        illustrators = metadata["artists"].split(",")
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
    # Set the cover image, if applicable
    if cover_id is not None:
        cover_tag = ElementTree.SubElement(base, "meta")
        cover_tag.attrib = {"name":"cover", "content":cover_id}
    # Set indents to make the XML more readable
    ElementTree.indent(base, space="    ")
    # Return xml as string
    return ElementTree.tostring(base).decode("UTF-8")

def get_manifest_xml(chapters:List[dict], output_directory:str) -> str:
    """
    Creates the manifest section of a content.opf XML file for the EPUB.
    
    :param chapters: Chapter info as returned by create_content_files
    :type chapters: List[dict], required
    :param output_directory: Directory in which to the content.opf file is being constructed
    :type output_directory: str, required
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
    # Add the images
    image_directory = abspath(join(output_directory, "images"))
    images = mm_sort.sort_alphanum(os.listdir(image_directory))
    for i in range(0, len(images)):
        attributes = dict()
        attributes["href"] = f"images/{images[i]}"
        attributes["id"] = re.sub(r"\..+$", "", basename(images[i]))
        # Set the mimetype
        extension = html_string_tools.html.get_extension(images[i])
        mimetype = "application/xhtml+xml"
        if extension == ".png":
            mimetype = "image/png"
        elif extension == ".jpg" or ".jpeg":
            mimetype = "image/jpeg"
        elif extension == ".bmp":
            mimetype = "image/bmp"
        elif extension == ".tiff":
            mimetype = "image/tiff"
        attributes["media-type"] = mimetype
        # Add the item to the manifest
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
    # Check images directory for cover image
    try:
        image_directory = abspath(join(output_directory, "images"))
        image = mm_sort.sort_alphanum(os.listdir(image_directory))[0]
        cover_id = re.sub(r"\..+$", "", basename(image))
    except IndexError:
        cover_id = None
    # Create the metadata tags
    metadata_attributes = dict()
    metadata_attributes["xmlns:dc"] = "http://purl.org/dc/elements/1.1/"
    metadata_attributes["xmlns:opf"] = "http://www.idpf.org/2007/opf"
    metadata_xml = get_metadata_xml(metadata, cover_id)
    metadata_element = ElementTree.fromstring(metadata_xml)
    metadata_element.attrib = metadata_attributes
    base.append(metadata_element)
    # Create the manifest tags
    manifest_xml = get_manifest_xml(chapters, output_directory)
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
    filename = mm_rename.get_available_filename(["a.epub"], metadata["title"], directory)
    epub_file = abspath(join(directory, f"{filename}.epub"))
    # Create the epub file
    assert mm_file_tools.create_zip(build_directory, epub_file, 8, "application/epub+zip")
    return epub_file

def create_epub_from_description(json_file:str, image_file:str, metadata:dict, directory:str) -> str:
    """
    Creates an EPUB file from a image+json pair with the json metadata description used as the text.
    Image file is used as the cover image.
    
    :param json_file: JSON file used to get the description and use as EPUB text
    :type json_file: str, required
    :param image_file: Image file to use as the EPUB cover image
    :type image_file: str, required
    :param metadata: Metadata dict as returned by meta_reader.py's get_empty_metadata function.
    :type metadata: dict, required
    :param directory: Directory to get file info from and to save finished EPUB into
    :type directory: str, required
    :return: The path of the created EPUB file
    :rtype: str
    """
    # Create a temporary directory for the generated epub contents
    temp_directory = mm_file_tools.get_temp_dir("dvk_meta_description")
    # Copy Files into the original directory
    json_name = basename(json_file)
    image_name = basename(image_file)
    original_directory = abspath(join(temp_directory, "original"))
    os.mkdir(original_directory)
    shutil.copy(json_file, abspath(join(original_directory, json_name)))
    shutil.copy(image_file, abspath(join(original_directory, image_name)))
    # Copy the cover image
    extension = html_string_tools.html.get_extension(image_name)
    cover_image = abspath(join(temp_directory, f"dvk-cover{extension}"))
    shutil.copy(image_file, cover_image)
    # Create the html from the json description
    html = mm_meta_reader.load_metadata(json_file, image_file)["description"]
    html_file = abspath(join(temp_directory, json_name[:len(json_name) - 5] + ".html"))
    mm_file_tools.write_text_file(html_file, html)
    # Create the chapters list
    chapters = [{"include":True, "title":"Cover", "files":[{"id":"item_cover", "file":cover_image}]},
            {"include":True, "title":metadata["title"], "files":[{"id":"item_text", "file":html_file}]}]
    # Create the epub file
    generated_epub = create_epub(chapters, metadata, temp_directory)
    # Get the final epub file path
    filename = mm_rename.get_available_filename(["a.epub"], metadata["title"], directory)
    epub_file = abspath(join(directory, f"{filename}.epub"))
    # Copy the epub file to the appropriate directory
    shutil.copy(generated_epub, epub_file)
    return epub_file

def get_info_from_epub(epub_file:str) -> dict:
    """
    Extracts content.opf from a given .epub file and returns the metadata as a dict.
    
    :param epub_file: Path to a .epub file
    :type epub_file: str, required
    :return: Dictionary containing metadata from the .epub file
    :rtype: dict
    """
    # Create temporary directory
    file = abspath(epub_file)
    extract_dir = mm_file_tools.get_temp_dir("dvk_meta_extract")
    assert exists(extract_dir)
    # Extract content.opf from given file
    xml_file = mm_file_tools.extract_file_from_zip(epub_file, extract_dir, "content.opf", True)
    if xml_file is None or not exists(xml_file):
        return mm_archive.get_empty_metadata()
    if xml_file is None or not exists(xml_file):
        return mm_archive.get_empty_metadata()
    # Read XML file
    try:
        # Get main namespace
        tree = ElementTree.parse(xml_file)
        base = tree.getroot()
        ns = {"0": re.findall("(?<=^{)[^}]+(?=}[^{}]+$)", str(base.tag))[0]}
        ElementTree.register_namespace("0", ns["0"])    
        meta_xml = base.find("0:metadata", ns)
    except (IndexError, ElementTree.ParseError): return mm_archive.get_empty_metadata()
    # Get DC namespace
    ns["dc"] = ""
    for tag in base.iter():
        try:
            ns["dc"] = re.findall(r"(?<=^{)[^}]*\/dc\/[^}]*(?=}[^{}]+$)", str(tag.tag))[0]
            break
        except IndexError:pass
    metadata = mm_archive.get_empty_metadata()
    # Extract title from the XML
    metadata["title"] = meta_xml.findtext("dc:title", namespaces=ns)
    # Extract date from the XML
    metadata["date"] = meta_xml.findtext("dc:date", namespaces=ns)[:10]
    if metadata["date"] == "0000-00-00":
        metadata["date"] = None
    # Extract the description from the XML
    metadata["description"] = meta_xml.findtext("dc:description", namespaces=ns)
    # Extract the publisher from the XML
    metadata["publisher"] = meta_xml.findtext("dc:publisher", namespaces=ns)
    # Get the URL from the xml
    metadata["url"] = meta_xml.findtext("dc:source", namespaces=ns)
    # Extract the score from the xml
    try:
        score = float(meta_xml.find(f".//{{{ns['0']}}}meta[@property='calibre:rating']").text)
        score = int(math.floor(score/2))
        metadata["score"] = str(score)
    except (AttributeError, ValueError): metadata["score"] = None
    # Get all writers and artists
    writers = []
    artists = []
    cover_artists = []
    meta_tags = meta_xml.findall("0:meta", namespaces=ns)
    for creator in meta_xml.findall("dc:creator", namespaces=ns):
        for meta_tag in meta_tags:
            try:
                if meta_tag.attrib["refines"] == creator.attrib["id"]:
                    if meta_tag.text == "aut":
                        writers.append(creator.text)
                    elif meta_tag.text == "ill":
                        artists.append(creator.text)
                    elif meta_tag.text == "cov":
                        cover_artists.append(creator.text)
                    break
            except KeyError: pass
    # Set creator metadata
    if len(writers) > 0:
        metadata["writers"] = ",".join(writers)
    if len(artists) > 0:
        metadata["artists"] = ",".join(artists)
    if len(cover_artists) > 0:
        metadata["cover_artists"] = ",".join(cover_artists)
    # Get the age rating
    try:
        metadata["age_rating"] = meta_xml.find(f".//{{{ns['0']}}}meta[@property='dcterms:audience']").text
    except AttributeError: metadata["age_rating"] = None
    # Get series name and position
    try:
        metadata["series"] = meta_xml.find(f".//{{{ns['0']}}}meta[@property='belongs-to-collection'][@id='series-title']").text
        metadata["series_number"] = meta_xml.find(f".//{{{ns['0']}}}meta[@property='group-position'][@refines='series-title']").text
    except AttributeError:
        metadata["series"] = None
        metadata["series_number"] = None
    # Get the cover ID
    try:
        metadata["cover_id"] = meta_xml.find(f".//{{{ns['0']}}}meta[@name='cover']").attrib["content"]
    except AttributeError: metadata["cover_id"] = None
    # Extract tags from the XML
    tags = []
    tag_elements = meta_xml.findall("dc:subject", namespaces=ns)
    for tag_element in tag_elements:
        tags.append(tag_element.text)
    if len(tags) > 0:
        metadata["tags"] = ",".join(tags)
    # Return the extracted metadata
    return metadata

def update_epub_info(epub_file:str, metadata:dict, update_cover:bool=False):
    """
    Replaces the content.opf file in a given .epub file to reflect the given metadata.
    
    :param epub_file: Path of the .epub file to update
    :type epub_file: str, required
    :param update_cover: Whether to regenerate the cover image for the epub, defaults to False
    :type update_cover: bool, optional
    :param metadata: Metadata to use for the new content.opf file
    :type metadata: dict
    """
    # Extract epub into temp file
    full_epub_file = abspath(epub_file)
    temp_dir = mm_file_tools.get_temp_dir("dvk_epub_info")
    mm_file_tools.extract_zip(full_epub_file, temp_dir)
    try:
        # Get the opf content file
        opf_file = mm_file_tools.find_files_of_type(temp_dir, ".opf")[0]
        opf_text = mm_file_tools.read_text_file(opf_file)
        # Get the tab value
        tab = re.findall(".+(?=<metadata)", opf_text)[0]
        # Replace the metadata XML
        metadata_xml = get_metadata_xml(metadata, metadata["cover_id"])
        opf_text = re.sub(r"\s*<metadata[\S\s]+<\/metadata>\s*", metadata_xml, opf_text)
        # Create element from the read xml
        base = ElementTree.fromstring(opf_text)
        ns = {"0": re.findall("(?<=^{)[^}]+(?=}[^{}]+$)", str(base.tag))[0]}
        ElementTree.register_namespace("", ns["0"])
        ElementTree.indent(base, space="    ")
        # Write the opf
        xml = ElementTree.tostring(base).decode("UTF-8")
        xml = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n{xml}"
        mm_file_tools.write_text_file(opf_file, xml)
        # Remove the mimetype
        mimetype = abspath(join(temp_dir, "mimetype"))
        if exists(mimetype):
            os.remove(mimetype)
        # Update the cover, if applicable
        epub_dir = abspath(join(temp_dir, "EPUB"))
        image_dir = abspath(join(epub_dir, "images"))
        cover_file = abspath(join(image_dir, "image1.jpg"))
        content_dir = abspath(join(epub_dir, "content"))
        cover_xml = abspath(join(content_dir, "mm_cover_image.xhtml"))
        if update_cover and exists(cover_xml) and exists(cover_file):
            # Delete the existing cover image
            os.remove(cover_file)
            # Create a cover image
            cover_image = mm_archive.get_cover_image(metadata["title"], metadata["writers"], uppercase=True)
            cover_image = cover_image.convert("RGB")
            cover_image.save(cover_file, quality=95)
        # Repack the epub file
        new_epub_file = abspath(join(temp_dir, "AAAA.epub"))
        assert mm_file_tools.create_zip(temp_dir, new_epub_file, 8, "application/epub+zip")
        # Replace the old epub file
        os.remove(full_epub_file)
        shutil.copy(new_epub_file, full_epub_file)
        os.remove(new_epub_file)
    except IndexError: pass
