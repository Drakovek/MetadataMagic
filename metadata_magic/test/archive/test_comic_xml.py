#!/usr/bin/env python3

import os
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.comic_xml as mm_comic_xml
from os.path import abspath, exists, join

def test_get_comic_xml():
    """
    Tests the get_comic_xml function.
    """
    start = "<?xml version=\"1.0\"?>\n<ComicInfo xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" "
    start = f"{start}xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\">"
    end = "<AgeRating>Unknown</AgeRating></ComicInfo>"
    # Test setting title in the XML file
    meta = mm_archive.get_empty_metadata()
    meta["title"] = "This's a title\\'"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Title>This's a title\\'</Title>{end}"
    # Test setting series info in the XML file
    meta = mm_archive.get_empty_metadata()
    meta["series"] = "Name!!"
    meta["series_number"] = "2.5"
    meta["series_total"] = "5"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Series>Name!!</Series><Number>2.5</Number><Count>5</Count>{end}"
    # Test setting invalid series number and total
    meta["series_number"] = "NotNumber"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Series>Name!!</Series>{end}"
    meta["series_number"] = "5.0"
    meta["series_total"] = "AlsoNotNumber"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Series>Name!!</Series><Number>5.0</Number>{end}"
    # Test setting description in the XML file
    meta = mm_archive.get_empty_metadata()
    meta["description"] = "Description of the thing."
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Summary>Description of the thing.</Summary>{end}"
    meta["description"] = "'Tis this & That's >.<"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Summary>'Tis this &amp; That's &gt;.&lt;</Summary>{end}"
    # Test setting date in the XML file
    meta = mm_archive.get_empty_metadata()
    meta["date"] = "2023-01-15"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Year>2023</Year><Month>1</Month><Day>15</Day>{end}"
    meta["date"] = "2014-12-08"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Year>2014</Year><Month>12</Month><Day>8</Day>{end}"
    # Test setting writer in XML file
    meta = mm_archive.get_empty_metadata()
    meta["writers"] = "Person!"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Writer>Person!</Writer>{end}"
    # Test setting cover artist in XML file
    meta = mm_archive.get_empty_metadata()
    meta["cover_artists"] = "Guest"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<CoverArtist>Guest</CoverArtist>{end}"
    # Test setting main artists in XML file
    meta = mm_archive.get_empty_metadata()
    meta["artists"] = "Bleh"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Penciller>Bleh</Penciller><Inker>Bleh</Inker><Colorist>Bleh</Colorist>{end}"
    # Test setting publisher in XML file
    meta = mm_archive.get_empty_metadata()
    meta["publisher"] = "Company"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Publisher>Company</Publisher>{end}"
    # Test setting tags in XML file
    meta = mm_archive.get_empty_metadata()
    meta["tags"] = "Some,Tags,&,stuff"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Tags>Some,Tags,&amp;,stuff</Tags>{end}"
    # Test setting URL in XML file
    meta = mm_archive.get_empty_metadata()
    meta["url"] = "www.ihopethisisntarealsite.com"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Web>www.ihopethisisntarealsite.com</Web>{end}"
    # Test setting the score in the XML file
    meta = mm_archive.get_empty_metadata()
    meta["score"] = "0"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<CommunityRating>0</CommunityRating>{end}"
    meta = mm_archive.get_empty_metadata()
    meta["score"] = "2"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<CommunityRating>2</CommunityRating><Tags>&#9733;&#9733;</Tags>{end}"
    meta = mm_archive.get_empty_metadata()
    meta["score"] = "5"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<CommunityRating>5</CommunityRating><Tags>&#9733;&#9733;&#9733;&#9733;&#9733;</Tags>{end}"
    # Test setting invalid score in XML file
    meta["title"] = "Thing!"
    meta["score"] = "Blah"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Title>Thing!</Title>{end}"
    meta["score"] = "6"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Title>Thing!</Title>{end}"
    meta["score"] = "-3"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Title>Thing!</Title>{end}"
    # Test adding score as tags
    meta = mm_archive.get_empty_metadata()
    meta["tags"] = "These,are,things"
    meta["score"] = "3"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<CommunityRating>3</CommunityRating><Tags>&#9733;&#9733;&#9733;,These,are,things</Tags>{end}"
    meta["score"] = "5"
    meta["tags"] = None
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<CommunityRating>5</CommunityRating><Tags>&#9733;&#9733;&#9733;&#9733;&#9733;</Tags>{end}"
    meta["score"] = "0"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<CommunityRating>0</CommunityRating>{end}"
    # Test setting the age rating in the XML file
    meta = mm_archive.get_empty_metadata()
    meta["age_rating"] = "Everyone"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<AgeRating>Everyone</AgeRating></ComicInfo>"
    meta = mm_archive.get_empty_metadata()
    meta["age_rating"] = None
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<AgeRating>Unknown</AgeRating></ComicInfo>"
    # Test getting XML with indents
    meta = mm_archive.get_empty_metadata()
    meta["title"] = "Name!"
    xml = mm_comic_xml.get_comic_xml(meta, True)
    result = "<?xml version=\"1.0\"?>\n"
    result = f"{result}<ComicInfo xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" "
    result = f"{result}xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\">"
    result = f"{result}\n  <Title>Name!</Title>"
    result = f"{result}\n  <AgeRating>Unknown</AgeRating>\n</ComicInfo>"
    assert xml == result

