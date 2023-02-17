#!/usr/bin/env python3

from metadata_magic.main.comic_archive.comic_archive import get_temp_dir
from metadata_magic.main.meta_reader import get_artist
from metadata_magic.main.meta_reader import get_date
from metadata_magic.main.meta_reader import get_description
from metadata_magic.main.meta_reader import get_id
from metadata_magic.main.meta_reader import get_publisher
from metadata_magic.main.meta_reader import get_tags
from metadata_magic.main.meta_reader import get_title
from metadata_magic.main.meta_reader import get_url
from metadata_magic.main.meta_reader import get_value_from_keylist
from metadata_magic.main.meta_reader import get_age_rating
from metadata_magic.main.meta_reader import load_metadata
from metadata_magic.test.temp_file_tools import create_json_file
from os.path import abspath, exists, join

def test_get_value_from_keylist():
    """
    Tests the get_value_from_keylist function.
    """
    dictionary = {"key":"Value", "next":None, "thing":54, "other":True, "inner":{"last":"Tag"}}
    # Test getting value from the first key
    assert get_value_from_keylist(dictionary, [["key"]], str) == "Value"
    assert get_value_from_keylist(dictionary, [["other"], ["blah"]], bool) is True
    assert get_value_from_keylist(dictionary, [["thing"], ["key"], ["other"]], int) == 54
    # Test getting value from secondary key
    assert get_value_from_keylist(dictionary, [["nope"], ["thing"]], int) == 54
    assert get_value_from_keylist(dictionary, [["next"], ["other"], ["blah"]], bool) == True
    # Test getting value from inner dictionary
    assert get_value_from_keylist(dictionary, [["blah"], ["inner","last"]], str) == "Tag"
    # Test getting value when some are the wrong type
    assert get_value_from_keylist(dictionary, [["key"], ["thing"]], int) == 54
    assert get_value_from_keylist(dictionary, [["thing"], ["key"]], str) == "Value"
    assert get_value_from_keylist(dictionary, [["inner"], ["key"]], str) == "Value"
    # Test getting value if no keys are valid
    assert get_value_from_keylist(dictionary, ["nope"], str) is None
    assert get_value_from_keylist(dictionary, ["nope", "not this either", ["or", "this"]], int) is None

def test_load_metadata():
    """
    Tests the load_metadata function.
    """
    # Create JSON to load
    temp_dir = get_temp_dir()
    test_json = abspath(join(temp_dir, "empty.json"))
    create_json_file(test_json, {"title":"test"})
    assert exists(test_json)
    # Attempt to load the JSON file
    meta = load_metadata(test_json)
    assert meta["json_path"] == test_json
    # Test loading from an invalid path
    meta = load_metadata("/not/real/directory/")
    assert not exists(meta["json_path"])
    assert meta["id"] is None
    assert meta["title"] is None
    assert meta["artist"] is None
    assert meta["writer"] is None
    assert meta["date"] is None
    assert meta["description"] is None
    assert meta["publisher"] is None
    assert meta["tags"] is None
    assert meta["url"] is None

def test_get_title():
    """
    Tests the get_title function.
    """
    # Test getting title from dictionary
    dictionary = {"thing":"blah", "inner":{"title":"Thing!"}, "title":"Bleh"}
    assert get_title(dictionary) == "Bleh"
    dictionary = {"info":{"title": "New Title", "artists":["thing"]}}
    assert get_title(dictionary) == "New Title"
    # Test if there is no title
    assert get_title({"no":"title"}) is None
    # Create JSON to load
    temp_dir = get_temp_dir()
    test_json = abspath(join(temp_dir, "title.json"))
    create_json_file(test_json, {"thing":"other", "title":"Loaded!"})
    assert exists(test_json)
    # Test getting title when read directly from JSON
    meta = load_metadata(test_json)
    assert meta["json_path"] == test_json
    assert meta["title"] == "Loaded!"

