#!/usr/bin/env python3

import os
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.epub as mm_epub
import metadata_magic.archive.comic_archive as mm_comic_archive
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
    # Test getting epub from folder with html files
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "thing.html")), "AAA")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "image.jpg")), "AAA")
    assert mm_archive.get_directory_archive_type(temp_dir) == "epub"
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "web.htm")), "AAA")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "image.jpeg")), "AAA")
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
    assert meta["writers"] is None
    assert meta["artists"] is None
    assert meta["cover_artists"] is None
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
    main_media = abspath(join(temp_dir, "json.jpg"))
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
    assert meta["artists"] is None
    assert meta["description"] is None
    # Test getting description
    json_meta["description"] = "Some caption."
    mm_file_tools.write_json_file(main_json, json_meta)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["description"] == "Some caption."
    assert meta["date"] is None
    assert meta["cover_artists"] is None
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
    assert meta["cover_artists"] is None
    # Test getting artist data
    json_meta["artists"] = ["Illustrator!"]
    json_meta["writers"] = ["Story", "People"]
    mm_file_tools.write_json_file(main_json, json_meta)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["writers"] == "Story,People"
    assert meta["cover_artists"] == "Illustrator!"
    assert meta["artists"] == "Illustrator!"
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
    assert meta["writers"] is None
    assert meta["artists"] is None
    assert meta["cover_artists"] is None
    assert meta["publisher"] is None
    assert meta["url"] is None
    # Test that only the writer field is credited to the artist if it is a text file
    temp_dir = mm_file_tools.get_temp_dir()
    main_media = abspath(join(temp_dir, "json.txt"))
    main_json = abspath(join(temp_dir, "json.json"))
    json_meta = {"title":"This is a title!", "author":"Some Person"}
    mm_file_tools.write_text_file(main_media, "This is text")
    mm_file_tools.write_json_file(main_json, json_meta)
    assert exists(main_media)
    assert exists(main_json)
    meta = mm_archive.get_info_from_jsons(temp_dir)
    assert meta["title"] == "This is a title!"
    assert meta["writers"] == "Some Person"
    assert meta["artists"] is None
    assert meta["cover_artists"] is None

