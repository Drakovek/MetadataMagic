#!/usr/bin/env python3

import os
import shutil
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.epub as mm_epub
import metadata_magic.archive.archive as mm_archive
import metadata_magic.archive.bulk_archive as mm_bulk_archive
import metadata_magic.archive.comic_archive as mm_comic_archive
from os.path import abspath, exists, join

def test_archive_all_media():
    """
    Tests the archive_all_media function.
    """
    # Create test files
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "image1.jpg")), "Blah")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "image1.json")), {"title": "First Image"})
    mm_file_tools.write_text_file(abspath(join(temp_dir, "image2.png")), "Blah")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "image2.json")), {"title": "Long", "caption":"A"*6000})
    mm_file_tools.write_text_file(abspath(join(temp_dir, "text1.txt")), "Stuff")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "text1.json")), {"title": "Book", "writer":"Person"})
    mm_file_tools.write_text_file(abspath(join(temp_dir, "text2.html")), "<p>Thing</p>")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "text2.json")), {"title": "Second Book", "writer":"Other"})
    sub_dir = abspath(join(temp_dir, "sub_dir"))
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(abspath(join(sub_dir, "sub_image.cbz")), "Duplicate CBZ")
    mm_file_tools.write_text_file(abspath(join(sub_dir, "sub_image.jpeg")), "Blah")
    mm_file_tools.write_json_file(abspath(join(sub_dir, "sub_image.json")), {"title": "Sub Image"})
    mm_file_tools.write_text_file(abspath(join(sub_dir, "sub_text.epub")), "Duplicate EPUB")
    mm_file_tools.write_text_file(abspath(join(sub_dir, "sub_text.htm")), "<p>Other</p>")
    mm_file_tools.write_json_file(abspath(join(sub_dir, "sub_text.json")), {"title": "Sub Text", "writers":["Writer"]})
    mm_file_tools.write_text_file(abspath(join(temp_dir, "unsupported.blah")), "Blah")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "unsupported.json")), {"title": "Unsupported"})
    mm_file_tools.write_text_file(abspath(join(temp_dir, "thing.png")), "Blah")
    mm_file_tools.write_text_file(abspath(join(sub_dir, "other.txt")), "Blah")
    files = sorted(os.listdir(temp_dir))
    assert files == ["image1.jpg", "image1.json", "image2.json", "image2.png", "sub_dir", 
            "text1.json", "text1.txt", "text2.html", "text2.json", "thing.png", "unsupported.blah", "unsupported.json"]
    files = sorted(os.listdir(sub_dir))
    assert files == ["other.txt", "sub_image.cbz", "sub_image.jpeg", "sub_image.json",
            "sub_text.epub", "sub_text.htm", "sub_text.json"]
    # Archive all supported files
    assert mm_bulk_archive.archive_all_media(temp_dir)
    assert sorted(os.listdir(temp_dir)) == ["image1.cbz", "image2.epub", "sub_dir", "text1.epub", "text2.epub",
            "thing.png", "unsupported.blah", "unsupported.json"]
    assert sorted(os.listdir(sub_dir)) == ["other.txt", "sub_image-2.cbz", "sub_image.cbz",
            "sub_text-2.epub", "sub_text.epub"]
    # Test that metadata in archives is correct
    assert mm_comic_archive.get_info_from_cbz(abspath(join(temp_dir, "image1.cbz")))["title"] == "First Image"
    assert mm_epub.get_info_from_epub(abspath(join(temp_dir, "image2.epub")))["title"] == "Long"
    assert mm_comic_archive.get_info_from_cbz(abspath(join(sub_dir, "sub_image-2.cbz")))["title"] == "Sub Image"
    assert mm_file_tools.read_text_file(abspath(join(sub_dir, "sub_image.cbz"))) == "Duplicate CBZ"
    assert mm_epub.get_info_from_epub(abspath(join(temp_dir, "text1.epub")))["title"] == "Book"
    assert mm_epub.get_info_from_epub(abspath(join(temp_dir, "text2.epub")))["writers"] == "Other"
    assert mm_epub.get_info_from_epub(abspath(join(sub_dir, "sub_text-2.epub")))["title"] == "Sub Text"
    assert mm_file_tools.read_text_file(abspath(join(sub_dir, "sub_text.epub"))) == "Duplicate EPUB"
    # Test that the internal file structure of archives are correct
    cbz_extract = abspath(join(temp_dir, "cbz_extract"))
    os.mkdir(cbz_extract)
    mm_file_tools.extract_zip(abspath(join(temp_dir, "image1.cbz")), cbz_extract)
    assert sorted(os.listdir(cbz_extract)) == ["ComicInfo.xml", "First Image"]
    assert sorted(os.listdir(abspath(join(cbz_extract, "First Image")))) == ["First Image.jpg", "First Image.json"]
    epub_extract = abspath(join(temp_dir, "epub_extract"))
    os.mkdir(epub_extract)
    mm_file_tools.extract_zip(abspath(join(temp_dir, "text1.epub")), epub_extract)
    assert sorted(os.listdir(epub_extract)) == ["EPUB", "META-INF", "mimetype"]
    epub_extract = abspath(join(epub_extract, "EPUB"))
    assert sorted(os.listdir(epub_extract)) == ["content", "content.opf", "images", "nav.xhtml", "original", "style", "toc.ncx"]
    epub_extract = abspath(join(epub_extract, "original"))
    assert sorted(os.listdir(epub_extract)) == ["Book.json", "Book.txt"]
    # Test bulk archiving while formatting the titles
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "image.png")), "Blah")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "image.json")), {"title": "just a test"})
    assert sorted(os.listdir(temp_dir)) == ["image.json", "image.png"]
    assert mm_bulk_archive.archive_all_media(temp_dir, True)    
    assert sorted(os.listdir(temp_dir)) == ["image.cbz"]
    assert mm_comic_archive.get_info_from_cbz(abspath(join(temp_dir, "image.cbz")))["title"] == "Just a Test"
    cbz_extract = abspath(join(temp_dir, "cbz_extract"))
    os.mkdir(cbz_extract)
    mm_file_tools.extract_zip(abspath(join(temp_dir, "image.cbz")), cbz_extract)
    assert sorted(os.listdir(cbz_extract)) == ["ComicInfo.xml", "Just a Test"]
    internal_dir = abspath(join(cbz_extract, "Just a Test"))
    assert sorted(os.listdir(internal_dir)) == ["Just a Test.json", "Just a Test.png"]
    # Test with a different description cutoff point
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "short.png")), "BLAH")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "short.json")), {"title":"Short", "caption":"A"*200})
    mm_file_tools.write_text_file(abspath(join(temp_dir, "long.png")), "BLAH")
    mm_file_tools.write_json_file(abspath(join(temp_dir, "long.json")), {"title":"Long", "caption":"A"*600})
    assert mm_bulk_archive.archive_all_media(temp_dir, description_length=500)
    assert sorted(os.listdir(temp_dir)) == ["long.epub", "short.cbz"]