def test_read_comic_info():
    """
    Tests the read_comic_info function.
    """
    # Test getting title from ComicInfo
    temp_dir = mm_file_tools.get_temp_dir()
    xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
    meta_write = mm_archive.get_empty_metadata()
    meta_write["title"] = "This is a title!"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    assert exists(xml_file)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["series"] is None
    # Test getting series info from ComicInfo.xml
    meta_write["series"] = "The Thing"
    meta_write["series_number"] = "3.0"
    meta_write["series_total"] = "4"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["series"] == "The Thing"
    assert meta_read["series_number"] == "3.0"
    assert meta_read["series_total"] == "4"
    assert meta_read["description"] is None
    # Test getting description from ComicInfo.xml
    meta_write["description"] = "Some words and such."
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["description"] == "Some words and such."
    assert meta_read["date"] is None
    meta_write["description"] = "'Tis this & That\\Other >.<"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["description"] == "'Tis this & That\\Other >.<"
    assert meta_read["date"] is None
    # Test getting date from ComicInfo.xml
    meta_write["date"] = "2012-03-09"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["date"] == "2012-03-09"
    assert meta_read["writers"] is None
    meta_write["date"] = "2021-12-12"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["date"] == "2021-12-12"
    assert meta_read["writers"] is None
    # Test getting writer from ComicInfo.xml
    meta_write["writers"] = "Author Dude"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["writers"] == "Author Dude"
    assert meta_read["cover_artists"] is None
    # Test getting cover artist from ComicInfo.xml
    meta_write["cover_artists"] = "Person"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["cover_artists"] == "Person"
    assert meta_read["artists"] is None
    # Test getting main artist from ComicInfo.xml
    meta_write["artists"] = "ArtGirl"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["artists"] == "ArtGirl"
    assert meta_read["publisher"] is None
    # Test getting the publisher from ComicInfo.xml
    meta_write["publisher"] = "Website"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["publisher"] == "Website"
    assert meta_read["url"] is None
    # Test getting url from ComicInfo.xml
    meta_write["url"] = "/web/page/"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["url"] == "/web/page/"
    assert meta_read["tags"] is None
    assert meta_read["age_rating"] == "Unknown"
    # Test getting age rating from ComicInfo.xml
    meta_write["age_rating"] = "Everyone"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["age_rating"] == "Everyone"
    assert meta_read["tags"] is None
    # Test getting score from ComicInfo.xml
    meta_write["score"] = "4"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["score"] == "4"
    assert meta_read["tags"] == None
    # Test getting tags from ComicInfo.xml
    meta_write["title"] = None
    meta_write["tags"] = " these, are , some tags  "
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["tags"] == "these,are,some tags"
    assert meta_read["title"] is None
    # Test that any star score tags are removed
    meta_write["title"] = "Hooray!"
    meta_write["tags"] = "★★★★"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["title"] == "Hooray!"
    assert meta_read["tags"] == None
    meta_write["tags"] = "★, Some,Tags!,Yay"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["tags"] == "Some,Tags!,Yay"
    meta_write["tags"] = "More, tags, and, such, ★★★"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["tags"] == "More,tags,and,such"
    meta_write["tags"] = "Other, ★★★★★, Final "
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["tags"] == "Other,Final"
    meta_write["tags"] = "Larger,Star,Count,★★★★★★★★★★"
    xml = mm_comic_xml.get_comic_xml(meta_write, False)
    mm_file_tools.write_text_file(xml_file, xml)
    meta_read = mm_comic_xml.read_comic_info(xml_file)
    assert meta_read["tags"] == "Larger,Star,Count,★★★★★★★★★★"
    # Test if given file is not a proper XML file
    unrelated = abspath(join(temp_dir, "blah.xml"))
    mm_file_tools.write_text_file(unrelated, "This is some unimportant non-xml text.")
    assert exists(unrelated)
    meta_read = mm_comic_xml.read_comic_info(unrelated)
    assert meta_read["title"] is None
    assert meta_read["series"] is None
