#!/usr/bin/env python3

from os import listdir
from os.path import abspath, exists, join
from metadata_magic.main.comic_archive.comic_archive import get_temp_dir
from metadata_magic.main.rename.rename_jsons import rename_json_pairs
from metadata_magic.test.temp_file_tools import create_json_file
from metadata_magic.test.temp_file_tools import create_text_file

def test_rename_json_pairs():
    """
    Tests the rename_json_pairs function.
    """
    # Write test media files
    temp_dir = get_temp_dir()
    image_file = abspath(join(temp_dir, "image.png"))
    create_text_file(image_file, "Test")
    text_file = abspath(join(temp_dir, "text.txt"))
    create_text_file(text_file, "Test")
    assert exists(image_file)
    assert exists(text_file)
    # Write test JSONS
    image_json = abspath(join(temp_dir, "image.json"))
    create_json_file(image_json, {"title":"Picture!", "index":"abc"})
    text_json = abspath(join(temp_dir, "text.json"))
    create_json_file(text_json, {"title":"Totally Text", "id":"1234"})
    assert exists(image_json)
    assert exists(text_json)
    # Test renaming files
    rename_json_pairs(temp_dir)
    assert len(listdir(temp_dir)) == 4
    image_file = abspath(join(temp_dir, "Picture!.png"))
    image_json = abspath(join(temp_dir, "Picture!.json"))
    text_file = abspath(join(temp_dir, "Totally Text.txt"))
    text_json = abspath(join(temp_dir, "Totally Text.json"))
    assert exists(image_file)
    assert exists(image_json)
    assert exists(text_file)
    assert exists(text_json)
    # Test renaming JSON with no title field
    new_file = abspath(join(temp_dir, "final.txt"))
    create_text_file(new_file, "Test")
    new_json = abspath(join(temp_dir, "final.txt.json"))
    create_json_file(new_json, {"thing":"other"})
    assert exists(new_file)
    assert exists(new_json)
    rename_json_pairs(temp_dir)
    assert exists(new_file)
    new_json = abspath(join(temp_dir, "final.json"))
    assert exists(new_json)
    # Test renaming files with the ID attatched
    rename_json_pairs(temp_dir, True)
    image_file = abspath(join(temp_dir, "[abc] Picture!.png"))
    image_json = abspath(join(temp_dir, "[abc] Picture!.json"))
    text_file = abspath(join(temp_dir, "[1234] Totally Text.txt"))
    text_json = abspath(join(temp_dir, "[1234] Totally Text.json"))
    assert exists(image_file)
    assert exists(image_json)
    assert exists(text_file)
    assert exists(text_json)
    # Test renaming files with ID if ID doesn't exist
    assert exists(new_file)
    assert exists(new_json)