def test_get_info_from_archive():
    """
    Tests the get_info_from_archive function.
    """
    # Test getting info from a CBZ file
    temp_dir = mm_file_tools.get_temp_dir()
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "CBZ Title!"
    metadata["tags"] = "Some,Tags"
    text_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "Text")
    assert exists(text_file)
    cbz_file = mm_comic_archive.create_cbz(temp_dir, metadata=metadata)
    assert exists(cbz_file)
    read_meta = mm_archive.get_info_from_archive(cbz_file)
    assert read_meta["title"] == "CBZ Title!"
    assert read_meta["tags"] == "Some,Tags"
    # Test getting info from an EPUB file
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "Here's some text!")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.txt")), "And")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.pdf")), "Stuff")
    chapters = mm_epub.get_default_chapters(temp_dir)
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "This is an epub!!"
    metadata["artists"] = "Art Person"
    metadata["description"] = "Some Words"
    epub_file = mm_epub.create_epub(chapters, metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_archive.get_info_from_archive(epub_file)
    assert read_meta["title"] == "This is an epub!!"
    assert read_meta["artists"] == "Art Person"
    assert read_meta["description"] == "Some Words"
    # Test getting info from an invalid file
    temp_dir = mm_file_tools.get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    assert mm_archive.get_info_from_archive(text_file) == mm_archive.get_empty_metadata()

def test_update_archive_info():
    """
    Test the update_archive_info function.
    """
    # Test updating a CBZ file
    temp_dir = mm_file_tools.get_temp_dir()
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "CBZ Title!"
    metadata["tags"] = "Some,Tags"
    text_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "Text")
    assert exists(text_file)
    cbz_file = mm_comic_archive.create_cbz(temp_dir, metadata=metadata)
    assert exists(cbz_file)
    read_meta = mm_archive.get_info_from_archive(cbz_file)
    assert read_meta["title"] == "CBZ Title!"
    assert read_meta["tags"] == "Some,Tags"
    assert read_meta["description"] is None
    metadata["title"] = "New!"
    metadata["description"] = "New Words..."
    mm_archive.update_archive_info(cbz_file, metadata)
    read_meta = mm_archive.get_info_from_archive(cbz_file)
    assert read_meta["title"] == "New!"
    assert read_meta["tags"] == "Some,Tags"
    assert read_meta["description"] == "New Words..."
    extract_dir = abspath(join(temp_dir, "extracted"))
    os.mkdir(extract_dir)
    mm_file_tools.extract_zip(cbz_file, extract_dir)
    assert sorted(os.listdir(extract_dir)) == ["CBZ Title!", "ComicInfo.xml"]
    # Test updating an EPUB file
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "1.txt")), "Here's some text!")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "2.txt")), "And")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "3.pdf")), "Stuff")
    chapters = mm_epub.get_default_chapters(temp_dir)
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "This is an epub!!"
    metadata["artists"] = "Art Person"
    metadata["description"] = "Some Words"
    chapters = mm_epub.add_cover_to_chapters(chapters, metadata)
    epub_file = mm_epub.create_epub(chapters, metadata, temp_dir)
    assert exists(epub_file)
    read_meta = mm_archive.get_info_from_archive(epub_file)
    assert read_meta["title"] == "This is an epub!!"
    assert read_meta["artists"] == "Art Person"
    assert read_meta["description"] == "Some Words"
    assert read_meta["writers"] is None
    metadata["cover_id"] = None
    metadata["title"] = "Different Title"
    metadata["writers"] = "Author"
    mm_archive.update_archive_info(epub_file, metadata)
    read_meta = mm_archive.get_info_from_archive(epub_file)
    assert read_meta["title"] == "Different Title"
    assert read_meta["artists"] == "Art Person"
    assert read_meta["description"] == "Some Words"
    assert read_meta["writers"] == "Author"
    extract_dir = abspath(join(temp_dir, "extracted"))
    os.mkdir(extract_dir)
    mm_file_tools.extract_zip(epub_file, extract_dir)
    assert sorted(os.listdir(extract_dir)) == ["EPUB", "META-INF", 'mimetype']
    # Test updating cover image
    epub_size = os.stat(epub_file).st_size
    mm_archive.update_archive_info(epub_file, metadata, update_cover=False)
    assert os.stat(epub_file).st_size == epub_size
    cover_updated = False
    for i in range(0, 20):
        mm_archive.update_archive_info(epub_file, metadata, update_cover=True)
        if not os.stat(epub_file).st_size == epub_size:
            cover_updated = True
            break
    assert cover_updated    
    # Test updating a non-archive file
    temp_dir = mm_file_tools.get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "This is text!")
    mm_archive.update_archive_info(text_file, metadata)
    assert mm_file_tools.read_text_file(text_file) == "This is text!"
    zip_file = abspath(join(temp_dir, "not_epub.zip"))
    mm_file_tools.create_zip(temp_dir, zip_file)
    mm_archive.update_archive_info(zip_file, metadata)
    extract_dir = abspath(join(temp_dir, "extract"))
    os.mkdir(extract_dir)
    assert mm_file_tools.extract_zip(zip_file, extract_dir)
    assert sorted(os.listdir(extract_dir)) == ["text.txt"]
    assert mm_file_tools.read_text_file(abspath(join(extract_dir, "text.txt"))) == "This is text!"