def test_extract_cbz():
    """
    Tests the extract_cbz function
    """
    # Create test files
    temp_dir = mm_file_tools.get_temp_dir()
    build_dir = mm_file_tools.get_temp_dir("dvk_test_builder")
    mm_file_tools.write_text_file(abspath(join(build_dir, "image1.jpg")), "Blah")
    mm_file_tools.write_text_file(abspath(join(build_dir, "image2.jpg")), "Blah")
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Simple"
    cbz_file = mm_comic_archive.create_cbz(build_dir, name="simple", metadata=metadata)
    shutil.copy(cbz_file, temp_dir)
    build_dir = mm_file_tools.get_temp_dir("dvk_test_builder")
    a_dir = abspath(join(build_dir, "A"))
    b_dir = abspath(join(build_dir, "B"))
    os.mkdir(a_dir)
    os.mkdir(b_dir)
    mm_file_tools.write_text_file(abspath(join(a_dir, "imageA.png")), "Blah")
    mm_file_tools.write_text_file(abspath(join(b_dir, "imageB1.png")), "Blah")
    mm_file_tools.write_text_file(abspath(join(b_dir, "imageB2.png")), "Blah")
    metadata["title"] = "Folders"
    cbz_file = mm_comic_archive.create_cbz(build_dir, name="folder", metadata=metadata)
    shutil.copy(cbz_file, temp_dir)
    build_dir = mm_file_tools.get_temp_dir("dvk_test_builder")
    mm_file_tools.write_text_file(abspath(join(build_dir, "notcbz.jpg")), "Blah")
    assert mm_file_tools.create_zip(build_dir, abspath(join(temp_dir, "notcbz.cbz")))
    mm_file_tools.write_text_file(abspath(join(temp_dir, "text.cbz")), "Blah")
    assert sorted(os.listdir(temp_dir)) == ["folder.cbz", "notcbz.cbz", "simple.cbz", "text.cbz"]
    # Test extracting cbz file with a containing folder
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    assert mm_bulk_archive.extract_cbz(abspath(join(temp_dir, "simple.cbz")), extract_dir, create_folder=True)
    assert os.listdir(extract_dir) == ["simple"]
    extract_dir = abspath(join(extract_dir, "simple"))
    assert sorted(os.listdir(extract_dir)) == ["ComicInfo.xml", "simple"]
    extract_dir = abspath(join(extract_dir, "simple"))
    assert sorted(os.listdir(extract_dir)) == ["image1.jpg", "image2.jpg"]
    # Test extracting cbz file with no containing folder
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    assert mm_bulk_archive.extract_cbz(abspath(join(temp_dir, "simple.cbz")), extract_dir, create_folder=False)
    assert sorted(os.listdir(extract_dir)) == ["ComicInfo.xml", "simple"]
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    assert mm_bulk_archive.extract_cbz(abspath(join(temp_dir, "folder.cbz")), extract_dir, create_folder=False)
    assert sorted(os.listdir(extract_dir)) == ["A", "B", "ComicInfo.xml"]
    # Test extracting cbz file while removing the original structure
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    assert mm_bulk_archive.extract_cbz(abspath(join(temp_dir, "simple.cbz")), extract_dir, create_folder=True, remove_structure=True)
    assert sorted(os.listdir(extract_dir)) == ["simple"]
    extract_dir = abspath(join(extract_dir, "simple"))
    assert sorted(os.listdir(extract_dir)) == ["image1.jpg", "image2.jpg"]
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    assert mm_bulk_archive.extract_cbz(abspath(join(temp_dir, "folder.cbz")), extract_dir, create_folder=True, remove_structure=True)
    assert sorted(os.listdir(extract_dir)) == ["folder"]
    extract_dir = abspath(join(extract_dir, "folder"))
    assert sorted(os.listdir(extract_dir)) == ["A", "B"]
    # Test removing original structure with no containing folder
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    assert mm_bulk_archive.extract_cbz(abspath(join(temp_dir, "simple.cbz")), extract_dir, create_folder=False, remove_structure=True)
    assert sorted(os.listdir(extract_dir)) == ["image1.jpg", "image2.jpg"]
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    assert mm_bulk_archive.extract_cbz(abspath(join(temp_dir, "folder.cbz")), extract_dir, create_folder=False, remove_structure=True)
    assert sorted(os.listdir(extract_dir)) == ["A", "B"]
    # Test overwriting existing files
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    mm_file_tools.write_text_file(abspath(join(extract_dir, "image1.jpg")), "Duplicate")
    assert mm_bulk_archive.extract_cbz(abspath(join(temp_dir, "simple.cbz")), extract_dir, create_folder=False, remove_structure=True)
    assert sorted(os.listdir(extract_dir)) == ["image1-2.jpg", "image1.jpg", "image2.jpg"]
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    mm_file_tools.write_text_file(abspath(join(extract_dir, "A")), "Duplicate")
    assert mm_bulk_archive.extract_cbz(abspath(join(temp_dir, "folder.cbz")), extract_dir, create_folder=False, remove_structure=True)
    assert sorted(os.listdir(extract_dir)) == ["A", "A-2", "B"]
    assert mm_file_tools.read_text_file(abspath(join(extract_dir, "A"))) == "Duplicate"
    extract_dir = abspath(join(extract_dir, "A-2"))
    assert sorted(os.listdir(extract_dir)) == ["imageA.png"]
    # Test trying to extract non-cbz file
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    assert mm_bulk_archive.extract_cbz(abspath(join(temp_dir, "notcbz.cbz")), extract_dir, create_folder=False)
    assert sorted(os.listdir(extract_dir)) == ["notcbz.jpg"]
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    assert not mm_bulk_archive.extract_cbz(abspath(join(temp_dir, "text.cbz")), extract_dir)
    assert os.listdir(extract_dir) == []

