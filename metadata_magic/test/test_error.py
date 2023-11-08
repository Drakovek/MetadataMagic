#!/usr/bin/env python3

import os
import shutil
import metadata_magic.error as mm_error
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.comic_archive as mm_comic_archive
import metadata_magic.archive.epub as mm_epub
from os.path import abspath, basename, exists, join

def test_find_missing_media():
    """
    Test the find_missing_media function.
    """
    # Test with empty directory
    temp_dir = mm_file_tools.get_temp_dir()
    assert exists(temp_dir)
    assert mm_error.find_missing_media(temp_dir) == []
    # Test with no unlinked files
    sub = abspath(join(temp_dir, "sub"))
    os.mkdir(sub)
    mm_file_tools.write_text_file(abspath(join(temp_dir, "main.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "main.png")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub, "unlinked.txt")), "BLAH")
    assert mm_error.find_missing_media(temp_dir) == []
    # Test with unlinked files
    mm_file_tools.write_text_file(abspath(join(temp_dir, "unlinked.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "thing.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub, "next.json")), "BLAH")
    missing_media = mm_error.find_missing_media(temp_dir)
    assert len(missing_media) == 3
    assert basename(missing_media[0]) == "next.json"
    assert abspath(join(missing_media[0], os.pardir)) == sub
    assert basename(missing_media[1]) == "thing.json"
    assert abspath(join(missing_media[1], os.pardir)) == temp_dir
    assert basename(missing_media[2]) == "unlinked.json"
    assert abspath(join(missing_media[2], os.pardir)) == temp_dir

def test_find_missing_metadata():
    """
    Tests the find_missing_metadata function.
    """
    # Test with empty directory
    temp_dir = mm_file_tools.get_temp_dir()
    assert exists(temp_dir)
    assert mm_error.find_missing_metadata(temp_dir) == []
    # Test with no unlinked files
    sub = abspath(join(temp_dir, "sub"))
    os.mkdir(sub)
    mm_file_tools.write_text_file(abspath(join(temp_dir, "main.json")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "main.png")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub, "unlinked.json")), "BLAH")
    assert mm_error.find_missing_metadata(temp_dir) == []
    # Test with unlinked files
    mm_file_tools.write_text_file(abspath(join(temp_dir, "unlinked.txt")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "thing.jpg")), "BLAH")
    mm_file_tools.write_text_file(abspath(join(sub, "next.cbz")), "BLAH")
    missing_metadata = mm_error.find_missing_metadata(temp_dir)
    assert len(missing_metadata) == 3
    assert basename(missing_metadata[0]) == "next.cbz"
    assert abspath(join(missing_metadata[0], os.pardir)) == sub
    assert basename(missing_metadata[1]) == "thing.jpg"
    assert abspath(join(missing_metadata[1], os.pardir)) == temp_dir
    assert basename(missing_metadata[2]) == "unlinked.txt"
    assert abspath(join(missing_metadata[2], os.pardir)) == temp_dir

