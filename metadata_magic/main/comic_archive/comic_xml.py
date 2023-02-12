#!/usr/bin/env python3

from html_string_tools.main.html_string_tools import get_extension
from html_string_tools.main.html_string_tools import remove_whitespace
from html_string_tools.main.html_string_tools import replace_entities
from re import findall
from re import sub as resub
from os import listdir
from os.path import abspath, exists, isdir, join
from metadata_magic.main.meta_reader import load_metadata
from metadata_magic.main.rename.sort_rename import sort_alphanum
from xml.etree.ElementTree import Element, SubElement
from xml.etree.ElementTree import indent as xml_indent
from xml.etree.ElementTree import parse as xml_parse
from xml.etree.ElementTree import ParseError
from xml.etree.ElementTree import tostring as xml_to_string

def get_empty_metadata() -> dict:
    """
    Returns a dictionary with keys for multiple metadata fields, populated as None.
    """
    meta_dict = dict()
    meta_dict["title"] = None
    meta_dict["series"] = None
    meta_dict["series_number"] = None
    meta_dict["series_total"] = None
    meta_dict["description"] = None
    meta_dict["date"] = None
    meta_dict["writer"] = None
    meta_dict["artist"] = None
    meta_dict["cover_artist"] = None
    meta_dict["publisher"] = None
    meta_dict["tags"] = None
    meta_dict["url"] = None
    return meta_dict

def get_comic_xml(metadata:dict, indent:bool=True) -> str:
    """
    Creates a ComicRack style ComicInfo XML string based on given metadata.
    
    :param metadata: Dict containing metadata to use in the XML
    :type metadata: dict, required
    :param indent: Whether to include indents and new lines to make XML look nicer, defaults to True
    :type indent: bool, optional
    :return: String with ComicRack style XML metadata
    :rtype: str
    """
    # Set the base element for a ComicInfo xml
    schemas = {"xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance"}
    schemas["xmlns:xsd"] = "http://www.w3.org/2001/XMLSchema"
    base = Element("ComicInfo")
    base.attrib = schemas
    # Set the title if applicable
    if metadata["title"] is not None:
        title = SubElement(base, "Title")
        title.text = metadata["title"]
    # Set the series title if applicable
    if metadata["series"] is not None:
        series = SubElement(base, "Series")
        series.text = metadata["series"]
    # Sets the series number if applicable
    if metadata["series_number"] is not None:
        number = SubElement(base, "Number")
        number.text = str(float(metadata["series_number"]))
    # Sets the series total if applicable
    if metadata["series_total"] is not None:
        total = SubElement(base, "Count")
        total.text = str(metadata["series_total"])
    # Set description if applicable
    if metadata["description"] is not None:
        summary = SubElement(base, "Summary")
        summary.text = metadata["description"]
    # Set the date if applicable
    if metadata["date"] is not None:
        # Set year
        year = SubElement(base, "Year")
        year.text = metadata["date"][0:4]
        # Set month
        month = SubElement(base, "Month")
        month.text = str(int(metadata["date"][5:7]))
        # Set day
        day = SubElement(base, "Day")
        day.text = str(int(metadata["date"][8:10]))
    # Set the writer if applicable
    if metadata["writer"] is not None:
        writer = SubElement(base, "Writer")
        writer.text = metadata["writer"]
    # Set all other artist categories if applicable
    if metadata["artist"] is not None:
        penciller = SubElement(base, "Penciller")
        inker = SubElement(base, "Inker")
        colorist = SubElement(base, "Colorist")
        penciller.text = metadata["artist"]
        inker.text = metadata["artist"]
        colorist.text = metadata["artist"]
    # Set the cover artist if applicable
    if metadata["cover_artist"] is not None:
        cover = SubElement(base, "CoverArtist")
        cover.text = metadata["cover_artist"]
    # Set publisher if applicable
    if metadata["publisher"] is not None:
        publisher = SubElement(base, "Publisher")
        publisher.text = metadata["publisher"]
    # Set tags if applicable
    if metadata["tags"] is not None:
        url = SubElement(base, "Tags")
        url.text = metadata["tags"]
    # Set URL if applicable
    if metadata["url"] is not None:
        url = SubElement(base, "Web")
        url.text = metadata["url"]
    # Set indents to make the XML more readable
    if indent:
        xml_indent(base, space="  ")
    # Get xml as string
    xml = xml_to_string(base).decode("UTF-8")
    # Return XML
    return f"<?xml version=\"1.0\"?>\n{xml}"

