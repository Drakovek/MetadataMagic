#!/usr/bin/env python3

import os
import metadata_magic.archive.archive as mm_archive
import metadata_magic.file_tools as mm_file_tools
from os.path import abspath, exists, join

def test_get_directory_archive_type():
    """
    Tests the get_directory_archive_type function.
    """
    # Test getting epub from folder with text files
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "text.txt")), "AAA")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "image.png")), "AAA")
    assert mm_archive.get_directory_archive_type(temp_dir) == "epub"
    # Test getting cbz from folder with images
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "meta.json")), "AAA")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "image.png")), "AAA")
    assert mm_archive.get_directory_archive_type(temp_dir) == "cbz"
    # Test getting cbz from subdirectory with images
    temp_dir = mm_file_tools.get_temp_dir()
    sub_dir = abspath(join(temp_dir, "sub"))
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(abspath(join(sub_dir, "meta.jpeg")), "AAA")
    assert mm_archive.get_directory_archive_type(temp_dir) == "cbz"
    # Test getting None from directory with no relevant files
    temp_dir = mm_file_tools.get_temp_dir()
    assert mm_archive.get_directory_archive_type(temp_dir) is None
    sub_dir = abspath(join(temp_dir, "sub"))
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(abspath(join(sub_dir, "meta.text")), "AAA")
    mm_file_tools.write_text_file(abspath(join(sub_dir, "meta.gif")), "AAA")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "meta.json")), "AAA")
    assert mm_archive.get_directory_archive_type(temp_dir) is None

def test_get_empty_metadata():
    """
    Tests the get_empty_metadata function.
    """
    meta = mm_archive.get_empty_metadata()
    assert meta["title"] is None
    assert meta["series"] is None
    assert meta["series_number"] is None
    assert meta["series_total"] is None
    assert meta["description"] is None
    assert meta["date"] is None
    assert meta["writer"] is None
    assert meta["artist"] is None
    assert meta["cover_artist"] is None
    assert meta["publisher"] is None
    assert meta["tags"] is None
    assert meta["url"] is None
    assert meta["age_rating"] == None
    assert meta["score"] is None

