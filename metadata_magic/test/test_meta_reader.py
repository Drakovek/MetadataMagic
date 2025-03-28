#!/usr/bin/env python3

import metadata_magic.test as mm_test
import metadata_magic.config as mm_config
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.meta_reader as mm_meta_reader
from os.path import abspath, join

def test_get_value_from_keylist():
    """
    Tests the get_value_from_keylist function.
    """
    dictionary = {"key":"Value", "next":None, "thing":54, "other":True, "inner":{"last":"Tag"}}
    # Test getting value from the first key
    assert mm_meta_reader.get_value_from_keylist(dictionary, [["key"]], str) == "Value"
    assert mm_meta_reader.get_value_from_keylist(dictionary, [["other"], ["blah"]], bool) is True
    assert mm_meta_reader.get_value_from_keylist(dictionary, [["thing"], ["key"], ["other"]], int) == 54
    # Test getting value from secondary key
    assert mm_meta_reader.get_value_from_keylist(dictionary, [["nope"], ["thing"]], int) == 54
    assert mm_meta_reader.get_value_from_keylist(dictionary, [["next"], ["other"], ["blah"]], bool) == True
    # Test getting value from inner dictionary
    assert mm_meta_reader.get_value_from_keylist(dictionary, [["blah"], ["inner","last"]], str) == "Tag"
    # Test getting value when some are the wrong type
    assert mm_meta_reader.get_value_from_keylist(dictionary, [["key"], ["thing"]], int) == 54
    assert mm_meta_reader.get_value_from_keylist(dictionary, [["thing"], ["key"]], str) == "Value"
    assert mm_meta_reader.get_value_from_keylist(dictionary, [["inner"], ["key"]], str) == "Value"
    # Test getting value if no keys are valid
    assert mm_meta_reader.get_value_from_keylist(dictionary, ["nope"], str) is None
    assert mm_meta_reader.get_value_from_keylist(dictionary, ["nope", "not this either", ["or", "this"]], int) is None
    assert mm_meta_reader.get_value_from_keylist(None, ["nope"], str) is None

def test_get_string_from_metadata():
    """
    Tests the get_string_from_metadata function
    """
    # Test getting string with no formatting
    assert mm_meta_reader.get_string_from_metadata({"name":"thing"}, "Blah") == "Blah"
    # Test getting string with some metadata keys
    metadata = {"title":"This is a title", "artist":"Person", "thing":"Other"}
    assert mm_meta_reader.get_string_from_metadata(metadata, "{title}") == "This is a title"
    assert mm_meta_reader.get_string_from_metadata(metadata, "{thing}_{title}") == "Other_This is a title"
    assert mm_meta_reader.get_string_from_metadata(metadata, "[{thing}] ({artist})") == "[Other] (Person)"
    # Test getting string with non-existant keys
    assert mm_meta_reader.get_string_from_metadata(metadata, "{blah}") is None
    assert mm_meta_reader.get_string_from_metadata(metadata, "{other} {title}  ") is None
    assert mm_meta_reader.get_string_from_metadata(metadata, "{a}{b}{c}{thing}{e}{f}") is None
    # Test getting string with existing JSON data
    metadata = {"title":"Name", "original":{"number":5, "other":"Final"}}
    assert mm_meta_reader.get_string_from_metadata(metadata, "[{number}] {title}") == "[5] Name"
    assert mm_meta_reader.get_string_from_metadata(metadata, "{title} - {other}") == "Name - Final"
    # Test padding number
    metadata = {"title":"Name", "other":25, "original":{"number":5, "other":"Final"}}
    assert mm_meta_reader.get_string_from_metadata(metadata, "[{number!p3}] {title}") == "[005] Name"
    assert mm_meta_reader.get_string_from_metadata(metadata, "{other!p5} {number!p02}") == "00025 05"
    assert mm_meta_reader.get_string_from_metadata(metadata, "{title!p5}") == "0Name"
    # Test that improper modifiers do nothing
    assert mm_meta_reader.get_string_from_metadata(metadata, "{title!pblah}") == "Name"
    assert mm_meta_reader.get_string_from_metadata(metadata, "{title!nothing}") == "Name"
    # Test getting string with empty keys
    metadata["id"] = None
    assert mm_meta_reader.get_string_from_metadata(metadata, "{id}") is None
    assert mm_meta_reader.get_string_from_metadata(metadata, "{id} Thing") is None

