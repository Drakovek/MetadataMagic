#!/usr/bin/env python3

import metadata_magic.sort as mm_sort

def test_get_first_section():
    """
    Tests the get_first_section function.
    """
    # Test getting number sections
    assert mm_sort.get_first_section("12") == "12"
    assert mm_sort.get_first_section("123 Thing!") == "123"
    assert mm_sort.get_first_section("1.25Words") == "1.25"
    assert mm_sort.get_first_section("1,000 Next") == "1,000"
    assert mm_sort.get_first_section("1,523.26!Numbers") == "1,523.26"
    # Test getting non-number sections
    assert mm_sort.get_first_section("Just text.") == "Just text."
    assert mm_sort.get_first_section("Text, then Numbers.137") == "Text, then Numbers."
    # Test getting section from string that has none
    assert mm_sort.get_first_section("") == ""

def test_compare_sections():
    """
    Tests the compare_sections function.
    """
    # Test comparing just numbers
    assert mm_sort.compare_sections("25", "0025") == 0
    assert mm_sort.compare_sections("1,000", "1000") == 0
    assert mm_sort.compare_sections("2", "2.000") == 0
    assert mm_sort.compare_sections("2", "3") == -1
    assert mm_sort.compare_sections("54", "023") == 1
    assert mm_sort.compare_sections("1,200", "1250") == -1
    assert mm_sort.compare_sections("3,500", "3,000") == 1
    assert mm_sort.compare_sections("0105.3", "105.38") == -1
    assert mm_sort.compare_sections("1.5", "1.25") == 1
    assert mm_sort.compare_sections("1", "1.5") == -1
    # Test comparing just text
    assert mm_sort.compare_sections("text", "text") == 0
    assert mm_sort.compare_sections("abc", "def") == -1
    assert mm_sort.compare_sections("test", "blah") == 1
    assert mm_sort.compare_sections("un", "unfinished") == -1
    assert mm_sort.compare_sections("ending", "end") == 1
    # Test comparing text and numbers
    assert mm_sort.compare_sections("43", "text") == -1
    assert mm_sort.compare_sections("other", "5.8") == 1
    # Test with missing sections
    assert mm_sort.compare_sections("", "540") == -1
    assert mm_sort.compare_sections("0", "") == 1
    assert mm_sort.compare_sections("", "word") == -1
    assert mm_sort.compare_sections("other", "")

def test_compare_alphanum():
    """
    Tests the compare_alphanum function.
    """
    # Test identical strings
    assert mm_sort.compare_alphanum("", "") == 0
    assert mm_sort.compare_alphanum("23 test", "23 test") == 0
    # Test comparing by number
    assert mm_sort.compare_alphanum("Test 4", "  test 10") == -1
    assert mm_sort.compare_alphanum("  Thing 34.5 more",  "Thing 5") == 1
    assert mm_sort.compare_alphanum("14 Name 1", "14   name 3") == -1
    assert mm_sort.compare_alphanum("024 thing next 5", "24 thing next 2") == 1
    # Test comparing by text
    assert mm_sort.compare_alphanum("45 abc", "45 Test") == -1
    assert mm_sort.compare_alphanum("987 banana", "0987   AAA") == 1
    assert mm_sort.compare_alphanum("5 Thing 65 next", "5 thing 65.0 other") == -1
    assert mm_sort.compare_alphanum("5.8 next 4 zzz", " 5.80 next 4 aaa") == 1
    assert mm_sort.compare_alphanum("12 thing", "12 thing next") == -1
    assert mm_sort.compare_alphanum("50 other next", "050 Other") == 1
    # Test comparing that with identical sections
    assert mm_sort.compare_alphanum("AAA", "aaa") == -1
    assert mm_sort.compare_alphanum("1.0", "1") == 1

def test_sort_alphanum():
    """
    Tests the sort_alphanum function.
    """
    lst = ["test 10", "test 1", "test 003", "3.5", "06 Next", "middle"]
    sort = mm_sort.sort_alphanum(lst)
    assert sort == ["3.5", "06 Next", "middle", "test 1", "test 003", "test 10"]

def test_get_value_from_dictionary():
    """
    Tests the get_value_from_dictionary function.
    """
    # Test getting a basic value
    dictionary = {"name":"thing", "other":"name"}
    assert mm_sort.get_value_from_dictionary(dictionary, ["name"]) == "thing"
    assert mm_sort.get_value_from_dictionary(dictionary, ["other"]) == "name"
    # Test getting a deeply nested value
    dictionary = {"thing":{"a":123, "b":456}, "even":{"deeper":{"a":"abc"}}}
    assert mm_sort.get_value_from_dictionary(dictionary, ["thing","a"]) == 123
    assert mm_sort.get_value_from_dictionary(dictionary, ["thing","b"]) == 456
    assert mm_sort.get_value_from_dictionary(dictionary, ["even","deeper","a"]) == "abc"
    # Test getting an array value
    dictionary = {"thing":["a","b","c","d"], "other":{"list":[10,20,30]}}
    assert mm_sort.get_value_from_dictionary(dictionary, ["thing",1]) == "b"
    assert mm_sort.get_value_from_dictionary(dictionary, ["other","list",1]) == 20
    # Test getting a mix of array and key values
    dictionary = {"a":[{"name":"title"}, {"name":"other"}]}
    assert mm_sort.get_value_from_dictionary(dictionary, ["a",0,"name"]) == "title"
    assert mm_sort.get_value_from_dictionary(dictionary, ["a",1,"name"]) == "other"
    # Test getting an invalid key
    assert mm_sort.get_value_from_dictionary(dictionary, [1]) is None
    assert mm_sort.get_value_from_dictionary(dictionary, ["item"]) is None
    assert mm_sort.get_value_from_dictionary(["thing"], [2]) is None
    assert mm_sort.get_value_from_dictionary(["thing"], ["item"]) is None
    assert mm_sort.get_value_from_dictionary(dictionary, ["a",5]) is None
    assert mm_sort.get_value_from_dictionary(dictionary, ["a","thing"]) is None

