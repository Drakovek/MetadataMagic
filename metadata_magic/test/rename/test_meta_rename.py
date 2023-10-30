#!/usr/bin/env python3

import os
import shutil
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.rename.meta_rename as mm_meta_rename
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.comic_archive as mm_comic_archive
from os.path import abspath, exists, join

def test_rename_cbz_files():
    """
    Tests the rename_cbz_files() function
    """
    # Write test media files
    temp_dir = mm_file_tools.get_temp_dir("dvk_meta_cbz")
    sub_dir_1 = abspath(join(temp_dir, "sub1"))
    sub_dir_2 = abspath(join(temp_dir, "sub2"))
    os.mkdir(sub_dir_1)
    os.mkdir(sub_dir_2)
    text_file_1 = abspath(join(sub_dir_1, "file1.txt"))
    text_file_2 = abspath(join(sub_dir_2, "file2.txt"))
    mm_file_tools.write_text_file(text_file_1, "Some Text.")
    mm_file_tools.write_text_file(text_file_2, "Some Text.")
    assert exists(text_file_1)
    assert exists(text_file_2)
    metadata1 = mm_archive.get_empty_metadata()
    metadata2 = mm_archive.get_empty_metadata()
    metadata1["title"] = "Some Name"
    metadata1["artist"] = "Person"
    metadata1["date"] = "2020-05-30"
    metadata2["title"] = "Thing"
    metadata2["writer"] = "Dude"
    metadata2["date"] = "2018-11-15"
    cbz1 = mm_comic_archive.create_cbz(sub_dir_1, metadata=metadata1, remove_files=True)
    cbz2 = mm_comic_archive.create_cbz(sub_dir_2, metadata=metadata2, remove_files=True)
    assert exists(cbz1)
    assert exists(cbz2)
    # Test renaming cbz files
    mm_meta_rename.rename_cbz_files(temp_dir)
    assert sorted(os.listdir(sub_dir_1)) == ["Some Name.cbz"]
    assert sorted(os.listdir(sub_dir_2)) == ["Thing.cbz"]
    # Test renaming with added artist
    mm_meta_rename.rename_cbz_files(temp_dir, add_artist=True)
    assert sorted(os.listdir(sub_dir_1)) == ["[Person] Some Name.cbz"]
    assert sorted(os.listdir(sub_dir_2)) == ["[Dude] Thing.cbz"]
    # Test renaming with added date
    mm_meta_rename.rename_cbz_files(temp_dir, add_date=True)
    assert sorted(os.listdir(sub_dir_1)) == ["[2020-05-30] Some Name.cbz"]
    assert sorted(os.listdir(sub_dir_2)) == ["[2018-11-15] Thing.cbz"]
    # Test renaming with no title
    new_metadata = mm_archive.get_empty_metadata()
    new_cbz = mm_comic_archive.create_cbz(temp_dir, metadata=new_metadata)
    mm_meta_rename.rename_cbz_files(temp_dir)
    assert sorted(os.listdir(temp_dir)) == ["dvk_meta_cbz.cbz", "sub1", "sub2"]
    # Test renaming files with identical names
    cbz1 = abspath(join(sub_dir_1, "Some Name.cbz"))
    shutil.copy(cbz1, abspath(join(sub_dir_1, "newer_cbz.cbz")))
    mm_meta_rename.rename_cbz_files(temp_dir)
    assert sorted(os.listdir(sub_dir_1)) == ["Some Name-2.cbz", "Some Name.cbz"]

