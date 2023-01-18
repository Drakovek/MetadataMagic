#!/usr/bin/env python3

from json import dump as dump_json
from os import listdir
from os.path import abspath, exists, join
from metadata_magic.main.rename.rename_jsons import rename_json_pairs
from metadata_magic.test.temp_dir import get_temp_dir

def test_rename_json_pairs():
    """
    Tests the rename_json_pairs function.
    """
    # Write test media files
    temp_dir = get_temp_dir()
    image_file = abspath(join(temp_dir, "image.png"))
    with open(image_file, "w") as out_file:
        out_file.write("Test")
    text_file = abspath(join(temp_dir, "text.txt"))
    with open(text_file, "w") as out_file:
        out_file.write("Test")
    assert exists(image_file)
    assert exists(text_file)
    # Write test JSONS
    image_json = abspath(join(temp_dir, "image.json"))
    with open(image_json, "w") as out_file:
        dump_json({"title":"Picture!"}, out_file)
    text_json = abspath(join(temp_dir, "text.json"))
    with open(text_json, "w") as out_file:
        dump_json({"title":"Totally Text"}, out_file)
    assert exists(image_json)
    assert exists(text_json)
    # Test renaming files
    rename_json_pairs(temp_dir)
    assert len(listdir(temp_dir)) == 4
    image_file = abspath(join(temp_dir, "Picture!.png"))
    assert exists(image_file)
    image_json = abspath(join(temp_dir, "Picture!.json"))
    assert exists(image_json)
    text_file = abspath(join(temp_dir, "Totally Text.txt"))
    assert exists(text_file)
    text_json = abspath(join(temp_dir, "Totally Text.json"))
    assert exists(text_json)
    # Test renaming JSON with no title field
    new_file = abspath(join(temp_dir, "final.txt"))
    with open(new_file, "w") as out_file:
        out_file.write("Test")
    new_json = abspath(join(temp_dir, "final.txt.json"))
    with open(new_json, "w") as out_file:
        dump_json({"thing":"other"}, out_file)
    assert exists(new_file)
    assert exists(new_json)
    rename_json_pairs(temp_dir)
    assert exists(new_file)
    new_json = abspath(join(temp_dir, "final.json"))
    assert exists(new_json)