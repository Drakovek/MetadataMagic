#!/usr/bin/env python3

from metadata_magic.main.meta_reader import get_artist
from metadata_magic.main.meta_reader import get_title
from metadata_magic.main.meta_reader import get_value_from_keylist
from metadata_magic.main.meta_reader import load_metadata
from metadata_magic.test.temp_file_tools import create_json_file, get_temp_dir
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

def test_get_title():
    """
    Tests the get_title function.
    """
    # Test getting title from dictionary
    dictionary = {"thing":"blah", "inner":{"title":"Thing!"}, "title":"Bleh"}
    assert get_title(dictionary) == "Bleh"
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
    Tests the get_artists function.
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
    dictionary = {"user":{"name":"Cpt. Human"}, "artist":50}
    assert get_artist(dictionary) == "Cpt. Human"
    # Test if there is no artist
    dictionary = {"no":"artist"}
    assert get_artist(dictionary) is None
    # Create JSON to load
    temp_dir = get_temp_dir()
    test_json = abspath(join(temp_dir, "title.json"))
    create_json_file(test_json, {"thing":"other", "uploader":"Name!!!"})
    assert exists(test_json)
    # Test getting artist when read directly from JSON
    meta = load_metadata(test_json)
    assert meta["json_path"] == test_json
    assert meta["artist"] == "Name!!!"