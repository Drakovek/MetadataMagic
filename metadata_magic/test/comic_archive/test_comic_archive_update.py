#!/usr/bin/env python3

from metadata_magic.main.meta_reader import get_empty_metadata
from metadata_magic.main.comic_archive.comic_archive import create_cbz
from metadata_magic.main.comic_archive.comic_archive import get_info_from_cbz
from metadata_magic.main.comic_archive.comic_archive_update import mass_update_cbzs
from metadata_magic.main.file_tools.file_tools import get_temp_dir
from metadata_magic.main.file_tools.file_tools import write_text_file
from os import listdir
from os.path import abspath, exists, join
from shutil import copy

def test_mass_update_cbzs():
    """
    Tests the mass_update_cbzs function.
    """
    # Create test CBZ files
    temp_dir = get_temp_dir()
    text_file = abspath(join(temp_dir, "text.txt"))
    write_text_file(text_file, "This is text.")
    assert exists(text_file)
    metadata = get_empty_metadata()
    metadata["title"] = "This is a title!"
    metadata["artist"] = "Person"
    metadata["writer"] = "New"
    metadata["cover_artist"] = "Cover"
    metadata["publisher"] = "Nobody"
    metadata["age_rating"] = "Unknown"
    metadata["score"] = 3
    cbz_file_1 = create_cbz(temp_dir, "Name", metadata=metadata)
    cbz_file_2 = abspath(join(temp_dir, "new.cbz"))
    cbz_file_3 = abspath(join(temp_dir, "other.cbz"))
    copy(cbz_file_1, cbz_file_2)
    copy(cbz_file_1, cbz_file_3)
    assert exists(cbz_file_1)
    assert exists(cbz_file_2)
    assert exists(cbz_file_3)
    assert sorted(listdir(temp_dir)) == ["Name.cbz", "new.cbz", "other.cbz", "text"]
    # Test updating publisher
    metadata = get_empty_metadata()
    metadata["publisher"] = "New Publisher"
    mass_update_cbzs(temp_dir, metadata)
    read_meta = get_info_from_cbz(cbz_file_1)
    assert read_meta["title"] == "This is a title!"
    assert read_meta["artist"] == "Person"
    assert read_meta["writer"] == "New"
    assert read_meta["cover_artist"] == "Cover"
    assert read_meta["publisher"] == "New Publisher"
    assert read_meta["age_rating"] == "Unknown"
    assert sorted(listdir(temp_dir)) == ["Name.cbz", "new.cbz", "other.cbz", "text"]
    # Test updating artists
    metadata = get_empty_metadata()
    metadata["artist"] = "New Guy"
    metadata["writer"] = "Writer Lad"
    metadata["cover_artist"] = "Other"
    mass_update_cbzs(temp_dir, metadata)
    read_meta = get_info_from_cbz(cbz_file_2)
    assert read_meta["title"] == "This is a title!"
    assert read_meta["artist"] == "New Guy"
    assert read_meta["writer"] == "Writer Lad"
    assert read_meta["cover_artist"] == "Other"
    assert read_meta["publisher"] == "New Publisher"
    assert read_meta["age_rating"] == "Unknown"
    assert read_meta["score"] == "3"
    assert sorted(listdir(temp_dir)) == ["Name.cbz", "new.cbz", "other.cbz", "text"]
    # Test updating age rating
    metadata = get_empty_metadata()
    metadata["age_rating"] = "Everyone"
    mass_update_cbzs(temp_dir, metadata)
    read_meta = get_info_from_cbz(cbz_file_3)
    assert read_meta["title"] == "This is a title!"
    assert read_meta["artist"] == "New Guy"
    assert read_meta["writer"] == "Writer Lad"
    assert read_meta["cover_artist"] == "Other"
    assert read_meta["publisher"] == "New Publisher"
    assert read_meta["age_rating"] == "Everyone"
    assert read_meta["score"] == "3"
    assert sorted(listdir(temp_dir)) == ["Name.cbz", "new.cbz", "other.cbz", "text"]
    # Test updating content rating
    metadata = get_empty_metadata()
    metadata["age_rating"] = "Everyone"
    mass_update_cbzs(temp_dir, metadata)
    read_meta = get_info_from_cbz(cbz_file_3)
    assert read_meta["title"] == "This is a title!"
    assert read_meta["artist"] == "New Guy"
    assert read_meta["writer"] == "Writer Lad"
    assert read_meta["cover_artist"] == "Other"
    assert read_meta["publisher"] == "New Publisher"
    assert read_meta["age_rating"] == "Everyone"
    assert read_meta["score"] == "3"
    assert sorted(listdir(temp_dir)) == ["Name.cbz", "new.cbz", "other.cbz", "text"]
    # Test updating score
    metadata = get_empty_metadata()
    metadata["score"] = 5
    mass_update_cbzs(temp_dir, metadata)
    read_meta = get_info_from_cbz(cbz_file_2)
    assert read_meta["title"] == "This is a title!"
    assert read_meta["artist"] == "New Guy"
    assert read_meta["writer"] == "Writer Lad"
    assert read_meta["cover_artist"] == "Other"
    assert read_meta["publisher"] == "New Publisher"
    assert read_meta["age_rating"] == "Everyone"
    assert read_meta["score"] == "5"
    assert sorted(listdir(temp_dir)) == ["Name.cbz", "new.cbz", "other.cbz", "text"]
    # Test updating multiple fields
    metadata = get_empty_metadata()
    metadata["title"] = "Blah"
    metadata["artist"] = "Madam Anonymous"
    metadata["writer"] = None
    metadata["publisher"] = "Blah Inc."
    metadata["score"] = None
    mass_update_cbzs(temp_dir, metadata)
    read_meta = get_info_from_cbz(cbz_file_1)
    assert read_meta["title"] == "This is a title!"
    assert read_meta["artist"] == "Madam Anonymous"
    assert read_meta["writer"] == "Writer Lad"
    assert read_meta["cover_artist"] == "Other"
    assert read_meta["publisher"] == "Blah Inc."
    assert read_meta["age_rating"] == "Everyone"
    assert read_meta["score"] == "5"
    assert sorted(listdir(temp_dir)) == ["Name.cbz", "new.cbz", "other.cbz", "text"]