def test_extract_epub():
    """
    Tests the extract_epub function.
    """
    # Create test files
    temp_dir = mm_file_tools.get_temp_dir()
    original_dir = abspath(join(temp_dir, "original"))
    sub_dir = abspath(join(original_dir, "sub"))
    os.mkdir(original_dir)
    os.mkdir(sub_dir)
    mm_file_tools.write_text_file(abspath(join(temp_dir, "removable.html")), "<p>Thing</p>")
    mm_file_tools.write_text_file(abspath(join(original_dir, "text.txt")), "Epub Text")
    mm_file_tools.write_text_file(abspath(join(original_dir, "image.png")), "Epub Image")
    mm_file_tools.write_text_file(abspath(join(sub_dir, "subtext.txt")), "Blah")
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "Book"
    metadata["writer"] = "Person"
    chapters = mm_epub.get_default_chapters(temp_dir, title="Book")
    chapters = mm_epub.add_cover_to_chapters(chapters, metadata)
    epub_file = mm_epub.create_epub(chapters, metadata, temp_dir)
    assert exists(epub_file)
    # Test extracting epub file with a containing folder
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    assert mm_bulk_archive.extract_epub(abspath(join(temp_dir, "Book.epub")), extract_dir, create_folder=True)
    assert sorted(os.listdir(extract_dir)) == ["Book"]
    extract_dir = abspath(join(extract_dir, "Book"))
    assert sorted(os.listdir(extract_dir)) == ["EPUB", "META-INF", "mimetype"]
    extract_dir = abspath(join(extract_dir, "EPUB"))
    assert sorted(os.listdir(extract_dir)) == ["content", "content.opf", "images", "nav.xhtml", "original", "style", "toc.ncx"]
    content_dir = abspath(join(extract_dir, "content"))
    assert sorted(os.listdir(content_dir)) == ["mm_cover_image.xhtml", "removable.xhtml"]
    original_dir = abspath(join(extract_dir, "original"))
    assert sorted(os.listdir(original_dir)) == ["image.png", "sub", "text.txt"]
    original_dir = abspath(join(original_dir, "sub"))
    assert sorted(os.listdir(original_dir)) == ["subtext.txt"]
    # Test extracting epub file with no containing folder
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    assert mm_bulk_archive.extract_epub(abspath(join(temp_dir, "Book.epub")), extract_dir, create_folder=False)
    assert sorted(os.listdir(extract_dir)) == ["EPUB", "META-INF", "mimetype"]
    extract_dir = abspath(join(extract_dir, "EPUB"))
    assert sorted(os.listdir(extract_dir)) == ["content", "content.opf", "images", "nav.xhtml", "original", "style", "toc.ncx"]
    content_dir = abspath(join(extract_dir, "content"))
    assert sorted(os.listdir(content_dir)) == ["mm_cover_image.xhtml", "removable.xhtml"]
    original_dir = abspath(join(extract_dir, "original"))
    assert sorted(os.listdir(original_dir)) == ["image.png", "sub", "text.txt"]
    original_dir = abspath(join(original_dir, "sub"))
    assert sorted(os.listdir(original_dir)) == ["subtext.txt"]
    # Test extracting epub file while removing original structure
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    assert mm_bulk_archive.extract_epub(abspath(join(temp_dir, "Book.epub")), extract_dir, create_folder=True, remove_structure=True)
    assert sorted(os.listdir(extract_dir)) == ["Book"]
    extract_dir = abspath(join(extract_dir, "Book"))
    assert sorted(os.listdir(extract_dir)) == ["image.png", "sub", "text.txt"]
    extract_dir = abspath(join(extract_dir, "sub"))
    assert sorted(os.listdir(extract_dir)) == ["subtext.txt"]
    # Test removing original structure with no containing folder
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    assert mm_bulk_archive.extract_epub(abspath(join(temp_dir, "Book.epub")), extract_dir, create_folder=False, remove_structure=True)
    assert sorted(os.listdir(extract_dir)) == ["image.png", "sub", "text.txt"]
    extract_dir = abspath(join(extract_dir, "sub"))
    assert sorted(os.listdir(extract_dir)) == ["subtext.txt"]
    # Test extracting to existing files
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    mm_file_tools.write_text_file(abspath(join(extract_dir, "text.txt")), "Duplicate")
    mm_file_tools.write_text_file(abspath(join(extract_dir, "sub")), "Substitute")
    assert mm_bulk_archive.extract_epub(abspath(join(temp_dir, "Book.epub")), extract_dir, create_folder=False, remove_structure=True)
    assert sorted(os.listdir(extract_dir)) == ["image.png", "sub", "sub-2", "text-2.txt", "text.txt"]
    assert mm_file_tools.read_text_file(abspath(join(extract_dir, "text.txt"))) == "Duplicate"
    assert mm_file_tools.read_text_file(abspath(join(extract_dir, "text-2.txt"))) == "Epub Text"
    extract_dir = abspath(join(extract_dir, "sub-2"))
    assert sorted(os.listdir(extract_dir)) == ["subtext.txt"]
    # Test trying to extract non-epub file
    temp_dir = mm_file_tools.get_temp_dir()
    mm_file_tools.write_text_file(abspath(join(temp_dir, "not_zip.epub")), "Text")
    mm_file_tools.write_text_file(abspath(join(temp_dir, "text.txt")), "Text")
    fake_epub = abspath(join(temp_dir, "not_epub.epub"))
    assert mm_file_tools.create_zip(temp_dir, fake_epub)
    extract_dir = mm_file_tools.get_temp_dir("dvk_test_extracted")
    assert not mm_bulk_archive.extract_epub(abspath(join(temp_dir, "not_zip.epub")), extract_dir, create_folder=False, remove_structure=False)
    assert not mm_bulk_archive.extract_epub(abspath(join(temp_dir, "not_zip.epub")), extract_dir, create_folder=False, remove_structure=True)
    assert not mm_bulk_archive.extract_epub(fake_epub, extract_dir, create_folder=True, remove_structure=True)
    assert os.listdir(extract_dir) == []
    assert mm_bulk_archive.extract_epub(fake_epub, extract_dir, create_folder=False, remove_structure=False)
    assert sorted(os.listdir(extract_dir)) == ["not_zip.epub", "text.txt"]

