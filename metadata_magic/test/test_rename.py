#!/usr/bin/env python3

import os
import shutil
import tempfile
import metadata_magic.test as mm_test
import metadata_magic.config as mm_config
import metadata_magic.rename as mm_rename
import python_file_tools as pft
from os.path import abspath, basename, join

def test_rename_media_archives():
    """
    Tests the rename_media_archives function.
    """
    # Test renaming cbz archives
    config = mm_config.get_config([])
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_dir = abspath(join(temp_dir, "cbz_dir"))
        shutil.copytree(mm_test.ARCHIVE_CBZ_DIRECTORY, cbz_dir)
        mm_rename.rename_archives(cbz_dir, "{title}")
        assert sorted(os.listdir(cbz_dir)) == ["Cómic.CBZ", "Internal.CBZ", "No Page.cbz", "empty.cbz"]
        # Test that files aren't renamed if already correct
        mm_rename.rename_archives(cbz_dir, "{title}")
        assert sorted(os.listdir(cbz_dir)) == ["Cómic.CBZ", "Internal.CBZ", "No Page.cbz", "empty.cbz"]
        # Test with different keys
        mm_rename.rename_archives(cbz_dir, "[{date}]")
        assert sorted(os.listdir(cbz_dir)) == ["Internal.CBZ", "[2012-12-21].CBZ", "[2023-04-13].cbz", "empty.cbz"]
    # Test renaming epub archives
    with tempfile.TemporaryDirectory() as temp_dir:
        epub_dir = abspath(join(temp_dir, "epub_dir"))
        shutil.copytree(mm_test.ARCHIVE_EPUB_DIRECTORY, epub_dir)
        mm_rename.rename_archives(epub_dir, "{title}")
        assert sorted(os.listdir(epub_dir)) == ["Básic EPUB.epub", "Long Book.EPUB", "small.epub"]
        # Test that files aren't renamed if already correct
        mm_rename.rename_archives(epub_dir, "{title}")
        assert sorted(os.listdir(epub_dir)) == ["Básic EPUB.epub", "Long Book.EPUB", "small.epub"]
        # Test with different keys
        mm_rename.rename_archives(epub_dir, "[{writers}]")
        assert sorted(os.listdir(epub_dir)) == ["[Author].EPUB", "[Multiple,Writers].epub", "[Writer].epub"]
    # Test renaming archives with an invalid key/empty filename
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_dir = abspath(join(temp_dir, "cbz_dir"))
        shutil.copytree(mm_test.ARCHIVE_CBZ_DIRECTORY, cbz_dir)
        mm_rename.rename_archives(cbz_dir, "{unused}")
        assert sorted(os.listdir(cbz_dir)) == ["NoPage.cbz", "SubInfo.CBZ", "basic.CBZ", "empty.cbz"]
    # Test renaming archives while only allowing basic ASCII characters
    with tempfile.TemporaryDirectory() as temp_dir:
        cbz_dir = abspath(join(temp_dir, "cbz_dir"))
        shutil.copytree(mm_test.ARCHIVE_CBZ_DIRECTORY, cbz_dir)
        mm_rename.rename_archives(cbz_dir, "{title}", True)
        assert sorted(os.listdir(cbz_dir)) == ["Comic.CBZ", "Internal.CBZ", "No Page.cbz", "empty.cbz"]