def test_get_artist():
    """
    Tests the get_artist function.
    """
    # Test getting artist from dictionary
    dictionary = {"thing":50, "artist":"Artist", "author":"other"}
    assert get_artist(dictionary) == "Artist"
    dictionary = {"uploader":"Person", "other":True, "innner":{"artist":"blah"}}
    assert get_artist(dictionary) == "Person"
    dictionary = {"thing":"Person", "user":"Third", "name":"blah"}
    assert get_artist(dictionary) == "Third"
    dictionary = {"author":"Person", "username":"another"}
    assert get_artist(dictionary) == "another"
    dictionary = {"thing":"blah", "author":{"username":"Yep"}, "person":"Next"}
    assert get_artist(dictionary) == "Yep"
    dictionary = {"user":{"name":"Cpt. Human"}, "artist":50, "owner":"thing"}
    assert get_artist(dictionary) == "Cpt. Human"
    dictionary = {"owner":"New", "type":"other"}
    assert get_artist(dictionary) == "New"
    dictionary = {"total":True, "creator":{"full_name":"Real Person"}}
    assert get_artist(dictionary) == "Real Person"
    assert get_artist(dictionary) == "Real Person"
    # Test getting artist from artist list in dictionary
    dictionary = {"artists":["New Person", "blah"], "type":"other"}
    assert get_artist(dictionary) == "New Person"
    dictionary = {"info":{"artists":["ArtLass"], "title":"blah"}, "next":"this"}
    assert get_artist(dictionary) == "ArtLass"
    # Test if there is no artist
    assert get_artist({"no":"artist"}) is None
    assert get_artist({"artists":[]}) is None
    # Create JSON to load
    temp_dir = get_temp_dir()
    test_json = abspath(join(temp_dir, "artists.json"))
    create_json_file(test_json, {"thing":"other", "uploader":"Name!!!"})
    assert exists(test_json)
    # Test getting artist when read directly from JSON
    meta = load_metadata(test_json)
    assert meta["json_path"] == test_json
    assert meta["artist"] == "Name!!!"
    assert meta["writer"] == "Name!!!"

def test_get_date():
    """
    Tests the get_date function.
    """
    # Test getting date from dictionary in YYYY-MM-DD format
    dictionary = {"thing":50, "date":"2022-12-25"}
    assert get_date(dictionary) == "2022-12-25"
    dictionary = {"upload_date":"1983/07-14", "other":False, "new":"Thing"}
    assert get_date(dictionary) == "1983-07-14"
    dictionary = {"published_at":"2019-05-01T00:31:00.000+00:00"}
    assert get_date(dictionary) == "2019-05-01"
    dictionary = {"info":{"time":"2012/12/21|22:33"}}
    assert get_date(dictionary) == "2012-12-21"
    # Test getting date from dictionary in YYYYMMDD format
    dictionary = {"date":"19990723", "next":24}
    assert get_date(dictionary) == "1999-07-23"
    dictionary = {"thing":"other", "upload_date":"20041115", "date":{"other":23}}
    assert get_date(dictionary) == "2004-11-15"
    dictionary = {"info":{"time":"20121221", "title":23}}
    assert get_date(dictionary) == "2012-12-21"
    # Test getting invalid date
    dictionary = {"date":"2012-02-35"}
    assert get_date(dictionary) is None
    dictionary = {"upload_date":"thing"}
    assert get_date(dictionary) is None
    dictionary = {"thing":"blah"}
    assert get_date(dictionary) is None
    # Create JSON to load
    temp_dir = get_temp_dir()
    test_json = abspath(join(temp_dir, "date.json"))
    create_json_file(test_json, {"thing":"other", "date":"20230513"})
    assert exists(test_json)
    # Test getting date when read directly from JSON
    meta = load_metadata(test_json)
    assert meta["json_path"] == test_json
    assert meta["date"] == "2023-05-13"

