#!/usr/bin/env python3

import os
import shutil
import tempfile
import metadata_magic.test as mm_test
import metadata_magic.archive as mm_archive
import metadata_magic.archive.epub as mm_epub
import metadata_magic.archive.update as mm_update
import metadata_magic.archive.comic_archive as mm_comic_archive
from os.path import abspath, join

def test_update_fields():
    """
    Tests the update_fields function.
    """
    # Test updating nothing
    existing_metadata = mm_archive.get_empty_metadata()
    updating_metadata = mm_archive.get_empty_metadata()
    existing_metadata["title"] = "This is a title."
    existing_metadata["series"] = "Series Name"
    existing_metadata["series_number"] = "5"
    existing_metadata["series_total"] = "10"
    existing_metadata["description"] = "Some words and such."
    existing_metadata["date"] = "2020-02-02"
    existing_metadata["writers"] = ["Writer"]
    existing_metadata["artists"] = ["Artist"]
    existing_metadata["cover_artists"] = ["Cover Artist"]
    existing_metadata["publisher"] = "Publisher"
    existing_metadata["tags"] = ["Some", "Tags"]
    existing_metadata["url"] = "a/page/url"
    existing_metadata["age_rating"] = "Everyone"
    existing_metadata["score"] = "3"
    existing_metadata["non-standard"] = "Blah!"
    new_metadata = mm_update.update_fields(existing_metadata, updating_metadata) 
    assert new_metadata["title"] == "This is a title."
    assert new_metadata["series"] == "Series Name"
    assert new_metadata["series_number"] == "5"
    assert new_metadata["series_total"] == "10"
    assert new_metadata["description"] == "Some words and such."
    assert new_metadata["date"] == "2020-02-02"
    assert new_metadata["writers"] == ["Writer"]
    assert new_metadata["artists"] == ["Artist"]
    assert new_metadata["cover_artists"] == ["Cover Artist"]
    assert new_metadata["publisher"] == "Publisher"
    assert new_metadata["tags"] == ["Some", "Tags"]
    assert new_metadata["url"] == "a/page/url"
    assert new_metadata["age_rating"] == "Everyone"
    assert new_metadata["score"] == "3"
    assert new_metadata["non-standard"] == "Blah!"
    # Test updating some fields
    updating_metadata["title"] = "New Title"
    updating_metadata["series_number"] = "2"
    updating_metadata["description"] = "New Description"
    updating_metadata["writers"] = ["New Author"]
    updating_metadata["publisher"] = "New Publisher"
    updating_metadata["url"] = "/new/page"
    updating_metadata["score"] = "5"
    new_metadata = mm_update.update_fields(existing_metadata, updating_metadata) 
    assert new_metadata["title"] == "New Title"
    assert new_metadata["series"] == "Series Name"
    assert new_metadata["series_number"] == "2"
    assert new_metadata["series_total"] == "10"
    assert new_metadata["description"] == "New Description"
    assert new_metadata["date"] == "2020-02-02"
    assert new_metadata["writers"] == ["New Author"]
    assert new_metadata["artists"] == ["Artist"]
    assert new_metadata["cover_artists"] == ["Cover Artist"]
    assert new_metadata["publisher"] == "New Publisher"
    assert new_metadata["tags"] == ["Some", "Tags"]
    assert new_metadata["url"] == "/new/page"
    assert new_metadata["age_rating"] == "Everyone"
    assert new_metadata["score"] == "5"

def test_mass_update_archives():
    """
    Tests the mass_update_archives function.
    """
    # Copy over archive files
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_file = abspath(join(temp_dir, "cbz.CBZ"))
        epub_file = abspath(join(temp_dir, "epub.epub"))
        shutil.copy(abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "basic.CBZ")), cbz_file)
        shutil.copy(abspath(join(mm_test.ARCHIVE_EPUB_DIRECTORY, "small.epub")), epub_file)
        # Test updating the publisher
        metadata = mm_archive.get_empty_metadata()
        metadata["cover_id"] = None
        metadata["publisher"] = "Updated Publisher"
        mm_update.mass_update_archives(temp_dir, metadata)
        read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
        assert read_meta["title"] == "Cómic"
        assert read_meta["artists"] == ["Illustrator"]
        assert read_meta["publisher"] == "Updated Publisher"
        read_meta = mm_epub.get_info_from_epub(epub_file)
        assert read_meta["title"] is None
        assert read_meta["writers"] == ["Writer"]
        assert read_meta["publisher"] == "Updated Publisher"
        # Test updating artists
        metadata["artists"] = ["Updated", "Artists"]
        metadata["writers"] = ["Updated", "Authors"]
        metadata["cover_artists"] = ["Updated", "Cover Artists"]
        mm_update.mass_update_archives(temp_dir, metadata)
        read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
        assert read_meta["title"] == "Cómic"
        assert read_meta["artists"] == ["Updated", "Artists"]
        assert read_meta["writers"] == ["Updated", "Authors"]
        assert read_meta["cover_artists"] == ["Updated", "Cover Artists"]
        assert read_meta["publisher"] == "Updated Publisher"
        read_meta = mm_epub.get_info_from_epub(epub_file)
        assert read_meta["title"] is None
        assert read_meta["artists"] == ["Updated", "Artists"]
        assert read_meta["writers"] == ["Updated", "Authors"]
        assert read_meta["cover_artists"] == ["Updated", "Cover Artists"]
        assert read_meta["publisher"] == "Updated Publisher"
        # Test updating multiple fields
        metadata["age_rating"] = "Teen"
        metadata["score"] = "5"
        mm_update.mass_update_archives(temp_dir, metadata)
        read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
        assert read_meta["title"] == "Cómic"
        assert read_meta["artists"] == ["Updated", "Artists"]
        assert read_meta["age_rating"] == "Teen"
        assert read_meta["score"] == "5"
        read_meta = mm_epub.get_info_from_epub(epub_file)
        assert read_meta["title"] is None
        assert read_meta["artists"] == ["Updated", "Artists"]
        assert read_meta["age_rating"] == "Teen"
        assert read_meta["score"] == "5"
        # Test updating cover images
        assert os.stat(cbz_file).st_size < 1200
        assert os.stat(epub_file).st_size < 5000
        metadata["description"] = "Updated Cover Image"
        mm_update.mass_update_archives(temp_dir, metadata, update_covers=True)
        read_meta = mm_comic_archive.get_info_from_cbz(cbz_file)
        assert read_meta["title"] == "Cómic"
        assert read_meta["artists"] == ["Updated", "Artists"]
        assert read_meta["description"] == "Updated Cover Image"
        read_meta = mm_epub.get_info_from_epub(epub_file)
        assert read_meta["title"] is None
        assert read_meta["artists"] == ["Updated", "Artists"]
        assert read_meta["description"] == "Updated Cover Image"
        assert os.stat(cbz_file).st_size < 1200
        assert os.stat(epub_file).st_size > 10000