def test_load_metadata():
    """
    Tests the load_metadata function.
    """
    # Get JSON file to load
    config = mm_config.get_config([])
    json_directory = abspath(join(mm_test.PAIR_DIRECTORY, "images"))
    json_file = abspath(join(json_directory, "bare.PNG.json"))
    # Check the loaded contents of the JSON file
    metadata = mm_meta_reader.load_metadata(json_file, config, "bare.png")
    assert metadata["json_path"] == json_file
    assert metadata["id"] is None
    assert metadata["title"] == "Émpty"
    assert metadata["num"] is None
    assert metadata["date"] is None
    assert metadata["description"] is None
    assert metadata["publisher"] is None
    assert metadata["tags"] is None
    assert metadata["url"] is None
    assert metadata["age_rating"] == "Unknown"
    assert metadata["artists"] is None
    assert metadata["writers"] is None
    assert metadata["original"] == mm_file_tools.read_json_file(json_file)
    # Test loading an invalid JSON file
    metadata = mm_meta_reader.load_metadata("/non/existant/file.json", config, "A")
    assert metadata["json_path"] == "/non/existant/file.json"
    assert metadata["id"] is None
    assert metadata["title"] is None
    assert metadata["num"] is None
    assert metadata["date"] is None
    assert metadata["description"] is None
    assert metadata["publisher"] is None
    assert metadata["tags"] is None
    assert metadata["url"] is None
    assert metadata["age_rating"] == "Unknown"
    assert metadata["artists"] is None
    assert metadata["writers"] is None
    assert metadata["original"] == {}

def test_get_title():
    """
    Tests the get_title function.
    """
    # Test getting title with the default config
    config = mm_config.get_config([])
    metadata = {"title":"Name", "info":{"title":"Different"}}
    assert mm_meta_reader.get_title(metadata, config) == "Name"
    metadata = {"other":"string", "info":{"title":"Different"}}
    assert mm_meta_reader.get_title(metadata, config) == "Different"
    # Test if there is no title in the metadata
    assert mm_meta_reader.get_title({"A":"B"}, config) is None
    # Test getting title when loading metadata
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "a.txt")
    assert metadata["title"] == "Pair #1"
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair-2.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "a.jpg")
    assert metadata["title"] == "JPEG Image"

def test_get_num():
    """
    Tests the get_num function.
    """
    # Test getting the index when it is a string
    config = mm_config.get_config([])
    metadata = {"title":"Name", "num":"12"}
    assert mm_meta_reader.get_num(metadata, config) == "12"
    metadata = {"title":"Name", "image_number":"123"}
    assert mm_meta_reader.get_num(metadata, config) == "123"
    # Test getting the index when it is an integer
    metadata = {"title":"Name", "image_num":5}
    assert mm_meta_reader.get_num(metadata, config) == "5"
    metadata = {"title":"Name", "part":42}
    assert mm_meta_reader.get_num(metadata, config) == "42"
    # Test getting the index when no valid index is present
    assert mm_meta_reader.get_num({"A":"B"}, config) is None
    assert mm_meta_reader.get_num({"num":None}, config) is None
    # Test getting index when loading metadata
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["num"] == "3"
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair-2.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["num"] == "32"

