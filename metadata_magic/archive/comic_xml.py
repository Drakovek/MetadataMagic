#!/usr/bin/env python3

import re
import html_string_tools
import metadata_magic.archive as mm_archive
import metadata_magic.file_tools as mm_file_tools
from os.path import abspath
from xml.etree import ElementTree

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
    base = ElementTree.Element("ComicInfo")
    base.attrib = schemas
    # Set the title if applicable
    if metadata["title"] is not None:
        title = ElementTree.SubElement(base, "Title")
        title.text = metadata["title"]
    # Set the page count if applicable
    if metadata["page_count"] is not None:
        page_count = ElementTree.SubElement(base, "PageCount")
        page_count.text = metadata["page_count"]
    # Set the series title if applicable
    if metadata["series"] is not None:
        series = ElementTree.SubElement(base, "Series")
        series.text = metadata["series"]
    try:
        # Sets the series number if applicable
        series_number = str(float(metadata["series_number"]))
        number = ElementTree.SubElement(base, "Number")
        number.text = series_number
        # Sets the series total if applicable
        total_number = str(int(metadata["series_total"]))
        total = ElementTree.SubElement(base, "Count")
        total.text = total_number
    except (TypeError, ValueError): pass
    # Set description if applicable
    if metadata["description"] is not None:
        summary = ElementTree.SubElement(base, "Summary")
        summary.text = metadata["description"]
    # Set the date if applicable
    if metadata["date"] is not None:
        # Set year
        year = ElementTree.SubElement(base, "Year")
        year.text = metadata["date"][0:4]
        # Set month
        month = ElementTree.SubElement(base, "Month")
        month.text = str(int(metadata["date"][5:7]))
        # Set day
        day = ElementTree.SubElement(base, "Day")
        day.text = str(int(metadata["date"][8:10]))
    # Set the writer if applicable
    if metadata["writers"] is not None and not metadata["writers"] == []:
        writer_string = ",".join(metadata["writers"])
        writer = ElementTree.SubElement(base, "Writer")
        writer.text = writer_string
    # Set all other artist categories if applicable
    if metadata["artists"] is not None and not metadata["artists"] == []:
        artist_string = ",".join(metadata["artists"])
        penciller = ElementTree.SubElement(base, "Penciller")
        inker = ElementTree.SubElement(base, "Inker")
        colorist = ElementTree.SubElement(base, "Colorist")
        penciller.text = artist_string
        inker.text = artist_string
        colorist.text = artist_string
    # Set the cover artist if applicable
    if metadata["cover_artists"] is not None and not metadata["cover_artists"] == []:
        cover_string = ",".join(metadata["cover_artists"])
        cover = ElementTree.SubElement(base, "CoverArtist")
        cover.text = cover_string
    # Set publisher if applicable
    if metadata["publisher"] is not None:
        publisher = ElementTree.SubElement(base, "Publisher")
        publisher.text = metadata["publisher"]
    # Set URL if applicable
    if metadata["url"] is not None:
        url = ElementTree.SubElement(base, "Web")
        url.text = metadata["url"]
    try:
        # Set the score
        score_number = int(metadata["score"])
        if score_number > -1 and score_number < 6:
            score = ElementTree.SubElement(base, "CommunityRating")
            score.text = str(score_number)
    except (TypeError, ValueError): pass
    # Set tags if applicable
    tags = metadata["tags"]
    try:
        # Add score as star rating in tags
        score_number = int(metadata["score"])
        if score_number > 0 and score_number < 6:
            stars = "★"*score_number
            if tags is None:
                tags = [stars]
            else:
                tags.insert(0, stars)
    except (TypeError, ValueError): pass
    if tags is not None and not tags == []:
        tag_element = ElementTree.SubElement(base, "Tags")
        tag_element.text = ",".join(tags)
    # Set the age rating
    age_rating = ElementTree.SubElement(base, "AgeRating")
    age_rating.text = "Unknown"
    if metadata["age_rating"] is not None:
        age_rating.text = metadata["age_rating"]
    # Set indents to make the XML more readable
    xml = ElementTree.tostring(base).decode("UTF-8").strip()
    if indent:
        xml = html_string_tools.make_human_readable(xml, "  ")
    xml = f"<?xml version=\"1.0\"?>\n{xml}"
    # Return XML
    return xml

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
    metadata = mm_archive.get_empty_metadata()
    try:
        tree = ElementTree.parse(file)
        base = tree.getroot()
    except ElementTree.ParseError: return metadata
    # Get metadata from XML
    metadata["title"] = base.findtext("Title")
    metadata["series"] = base.findtext("Series")
    metadata["series_number"] = base.findtext("Number")
    metadata["series_total"] = base.findtext("Count")
    metadata["description"] = base.findtext("Summary")
    metadata["writers"] = base.findtext("Writer")
    metadata["cover_artists"] = base.findtext("CoverArtist")
    metadata["publisher"] = base.findtext("Publisher")
    metadata["url"] = base.findtext("Web")
    metadata["age_rating"] = base.findtext("AgeRating")
    metadata["score"] = base.findtext("CommunityRating")
    metadata["page_count"] = base.findtext("PageCount")
    # Get the main artist from XML
    metadata["artists"] = base.findtext("Penciller")
    if metadata["artists"] is None:
        metadata["artists"] = base.findtext("Colorist")
    if metadata["artists"] is None:
        metadata["artists"] = base.findtext("Inker")
    # Update artists and writers to be in list form
    list_format = lambda a: re.sub(r"^[\s,]*$", "", re.sub(r"\s*,\s*", ",", a)).strip().split(",")
    if metadata["writers"] is not None:
        metadata["writers"] = list_format(metadata["writers"])
    if metadata["artists"] is not None:
        metadata["artists"] = list_format(metadata["artists"])
    if metadata["cover_artists"] is not None:
        metadata["cover_artists"] = list_format(metadata["cover_artists"])
    # Get the tags, removing score tags if necessary
    try:
        metadata["tags"] = base.findtext("Tags").strip()
        metadata["tags"] = re.sub(r"(?<=,)\s*★{1,5}\s*,", "", metadata["tags"])
        metadata["tags"] = re.sub(r"^\s*★{1,5}\s*,?|,?\s*★{1,5}\s*$", "", metadata["tags"])
        metadata["tags"] = list_format(metadata["tags"])
    except (AttributeError, TypeError): metadata["tags"] = None
    # Get date from XML
    year = base.findtext("Year")
    month = base.findtext("Month")
    day = base.findtext("Day")
    try:
        assert year is not None and month is not None and day is not None
        assert int(year) > 999
        assert int(month) < 13
        assert int(day) < 32
        month = month.zfill(2)
        day = day.zfill(2)
        metadata["date"] = f"{year}-{month}-{day}"
    except (AssertionError, ValueError): metadata["date"] = None
    # Replace empty text with None
    for entry in metadata.items():
        if entry[1] is None:
            continue
        if ((isinstance(entry[1], str) and len(re.findall(r"^\s*$", entry[1])) > 0)
            or len(entry[1]) == 0 or entry[1] == [""]):
            metadata[entry[0]] = None
    # Return the gathered metadata
    return metadata