def test_extract_all_archives():
    """
    Tests the extract_all_archives function.
    """
    # Create test files
    temp_dir = mm_file_tools.get_temp_dir()
    sub_dir = abspath(join(temp_dir, "sub"))
    os.mkdir(sub_dir)
    build_dir = mm_file_tools.get_temp_dir("dvk_test_build")
    metadata = mm_archive.get_empty_metadata()
    metadata["title"] = "cbzA"
    mm_file_tools.write_text_file(abspath(join(build_dir, "imageA.jpg")), "Blah")
    cbz_file = mm_comic_archive.create_cbz(build_dir, name="cbzA", metadata=metadata)
    shutil.copy(cbz_file, temp_dir)
    build_dir = mm_file_tools.get_temp_dir("dvk_test_build")
    metadata["title"] = "cbzB"
    mm_file_tools.write_text_file(abspath(join(build_dir, "imageB.png")), "Blah")
    cbz_file = mm_comic_archive.create_cbz(build_dir, name="cbzB", metadata=metadata)
    shutil.copy(cbz_file, sub_dir)
    build_dir = mm_file_tools.get_temp_dir("dvk_test_build")
    metadata["title"] = "epubA"
    mm_file_tools.write_text_file(abspath(join(build_dir, "textA.txt")), "Blah")
    chapters = mm_epub.get_default_chapters(temp_dir, title="epubA")
    epub_file = mm_epub.create_epub(chapters, metadata, build_dir)
    shutil.copy(epub_file, temp_dir)
    build_dir = mm_file_tools.get_temp_dir("dvk_test_build")
    metadata["title"] = "epubB"
    mm_file_tools.write_text_file(abspath(join(build_dir, "textB.txt")), "Blah")
    chapters = mm_epub.get_default_chapters(temp_dir, title="epubB")
    epub_file = mm_epub.create_epub(chapters, metadata, build_dir)
    shutil.copy(epub_file, sub_dir)
    assert sorted(os.listdir(temp_dir)) == ["cbzA.cbz", "epubA.epub", "sub"]
    assert sorted(os.listdir(sub_dir)) == ["cbzB.cbz", "epubB.epub"]
    # Test extracting without removing structure
    extract_dir = abspath(join(temp_dir, "extracted"))
    extract_sub = abspath(join(extract_dir, "sub"))
    shutil.copytree(temp_dir, extract_dir)
    assert exists(extract_dir)
    assert mm_bulk_archive.extract_all_archives(extract_dir, create_folders=True, remove_structure=False)
    assert sorted(os.listdir(extract_dir)) == ["cbzA", "epubA", "sub"]
    cbz_dir = abspath(join(extract_dir, "cbzA"))
    assert sorted(os.listdir(cbz_dir)) == ["ComicInfo.xml", "cbzA"]
    assert sorted(os.listdir(abspath(join(cbz_dir, "cbzA")))) == ["imageA.jpg"]
    assert sorted(os.listdir(abspath(join(extract_dir, "epubA")))) == ["EPUB", "META-INF", "mimetype"]
    assert sorted(os.listdir(extract_sub)) == ["cbzB", "epubB"]
    assert sorted(os.listdir(abspath(join(extract_sub, "cbzB")))) == ["ComicInfo.xml", "cbzB"]
    assert sorted(os.listdir(abspath(join(extract_sub, "epubB")))) == ["EPUB", "META-INF", "mimetype"]
    # Test extracting while removing structure
    shutil.rmtree(extract_dir)
    assert not exists(extract_dir)
    shutil.copytree(temp_dir, extract_dir)
    assert exists(extract_dir)
    assert mm_bulk_archive.extract_all_archives(extract_dir, create_folders=False, remove_structure=True)
    assert sorted(os.listdir(extract_dir)) == ["imageA.jpg", "sub", "textA.txt"]
    assert sorted(os.listdir(extract_sub)) == ["imageB.png", "textB.txt"]
    # Test extracting invalid archives
    fake_archive = abspath(join(temp_dir, "notepub.epub"))
    mm_file_tools.write_text_file(fake_archive, "Blah")
    assert not mm_bulk_archive.extract_all_archives(temp_dir, create_folders=False, remove_structure=True)
    os.remove(fake_archive)
    fake_archive = abspath(join(temp_dir, "notcbz.cbz"))
    mm_file_tools.write_text_file(fake_archive, "Blah")
    assert not mm_bulk_archive.extract_all_archives(temp_dir, create_folders=False, remove_structure=True)