def test_get_artists_and_writers():
    """
    Tests the get_artists_and_writers function.
    """
    # Test getting separate single artist and writer
    config = mm_config.get_config([])
    metadata = {"title":"AAA", "artist":"Illustrator", "writer":"Author"}
    artists, writers = mm_meta_reader.get_artists_and_writers(metadata, config, ".jpg")
    assert artists == ["Illustrator"]
    assert writers == ["Author"]
    # Test getting multiple artists and writers
    metadata = {"title":"B", "artists":["A","B"], "writers":["1","2","3"]}
    artists, writers = mm_meta_reader.get_artists_and_writers(metadata, config, ".txt")
    assert artists == ["A", "B"]
    assert writers == ["1", "2", "3"]
    # Test that writers are the same as artists if only artist tags are present
    metadata = {"author":{"username":"Artist"}, "title":"AAA"}
    artists, writers = mm_meta_reader.get_artists_and_writers(metadata, config, ".jpg")
    assert artists == ["Artist"]
    assert writers == ["Artist"]
    metadata = {"user":["Multiple", "Artists"], "title":"AAA"}
    artists, writers = mm_meta_reader.get_artists_and_writers(metadata, config, ".jpg")
    assert artists == ["Multiple", "Artists"]
    assert writers == ["Multiple", "Artists"]
    # Test that artists are the same as artists if not a written work
    metadata = {"author":"Writer", "title":"AAA"}
    artists, writers = mm_meta_reader.get_artists_and_writers(metadata, config, ".jpg")
    assert artists == ["Writer"]
    assert writers == ["Writer"]
    metadata = {"writer":["Multiple", "Writers"], "title":"AAA"}
    artists, writers = mm_meta_reader.get_artists_and_writers(metadata, config, ".jpg")
    assert artists == ["Multiple", "Writers"]
    assert writers == ["Multiple", "Writers"]
    # Test that only writers are included for written works if no illustrator is provided
    metadata = {"writer":"Not Artist", "title":"AAA"}
    artists, writers = mm_meta_reader.get_artists_and_writers(metadata, config, ".html")
    assert artists is None
    assert writers == ["Not Artist"]
    metadata = {"artists":["Multiple", "Authors"], "title":"AAA"}
    artists, writers = mm_meta_reader.get_artists_and_writers(metadata, config, ".txt")
    assert artists is None
    assert writers == ["Multiple", "Authors"]
    # Test if there are no valid artists or authors in the metadata
    metadata = {"A": "B"}
    artists, writers = mm_meta_reader.get_artists_and_writers(metadata, config, ".png")
    assert artists is None
    assert writers is None
    # Test getting artists and writers when loading metadata
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "a.txt")
    assert metadata["artists"] is None
    assert metadata["writers"] == ["Different", "People"]
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair-2.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "a.jpg")
    assert metadata["artists"] == ["Creator"]
    assert metadata["writers"] == ["Creator"]

def test_get_date():
    """
    Tests the get_date function.
    """
    # Test getting date from dictionary in YYYY-MM-DD format
    config = mm_config.get_config([])
    metadata = {"title":"AAA", "date":"2022-12-25"}
    assert mm_meta_reader.get_date(metadata, config) == "2022-12-25"
    metadata = {"upload_date":"1983/07-14", "title":"AAA"}
    assert mm_meta_reader.get_date(metadata, config) == "1983-07-14"
    metadata = {"published_at":"2019-05-01T00:31:00.000+00:00"}
    assert mm_meta_reader.get_date(metadata, config) == "2019-05-01"
    metadata = {"info":{"time":"2012/12/21|22:33"}, "artist":"BBB"}
    assert mm_meta_reader.get_date(metadata, config) == "2012-12-21"
    # Test getting date from metadata in YYYYMMDD format
    metadata = {"date":"19990723", "title":"AAA"}
    assert mm_meta_reader.get_date(metadata, config) == "1999-07-23"
    metadata = {"title":"B", "upload_date":"20041115"}
    assert mm_meta_reader.get_date(metadata, config) == "2004-11-15"
    metadata = {"info":{"time":"20121221", "title":"BBB"}}
    assert mm_meta_reader.get_date(metadata, config) == "2012-12-21"
    # Test if there is no valid date in the metadata
    metadata = {"date":"2012-02-35"}
    assert mm_meta_reader.get_date(metadata, config) is None
    metadata = {"upload_date":"AAA"}
    assert mm_meta_reader.get_date(metadata, config) is None
    metadata = {"title":"AAA"}
    assert mm_meta_reader.get_date(metadata, config) is None
    # Test getting date from when loading metadata
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["date"] == "2024-07-01"
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair-2.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["date"] == "1997-11-28"

