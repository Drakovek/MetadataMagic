#!/usr/bin/env python3

import os
import shutil
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.epub as mm_epub
import metadata_magic.archive.update as mm_update
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.comic_archive as mm_comic_archive
from os.path import abspath, exists, join

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
    existing_metadata["writer"] = "Writer"
    existing_metadata["artist"] = "Artist"
    existing_metadata["cover_artist"] = "Cover Artist"
    existing_metadata["publisher"] = "Publisher"
    existing_metadata["tags"] = "Some,Tags"
    existing_metadata["url"] = "a/page/url"
    existing_metadata["age_rating"] = "Everyone"
    existing_metadata["score"] = "3"
    new_metadata = mm_update.update_fields(existing_metadata, updating_metadata) 
    assert new_metadata["title"] == "This is a title."
    assert new_metadata["series"] == "Series Name"
    assert new_metadata["series_number"] == "5"
    assert new_metadata["series_total"] == "10"
    assert new_metadata["description"] == "Some words and such."
    assert new_metadata["date"] == "2020-02-02"
    assert new_metadata["writer"] == "Writer"
    assert new_metadata["artist"] == "Artist"
    assert new_metadata["cover_artist"] == "Cover Artist"
    assert new_metadata["publisher"] == "Publisher"
    assert new_metadata["tags"] == "Some,Tags"
    assert new_metadata["url"] == "a/page/url"
    assert new_metadata["age_rating"] == "Everyone"
    assert new_metadata["score"] == "3"
    # Test updating some fields
    updating_metadata["title"] = "New Title"
    updating_metadata["series_number"] = "2"
    updating_metadata["description"] = "New Description"
    updating_metadata["writer"] = "New Author"
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
    assert new_metadata["writer"] == "New Author"
    assert new_metadata["artist"] == "Artist"
    assert new_metadata["cover_artist"] == "Cover Artist"
    assert new_metadata["publisher"] == "New Publisher"
    assert new_metadata["tags"] == "Some,Tags"
    assert new_metadata["url"] == "/new/page"
    assert new_metadata["age_rating"] == "Everyone"
    assert new_metadata["score"] == "5"

