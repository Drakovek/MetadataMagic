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
    meta_dict["age_rating"] = None
    meta_dict["score"] = None
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
    try:
        # Sets the series number if applicable
        series_number = str(float(metadata["series_number"]))
        number = SubElement(base, "Number")
        number.text = series_number
        # Sets the series total if applicable
        total_number = str(int(metadata["series_total"]))
        total = SubElement(base, "Count")
        total.text = total_number
    except (TypeError, ValueError): pass
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
    # Set URL if applicable
    if metadata["url"] is not None:
        url = SubElement(base, "Web")
        url.text = metadata["url"]
    try:
        # Set the score
        score_number = int(metadata["score"])
        if score_number > -1 and score_number < 6:
            score = SubElement(base, "CommunityRating")
            score.text = str(score_number)
    except (TypeError, ValueError): pass
    # Set tags if applicable
    tags = metadata["tags"]
    try:
        # Add score as star rating in tags
        score_number = int(metadata["score"])
        if score_number > 0 and score_number < 6:
            stars = "★"
            while len(stars) < score_number:
                stars = f"{stars}★"
            if tags is None or tags == "":
                tags = stars
            else:
                tags = f"{stars},{tags}"
    except (TypeError, ValueError): pass
    if tags is not None:
        tag_element = SubElement(base, "Tags")
        tag_element.text = tags
    # Set the age rating
    age_rating = SubElement(base, "AgeRating")
    age_rating.text = "Unknown"
    if metadata["age_rating"] is not None:
        age_rating.text = metadata["age_rating"]
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
    metadata["age_rating"] = base.findtext("AgeRating")
    metadata["score"] = base.findtext("CommunityRating")
    # Get the tags, removing score tags if necessary
    try:
        metadata["tags"] = resub("\\s*,+\\s*", ",", base.findtext("Tags"))
        metadata["tags"] = resub("^\\s+|\\s+$|★{1,5},|,★{1,5}$", "", metadata["tags"])
        metadata["tags"] = resub("^★{1,5}$", "", metadata["tags"])
        if metadata["tags"] == "":
            metadata["tags"] = None
    except TypeError: metadata["tags"] = None
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
    # Get all the JSONS
    jsons = []
    for file in files:
        if get_extension(file) == ".json":
            jsons.append(file)
    jsons = sort_alphanum(jsons)
    # Get metadata from all JSONs
    try:
        json_metas = []
        for json in jsons:
            json_metas.append(load_metadata(json))
        main_meta = json_metas[0]
    except IndexError: return get_empty_metadata()
    # Get most metadata from first JSON
    metadata = get_empty_metadata()
    metadata["title"] = main_meta["title"]
    metadata["date"] = main_meta["date"]
    metadata["writer"] = main_meta["writer"]
    metadata["artist"] = main_meta["artist"]
    metadata["cover_artist"] = main_meta["artist"]
    metadata["publisher"] = main_meta["publisher"]
    metadata["url"] = main_meta["url"]
    # Get description metadata
    description = main_meta["description"]
    if description is not None:
        description = replace_entities(description)
        description = resub("<a [^<>]*>|<\\/a[^<>]*>|<b>|<i>|</b>|</i>", "", description)
        description = resub("<[^<>]*>", " ", description)
        description = resub("\\s+", " ", description)
        description = remove_whitespace(description)
    metadata["description"] = description
    # Get tag metadata
    tags = main_meta["tags"]
    if tags is not None and tags is not []:
        tag_string = tags[0]
        for i in range(1, len(tags)):
            tag_string = f"{tag_string},{tags[i]}"
        metadata["tags"] = tag_string
    # Get highest age rating in list of JSON metadata
    highest_age = "Unknown"
    for json_meta in json_metas:
        if json_meta["age_rating"] == "X18+":
            highest_age = "X18+"
            continue
        elif json_meta["age_rating"] == "Mature 17+" and not highest_age == "X18+":
            highest_age = "Mature 17+"
            continue
        elif json_meta["age_rating"] == "Teen" and (highest_age == "Everyone" or highest_age == "Unknown"):
            highest_age = "Teen"
            continue
        elif json_meta["age_rating"] == "Everyone" and highest_age == "Unknown":
            highest_age = "Everyone"
    metadata["age_rating"] = highest_age
    # Return metadata
    return metadata