def test_get_description():
    """
    Tests the get_description function.
    """
    # Test getting description from metadata with default config
    config = mm_config.get_config([])
    metadata = {"title":"AAA", "description":"A<br/>B"}
    assert mm_meta_reader.get_description(metadata, config) == "A<br/>B"
    metadata = {"caption":"Description", "title":"BBB"}
    assert mm_meta_reader.get_description(metadata, config) == "Description"
    metadata = {"Artist":"AAA", "content":"Text"}
    assert mm_meta_reader.get_description(metadata, config) == "Text"
    metadata = {"title":"AAA", "info":{"description":"Internal"}}
    assert mm_meta_reader.get_description(metadata, config) == "Internal"
    # Test getting description if there is no valid description
    assert mm_meta_reader.get_description({"A":"B"}, config) is None
    # Test getting description when loading metadata
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["description"] == "<div>Text Description</div>"
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair-2.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["description"] == ".DVK Style"

def test_get_id():
    """
    Tests the get_id function.
    """
    # Test getting an ID that is a string
    config = mm_config.get_config([])
    metadata = {"title":"AAA", "id":"abc123"}
    assert mm_meta_reader.get_id(metadata, config) == "abc123"
    metadata = {"title":"AAA", "index":"Identifier"}
    assert mm_meta_reader.get_id(metadata, config) == "Identifier"
    # Test getting an ID that is an integer
    metadata = {"artist":"AAA", "submission_id":12345}
    assert mm_meta_reader.get_id(metadata, config) == "12345"
    metadata = {"title":"AAA", "display_id":246}
    assert mm_meta_reader.get_id(metadata, config) == "246"
    # Test getting an ID in the old .DVK format
    metadata = {"title":"AAA", "id":"DVA1234"}
    assert mm_meta_reader.get_id(metadata, config) == "1234"
    metadata = {"title":"AAA", "id":"FAF0123"}
    assert mm_meta_reader.get_id(metadata, config) == "0123"
    metadata = {"title":"AAA", "id":"NEW-246"}
    assert mm_meta_reader.get_id(metadata, config) == "246"
    metadata = {"title":"AAA", "id":"new123"}
    assert mm_meta_reader.get_id(metadata, config) == "new123"
    metadata = {"title":"AAA", "id":"DVNT987"}
    assert mm_meta_reader.get_id(metadata, config) == "DVNT987"
    metadata = {"title":"AAA", "id":"FAF123Q"}
    assert mm_meta_reader.get_id(metadata, config) == "FAF123Q"
    # Test if there is no valid ID
    assert mm_meta_reader.get_id({"A", "B"}, config) is None
    # Test getting ID when loading metadata
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["id"] == "702725"
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair-2.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["id"] == "2468"

def test_get_publisher():
    """
    Tests the get_publisher function.
    """
    # Test getting DeviantArt as publisher
    config = mm_config.get_config([])
    metadata = {"url":"www.deviantart.com/AAA", "title":"AAA"}
    assert mm_meta_reader.get_publisher(metadata, config) == "DeviantArt"
    metadata = {"category":"DeviantArt", "url":False}
    assert mm_meta_reader.get_publisher(metadata, config) == "DeviantArt"
    # Test getting FurAffinity as publisher
    metadata = {"webpage_url":"www.furaffinity.net/art/AAA", "artist":"AAA"}
    assert mm_meta_reader.get_publisher(metadata, config) == "Fur Affinity"
    metadata = {"category":"FurAffinity", "title":"AAA"}
    assert mm_meta_reader.get_publisher(metadata, config) == "Fur Affinity"
    # Test getting Newgrounds as publisher
    metadata = {"title":"BBB", "post_url":"www.newgrounds.com/art/AAA"}
    assert mm_meta_reader.get_publisher(metadata, config) == "Newgrounds"
    dictionary = {"artist":"BBB", "category":"newgrounds"}
    assert mm_meta_reader.get_publisher(metadata, config) == "Newgrounds"
    #Test if there is no viable publisher
    assert mm_meta_reader.get_publisher({"post_url", "AAA"}, config) is None
    assert mm_meta_reader.get_publisher({"AAA":"BBB"}, config) is None
    # Test getting publisher when loading metadata
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["publisher"] == "DVK Test"
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair-2.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["publisher"] == "DVK Test"