def test_get_description():
    """
    Tests the get_description function.
    """
    # Test getting description from dictionary
    dictionary = {"thing":"other", "description":"Some words.<br>Thing"}
    assert get_description(dictionary) == "Some words.<br>Thing"
    dictionary = {"description":{"inner":"thing"}, "caption":"New", "content":False}
    assert get_description(dictionary) == "New"
    dictionary = {"other":"Key", "content":"More text"}
    assert get_description(dictionary) == "More text"
    dictionary = {"thing":"other", "info":{"description":"New Text"}}
    assert get_description(dictionary) == "New Text"
    # Test if there is no description
    dictionary = {"no":"description"}
    assert get_description(dictionary) is None
    # Create JSON to load
    temp_dir = get_temp_dir()
    test_json = abspath(join(temp_dir, "description.json"))
    create_json_file(test_json, {"thing":"other", "description":"New<br><br>Description!"})
    assert exists(test_json)
    # Test getting decscription when read directly from JSON
    meta = load_metadata(test_json)
    assert meta["json_path"] == test_json
    assert meta["description"] == "New<br><br>Description!"

def test_get_id():
    """
    Tests the get_id function.
    """
    # Test getting string ID
    dictionary = {"test":"thing", "id":"abc123"}
    assert get_id(dictionary) == "abc123"
    dictionary = {"test":"thing", "display_id":"thing", "id":{"inner":"thing"}}
    assert get_id(dictionary) == "thing"
    dictionary = {"index":"New1"}
    assert get_id(dictionary) == "New1"
    dictionary = {"submission_id":"Final", "other":23}
    assert get_id(dictionary) == "Final"
    dictionary = {"submitid":"Other"}
    assert get_id(dictionary) == "Other"
    # Test getting int ID
    dictionary = {"test":"thing", "id":4254}
    assert get_id(dictionary) == "4254"
    dictionary = {"test":"thing", "display_id":3600, "id":{"inner":"thing"}}
    assert get_id(dictionary) == "3600"
    dictionary = {"index":3}
    assert get_id(dictionary) == "3"
    dictionary = {"submission_id":58403, "other":23}
    assert get_id(dictionary) == "58403"
    dictionary = {"submitid":483}
    assert get_id(dictionary) == "483"
    # Test getting old DVK ID format
    dictionary = {"id":"DVA48305"}
    assert get_id(dictionary) == "48305"
    dictionary = {"index":"FAF29045"}
    assert get_id(dictionary) == "29045"
    dictionary = {"display_id":"INK-1234"}
    assert get_id(dictionary) == "1234"
    dictionary = {"display_id":"ink123"}
    assert get_id(dictionary) == "ink123"
    dictionary = {"id":"DVAV225"}
    assert get_id(dictionary) == "DVAV225"
    # Test adding file id, if necessary
    dictionary = {"id":"INK135", "file_id":"987"}
    assert get_id(dictionary) == "135-987"
    dictionary = {"index":"4829", "thing":54, "file_id":"27606"}
    assert get_id(dictionary) == "4829-27606"
    # Test if there is no ID
    dictionary = {"no":"id"}
    assert get_id(dictionary) is None
    # Create JSON to load
    temp_dir = get_temp_dir()
    test_json = abspath(join(temp_dir, "id.json"))
    create_json_file(test_json, {"thing":"other", "id":"Blah"})
    assert exists(test_json)
    # Test getting ID when read directly from JSON
    meta = load_metadata(test_json)
    assert meta["json_path"] == test_json
    assert meta["id"] == "Blah"