def test_rename_json_pairs():
    """
    Tests the rename_json_pairs function.
    """
    # Write test media files
    temp_dir = mm_file_tools.get_temp_dir()
    image_file = abspath(join(temp_dir, "image.png"))
    mm_file_tools.write_text_file(image_file, "Test")
    text_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "Test")
    assert exists(image_file)
    assert exists(text_file)
    # Write test JSONS
    image_json = abspath(join(temp_dir, "image.json"))
    mm_file_tools.write_json_file(image_json, {"title":"Picture!", "artist":"Person", "index":"abc", "date":"2020-01-01"})
    text_json = abspath(join(temp_dir, "text.json"))
    mm_file_tools.write_json_file(text_json, {"title":"Totally Text", "artist":"Other", "id":"1234", "date":"2019-10-31"})
    assert exists(image_json)
    assert exists(text_json)
    # Test renaming files
    mm_meta_rename.rename_json_pairs(temp_dir)
    files = sorted(os.listdir(temp_dir))
    assert len(files) == 4
    assert files[0] == "Picture!.json"
    assert files[1] == "Picture!.png"
    assert files[2] == "Totally Text.json"
    assert files[3] == "Totally Text.txt"
    # Test renaming with added ID
    mm_meta_rename.rename_json_pairs(temp_dir, add_id=True)
    files = sorted(os.listdir(temp_dir))
    assert len(files) == 4
    assert files[0] == "[1234] Totally Text.json"
    assert files[1] == "[1234] Totally Text.txt"
    assert files[2] == "[abc] Picture!.json"
    assert files[3] == "[abc] Picture!.png"
    # Test renaming with added Artist
    mm_meta_rename.rename_json_pairs(temp_dir, add_artist=True)
    files = sorted(os.listdir(temp_dir))
    assert len(files) == 4
    assert files[0] == "[Other] Totally Text.json"
    assert files[1] == "[Other] Totally Text.txt"
    assert files[2] == "[Person] Picture!.json"
    assert files[3] == "[Person] Picture!.png"
    # Test renaming with added Date
    mm_meta_rename.rename_json_pairs(temp_dir, add_date=True)
    files = sorted(os.listdir(temp_dir))
    assert len(files) == 4
    assert files[0] == "[2019-10-31] Totally Text.json"
    assert files[1] == "[2019-10-31] Totally Text.txt"
    assert files[2] == "[2020-01-01] Picture!.json"
    assert files[3] == "[2020-01-01] Picture!.png"
    # Test renaming files with no title field
    new_file = abspath(join(temp_dir, "final.txt"))
    new_json = abspath(join(temp_dir, "final.txt.json"))
    mm_file_tools.write_text_file(new_file, "Test")
    mm_file_tools.write_json_file(new_json, {"thing":"other"})
    assert exists(new_file)
    assert exists(new_json)
    mm_meta_rename.rename_json_pairs(temp_dir)
    files = sorted(os.listdir(temp_dir))
    assert len(files) == 6
    assert files[0] == "Picture!.json"
    assert files[1] == "Picture!.png"
    assert files[2] == "Totally Text.json"
    assert files[3] == "Totally Text.txt"
    assert files[4] == "final.json"
    assert files[5] == "final.txt"
    # Test renaming files with identical names
    new_json = abspath(join(temp_dir, "Totally Text.json"))
    mm_file_tools.write_json_file(new_json, {"title":"final"})
    mm_meta_rename.rename_json_pairs(temp_dir)
    files = sorted(os.listdir(temp_dir))
    assert len(files) == 6
    assert files[0] == "Picture!.json"
    assert files[1] == "Picture!.png"
    assert files[2] == "final-2.json"
    assert files[3] == "final-2.txt"
    assert files[4] == "final.json"
    assert files[5] == "final.txt"
    