def test_get_url():
    """
    Tests the get_url function.
    """
    # Test getting the URL from only the metadata
    config = mm_config.get_config([])
    metadata = {"url":"/url/", "title":"AAA"}
    assert mm_meta_reader.get_url(metadata, config) == "/url/"
    metadata = {"post_url":"page/url/", "title":"AAA"}
    assert mm_meta_reader.get_url(metadata, config) == "page/url/" 
    # Test getting Fur Affinity URL based on publisher and ID from config
    url = mm_meta_reader.get_url({"id":"ID123"}, config, "Fur Affinity")
    assert url == "https://www.furaffinity.net/view/ID123"
    url = mm_meta_reader.get_url({"id":"Other"}, config, "Fur Affinity")
    assert url == "https://www.furaffinity.net/view/Other"
    # Test getting pixiv URL
    url = mm_meta_reader.get_url({"id":"ID123"}, config, "Pixiv")
    assert url == "https://www.pixiv.net/en/artworks/ID123"
    url = mm_meta_reader.get_url({"id":"Other"}, config, "Pixiv")
    assert url == "https://www.pixiv.net/en/artworks/Other"
    # Test getting Bluesky URL
    url = mm_meta_reader.get_url({"artists":["person.net"], "id":"abcd"}, config, "Bluesky")
    assert url == "https://bsky.app/profile/person.net/post/abcd"
    # Test getting Twitter URL
    url = mm_meta_reader.get_url({"artists":["person.net"], "id":"abcd"}, config, "Twitter")
    assert url == "https://twitter.com/person.net/status/abcd"
    # Test if the publisher or ID are invalid
    assert mm_meta_reader.get_url({}, config, "NonExistant") is None
    assert mm_meta_reader.get_url({}, config, None) is None
    assert mm_meta_reader.get_url({}, config, "Fur Affinity") is None
    # Test if there is no url or publisher info
    assert mm_meta_reader.get_url({}, config) is None
    # Test getting URL when loading metadata
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["url"] == "https://www.non-existant-website.ca/no/page/"
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair-2.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["url"] == "https://www.non-existant-website.ca/no/page/2"

def test_get_tags():
    """
    Tests the get_tags function.
    """
    # Test getting tags from multiple lists of tags
    config = mm_config.get_config([])
    metadata = {"title":"123", "tags":["A", "B"], "categories":["C", "D"]}
    assert mm_meta_reader.get_tags(metadata, config) == ["A", "B", "C", "D"]
    # Test getting tags from multiple single string entries in the metadata
    metadata = {"artist":"AAA", "theme":"Art", "species":"Cat"}
    assert mm_meta_reader.get_tags(metadata, config) == ["Art", "Cat"]
    # Test getting tags that are nested
    metadata = {"title":"AAA", "tags":[{"name":"Tag1"}, {"name":"Tag2"}]}
    assert mm_meta_reader.get_tags(metadata, config) == ["Tag1", "Tag2"]
    metadata = {"title":"AAA", "tags":[{"name":"BBB", "translated_name":"Single"}]}
    assert mm_meta_reader.get_tags(metadata, config) == ["Single"]
    # Test getting tags from list and string sources
    metadata = {"title":"AAA", "tags":["1", "2", "3"], "theme":"Single"}
    assert mm_meta_reader.get_tags(metadata, config) == ["1", "2", "3", "Single"]
    # Test if there are no valid tags
    assert mm_meta_reader.get_tags({"tags":[]}, config) is None
    assert mm_meta_reader.get_tags({"tags":None}, config) is None
    assert mm_meta_reader.get_tags({"tags":123}, config) is None
    assert mm_meta_reader.get_tags({"A", "B"}, config) is None
    # Test getting tags when loading metadata
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["tags"] == ["Multiple", "Tags", "New"]
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair-2.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["tags"] == ["Internal", "Tags"]