def test_get_publisher():
    """
    Tests the get_publisher function.
    """
    # Test getting DeviantArt as publisher
    dictionary = {"url":"www.deviantart.com/person/art/thing20398462-183", "thing":"blah"}
    assert get_publisher(dictionary) == "DeviantArt"
    dictionary = {"category":"DeviantArt", "url":{"inner":"thing"}}
    assert get_publisher(dictionary) == "DeviantArt"
    # Test getting FurAffinity as publisher
    dictionary = {"a":"thing", "webpage_url":"www.furaffinity.net/art/091289023001290389012"}
    assert get_publisher(dictionary) == "Fur Affinity"
    dictionary = {"category":"FurAffinity", "some":292}
    assert get_publisher(dictionary) == "Fur Affinity"
    # Test getting Inkbunny as publisher
    dictionary = {"b":"thing", "post_url":"www.inkbunny.net/thing/", "a":"blah"}
    assert get_publisher(dictionary) == "Inkbunny"
    dictionary = {"this":"thing", "category":"inkbunny"}
    assert get_publisher(dictionary) == "Inkbunny"
    # Test getting Newgrounds as publisher
    dictionary = {"b":"thing", "post_url":"www.newgrounds.com/art/qojkadskljfd", "a":"blah"}
    assert get_publisher(dictionary) == "Newgrounds"
    dictionary = {"this":"thing", "category":"newgrounds", "id":"other"}
    assert get_publisher(dictionary) == "Newgrounds"
    # Test getting Patreon as publisher
    dictionary = {"thing":"Blah", "web":{"page_url":"www.patreon.com/test/url"}}
    assert get_publisher(dictionary) == "Patreon"
    dictionary = {"category":"patreon"}
    assert get_publisher(dictionary) == "Patreon"
    # Test getting pixiv as publisher
    dictionary = {"b":"blah", "url":"www.pixiv.net/thing", "2":2}
    assert get_publisher(dictionary) == "pixiv"
    dictionary = {"category":"pixiv"}
    assert get_publisher(dictionary) == "pixiv"
    # Test getting Weasyl as publisher
    dictionary = {"link":"www.weasyl.com", "url":"not-deviantart", "a":"blah"}
    assert get_publisher(dictionary) == "Weasyl"
    dictionary = {"category":"WEASYL", "other":True}
    assert get_publisher(dictionary) == "Weasyl"
    # Test getting YouTube as publisher
    dictionary = {"webpage_url":"www.youtube.com/thing/other", "a":"blah"}
    assert get_publisher(dictionary) == "YouTube"
    dictionary = {"this":"thing", "category":"YouTube"}
    assert get_publisher(dictionary) == "YouTube"
    # Test if there is no viable publisher
    dictionary = {"url":"none"}
    assert get_publisher(dictionary) is None
    dictionary = {"no":"URLS"}
    assert get_publisher(dictionary) is None
    # Create JSON to load
    temp_dir = get_temp_dir()
    test_json = abspath(join(temp_dir, "publisher.json"))
    create_json_file(test_json, {"thing":"other", "url":"www.deviantart.com/art/blah"})
    assert exists(test_json)
    # Test getting publisher when read directly from JSON
    meta = load_metadata(test_json)
    assert meta["json_path"] == test_json
    assert meta["publisher"] == "DeviantArt"

def test_get_url():
    """
    Tests the get_url function.
    """
    # Test getting URL strictly from JSON dictionary
    dictionary = {"url":"www.thisisatest.pizza", "thing":True}
    assert get_url(dictionary) == "www.thisisatest.pizza"
    dictionary = {"link":"URL.thing", "id":"other"}
    assert get_url(dictionary, "NotPublisher", "ID123") == "URL.thing"
    dictionary = {"total":124, "post_url":"New.url.thing"}
    assert get_url(dictionary, None, "123") == "New.url.thing"
    dictionary = {"webpage_url":"newthing.txt.thing", "id":"ABC"}
    assert get_url(dictionary, "Fur Affinity", None) == "newthing.txt.thing"
    dictionary = {"web":{"page_url":"new/url/value"}, "id":"ABC"}
    assert get_url(dictionary, "Deviantart", None) == "new/url/value"
    # Test getting Fur Affinity URL
    assert get_url({"D":"M"}, "Fur Affinity", "ID123") == "https://www.furaffinity.net/view/ID123/"
    assert get_url({"A":"B"}, "Fur Affinity", "Other") == "https://www.furaffinity.net/view/Other/"
    # Test getting Inkbunny URL
    assert get_url({"D":"M"}, "Inkbunny", "ID123") == "https://inkbunny.net/s/ID123"
    assert get_url({"A":"B"}, "Inkbunny", "Other") == "https://inkbunny.net/s/Other"
    # Test getting pixiv URL
    assert get_url({"D":"M"}, "pixiv", "ID123") == "https://www.pixiv.net/en/artworks/ID123"
    assert get_url({"A":"B"}, "pixiv", "Other") == "https://www.pixiv.net/en/artworks/Other"
    # Test when there is no URL
    assert get_url({"no":"url"}) is None
    # Create JSON to load
    temp_dir = get_temp_dir()
    dictionary = {"url":"www.furaffinity.net/thing/", "id":"ID-ABC"}
    test_json = abspath(join(temp_dir, "url.json"))
    create_json_file(test_json, dictionary)
    assert exists(test_json)
    # Test getting URL when read directly from JSON
    meta = load_metadata(test_json)
    assert meta["json_path"] == test_json
    assert meta["id"] == "ID-ABC"
    assert meta["publisher"] == "Fur Affinity"
    assert meta["url"] == "https://www.furaffinity.net/view/ID-ABC/"

