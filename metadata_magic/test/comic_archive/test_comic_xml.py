#!/usr/bin/env python3

from metadata_magic.main.comic_archive.comic_archive import get_temp_dir
from metadata_magic.main.comic_archive.comic_xml import get_comic_xml
from metadata_magic.main.comic_archive.comic_xml import get_empty_metadata
from metadata_magic.main.comic_archive.comic_xml import generate_info_from_jsons
from metadata_magic.main.comic_archive.comic_xml import read_comic_info
from metadata_magic.test.temp_file_tools import create_text_file, create_json_file
from os import mkdir
from os.path import abspath, exists, join

def test_get_empty_metadata():
    """
    Tests the get_empty_metadata function.
    """
    meta = get_empty_metadata()
    assert meta["title"] is None
    assert meta["series"] is None
    assert meta["series_number"] is None
    assert meta["description"] is None
    assert meta["date"] is None
    assert meta["writer"] is None
    assert meta["artist"] is None
    assert meta["cover_artist"] is None
    assert meta["publisher"] is None
    assert meta["tags"] is None
    assert meta["url"] is None

def test_get_comic_xml():
    """
    Tests the get_comic_xml function.
    """
    start = "<?xml version=\"1.0\"?>\n<ComicInfo xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" "
    start = f"{start}xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\">"
    # Test setting title in the XML file
    meta = get_empty_metadata()
    meta["title"] = "This's a title\\'"
    xml = get_comic_xml(meta, False)
    assert xml == f"{start}<Title>This's a title\\'</Title></ComicInfo>"
    # Test setting series info in the XML file
    meta = get_empty_metadata()
    meta["series"] = "Name!!"
    meta["series_number"] = "2.5"
    xml = get_comic_xml(meta, False)
    assert xml == f"{start}<Series>Name!!</Series><Number>2.5</Number></ComicInfo>"
    # Test setting description in the XML file
    meta = get_empty_metadata()
    meta["description"] = "Description of the thing."
    xml = get_comic_xml(meta, False)
    assert xml == f"{start}<Summary>Description of the thing.</Summary></ComicInfo>"
    meta["description"] = "'Tis this & That's >.<"
    xml = get_comic_xml(meta, False)
    assert xml == f"{start}<Summary>'Tis this &amp; That's &gt;.&lt;</Summary></ComicInfo>"
    # Test setting date in the XML file
    meta = get_empty_metadata()
    meta["date"] = "2023-01-15"
    xml = get_comic_xml(meta, False)
    assert xml == f"{start}<Year>2023</Year><Month>1</Month><Day>15</Day></ComicInfo>"
    meta["date"] = "2014-12-08"
    xml = get_comic_xml(meta, False)
    assert xml == f"{start}<Year>2014</Year><Month>12</Month><Day>8</Day></ComicInfo>"
    # Test setting writer in XML file
    meta = get_empty_metadata()
    meta["writer"] = "Person!"
    xml = get_comic_xml(meta, False)
    assert xml == f"{start}<Writer>Person!</Writer></ComicInfo>"
    # Test setting cover artist in XML file
    meta = get_empty_metadata()
    meta["cover_artist"] = "Guest"
    xml = get_comic_xml(meta, False)
    assert xml == f"{start}<CoverArtist>Guest</CoverArtist></ComicInfo>"
    # Test setting main artists in XML file
    meta = get_empty_metadata()
    meta["artist"] = "Bleh"
    xml = get_comic_xml(meta, False)
    assert xml == f"{start}<Penciller>Bleh</Penciller><Inker>Bleh</Inker><Colorist>Bleh</Colorist></ComicInfo>"
    # Test setting publisher in XML file
    meta = get_empty_metadata()
    meta["publisher"] = "Company"
    xml = get_comic_xml(meta, False)
    assert xml == f"{start}<Publisher>Company</Publisher></ComicInfo>"
    # Test setting tags in XML file
    meta = get_empty_metadata()
    meta["tags"] = "Some,Tags,&,stuff"
    xml = get_comic_xml(meta, False)
    assert xml == f"{start}<Tags>Some,Tags,&amp;,stuff</Tags></ComicInfo>"
    # Test setting URL in XML file
    meta = get_empty_metadata()
    meta["url"] = "www.ihopethisisntarealsite.com"
    xml = get_comic_xml(meta, False)
    assert xml == f"{start}<Web>www.ihopethisisntarealsite.com</Web></ComicInfo>"
    # Test getting XML with indents
    meta = get_empty_metadata()
    meta["title"] = "Name!"
    xml = get_comic_xml(meta, True)
    result = "<?xml version=\"1.0\"?>\n"
    result = f"{result}<ComicInfo xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" "
    result = f"{result}xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\">"
    result = f"{result}\n  <Title>Name!</Title>\n</ComicInfo>"
    assert xml == result