def test_get_age_rating():
    """
    Tests the get_age_rating function.
    """
    # Test getting general style age ratings from Fur Affinity
    config = mm_config.get_config([])
    metadata = {"title":"AAA", "rating":"General"}
    assert mm_meta_reader.get_age_rating(metadata, config, "Fur Affinity") == "Everyone"
    metadata = {"title":"AAA", "rating":"Mature"}
    assert mm_meta_reader.get_age_rating(metadata, config, "Fur Affinity") == "Mature 17+"
    metadata = {"title":"AAA", "rating":"Adult"}
    assert mm_meta_reader.get_age_rating(metadata, config, "Fur Affinity") == "X18+"
    metadata = {"title":"AAA", "rating":"???"}
    assert mm_meta_reader.get_age_rating(metadata, config, "Fur Affinity") == "Unknown"
    # Test getting general style age ratings from Fur Affinity
    metadata = {"title":"AAA", "rating":"e"}
    assert mm_meta_reader.get_age_rating(metadata, config, "Newgrounds") == "Everyone"
    metadata = {"title":"AAA", "rating":"T"}
    assert mm_meta_reader.get_age_rating(metadata, config, "Newgrounds") == "Teen"
    metadata = {"title":"AAA", "rating":"m"}
    assert mm_meta_reader.get_age_rating(metadata, config, "Newgrounds") == "Mature 17+"
    metadata = {"title":"AAA", "rating":"A"}
    assert mm_meta_reader.get_age_rating(metadata, config, "Newgrounds") == "X18+"
    metadata = {"title":"AAA", "rating":"f"}
    assert mm_meta_reader.get_age_rating(metadata, config, "Newgrounds") == "Unknown"
    # Test getting specialized age ratings from Deviantart
    metadata = {"title":"AAA", "is_mature":"False"}
    assert mm_meta_reader.get_age_rating(metadata, config, "DeviantArt") == "Everyone"
    metadata = {"title":"AAA", "is_mature":"True", "mature_level":"moderate"}
    assert mm_meta_reader.get_age_rating(metadata, config, "DeviantArt") == "Mature 17+"
    metadata = {"title":"AAA", "is_mature":"True", "mature_level":"strict"}
    assert mm_meta_reader.get_age_rating(metadata, config, "DeviantArt") == "X18+"
    metadata = {"title":"AAA", "is_mature":"True", "mature_level":"???"}
    assert mm_meta_reader.get_age_rating(metadata, config, "DeviantArt") == "Unknown"
    metadata = {"title":"AAA", "is_mature":"Unknown"}
    assert mm_meta_reader.get_age_rating(metadata, config, "DeviantArt") == "Unknown"
    metadata = {"A":"B"}
    assert mm_meta_reader.get_age_rating(metadata, config, "DeviantArt") == "Unknown"
    # Test getting age rating for a Publisher not in the config file
    metadata = {"title":"AAA", "rating":"General"}
    assert mm_meta_reader.get_age_rating(metadata, config, "Unknown") == "Unknown"
    metadata = {"title":"AAA", "rating":"mature"}
    assert mm_meta_reader.get_age_rating(metadata, config, "Publisher") == "Unknown"
    metadata = {"title":"AAA", "rating":"adult"}
    assert mm_meta_reader.get_age_rating(metadata, config, None) == "Unknown"
    # Test getting age rating when loading metadata
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["age_rating"] == "Teen"
    json_file = abspath(join(mm_test.PAIR_DIRECTORY, "pair-2.json"))
    metadata = mm_meta_reader.load_metadata(json_file, config, "A.txt")
    assert metadata["age_rating"] == "Unknown"