def test_format_title():
    """
    Tests the format_title function
    """
    # Test Removing a standalone number
    assert mm_archive.format_title("Test 123") == "Test"
    assert mm_archive.format_title("1 Number 01 ") == "1 Number"
    assert mm_archive.format_title("New Thing15") == "New Thing"
    assert mm_archive.format_title("1. A Thing") == "1. a Thing"
    assert mm_archive.format_title("12 13 B 14 C") == "12 13 B 14 C"
    assert mm_archive.format_title("Thing - 05") == "Thing"
    assert mm_archive.format_title("New - #05 ") == "New"
    # Test Removing number with total
    assert mm_archive.format_title("Something 1/2") == "Something"
    assert mm_archive.format_title("Other Name  17/43  ") == "Other Name"
    assert mm_archive.format_title("Another 1 / 2") == "Another"
    assert mm_archive.format_title("Text 1-0") == "Text"
    assert mm_archive.format_title("Title 12 - 43") == "Title"
    assert mm_archive.format_title("1/2 Name") == "1/2 Name"
    assert mm_archive.format_title("Two 1 / 2 Name") == "Two 1 / 2 Name"
    assert mm_archive.format_title("3-4 Thing") == "3-4 Thing"
    assert mm_archive.format_title("Title 1 of 3") == "Title"
    assert mm_archive.format_title("Name 4OF7") == "Name"
    # Test Removing number with number symbol
    assert mm_archive.format_title("4 Test #123") == "4 Test"
    assert mm_archive.format_title("Thing #1/2 ") == "Thing"
    assert mm_archive.format_title("Another # 16  ") == "Another"
    assert mm_archive.format_title("#1 Fan") == "#1 Fan"
    assert mm_archive.format_title("#1 #2 #3 Thing") == "#1 #2 #3 Thing"
    # Test Removing number with "page" or "part"
    assert mm_archive.format_title("Test Part 1") == "Test"
    assert mm_archive.format_title("Thing page2") == "Thing"
    assert mm_archive.format_title("Other P. 1/2 ") == "Other"
    assert mm_archive.format_title("Name Pg. 4 ") == "Name"
    assert mm_archive.format_title("Passof Page2-3") == "Passof"
    assert mm_archive.format_title("Test part1") == "Test"
    assert mm_archive.format_title("Thing Page 25") == "Thing"
    assert mm_archive.format_title("Other p.12 ") == "Other"
    assert mm_archive.format_title("Part 1 of 5 ") == "Part 1 of 5 "
    assert mm_archive.format_title("Some Pages 5") == "Some Pages"
    assert mm_archive.format_title("New Thing Pt. 23") == "New Thing"
    assert mm_archive.format_title("p.3 Something") == "P.3 Something"
    assert mm_archive.format_title("stoppage 5") == "Stoppage"
    assert mm_archive.format_title("rampart 10") == "Rampart"
    assert mm_archive.format_title("Tempt 12") == "Tempt"
    assert mm_archive.format_title("Stop. 5") == "Stop."
    assert mm_archive.format_title("Thing - Part 5") == "Thing"
    # Test Removing number with brackets or parenthesis
    assert mm_archive.format_title("Test[01]") == "Test"
    assert mm_archive.format_title("Name [Part 1/3] ") == "Name"
    assert mm_archive.format_title("Something [P. 4-5] ") == "Something"
    assert mm_archive.format_title("Thing [ #06 ]") == "Thing"
    assert mm_archive.format_title("Test(01)") == "Test"
    assert mm_archive.format_title("Name (page 3/6 ) ") == "Name"
    assert mm_archive.format_title("Another (page 4-6) ") == "Another"
    assert mm_archive.format_title("Thing ( #09 )") == "Thing"
    assert mm_archive.format_title("Next (page 1)") == "Next"
    assert mm_archive.format_title("Other (p. 1)") == "Other"
    assert mm_archive.format_title("(01) Thing") == "(01) Thing"
    assert mm_archive.format_title("Test (Not Num)") == "Test (Not Num)"
    assert mm_archive.format_title("Other [1] Thing") == "Other [1] Thing"
    assert mm_archive.format_title("Other (1") == "Other ("
    assert mm_archive.format_title("Other 12)") == "Other 12)"
    assert mm_archive.format_title("Thing [12)") == "Thing [12)"
    assert mm_archive.format_title("Thing [1") == "Thing ["
    assert mm_archive.format_title("Final 23]") == "Final 23]"
    # Test Removing starting brackets and capitalizing titles
    assert mm_archive.format_title("[Blah] some title ") == "Some Title"
    assert mm_archive.format_title("[2020-01-01] title of   thing part 2") == "Title of Thing"
    assert mm_archive.format_title("[A] of something for something") == "Of Something for Something"
    assert mm_archive.format_title("[B] part Of A title") == "Part of a Title"
    assert mm_archive.format_title("[B] part Of An object") == "Part of an Object"
    assert mm_archive.format_title("[ABC] This's A thing's") == "This's a Thing's"
    assert mm_archive.format_title("[ABC] this to that") == "This to That"
    assert mm_archive.format_title("[ABC] this And that") == "This and That"
    assert mm_archive.format_title("[ABC] thing the title") == "Thing the Title"
    assert mm_archive.format_title("[ABC] SOMETHING") == "SOMETHING"
    # Test Removing number with all options
    assert mm_archive.format_title("A Picture [Page #15/30]") == "A Picture"
    assert mm_archive.format_title("Something Else ( Part #1 / 2 ) ") == "Something Else"
    # Test that the original text is returned if there is nothing left
    assert mm_archive.format_title("34") == "34"
    assert mm_archive.format_title(" [1/5] ") == " [1/5] "
    # Test returning None if text is None
    assert mm_archive.format_title(None) is None

def test_get_cover_image():
    """
    Tests the get_cover_image function.
    """
    image = mm_archive.get_cover_image("This is something different", "Drakovek, Other Person")
    assert image.size == (900, 1200)
    image = mm_archive.get_cover_image("This is a title", None, portrait=False)
    assert image.size == (1200, 900)