def test_read_comic_info():
    """
    Tests the read_comic_info function.
    """
    # Test getting title from ComicInfo
    temp_dir = get_temp_dir()
    xml_file = abspath(join(temp_dir, "ComicInfo.xml"))
    meta_write = get_empty_metadata()
    meta_write["title"] = "This is a title!"
    xml = get_comic_xml(meta_write, False)
    create_text_file(xml_file, xml)
    assert exists(xml_file)
    meta_read = read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["series"] is None
    # Test getting series info from ComicInfo.xml
    meta_write["series"] = "The Thing"
    meta_write["series_number"] = "3.0"
    xml = get_comic_xml(meta_write, False)
    create_text_file(xml_file, xml)
    meta_read = read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["series"] == "The Thing"
    assert meta_read["series_number"] == "3.0"
    assert meta_read["description"] is None
    # Test getting description from ComicInfo.xml
    meta_write["description"] = "Some words and such."
    xml = get_comic_xml(meta_write, False)
    create_text_file(xml_file, xml)
    meta_read = read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["description"] == "Some words and such."
    assert meta_read["date"] is None
    meta_write["description"] = "'Tis this & That\\Other >.<"
    xml = get_comic_xml(meta_write, False)
    create_text_file(xml_file, xml)
    meta_read = read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["description"] == "'Tis this & That\\Other >.<"
    assert meta_read["date"] is None
    # Test getting date from ComicInfo.xml
    meta_write["date"] = "2012-03-09"
    xml = get_comic_xml(meta_write, False)
    create_text_file(xml_file, xml)
    meta_read = read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["date"] == "2012-03-09"
    assert meta_read["writer"] is None
    meta_write["date"] = "2021-12-12"
    xml = get_comic_xml(meta_write, False)
    create_text_file(xml_file, xml)
    meta_read = read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["date"] == "2021-12-12"
    assert meta_read["writer"] is None
    # Test getting writer from ComicInfo.xml
    meta_write["writer"] = "Author Dude"
    xml = get_comic_xml(meta_write, False)
    create_text_file(xml_file, xml)
    meta_read = read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["writer"] == "Author Dude"
    assert meta_read["cover_artist"] is None
    # Test getting cover artist from ComicInfo.xml
    meta_write["cover_artist"] = "Person"
    xml = get_comic_xml(meta_write, False)
    create_text_file(xml_file, xml)
    meta_read = read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["cover_artist"] == "Person"
    assert meta_read["artist"] is None
    # Test getting main artist from ComicInfo.xml
    meta_write["artist"] = "ArtGirl"
    xml = get_comic_xml(meta_write, False)
    create_text_file(xml_file, xml)
    meta_read = read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["artist"] == "ArtGirl"
    assert meta_read["publisher"] is None
    # Test getting the publisher from ComicInfo.xml
    meta_write["publisher"] = "Website"
    xml = get_comic_xml(meta_write, False)
    create_text_file(xml_file, xml)
    meta_read = read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["publisher"] == "Website"
    assert meta_read["url"] is None
    # Test getting url from ComicInfo.xml
    meta_write["url"] = "/web/page/"
    xml = get_comic_xml(meta_write, False)
    create_text_file(xml_file, xml)
    meta_read = read_comic_info(xml_file)
    assert meta_read["title"] == "This is a title!"
    assert meta_read["url"] == "/web/page/"
    assert meta_read["tags"] is None
    # Test getting tags from ComicInfo.xml
    meta_write["title"] = None
    meta_write["tags"] = "these,are,tags"
    xml = get_comic_xml(meta_write, False)
    create_text_file(xml_file, xml)
    meta_read = read_comic_info(xml_file)
    assert meta_read["tags"] == "these,are,tags"
    assert meta_read["title"] is None
    # Test if given file is not a proper XML file
    unrelated = abspath(join(temp_dir, "blah.xml"))
    create_text_file(unrelated, "This is some unimportant non-xml text.")
    assert exists(unrelated)
    meta_read = read_comic_info(unrelated)
    assert meta_read["title"] is None
    assert meta_read["series"] is None

