#!/usr/bin/env python3

import os
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive_all as mm_archive_all
import metadata_magic.archive.comic_archive as mm_comic_archive
from os.path import abspath, join

def test_archive_all():
    """
    Tests the archive_all function.
    """
    # Test archiving all JSON-media pairs
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "media.jpg")), "Blah")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "media.json")), {"title": "Blah!"})
    mm_file_tools.write_text_file(abspath(join(temp_dir, "other.png")), "Blah")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "other.json")), {"artist":"Person"})
    assert sorted(os.listdir(temp_dir)) == ["media.jpg", "media.json", "other.json", "other.png"]
    mm_archive_all.archive_all(temp_dir)
    assert sorted(os.listdir(temp_dir)) == ["media.cbz", "other.cbz"]
    # Test that created cbz files contain JSON metadata
    read_meta = mm_comic_archive.get_info_from_cbz(abspath(join(temp_dir, "media.cbz")))
    assert read_meta["title"] == "Blah!"
    assert read_meta["artist"] is None
    read_meta = mm_comic_archive.get_info_from_cbz(abspath(join(temp_dir, "other.cbz")))
    assert read_meta["title"] is None
    assert read_meta["artist"] == "Person"
    # Test archiving when there are non-image files
    mm_file_tools.write_text_file(abspath(join(temp_dir, "movie.mp4")), "Blah")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "movie.json")), {"title": "Movie"})
    mm_file_tools.write_text_file(abspath(join(temp_dir, "new.png")), "Blah")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "new.json")), {"artist":"Person"})
    files = ["media.cbz", "movie.json", "movie.mp4", "new.json", "new.png", "other.cbz"]
    assert sorted(os.listdir(temp_dir)) == files
    mm_archive_all.archive_all(temp_dir)
    files = ["media.cbz", "movie.json", "movie.mp4", "new.cbz", "other.cbz"]
    assert sorted(os.listdir(temp_dir)) == files
    # Test archiving when there are unpaired files
    mm_file_tools.write_text_file(abspath(join(temp_dir, "different.png")), "Blah")
    files = ["different.png", "media.cbz", "movie.json", "movie.mp4", "new.cbz", "other.cbz"]
    assert sorted(os.listdir(temp_dir)) == files
    mm_archive_all.archive_all(temp_dir)
    files = ["different.png", "media.cbz", "movie.json", "movie.mp4", "new.cbz", "other.cbz"]
    assert sorted(os.listdir(temp_dir)) == files
    # Test that internal file structure is correct
    extract_dir = abspath(join(temp_dir, "extracted"))
    os.mkdir(extract_dir)
    mm_file_tools.extract_zip(abspath(join(temp_dir, "new.cbz")), extract_dir)
    assert sorted(os.listdir(extract_dir)) == ["ComicInfo.xml", "new"]
    sub_dir = abspath(join(extract_dir, "new"))
    assert sorted(os.listdir(sub_dir)) == ["new.json", "new.png"]
    assert mm_file_tools.read_text_file(abspath(join(sub_dir, "new.png"))) == "Blah"