def test_rename_json_pairs():
    """
    Tests the rename_json_pairs function.
    """
    # Test renaming JSON pairs
    config = mm_config.get_config([])
    with tempfile.TemporaryDirectory() as temp_dir:
        text_dir = abspath(join(temp_dir, "text"))
        image_dir = abspath(join(temp_dir, "image"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, text_dir)
        shutil.copytree(mm_test.PAIR_IMAGE_DIRECTORY, image_dir)
        mm_rename.rename_json_pairs(temp_dir, "{title}", config)
        assert sorted(os.listdir(text_dir)) == ["HTML.htm", "HTML.json", "TXT.JSON", "TXT.TXT"]
        assert sorted(os.listdir(image_dir)) == [".empty", "LRG.json", "LRG.webp", "LÑG.JPG", "LÑG.JSON", "Émpty.json", "Émpty.png"]
        # Test that files aren't renamed if not necessary
        mm_rename.rename_json_pairs(temp_dir, "{title}", config)
        assert sorted(os.listdir(text_dir)) == ["HTML.htm", "HTML.json", "TXT.JSON", "TXT.TXT"]
        assert sorted(os.listdir(image_dir)) == [".empty", "LRG.json", "LRG.webp", "LÑG.JPG", "LÑG.JSON", "Émpty.json", "Émpty.png"]
    # Test with multiple keys
    with tempfile.TemporaryDirectory() as temp_dir:
        text_dir = abspath(join(temp_dir, "text"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, text_dir)
        mm_rename.rename_json_pairs(text_dir, "{unused}-{writers}", config)
        assert sorted(os.listdir(text_dir)) == ["1-AAA.htm", "1-AAA.json", "2-BBB.JSON", "2-BBB.TXT"]
    # Test if JSON filename already exists
    with tempfile.TemporaryDirectory() as temp_dir:
        text_dir = abspath(join(temp_dir, "text"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, text_dir)
        pft.write_text_file(abspath(join(text_dir, "2.json")), "A")
        mm_rename.rename_json_pairs(text_dir, "{unused}", config)
        assert sorted(os.listdir(text_dir)) == ["1.htm", "1.json", "2-2.JSON", "2-2.TXT", "2.json"]
    # Test if media filename already exists
    with tempfile.TemporaryDirectory() as temp_dir:
        text_dir = abspath(join(temp_dir, "text"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, text_dir)
        pft.write_text_file(abspath(join(text_dir, "1.htm")), "A")
        mm_rename.rename_json_pairs(text_dir, "{unused}", config)
        assert sorted(os.listdir(text_dir)) == ["1-2.htm", "1-2.json", "1.htm", "2.JSON", "2.TXT"]
    # Test with an invalid filename template
    with tempfile.TemporaryDirectory() as temp_dir:
        text_dir = abspath(join(temp_dir, "text"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, text_dir)
        mm_rename.rename_json_pairs(text_dir, "{NONE}", config)
        assert sorted(os.listdir(text_dir)) == ["text 02.TXT", "text 02.txt.JSON", "text 1.htm", "text 1.json"]
    # Test renaming while only allowing basic ASCII characters
    with tempfile.TemporaryDirectory() as temp_dir:
        text_dir = abspath(join(temp_dir, "text"))
        image_dir = abspath(join(temp_dir, "image"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, text_dir)
        shutil.copytree(mm_test.PAIR_IMAGE_DIRECTORY, image_dir)
        mm_rename.rename_json_pairs(temp_dir, "{title}", config, True)
        assert sorted(os.listdir(text_dir)) == ["HTML.htm", "HTML.json", "TXT.JSON", "TXT.TXT"]
        assert sorted(os.listdir(image_dir)) == [".empty", "Empty.json", "Empty.png", "LNG.JPG", "LNG.JSON", "LRG.json", "LRG.webp"]

def test_sort_rename():
    """
    Tests the sort_rename function.
    """
    # Test sorting unlinked files
    with tempfile.TemporaryDirectory() as temp_dir:
        file_dir = abspath(join(temp_dir, "copy"))
        shutil.copytree(mm_test.BASIC_TEXT_DIRECTORY, file_dir)
        mm_rename.sort_rename(file_dir, "A [###]")
        assert sorted(os.listdir(file_dir)) == ["A [001].TXT", "A [002].txt", "A [003].txt"]
    # Test sorting JSON-media pairs
    with tempfile.TemporaryDirectory() as temp_dir:
        file_dir = abspath(join(temp_dir, "copy"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, file_dir)
        mm_rename.sort_rename(file_dir, "B#")
        assert sorted(os.listdir(file_dir)) == ["B1.htm", "B1.json", "B2.JSON", "B2.TXT"]
        # Test that files aren't renamed if unnecessary
        mm_rename.sort_rename(file_dir, "B#")
        assert sorted(os.listdir(file_dir)) == ["B1.htm", "B1.json", "B2.JSON", "B2.TXT"]
    # Test sorting a combination of JSON-media pairs and unlinked files
    with tempfile.TemporaryDirectory() as temp_dir:
        file_dir = abspath(join(temp_dir, "copy"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, file_dir)
        pft.write_text_file(abspath(join(file_dir, "text.txt")), "A")
        mm_rename.sort_rename(file_dir, "#")
        assert sorted(os.listdir(file_dir)) == ["1.htm", "1.json", "2.JSON", "2.TXT", "3.txt"]
    # Test Using a different starting index
    with tempfile.TemporaryDirectory() as temp_dir:
        file_dir = abspath(join(temp_dir, "copy"))
        shutil.copytree(mm_test.BASIC_TEXT_DIRECTORY, file_dir)
        mm_rename.sort_rename(file_dir, "[##]", 42)
        assert sorted(os.listdir(file_dir)) == ["[42].TXT", "[43].txt", "[44].txt"]
        # Test that subdirectories are not affected
        mm_rename.sort_rename(temp_dir, "NONE [#####]", 500)
        assert sorted(os.listdir(file_dir)) == ["[42].TXT", "[43].txt", "[44].txt"]
    # Test limiting to a certain file pattern
    with tempfile.TemporaryDirectory() as temp_dir:
        file_dir = abspath(join(temp_dir, "copy"))
        shutil.copytree(mm_test.PAIR_TEXT_DIRECTORY, file_dir)
        pft.write_text_file(abspath(join(file_dir, "text.txt")), "A")
        mm_rename.sort_rename(file_dir, "#", file_pattern=r"\.txt$")
        assert sorted(os.listdir(file_dir)) == ["1.JSON", "1.TXT", "2.txt", "text 1.htm", "text 1.json"]
        mm_rename.sort_rename(file_dir, "A!", file_pattern=r"2")
        assert sorted(os.listdir(file_dir)) == ["1.JSON", "1.TXT", "A!.txt", "text 1.htm", "text 1.json"]
    # Test renaming a single file
    with tempfile.TemporaryDirectory() as temp_dir:
        pft.write_text_file(abspath(join(temp_dir, "AAA.png")), "AAA")
        mm_rename.sort_rename(temp_dir, "Title", 500)
        assert sorted(os.listdir(temp_dir)) == ["Title [500].png"]
        mm_rename.sort_rename(temp_dir, "Title")
        assert sorted(os.listdir(temp_dir)) == ["Title.png"]
        mm_rename.sort_rename(temp_dir, "#")
        assert sorted(os.listdir(temp_dir)) == ["1.png"]
