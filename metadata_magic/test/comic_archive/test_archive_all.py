#!/usr/bin/env python3

from metadata_magic.main.comic_archive.archive_all import archive_all
from metadata_magic.main.comic_archive.comic_archive import get_info_from_cbz
from metadata_magic.main.file_tools.file_tools import get_temp_dir
from metadata_magic.main.file_tools.file_tools import read_text_file
from metadata_magic.main.file_tools.file_tools import write_text_file
from metadata_magic.main.file_tools.file_tools import write_json_file
from metadata_magic.main.file_tools.file_tools import extract_zip
from os import listdir, mkdir
from os.path import abspath, join

def test_archive_all():
    """
    Tests the archive_all function.
    """
    # Test archiving all JSON-media pairs
    temp_dir = get_temp_dir()
    write_text_file(abspath(join(temp_dir, "media.jpg")), "Blah")
    write_json_file(abspath(join(temp_dir, "media.json")), {"title": "Blah!"})
    write_text_file(abspath(join(temp_dir, "other.png")), "Blah")
    write_json_file(abspath(join(temp_dir, "other.json")), {"artist":"Person"})
    assert sorted(listdir(temp_dir)) == ["media.jpg", "media.json", "other.json", "other.png"]
    archive_all(temp_dir)
    assert sorted(listdir(temp_dir)) == ["media.cbz", "other.cbz"]
    # Test that created cbz files contain JSON metadata
    read_meta = get_info_from_cbz(abspath(join(temp_dir, "media.cbz")))
    assert read_meta["title"] == "Blah!"
    assert read_meta["artist"] is None
    read_meta = get_info_from_cbz(abspath(join(temp_dir, "other.cbz")))
    assert read_meta["title"] is None
    assert read_meta["artist"] == "Person"
    # Test archiving when there are non-image files
    write_text_file(abspath(join(temp_dir, "movie.mp4")), "Blah")
    write_json_file(abspath(join(temp_dir, "movie.json")), {"title": "Movie"})
    write_text_file(abspath(join(temp_dir, "new.png")), "Blah")
    write_json_file(abspath(join(temp_dir, "new.json")), {"artist":"Person"})
    files = ["media.cbz", "movie.json", "movie.mp4", "new.json", "new.png", "other.cbz"]
    assert sorted(listdir(temp_dir)) == files
    archive_all(temp_dir)
    files = ["media.cbz", "movie.json", "movie.mp4", "new.cbz", "other.cbz"]
    assert sorted(listdir(temp_dir)) == files
    # Test archiving when there are unpaired files
    write_text_file(abspath(join(temp_dir, "different.png")), "Blah")
    files = ["different.png", "media.cbz", "movie.json", "movie.mp4", "new.cbz", "other.cbz"]
    assert sorted(listdir(temp_dir)) == files
    archive_all(temp_dir)
    files = ["different.png", "media.cbz", "movie.json", "movie.mp4", "new.cbz", "other.cbz"]
    assert sorted(listdir(temp_dir)) == files
    # Test that internal file structure is correct
    extract_dir = abspath(join(temp_dir, "extracted"))
    mkdir(extract_dir)
    extract_zip(abspath(join(temp_dir, "new.cbz")), extract_dir)
    assert sorted(listdir(extract_dir)) == ["ComicInfo.xml", "new"]
    sub_dir = abspath(join(extract_dir, "new"))
    assert sorted(listdir(sub_dir)) == ["new.json", "new.png"]
    assert read_text_file(abspath(join(sub_dir, "new.png"))) == "Blah"