def test_compare_dictionaries_alphanum():
    """
    Tests the compare_dictionaries_alphanum function.
    """
    # Test comparing dictionaries one key deep
    dict1 = {"dvk_alpha_sort_key":"name", "name":"", "other":"blah"}
    dict2 = {"dvk_alpha_sort_key":"name", "name":"", "other":"thing"}
    assert mm_sort.compare_dictionaries_alphanum(dict1, dict2) == 0
    dict1 = {"dvk_alpha_sort_key":"name", "name":"001", "other":"blah"}
    dict2 = {"dvk_alpha_sort_key":"name", "name":"2", "other":"thing"}
    assert mm_sort.compare_dictionaries_alphanum(dict1, dict2) == -1
    dict1 = {"dvk_alpha_sort_key":"other", "name":"001", "other":"Part 23.5"}
    dict2 = {"dvk_alpha_sort_key":"other", "name":"2", "other":"Part 23"}
    assert mm_sort.compare_dictionaries_alphanum(dict1, dict2) == 1
    # Test comparing dictionaries multiple keys deep
    dict1 = {"dvk_alpha_sort_key":["name","thing"], "name":{"thing":"0"}, "other":"blah"}
    dict2 = {"dvk_alpha_sort_key":["name","thing"], "name":{"thing":"0"}, "other":"new"}
    assert mm_sort.compare_dictionaries_alphanum(dict1, dict2) == 0
    dict1 = {"dvk_alpha_sort_key":["name","thing"], "name":{"thing":"A"}, "other":"blah"}
    dict2 = {"dvk_alpha_sort_key":["name","thing"], "name":{"thing":"B"}, "other":"new"}
    assert mm_sort.compare_dictionaries_alphanum(dict1, dict2) == -1
    dict1 = {"dvk_alpha_sort_key":["name","thing","a"], "name":{"thing":{"a":"thing"}}, "other":"blah"}
    dict2 = {"dvk_alpha_sort_key":["name","thing","a"], "name":{"thing":{"a":"other"}}, "other":"new"}
    assert mm_sort.compare_dictionaries_alphanum(dict1, dict2) == 1
    # Test comparing dictionaries with keys referencing a given array value
    dict1 = {"dvk_alpha_sort_key":["list",2], "list":["1","2","c","3"]}
    dict2 = {"dvk_alpha_sort_key":["list",2], "list":["a","b","c","d"]}
    assert mm_sort.compare_dictionaries_alphanum(dict1, dict2) == 0
    dict1 = {"dvk_alpha_sort_key":["list",0], "list":["1","2","c","3"]}
    dict2 = {"dvk_alpha_sort_key":["list",0], "list":["a","b","c","d"]}
    assert mm_sort.compare_dictionaries_alphanum(dict1, dict2) == -1
    dict1 = {"dvk_alpha_sort_key":["list",3], "list":["1","2","c","Other"]}
    dict2 = {"dvk_alpha_sort_key":["list",3], "list":["a","b","c","25"]}
    assert mm_sort.compare_dictionaries_alphanum(dict1, dict2) == 1

def test_sort_dictionaries_alphanum():
    """
    Tests the sort_dictionaries_alphanum function.
    """
    dictionaries = []
    dictionaries.append({"name":"Title 1", "other":{"a":"123", "b":"245"}})
    dictionaries.append({"name":"Title 10", "other":{"a":"523", "b":"Thing"}})
    dictionaries.append({"name":"Name", "other":{"a":"a", "b":"b"}})
    dictionaries.append({"name":"ZZZ", "other":{"a":"name", "b":"title"}})
    dictionaries.append({"name":"AAA", "other":{"a":"123.5", "b":"Blah"}})
    # Test sorting by a standard value
    dictionaries = mm_sort.sort_dictionaries_alphanum(dictionaries, "name")
    assert len(dictionaries) == 5
    assert dictionaries[0] == {"name":"AAA", "other":{"a":"123.5", "b":"Blah"}}
    assert dictionaries[1] == {"name":"Name", "other":{"a":"a", "b":"b"}}
    assert dictionaries[2] == {"name":"Title 1", "other":{"a":"123", "b":"245"}}
    assert dictionaries[3] == {"name":"Title 10", "other":{"a":"523", "b":"Thing"}}
    assert dictionaries[4] == {"name":"ZZZ", "other":{"a":"name", "b":"title"}}
    # Test sorting by a deeper value
    dictionaries = mm_sort.sort_dictionaries_alphanum(dictionaries, ["other","a"])
    assert len(dictionaries) == 5
    assert dictionaries[0] == {"name":"Title 1", "other":{"a":"123", "b":"245"}}
    assert dictionaries[1] == {"name":"AAA", "other":{"a":"123.5", "b":"Blah"}}
    assert dictionaries[2] == {"name":"Title 10", "other":{"a":"523", "b":"Thing"}}
    assert dictionaries[3] == {"name":"Name", "other":{"a":"a", "b":"b"}}
    assert dictionaries[4] == {"name":"ZZZ", "other":{"a":"name", "b":"title"}}