def test_get_tags():
    """
    Tests the get_tags function.
    """
    # Test getting tags from only JSON lists
    dictionary = {"tags":["These", "are"], "categories":["some", "tags"]}
    assert get_tags(dictionary) == ["These", "are", "some", "tags"]
    dictionary = {"categories":"blah", "tags":["New", "Tags"]}
    assert get_tags(dictionary) == ["New", "Tags"]
    # Test getting tags from only single strings
    dictionary = {"da_category":"Artwork", "theme":"Something", "thing":"other"}
    assert get_tags(dictionary) == ["Artwork", "Something"]
    dictionary = {"theme":234, "species":"Cat", "gender":"Female"}
    assert get_tags(dictionary) == ["Cat", "Female"]
    # Test getting tags from internal parts of lists
    dictionary = {"tags":[{"name":"Thing"}, {"blah":"Thing"}, {"name":"other"}, {"no":"tags"}]}
    assert get_tags(dictionary) == ["Thing", "other"]
    dictionary = {"tags":[{"name":"Nope", "translated_name":"Over"}], "categories":[{"name":"blah"}, {"translated_name":"next"}]}
    assert get_tags(dictionary) == ["Over", "blah", "next"]
    dictionary = {"tags":["blah"], "info":{"web_tags":["DVK", "Style", "Tags"]}}
    assert get_tags(dictionary) == ["DVK", "Style", "Tags", "blah"]
    # Test getting tags from multiple sources
    dictionary = {"tags":[{"name":"thing"}], "categories":["Tag", "Things"], "theme":"other", "species":["nope"]}
    assert get_tags(dictionary) == ["thing", "Tag", "Things", "other"]
    # Test with no tags
    assert get_tags({"no":"tags"}) is None
    assert get_tags({"tags":[{"nope":"nope"}]}) is None
    # Create JSON to load
    temp_dir = get_temp_dir()
    dictionary = {"tags":["These", "are", "some", "tags"]}
    test_json = abspath(join(temp_dir, "tags.json"))
    create_json_file(test_json, dictionary)
    assert exists(test_json)
    # Test getting tags when read directly from JSON
    meta = load_metadata(test_json)
    assert meta["json_path"] == test_json
    assert meta["tags"] == ["These", "are", "some", "tags"]