def test_get_filename_from_metadata():
    """
    Tests the get_filename_from_metadata.
    """
    # Test getting filename from JSON
    temp_dir = mm_file_tools.get_temp_dir()
    json_file = abspath(join(temp_dir, "json.json"))
    mm_file_tools.write_json_file(json_file, {"title":"This is a title!"})
    assert exists(json_file)
    assert mm_meta_rename.get_filename_from_metadata(json_file) == "This is a title!"
    # Test getting filename from CBZ
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "CBZ Time"
    cbz_file = mm_comic_archive.create_cbz(temp_dir, metadata=metadata)
    assert exists(cbz_file)
    assert mm_meta_rename.get_filename_from_metadata(cbz_file) == "CBZ Time"
    # Test getting filename with no metadata
    text_file = abspath(join(temp_dir, "Nope!.txt"))
    mm_file_tools.write_text_file(text_file, "Some Text!")
    assert exists(text_file)
    assert mm_meta_rename.get_filename_from_metadata(text_file) == "Nope!"
    # Test adding a date
    mm_file_tools.write_json_file(json_file, {"title":"Thing", "date":"2020-03-01"})
    assert mm_meta_rename.get_filename_from_metadata(json_file, add_date=True) == "[2020-03-01] Thing"
    metadata["date"] = "2017-08-05"
    os.remove(cbz_file)
    cbz_file = mm_comic_archive.create_cbz(temp_dir, metadata=metadata)
    assert mm_meta_rename.get_filename_from_metadata(cbz_file, add_date=True) == "[2017-08-05] CBZ Time"
    # Test adding an artist/writer
    mm_file_tools.write_json_file(json_file, {"title":"Other", "artist":"Person"})
    assert mm_meta_rename.get_filename_from_metadata(json_file, add_artist=True) == "[Person] Other"
    metadata["writer"] = "Writer"
    os.remove(cbz_file)
    cbz_file = mm_comic_archive.create_cbz(temp_dir, metadata=metadata)
    assert mm_meta_rename.get_filename_from_metadata(cbz_file, add_artist=True) == "[Writer] CBZ Time"
    # Test adding an ID
    mm_file_tools.write_json_file(json_file, {"title":"Identifier", "id":"ID12345"})
    assert mm_meta_rename.get_filename_from_metadata(json_file, add_id=True) == "[ID12345] Identifier"
    # Test adding multiple fields
    mm_file_tools.write_json_file(json_file, {"title":"Title", "date":"2012-12-21", "id":"ID36", "artist":"Guy"})
    title = mm_meta_rename.get_filename_from_metadata(json_file, add_id=True, add_date=True)
    assert title == "[2012-12-21_ID36] Title"
    title = mm_meta_rename.get_filename_from_metadata(cbz_file, add_artist=True, add_date=True)
    assert title == "[Writer_2017-08-05] CBZ Time"
    title = mm_meta_rename.get_filename_from_metadata(json_file, add_artist=True, add_date=True)
    assert title == "[Guy_2012-12-21] Title"
    title = mm_meta_rename.get_filename_from_metadata(json_file, add_artist=True, add_date=True, add_id=True)
    assert title == "[Guy_2012-12-21_ID36] Title"
    # Test if date is invalid
    mm_file_tools.write_json_file(json_file, {"title":"New", "id":"Thing"})
    assert mm_meta_rename.get_filename_from_metadata(json_file, add_date=True) == "New"
    assert mm_meta_rename.get_filename_from_metadata(json_file, add_date=True, add_id=True) == "[Thing] New"
    # Test if artist is invalid
    mm_file_tools.write_json_file(json_file, {"title":"No Artist", "id":"Thing"})
    assert mm_meta_rename.get_filename_from_metadata(json_file, add_artist=True) == "No Artist"
    assert mm_meta_rename.get_filename_from_metadata(json_file, add_artist=True, add_id=True) == "[Thing] No Artist"
    # Test if ID is invalid
    mm_file_tools.write_json_file(json_file, {"title":"No ID", "artist":"Lad"})
    assert mm_meta_rename.get_filename_from_metadata(json_file, add_id=True) == "No ID"
    assert mm_meta_rename.get_filename_from_metadata(json_file, add_artist=True, add_id=True) == "[Lad] No ID"
    # Test if title is invalid
    mm_file_tools.write_json_file(json_file, {"blah":"blah"})
    assert mm_meta_rename.get_filename_from_metadata(json_file) == "json"
    new_json = abspath(join(temp_dir, "New JSON.txt.json"))
    mm_file_tools.write_json_file(new_json, {"no":"title"})
    assert exists(new_json)
    assert mm_meta_rename.get_filename_from_metadata(new_json) == "New JSON"