def test_mass_update_cbzs():
    """
    Tests the mass_update_cbzs function.
    """
    # Create test CBZ files
    temp_dir = mm_file_tools.get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "This is text.")
    assert exists(text_file)
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "This is a title!"
    metadata["artist"] = "Person"
    metadata["writer"] = "New"
    metadata["cover_artist"] = "Cover"
    metadata["publisher"] = "Nobody"
    metadata["age_rating"] = "Unknown"
    metadata["score"] = 3
    cbz_file_1 = mm_comic_archive.create_cbz(temp_dir, "Name", metadata=metadata)
    cbz_file_2 = abspath(join(temp_dir, "new.cbz"))
    cbz_file_3 = abspath(join(temp_dir, "other.cbz"))
    shutil.copy(cbz_file_1, cbz_file_2)
    shutil.copy(cbz_file_1, cbz_file_3)
    assert exists(cbz_file_1)
    assert exists(cbz_file_2)
    assert exists(cbz_file_3)
    assert sorted(os.listdir(temp_dir)) == ["Name", "Name.cbz", "new.cbz", "other.cbz"]
    # Test updating publisher
    metadata = mm_archive.get_empty_metadata()
    metadata["publisher"] = "New Publisher"
    mm_update.mass_update_cbzs(temp_dir, metadata)
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file_1)
    assert read_meta["title"] == "This is a title!"
    assert read_meta["artist"] == "Person"
    assert read_meta["writer"] == "New"
    assert read_meta["cover_artist"] == "Cover"
    assert read_meta["publisher"] == "New Publisher"
    assert read_meta["age_rating"] == "Unknown"
    assert sorted(os.listdir(temp_dir)) == ["Name", "Name.cbz", "new.cbz", "other.cbz"]
    # Test updating artists
    metadata = mm_archive.get_empty_metadata()
    metadata["artist"] = "New Guy"
    metadata["writer"] = "Writer Lad"
    metadata["cover_artist"] = "Other"
    mm_update.mass_update_cbzs(temp_dir, metadata)
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file_2)
    assert read_meta["title"] == "This is a title!"
    assert read_meta["artist"] == "New Guy"
    assert read_meta["writer"] == "Writer Lad"
    assert read_meta["cover_artist"] == "Other"
    assert read_meta["publisher"] == "New Publisher"
    assert read_meta["age_rating"] == "Unknown"
    assert read_meta["score"] == "3"
    assert sorted(os.listdir(temp_dir)) == ["Name", "Name.cbz", "new.cbz", "other.cbz"]
    # Test updating age rating
    metadata = mm_archive.get_empty_metadata()
    metadata["age_rating"] = "Everyone"
    mm_update.mass_update_cbzs(temp_dir, metadata)
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file_3)
    assert read_meta["title"] == "This is a title!"
    assert read_meta["artist"] == "New Guy"
    assert read_meta["writer"] == "Writer Lad"
    assert read_meta["cover_artist"] == "Other"
    assert read_meta["publisher"] == "New Publisher"
    assert read_meta["age_rating"] == "Everyone"
    assert read_meta["score"] == "3"
    assert sorted(os.listdir(temp_dir)) == ["Name", "Name.cbz", "new.cbz", "other.cbz"]
    # Test updating score
    metadata = mm_archive.get_empty_metadata()
    metadata["score"] = 5
    mm_update.mass_update_cbzs(temp_dir, metadata)
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file_2)
    assert read_meta["title"] == "This is a title!"
    assert read_meta["artist"] == "New Guy"
    assert read_meta["writer"] == "Writer Lad"
    assert read_meta["cover_artist"] == "Other"
    assert read_meta["publisher"] == "New Publisher"
    assert read_meta["age_rating"] == "Everyone"
    assert read_meta["score"] == "5"
    assert sorted(os.listdir(temp_dir)) == ["Name", "Name.cbz", "new.cbz", "other.cbz"]
    # Test updating multiple fields
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Blah"
    metadata["artist"] = "Madam Anonymous"
    metadata["writer"] = None
    metadata["publisher"] = "Blah Inc."
    metadata["score"] = None
    mm_update.mass_update_cbzs(temp_dir, metadata)
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file_1)
    assert read_meta["title"] == "Blah"
    assert read_meta["artist"] == "Madam Anonymous"
    assert read_meta["writer"] == "Writer Lad"
    assert read_meta["cover_artist"] == "Other"
    assert read_meta["publisher"] == "Blah Inc."
    assert read_meta["age_rating"] == "Everyone"
    assert read_meta["score"] == "5"
    assert sorted(os.listdir(temp_dir)) == ["Name", "Name.cbz", "new.cbz", "other.cbz"]

