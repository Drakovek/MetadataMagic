#!/usr/bin/env python3

import os
import shutil
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.comic_archive as mm_comic_archive
import metadata_magic.archive.comic_archive_update as mm_comic_archive_update
from os.path import abspath, exists, join

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
    mm_comic_archive_update.mass_update_cbzs(temp_dir, metadata)
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
    mm_comic_archive_update.mass_update_cbzs(temp_dir, metadata)
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
    mm_comic_archive_update.mass_update_cbzs(temp_dir, metadata)
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file_3)
    assert read_meta["title"] == "This is a title!"
    assert read_meta["artist"] == "New Guy"
    assert read_meta["writer"] == "Writer Lad"
    assert read_meta["cover_artist"] == "Other"
    assert read_meta["publisher"] == "New Publisher"
    assert read_meta["age_rating"] == "Everyone"
    assert read_meta["score"] == "3"
    assert sorted(os.listdir(temp_dir)) == ["Name", "Name.cbz", "new.cbz", "other.cbz"]
    # Test updating content rating
    metadata = mm_archive.get_empty_metadata()
    metadata["age_rating"] = "Everyone"
    mm_comic_archive_update.mass_update_cbzs(temp_dir, metadata)
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
    mm_comic_archive_update.mass_update_cbzs(temp_dir, metadata)
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
    mm_comic_archive_update.mass_update_cbzs(temp_dir, metadata)
    read_meta = mm_comic_archive.get_info_from_cbz(cbz_file_1)
    assert read_meta["title"] == "This is a title!"
    assert read_meta["artist"] == "Madam Anonymous"
    assert read_meta["writer"] == "Writer Lad"
    assert read_meta["cover_artist"] == "Other"
    assert read_meta["publisher"] == "Blah Inc."
    assert read_meta["age_rating"] == "Everyone"
    assert read_meta["score"] == "5"
    assert sorted(os.listdir(temp_dir)) == ["Name", "Name.cbz", "new.cbz", "other.cbz"]