def test_get_age_rating():
    """
    Tests the get_age_rating function.
    """
    # Test deviantart-style rating
    dictionary = {"is_mature":False, "thing":"blah"}
    assert get_age_rating(dictionary, "DeviantArt") == "Everyone"
    dictionary = {"is_mature":True, "mature_level":"moderate"}
    assert get_age_rating(dictionary, "DeviantArt") == "Mature 17+"
    dictionary = {"is_mature":True, "mature_level":"strict"}
    assert get_age_rating(dictionary, "DeviantArt") == "X18+"
    dictionary = {"is_mature":True, "mature_level":"blah"}
    assert get_age_rating(dictionary, "DeviantArt") == "Unknown"
    dictionary = {"is_mature":"nope"}
    assert get_age_rating(dictionary, "DeviantArt") == "Unknown"
    dictionary = {"is_mature":True, "blah":"thing"}
    assert get_age_rating(dictionary, "DeviantArt") == "Unknown"
    dictionary = {"thing":False}
    assert get_age_rating(dictionary, "DeviantArt") == "Unknown"
    # Test Fur Affinity style ratings
    dictionary = {"rating":"General", "other":"thing"}
    assert get_age_rating(dictionary, "Fur Affinity") == "Everyone"
    dictionary = {"rating":"Mature", "other":False}
    assert get_age_rating(dictionary, "Fur Affinity") == "Mature 17+"
    dictionary = {"3":True, "rating":"Adult"}
    assert get_age_rating(dictionary, "Fur Affinity") == "X18+"
    dictionary = {"rating":"Who Knows?"}
    assert get_age_rating(dictionary, "Fur Affinity") == "Unknown"
    dictionary = {"thing":"Other"}
    assert get_age_rating(dictionary, "Fur Affinity") == "Unknown"
    # Test Inkbunny style ratings
    dictionary = {"rating_name":"General", "other":"thing"}
    assert get_age_rating(dictionary, "Inkbunny") == "Everyone"
    dictionary = {"rating_name":"Mature", "other":False}
    assert get_age_rating(dictionary, "Inkbunny") == "Mature 17+"
    dictionary = {"3":True, "rating_name":"Adult"}
    assert get_age_rating(dictionary, "Inkbunny") == "X18+"
    dictionary = {"rating_name":"Who Knows?"}
    assert get_age_rating(dictionary, "Inkbunny") == "Unknown"
    dictionary = {"thing":"Other"}
    assert get_age_rating(dictionary, "Inkbunny") == "Unknown"
    # Test Newgrounds style ratings
    dictionary = {"rating":"e", "info":"other"}
    assert get_age_rating(dictionary, "Newgrounds") == "Everyone"
    dictionary = {"4":True, "rating":"T"}
    assert get_age_rating(dictionary, "Newgrounds") == "Teen"
    dictionary = {"rating":"m", "Final":"Not"}
    assert get_age_rating(dictionary, "Newgrounds") == "Mature 17+"
    dictionary = {"rating":"A"}
    assert get_age_rating(dictionary, "Newgrounds") == "X18+"
    dictionary = {"rating":"thing"}
    assert get_age_rating(dictionary, "Newgrounds") == "Unknown"
    dictionary = {"blah":"thing"}
    assert get_age_rating(dictionary, "Newgrounds") == "Unknown"
    # Test pixiv style ratings
    dictionary = {"rating":"General", "thing":12}
    assert get_age_rating(dictionary, "pixiv") == "Everyone"
    dictionary = {"true":False, "rating":"R-18"}
    assert get_age_rating(dictionary, "pixiv") == "X18+"
    dictionary = {"rating":"blah"}
    assert get_age_rating(dictionary, "pixiv") == "Unknown"
    dictionary = {"blah":"blah"}
    assert get_age_rating(dictionary, "pixiv") == "Unknown"
    # Test Weasyl style ratings
    dictionary = {"rating":"General", "info":"other"}
    assert get_age_rating(dictionary, "Weasyl") == "Everyone"
    dictionary = {"rating":"Mature", "Final":"Not"}
    assert get_age_rating(dictionary, "Weasyl") == "Mature 17+"
    dictionary = {"rating":"Explicit"}
    assert get_age_rating(dictionary, "Weasyl") == "X18+"
    dictionary = {"rating":"thing"}
    assert get_age_rating(dictionary, "Weasyl") == "Unknown"
    dictionary = {"blah":"thing"}
    assert get_age_rating(dictionary, "Weasyl") == "Unknown"
    # Test with invalid Publisher
    dictionary = {"rating":"General"}
    assert get_age_rating(dictionary, "NotRecognized") == "Unknown"
    dictionary = {"rating":"mature"}
    assert get_age_rating(dictionary, "Other") == "Unknown"
    dictionary = {"rating":"mature"}
    assert get_age_rating(dictionary, None) == "Unknown"
    # Create JSON to load
    temp_dir = get_temp_dir()
    dictionary = {"url":"www.furaffinity.net/thing/", "rating":"Mature"}
    test_json = abspath(join(temp_dir, "url.json"))
    create_json_file(test_json, dictionary)
    assert exists(test_json)
    # Test getting age rating when read directly from JSON
    meta = load_metadata(test_json)
    assert meta["json_path"] == test_json
    assert meta["publisher"] == "Fur Affinity"
    assert meta["age_rating"] == "Mature 17+"