def test_mass_update_epubs():
    """
    Tests the mass_update_epubs function.
    """
    # Create test CBZ files
    temp_dir = mm_file_tools.get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    mm_file_tools.write_text_file(text_file, "This is text.")
    assert exists(text_file)
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Epub Title!"
    metadata["artist"] = "Art Person"
    metadata["writer"] = "Writer Person"
    metadata["cover_artist"] = "Cover Person"
    metadata["publisher"] = "BookCo"
    metadata["age_rating"] = "Everyone"
    metadata["score"] = 4
    chapters = mm_epub.get_default_chapters(temp_dir)
    epub_file_1 = mm_epub.create_epub(chapters, metadata, temp_dir)
    epub_file_2 = abspath(join(temp_dir, "new.epub"))
    epub_file_3 = abspath(join(temp_dir, "other.epub"))
    shutil.copy(epub_file_1, epub_file_2)
    shutil.copy(epub_file_1, epub_file_3)
    assert exists(epub_file_1)
    assert exists(epub_file_2)
    assert exists(epub_file_3)
    assert sorted(os.listdir(temp_dir)) == ["Epub Title!.epub", "new.epub", "other.epub", "text.txt"]
    # Test updating publisher
    metadata = mm_archive.get_empty_metadata()
    metadata["publisher"] = "New Publisher"
    mm_update.mass_update_epubs(temp_dir, metadata)
    read_meta = mm_epub.get_info_from_epub(epub_file_1)
    assert read_meta["title"] == "Epub Title!"
    assert read_meta["artist"] == "Art Person"
    assert read_meta["writer"] == "Writer Person"
    assert read_meta["cover_artist"] == "Cover Person"
    assert read_meta["publisher"] == "New Publisher"
    assert read_meta["age_rating"] == "Everyone"
    assert read_meta["score"] == "4"
    assert sorted(os.listdir(temp_dir)) == ["Epub Title!.epub", "new.epub", "other.epub", "text.txt"]
    # Test updating artists
    metadata = mm_archive.get_empty_metadata()
    metadata["artist"] = "New Guy"
    metadata["writer"] = "Writer Lad"
    metadata["cover_artist"] = "Other"
    mm_update.mass_update_epubs(temp_dir, metadata)
    read_meta = mm_epub.get_info_from_epub(epub_file_2)
    assert read_meta["title"] == "Epub Title!"
    assert read_meta["artist"] == "New Guy"
    assert read_meta["writer"] == "Writer Lad"
    assert read_meta["cover_artist"] == "Other"
    assert read_meta["publisher"] == "New Publisher"
    assert read_meta["age_rating"] == "Everyone"
    assert read_meta["score"] == "4"
    assert sorted(os.listdir(temp_dir)) == ["Epub Title!.epub", "new.epub", "other.epub", "text.txt"]
    # Test updating age rating
    metadata = mm_archive.get_empty_metadata()
    metadata["age_rating"] = "Teen"
    mm_update.mass_update_epubs(temp_dir, metadata)
    read_meta = mm_epub.get_info_from_epub(epub_file_3)
    assert read_meta["title"] == "Epub Title!"
    assert read_meta["artist"] == "New Guy"
    assert read_meta["writer"] == "Writer Lad"
    assert read_meta["cover_artist"] == "Other"
    assert read_meta["publisher"] == "New Publisher"
    assert read_meta["age_rating"] == "Teen"
    assert read_meta["score"] == "4"
    assert sorted(os.listdir(temp_dir)) == ["Epub Title!.epub", "new.epub", "other.epub", "text.txt"]
    # Test updating score
    metadata = mm_archive.get_empty_metadata()
    metadata["score"] = 5
    mm_update.mass_update_epubs(temp_dir, metadata)
    read_meta = mm_epub.get_info_from_epub(epub_file_2)
    assert read_meta["title"] == "Epub Title!"
    assert read_meta["artist"] == "New Guy"
    assert read_meta["writer"] == "Writer Lad"
    assert read_meta["cover_artist"] == "Other"
    assert read_meta["publisher"] == "New Publisher"
    assert read_meta["age_rating"] == "Teen"
    assert read_meta["score"] == "5"
    assert sorted(os.listdir(temp_dir)) == ["Epub Title!.epub", "new.epub", "other.epub", "text.txt"]
    # Test updating multiple fields
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Blah"
    metadata["artist"] = "Madam Anonymous"
    metadata["writer"] = None
    metadata["publisher"] = "Blah Inc."
    metadata["score"] = None
    mm_update.mass_update_epubs(temp_dir, metadata)
    read_meta = mm_epub.get_info_from_epub(epub_file_1)
    assert read_meta["title"] == "Blah"
    assert read_meta["artist"] == "Madam Anonymous"
    assert read_meta["writer"] == "Writer Lad"
    assert read_meta["cover_artist"] == "Other"
    assert read_meta["publisher"] == "Blah Inc."
    assert read_meta["age_rating"] == "Teen"
    assert read_meta["score"] == "5"
    assert sorted(os.listdir(temp_dir)) == ["Epub Title!.epub", "new.epub", "other.epub", "text.txt"]