def read_comic_info(xml_file:str) -> dict:
    """
    Reads metaata from a ComicInfo.xml file and stores it in dictionary like get_comic_xml.
    
    :param xml_file: Path of the XML file to read from
    :type xml_file: str, required
    :return: Dictionary containing ComicInfo metadata
    :rtype: dict
    """
    # Set up xml
    file = abspath(xml_file)
    metadata = get_empty_metadata()
    try:
        tree = xml_parse(file)
        base = tree.getroot()
    except ParseError: return metadata
    # Get metadata from XML
    metadata["title"] = base.findtext("Title")
    metadata["series"] = base.findtext("Series")
    metadata["series_number"] = base.findtext("Number")
    metadata["series_total"] = base.findtext("Count")
    metadata["description"] = base.findtext("Summary")
    metadata["writer"] = base.findtext("Writer")
    metadata["cover_artist"] = base.findtext("CoverArtist")
    metadata["publisher"] = base.findtext("Publisher")
    metadata["url"] = base.findtext("Web")
    metadata["tags"] = base.findtext("Tags")
    # Get the main artist from XML
    metadata["artist"] = base.findtext("Penciller")
    if metadata["artist"] is None:
        metadata["artist"] = base.findtext("Colorist")
    if metadata["artist"] is None:
        metadata["artist"] = base.findtext("Inker")
    # Get date from XML
    year = base.findtext("Year")
    month = base.findtext("Month")
    day = base.findtext("Day")
    if year is not None and month is not None and day is not None:
        while len(month) < 2:
            month = f"0{month}"
        while len(day) < 2:
            day = f"0{day}"
        metadata["date"] = f"{year}-{month}-{day}"
    # Return the gathered metadata
    return metadata

def generate_info_from_jsons(path:str) -> dict:
    """
    Extracts the data to be put into a ComicInfo file from a JSON file in a given directory.
    Extracts data from the first JSON file found in directory when alphanumerically sorted.
    Searches sub-directories as well.
    
    :param path: Directory in which to search for JSON files
    :type path: str, required
    :return: Dictionary containing the metadata info
    :rtype: dict
    """
    # Get list of all files in a directory
    full_directory = abspath(path)
    files = listdir(full_directory)
    for i in range(0, len(files)):
        files[i] = abspath(join(full_directory, files[i]))
    for file in files:
        if isdir(file):
            sub_files = listdir(file)
            for i in range(0, len(sub_files)):
                files.append(abspath(join(file, sub_files[i])))
    # Get the first JSON in a directory
    json_file = None
    files = sort_alphanum(files)
    for file in files:
        if get_extension(file) == ".json":
            json_file = file
            break
    # Get metadata from JSON
    metadata = get_empty_metadata()
    try:
        json_meta = load_metadata(json_file)
    except TypeError: return metadata
    metadata["title"] = json_meta["title"]
    metadata["date"] = json_meta["date"]
    metadata["writer"] = json_meta["writer"]
    metadata["artist"] = json_meta["artist"]
    metadata["cover_artist"] = json_meta["artist"]
    metadata["publisher"] = json_meta["publisher"]
    metadata["url"] = json_meta["url"]
    # Get description metadata
    description = json_meta["description"]
    if description is not None:
        description = replace_entities(description)
        description = resub("<a [^<>]*>|<\\/a[^<>]*>|<b>|<i>|</b>|</i>", "", description)
        description = resub("<[^<>]*>", " ", description)
        description = resub("\\s+", " ", description)
        description = remove_whitespace(description)
    metadata["description"] = description
    # Get tag metadata
    tags = json_meta["tags"]
    if tags is not None and tags is not []:
        tag_string = tags[0]
        for i in range(1, len(tags)):
            tag_string = f"{tag_string},{tags[i]}"
        metadata["tags"] = tag_string
    # Return metadata
    return metadata