def test_generate_info_from_jsons():
    """
    Tests the generate_info_from_jsons function.
    """
    # Test getting title
    temp_dir = get_temp_dir()
    sub_dir = abspath(join(temp_dir, "sub"))
    mkdir(sub_dir)
    not_json = abspath(join(temp_dir, "aaa.txt"))
    main_json = abspath(join(temp_dir, "json.json"))
    sub_json = abspath(join(sub_dir, "blah.json"))
    json_meta = {"title":"This is a title!"}
    create_text_file(not_json, "This is text")
    create_json_file(main_json, json_meta)
    create_json_file(sub_json, {"no":"info"})
    assert exists(not_json)
    assert exists(main_json)
    assert exists(sub_json)
    meta = generate_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["artist"] is None
    assert meta["description"] is None
    # Test getting description
    json_meta["description"] = "Some caption."
    create_json_file(main_json, json_meta)
    meta = generate_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["description"] == "Some caption."
    assert meta["date"] is None
    assert meta["cover_artist"] is None
    # Test simplifying description with HTML info contained
    json_meta["description"] = "Let's say there's a <a href='ajsdlf'>link</a>.<br>Other!!"
    create_json_file(main_json, json_meta)
    meta = generate_info_from_jsons(temp_dir)
    assert meta["description"] == "Let's say there's a link. Other!!"
    json_meta["description"] = "<div><p>Way too many tags!</p><br>\n<br/> <b>B</b>ut it's <i>o</i>kay right?</div>"
    create_json_file(main_json, json_meta)
    meta = generate_info_from_jsons(temp_dir)
    assert meta["description"] == "Way too many tags! But it's okay right?"
    json_meta["description"] = "What about 'em elements &amp; such? &gt;.&gt;"
    create_json_file(main_json, json_meta)
    meta = generate_info_from_jsons(temp_dir)
    assert meta["description"] == "What about 'em elements & such? >.>"
    # Test getting date
    json_meta["date"] = "2012-12-21"
    create_json_file(main_json, json_meta)
    meta = generate_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["date"] == "2012-12-21"
    assert meta["cover_artist"] is None
    # Test getting artist data
    json_meta["artist"] = "Person!"
    create_json_file(main_json, json_meta)
    meta = generate_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["writer"] == "Person!"
    assert meta["cover_artist"] == "Person!"
    assert meta["artist"] == "Person!"
    assert meta["publisher"] is None
    # Test getting publisher
    json_meta["url"] = "youtube.com/something"
    create_json_file(main_json, json_meta)
    meta = generate_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["publisher"] == "YouTube"
    assert meta["tags"] is None
    # Test getting tags
    json_meta["tags"] = ["These", "Are", "Tags"]
    create_json_file(main_json, json_meta)
    meta = generate_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["tags"] == "These,Are,Tags"
    json_meta["tags"] = ["Tag"]
    create_json_file(main_json, json_meta)
    meta = generate_info_from_jsons(temp_dir)
    assert meta["tags"] == "Tag"
    json_meta["tags"] = []
    create_json_file(main_json, json_meta)
    meta = generate_info_from_jsons(temp_dir)
    assert meta["tags"] is None
    # Test getting url
    json_meta["url"] = "someurlthing.net"
    create_json_file(main_json, json_meta)
    meta = generate_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["url"] == "someurlthing.net"
    assert meta["tags"] is None
    # Test with JSON files only in subdirectories
    temp_dir = get_temp_dir()
    sub1 = abspath(join(temp_dir, "aaaa"))
    sub2 = abspath(join(temp_dir, "bbbb"))
    main_json = abspath(join(sub1, "thing.json"))
    sub_json = abspath(join(sub2, "first.json"))
    mkdir(sub1)
    mkdir(sub2)
    create_json_file(main_json, {"title":"Real Title."})
    create_json_file(sub_json, {"title":"Not this one."})
    assert exists(main_json)
    assert exists(sub_json)
    meta = generate_info_from_jsons(temp_dir)
    assert meta["title"] == "Real Title."
    # Test with no JSON files
    temp_dir = get_temp_dir()
    test_file = abspath(join(temp_dir, "File!.txt"))
    create_text_file(test_file, "Blah.")
    assert exists(test_file)
    meta = generate_info_from_jsons(temp_dir)
    assert meta["title"] is None
    assert meta["description"] is None
    assert meta["date"] is None
    assert meta["writer"] is None
    assert meta["artist"] is None
    assert meta["cover_artist"] is None
    assert meta["publisher"] is None
    assert meta["url"] is None