def test_find_missing_fields():
    """
    Tests the find_missing_fields function.
    """
    # Create CBZ test file A
    temp_dir = mm_file_tools.get_temp_dir()
    sub_dir = abspath(join(temp_dir, "sub"))
    os.mkdir(sub_dir)
    build_dir = mm_file_tools.get_temp_dir("builder")
    text_file = abspath(join(build_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "This is text!!!")
    assert exists(text_file)
    metadata = mm_archive.get_empty_metadata()
    metadata["series"] = "The Series"
    metadata["description"] = "Unknown"
    metadata["tags"] = "More Stuff"
    metadata["score"] = 5
    cbz_file = mm_comic_archive.create_cbz(build_dir, "CBZ-A", metadata=metadata)
    assert exists(cbz_file)
    shutil.copy(cbz_file, abspath(join(temp_dir, basename(cbz_file))))
    os.remove(cbz_file)
    # Create CBZ test file B
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Comic Book B"
    metadata["description"] = "Something"
    metadata["date"] = "2054-03-29"
    metadata["tags"] = "something"
    metadata["url"] = "www.page/thing"
    metadata["age_rating"] = "Unknown"
    metadata["score"] = 2
    cbz_file = mm_comic_archive.create_cbz(build_dir, "CBZ-B", metadata=metadata)
    assert exists(cbz_file)
    shutil.copy(cbz_file, abspath(join(sub_dir, basename(cbz_file))))
    os.remove(cbz_file)
    # Create EPUB test file C
    build_dir = mm_file_tools.get_temp_dir("builder")
    text_file = abspath(join(build_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "This is text!!!")
    assert exists(text_file)
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "This is a title."
    metadata["date"] = "2040-12-03"
    metadata["artist"] = "Person"
    metadata["publisher"] = "New Thing LLC"
    metadata["url"] = "www.HopefullyNotReal.website"
    metadata["age_rating"] = "Everyone"
    chapters = mm_epub.get_default_chapters(build_dir)
    epub_file = mm_epub.create_epub(chapters, metadata, build_dir)
    assert exists(epub_file)
    shutil.copy(epub_file, abspath(join(temp_dir, "EPUB-C.epub")))
    os.remove(epub_file)
    # Create CBZ test file D
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Book D"
    metadata["series"] = "The Series"
    metadata["series_number"] = "4"
    metadata["writer"] = "Different Person"
    metadata["tags"] = "these,are,tags"
    metadata["age_rating"] = "Teen"
    chapters = mm_epub.get_default_chapters(build_dir)
    epub_file = mm_epub.create_epub(chapters, metadata, build_dir)
    assert exists(epub_file)
    shutil.copy(epub_file, abspath(join(sub_dir, "EPUB-D.epub")))
    os.remove(epub_file)
    assert sorted(os.listdir(temp_dir)) == ["CBZ-A.cbz", "EPUB-C.epub", "sub"]
    assert sorted(os.listdir(sub_dir)) == ["CBZ-B.cbz", "EPUB-D.epub"]
    # Test finding missing title
    missing = mm_error.find_missing_fields(temp_dir, ["title"])
    assert len(missing) == 1
    assert basename(missing[0]) == "CBZ-A.cbz"
    # Test finding missing series
    missing = mm_error.find_missing_fields(temp_dir, ["series"])
    assert len(missing) == 2
    assert basename(missing[0]) == "EPUB-C.epub"
    assert basename(missing[1]) == "CBZ-B.cbz"
    # Test finding missing description
    missing = mm_error.find_missing_fields(temp_dir, ["description"])
    assert len(missing) == 2
    assert basename(missing[0]) == "EPUB-C.epub"
    assert basename(missing[1]) == "EPUB-D.epub"
    # Test finding missing date
    missing = mm_error.find_missing_fields(temp_dir, ["date"])
    assert len(missing) == 2
    assert basename(missing[0]) == "CBZ-A.cbz"
    assert basename(missing[1]) == "EPUB-D.epub"
    # Test finding missing artist
    missing = mm_error.find_missing_fields(temp_dir, ["artist", "writer"])
    assert len(missing) == 2
    assert basename(missing[0]) == "CBZ-A.cbz"
    assert basename(missing[1]) == "CBZ-B.cbz"
    # Test finding missing publisher
    missing = mm_error.find_missing_fields(temp_dir, ["publisher"])
    assert len(missing) == 3
    assert basename(missing[0]) == "CBZ-A.cbz"
    assert basename(missing[1]) == "CBZ-B.cbz"
    assert basename(missing[2]) == "EPUB-D.epub"
    # Test finding missing tags
    missing = mm_error.find_missing_fields(temp_dir, ["tags"])
    assert len(missing) == 1
    assert basename(missing[0]) == "EPUB-C.epub"
    # Test finding missing url
    missing = mm_error.find_missing_fields(temp_dir, ["url"])
    assert len(missing) == 2
    assert basename(missing[0]) == "CBZ-A.cbz"
    assert basename(missing[1]) == "EPUB-D.epub"
    # Test finding missing age_rating
    missing = mm_error.find_missing_fields(temp_dir, ["age_rating"])
    assert len(missing) == 2
    assert basename(missing[0]) == "CBZ-A.cbz"
    assert basename(missing[1]) == "CBZ-B.cbz"
    # Test finding missing score
    missing = mm_error.find_missing_fields(temp_dir, ["score"])
    assert len(missing) == 2
    assert basename(missing[0]) == "EPUB-C.epub"
    assert basename(missing[1]) == "EPUB-D.epub"
    # Test finding missing field that doesn't exist
    missing = mm_error.find_missing_fields(temp_dir, ["non_existant"])
    assert len(missing) == 4
    assert basename(missing[0]) == "CBZ-A.cbz"
    assert basename(missing[1]) == "EPUB-C.epub"
    assert basename(missing[2]) == "CBZ-B.cbz"
    assert basename(missing[3]) == "EPUB-D.epub"