def test_get_info_from_jsons():
    """
    Tests the get_info_from_jsons function.
    """
    # Test getting title
    temp_dir = mm_file_tools.get_temp_dir()
    sub_dir = abspath(join(temp_dir, "sub"))
    os.mkdir(sub_dir)
    main_media = abspath(join(temp_dir, "json.txt"))
    main_json = abspath(join(temp_dir, "json.json"))
    sub_media = abspath(join(sub_dir, "blah.png"))
    sub_json = abspath(join(sub_dir, "blah.json"))
    json_meta = {"title":"This is a title!"}
    mm_file_tools.write_text_file(main_media, "This is text")
    mm_file_tools.write_json_file(main_json, json_meta)
    mm_file_tools.write_text_file(sub_media, "Not actually an image")
    mm_file_tools.write_json_file(sub_json, {"no":"info"})
    assert exists(main_media)
    assert exists(main_json)
    assert exists(sub_media)
    assert exists(sub_json)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["artist"] is None
    assert meta["description"] is None
    # Test getting description
    json_meta["description"] = "Some caption."
    mm_file_tools.write_json_file(main_json, json_meta)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["description"] == "Some caption."
    assert meta["date"] is None
    assert meta["cover_artist"] is None
    # Test simplifying description with HTML info contained
    json_meta["description"] = "Let's say there's a <a href='ajsdlf'>link</a>.<br>Other!!"
    mm_file_tools.write_json_file(main_json, json_meta)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["description"] == "Let's say there's a link. Other!!"
    json_meta["description"] = "<div><p>Way too many tags!</p><br>\n<br/> <b>B</b>ut it's <i>o</i>kay right?</div>"
    mm_file_tools.write_json_file(main_json, json_meta)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["description"] == "Way too many tags! But it's okay right?"
    json_meta["description"] = "What about 'em elements &amp; such? &gt;.&gt;"
    mm_file_tools.write_json_file(main_json, json_meta)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["description"] == "What about 'em elements & such? >.>"
    # Test getting date
    json_meta["date"] = "2012-12-21"
    mm_file_tools.write_json_file(main_json, json_meta)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["date"] == "2012-12-21"
    assert meta["cover_artist"] is None
    # Test getting artist data
    json_meta["artist"] = "Person!"
    mm_file_tools.write_json_file(main_json, json_meta)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["writer"] == "Person!"
    assert meta["cover_artist"] == "Person!"
    assert meta["artist"] == "Person!"
    assert meta["publisher"] is None
    # Test getting publisher
    json_meta["url"] = "youtube.com/something"
    mm_file_tools.write_json_file(main_json, json_meta)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["publisher"] == "YouTube"
    assert meta["tags"] is None
    # Test getting tags
    json_meta["tags"] = ["These", "Are", "Tags"]
    mm_file_tools.write_json_file(main_json, json_meta)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["tags"] == "These,Are,Tags"
    json_meta["tags"] = ["Tag"]
    mm_file_tools.write_json_file(main_json, json_meta)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["tags"] == "Tag"
    json_meta["tags"] = []
    mm_file_tools.write_json_file(main_json, json_meta)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["tags"] is None
    # Test getting url
    json_meta["url"] = "someurlthing.net"
    mm_file_tools.write_json_file(main_json, json_meta)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["url"] == "someurlthing.net"
    assert meta["tags"] is None
    assert meta["age_rating"] == "Unknown"
    # Test getting age rating
    temp_dir = mm_file_tools.get_temp_dir()
    media_everyone = abspath(join(temp_dir, "everyone.png"))
    json_everyone = abspath(join(temp_dir, "everyone.json"))
    mm_file_tools.write_text_file(media_everyone, "E For All")
    mm_file_tools.write_json_file(json_everyone, {"title":"Thing!", "url":"newgrounds.com/", "rating":"E"})
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["title"] == "Thing!"
    assert meta["age_rating"] == "Everyone"
    media_teen = abspath(join(temp_dir, "teen.gif"))
    json_teen = abspath(join(temp_dir, "teen.json"))
    mm_file_tools.write_json_file(media_teen, "Edgy")
    mm_file_tools.write_json_file(json_teen, {"rating":"t", "url":"www.newgrounds.com"})
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["age_rating"] == "Teen"
    media_mature = abspath(join(temp_dir, "mature.txt"))
    json_mature = abspath(join(temp_dir, "mature.json"))
    mm_file_tools.write_text_file(media_mature, "Blood Bleeder")
    mm_file_tools.write_json_file(json_mature, {"url":"newgrounds", "rating":"m"})
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["age_rating"] == "Mature 17+"
    media_adult = abspath(join(temp_dir, "adult.png"))
    json_adult = abspath(join(temp_dir, "adult.json"))
    mm_file_tools.write_text_file(media_adult, "AAAAAAAAAA!")
    mm_file_tools.write_json_file(json_adult, {"url":"www.newgrounds.com/thing", "rating":"A"})
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["age_rating"] == "X18+"
    assert exists(json_everyone)
    assert exists(json_teen)
    assert exists(json_mature)
    assert exists(json_adult)
    # Test with JSON files only in subdirectories
    temp_dir = mm_file_tools.get_temp_dir()
    sub1 = abspath(join(temp_dir, "aaaa"))
    sub2 = abspath(join(temp_dir, "bbbb"))
    main_media = abspath(join(sub1, "thing.png"))
    main_json = abspath(join(sub1, "thing.json"))
    sub_media = abspath(join(sub2, "first.txt"))
    sub_json = abspath(join(sub2, "first.json"))
    os.mkdir(sub1)
    os.mkdir(sub2)
    mm_file_tools.write_text_file(main_media, "Main File")
    mm_file_tools.write_json_file(main_json, {"title":"Real Title."})
    mm_file_tools.write_text_file(sub_media, "Sub file")
    mm_file_tools.write_json_file(sub_json, {"title":"Not this one."})
    assert exists(main_media)
    assert exists(main_json)
    assert exists(sub_media)
    assert exists(sub_json)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["title"] == "Real Title."
    # Test with no JSON files
    temp_dir = mm_file_tools.get_temp_dir()
    test_file = abspath(join(temp_dir, "File!.txt"))
    mm_file_tools.write_text_file(test_file, "Blah.")
    assert exists(test_file)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["title"] is None
    assert meta["description"] is None
    assert meta["date"] is None
    assert meta["writer"] is None
    assert meta["artist"] is None
    assert meta["cover_artist"] is None
    assert meta["publisher"] is None
    assert meta["url"] is None
