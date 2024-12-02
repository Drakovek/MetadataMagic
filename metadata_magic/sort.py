#!/usr/bin/env python3

import re
import _functools
from typing import List

def get_first_section(string:str) -> str:
    """
    Gets the first "section" of a given string.
    A section should contain either only text or only a number.
    
    :param string: String to get section from
    :type string: str, required
    :return: The first "section" of the given string
    :rtype: str
    """
    # Check if string starts with a number
    if len(re.findall("^[0-9]", string)) > 0:
        # Return number section if string starts with a number
        return re.findall(r"[0-9]+[0-9,\.]*", string)[0]
    # Return non-number section if string doesn't start with number
    sections = re.findall("[^0-9]+", string)
    if len(sections) > 0:
        return sections[0]
    # Return empty string if no sections could be found
    return ""

def compare_sections(section1:str, section2:str) -> int:
    """
    Compares two sections alphanumerically.
    Returns -1 if section1 comes first, 1 if section2 comes first.
    Returns 0 if section1 and section2 are identical.
    
    :param section1: First section to compare
    :type section1: str, required
    :param section2: Second section to compare
    :type section2: str, required
    :return: Integer describing which section should come first
    :rtype: int
    """
    try:
        # Compare numbers, if applicable.
        float1 = float(section1.replace(",", ""))
        float2 = float(section2.replace(",", ""))
        if float1 > float2:
            return 1
        elif float1 < float2:
            return -1
        return 0
    except ValueError:
        # Return 0 if sections are identical
        if section1 == section2:
            return 0
        # Compare text values
        sort = sorted([section1, section2])
        if sort[0] == section1:
            return -1
        return 1

def compare_alphanum(string1:str, string2:str) -> int:
    """
    Compares two strings alphanumerically.
    Returns -1 if string1 comes first, 1 if string2 comes first.
    Returns 0 if string1 and string2 are identical.
    
    :param string1: First string to compare
    :type string1: str, required
    :param string2: Second string to compare
    :type string2: str, required
    :return: Integer describing which string should come first
    :rtype: int
    """
    # Prepare strings for comparison
    compare = 0
    left1 = re.sub(r"\s+", " ", string1.lower()).strip()
    left2 = re.sub(r"\s+", " ", string2.lower()).strip()
    # Run through comparing strings section by section
    while compare == 0 and not left1 == "" and not left2 == "":
        # Get the first sections
        section1 = get_first_section(left1)
        section2 = get_first_section(left2)
        # Modify what's left of strings
        left1 = left1[len(section1):]
        left2 = left2[len(section2):]
        # Compare sections
        compare = compare_sections(section1, section2)
    # Compare full strings if comparing by section inconclusive
    if compare == 0:
        compare = compare_sections(f"T{string1}", f"T{string2}")
    # Return result
    return compare

def sort_alphanum(lst:List[str]) -> List[str]:
    """
    Sorts a given list alphanumerically.
    
    :param lst: List to sort
    :type lst: list[str], required
    :return: Sorted list
    :rtype: list[str]
    """
    comparator = _functools.cmp_to_key(compare_alphanum)
    return sorted(lst, key=comparator)

def get_value_from_dictionary(dictionary:dict, key_list:List):
    """
    Returns a value from a dictionary based on a list of keys.
    If there is only one key, it will get the dictionary value as standard.
    If there are multiple keys, the nested dictionary will be returned.
    Keys can be either a named key or an index value for an array.

    :param dictionary: Dictionary or List to get the value from
    :type dictionary: dict/List, required
    :param key_list: List of keys/index values
    :type key_list: List, required
    :return: Value of the nested key
    :rtype: any
    """
    try:
        # Get the base value from the dictionary
        value = dictionary[key_list[0]]
        # Return the value if base value is all that's needed
        if len(key_list) == 1:
            return value
        # Get the next value recursively, if required
        return get_value_from_dictionary(value, key_list[1:])
    except (IndexError, KeyError, TypeError): return None

def compare_dictionaries_alphanum(dict1:dict, dict2:dict) -> int:
    """
    Compares two dictionaries alphanumerically
    Returns -1 if dict1 comes first, 1 if dict2 comes first.
    Returns 0 if dict1 and dict2 values are identical.
    
    Dictionaries are compared by the values of a given key list.
    The key list should be stored as a value in the dictionary under the key "dvk_alpha_sort_key"
    
    :param dict1: First dictionary to compare
    :type dict1: dict, required
    :param dict2: Second dictionary to compare
    :type dict2: str, required
    :return: Integer describing which dictionary should come first
    :rtype: int
    """
    # Get the key to search for
    key = dict1["dvk_alpha_sort_key"]
    if isinstance(key, str):
        key = [key]
    # Get the string values
    string1 = get_value_from_dictionary(dict1, key)
    string2 = get_value_from_dictionary(dict2, key)
    # Return the string comparison
    return compare_alphanum(str(string1), str(string2))

def sort_dictionaries_alphanum(lst:List[dict], key_list:List) -> List[dict]:
    """
    Sorts a given list of dictionaries alphanumerically.
    Comparisons are made based on the value of the nested key given in the key list.
    
    :param lst: List to sort
    :type lst: list[str], required
    :param key_list: List of keys/index values
    :type key_list: List, required
    :return: Sorted list
    :rtype: List[dict]
    """
    # Add the key list to each dictionary
    dict_list = []
    for item in lst:
        dictionary = item
        dictionary["dvk_alpha_sort_key"] = key_list
        dict_list.append(dictionary)
    # Sort the list of dictionaries
    comparator = _functools.cmp_to_key(compare_dictionaries_alphanum)
    dict_list = sorted(dict_list, key=comparator)
    # Remove the key list from each dict
    for item in dict_list:
        item.pop("dvk_alpha_sort_key")
    # Return the sorted list
    return dict_list
