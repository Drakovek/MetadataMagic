#!/usr/bin/env python3

import metadata_magic.test as mm_test
import metadata_magic.archive as mm_archive
import metadata_magic.archive.comic_xml as mm_comic_xml
from os.path import abspath, join

def test_get_comic_xml():
    """
    Tests the get_comic_xml function.
    """
    start = "<?xml version=\"1.0\"?>\n<ComicInfo xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" "
    start = f"{start}xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\">"
    end = "<AgeRating>Unknown</AgeRating></ComicInfo>"
    # Test setting title in the XML file
    meta = mm_archive.get_empty_metadata()
    meta["title"] = "AAA\\';"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Title>AAA\\';</Title>{end}"
    # Test setting page count in the XML file
    meta = mm_archive.get_empty_metadata()
    meta["title"] = "Test"
    meta["page_count"] = "23"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Title>Test</Title><PageCount>23</PageCount>{end}"
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
    # Test setting writers in the XML file
    meta = mm_archive.get_empty_metadata()
    meta["writers"] = ["Writer"]
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Writer>Writer</Writer>{end}"
    meta["writers"] = ["Multiple", "People"]
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Writer>Multiple,People</Writer>{end}"
    # Test setting cover artist in XML file
    meta = mm_archive.get_empty_metadata()
    meta["cover_artists"] = ["Artist"]
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<CoverArtist>Artist</CoverArtist>{end}"
    meta["cover_artists"] = ["AAA", "BBB"]
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<CoverArtist>AAA,BBB</CoverArtist>{end}"
    # Test setting main artists in XML file
    meta = mm_archive.get_empty_metadata()
    meta["artists"] = ["Person"]
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Penciller>Person</Penciller><Inker>Person</Inker><Colorist>Person</Colorist>{end}"
    meta["artists"] = ["A","B"]
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Penciller>A,B</Penciller><Inker>A,B</Inker><Colorist>A,B</Colorist>{end}"
    # Test setting publisher in XML file
    meta = mm_archive.get_empty_metadata()
    meta["publisher"] = "Company"
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Publisher>Company</Publisher>{end}"
    # Test setting tags in XML file
    meta = mm_archive.get_empty_metadata()
    meta["tags"] = ["Some", "Tags", "&", "Stuff"]
    xml = mm_comic_xml.get_comic_xml(meta, False)
    assert xml == f"{start}<Tags>Some,Tags,&amp;,Stuff</Tags>{end}"
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
    meta["tags"] = ["These","are","things"]
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
    # Test getting info from ComicInfo file
    xml_file = abspath(join(mm_test.COMIC_XML_DIRECTORY, "ComicInfoFull.xml"))
    metadata = mm_comic_xml.read_comic_info(xml_file)
    assert metadata["title"] == "Comic Title"
    assert metadata["page_count"] == "42"
    assert metadata["series"] == "Series Title"
    assert metadata["series_number"] == "3.0"
    assert metadata["series_total"] == "4"
    assert metadata["description"] == "This & That!"
    assert metadata["date"] == "2012-03-09"
    assert metadata["writers"] == ["Multiple", "Authors"]
    assert metadata["artists"] == ["More", "People"]
    assert metadata["cover_artists"] == ["A", "B", "C"]
    assert metadata["publisher"] == "Website"
    assert metadata["url"] == "/url/page/"
    assert metadata["age_rating"] == "Teen"
    assert metadata["score"] == "4"
    assert metadata["tags"] == ["A", "B", "C", "D", "E"]
    # Test getting info from ComicInfo file with only title
    xml_file = abspath(join(mm_test.COMIC_XML_DIRECTORY, "ComicInfoTiny.xml"))
    metadata = mm_comic_xml.read_comic_info(xml_file)
    assert metadata["title"] == "Solo"
    assert metadata["page_count"] is None
    assert metadata["series"] is None
    assert metadata["series_number"] is None
    assert metadata["series_total"] is None
    assert metadata["description"] is None
    assert metadata["date"] is None
    assert metadata["writers"] is None
    assert metadata["artists"] is None
    assert metadata["cover_artists"] is None
    assert metadata["publisher"] is None
    assert metadata["url"] is None
    assert metadata["age_rating"] is None
    assert metadata["score"] is None
    assert metadata["tags"] is None
    # Test getting comic info from file with tags but no contents
    xml_file = abspath(join(mm_test.COMIC_XML_DIRECTORY, "ComicInfoEmpty.xml"))
    metadata = mm_comic_xml.read_comic_info(xml_file)
    assert metadata["title"] == "Empty"
    assert metadata["page_count"] is None
    assert metadata["series"] is None
    assert metadata["series_number"] is None
    assert metadata["series_total"] is None
    assert metadata["description"] is None
    assert metadata["date"] is None
    assert metadata["writers"] is None
    assert metadata["artists"] is None
    assert metadata["cover_artists"] is None
    assert metadata["publisher"] is None
    assert metadata["url"] is None
    assert metadata["age_rating"] is None
    assert metadata["score"] is None
    assert metadata["tags"] is None
    # Test removing score tags
    xml_file = abspath(join(mm_test.COMIC_XML_DIRECTORY, "ComicInfoRating.xml"))
    metadata = mm_comic_xml.read_comic_info(xml_file)
    assert metadata["tags"] == ["★★★★★★", "Remaining", "Tags"]
    # Test invalid XML file
    xml_file = abspath(join(mm_test.BASIC_TEXT_DIRECTORY, "latin1.txt"))
    metadata = mm_comic_xml.read_comic_info(xml_file)
    assert metadata["title"] is None
    assert metadata["page_count"] is None
    assert metadata["series"] is None
    assert metadata["series_number"] is None
    assert metadata["series_total"] is None
    assert metadata["description"] is None
    assert metadata["date"] is None
    assert metadata["writers"] is None
    assert metadata["artists"] is None
    assert metadata["cover_artists"] is None
    assert metadata["publisher"] is None
    assert metadata["url"] is None
    assert metadata["age_rating"] is None
    assert metadata["score"] is None
    assert metadata["tags"] is None
