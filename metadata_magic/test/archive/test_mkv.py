#!/usr/bin/env python3

import os
import shutil
import tempfile
import metadata_magic.test as mm_test
import metadata_magic.archive as mm_archive
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.archive.mkv as mm_mkv
from os.path import abspath, exists, join
from ffmpeg import FFmpeg
from ffmpeg.errors import FFmpegError

def test_create_mkv():
    """
    Tests the create_mkv function.
    """
    # Test creating MKV with metadata, JSON, and name
    basic_video_file = abspath(join(mm_test.PAIR_VIDEO_DIRECTORY, "basicvideo.mp4"))
    basic_video_json = abspath(join(mm_test.PAIR_VIDEO_DIRECTORY, "basicvideo.json"))
    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.copy(basic_video_file, abspath(join(temp_dir, "basic.mp4")))
        shutil.copy(basic_video_json, abspath(join(temp_dir, "basic.json")))
        assert sorted(os.listdir(temp_dir)) == ["basic.json", "basic.mp4"]
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "Created MKV"
        metadata["date"] = "2020-02-29"
        metadata["artists"] = ["Some", "Artists"]
        mkv_file = mm_mkv.create_mkv(temp_dir, "Video", metadata, False)
        assert exists(mkv_file)
        assert sorted(os.listdir(temp_dir)) == ["Video.mkv", "basic.json", "basic.mp4"]
        read_meta = mm_mkv.get_info_from_mkv(mkv_file)
        assert read_meta["metadata"]["title"] == "Created MKV"
        assert read_meta["metadata"]["date"] == "2020-02-29"
        assert read_meta["metadata"]["artists"] == ["Some", "Artists"]
        assert read_meta["original"]["title"] == "BasicVideo"
        assert read_meta["original"]["date"] == "2000-01-02"
        assert read_meta["original"]["other"] == "thing"
    # Test creating MKV with no JSON or name
    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.copy(basic_video_file, abspath(join(temp_dir, "new_video.mp4")))
        assert sorted(os.listdir(temp_dir)) == ["new_video.mp4"]
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "No JSON"
        metadata["artists"] = ["New"]
        metadata["description"] = "Some Words."
        mkv_file = mm_mkv.create_mkv(temp_dir, None, metadata, False)
        assert exists(mkv_file)
        assert sorted(os.listdir(temp_dir)) == ["new_video.mkv", "new_video.mp4"]
        read_meta = mm_mkv.get_info_from_mkv(mkv_file)
        assert read_meta["metadata"]["title"] == "No JSON"
        assert read_meta["metadata"]["artists"] == ["New"]
        assert read_meta["metadata"]["description"] == "Some Words."
        assert read_meta["original"] == {}
    # Test creating MKV with no title
    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.copy(basic_video_file, abspath(join(temp_dir, "next.mp4")))
        assert sorted(os.listdir(temp_dir)) == ["next.mp4"]
        metadata = mm_archive.get_empty_metadata()
        metadata["artists"] = ["New"]
        metadata["description"] = "No Title"
        mkv_file = mm_mkv.create_mkv(temp_dir, None, metadata, False)
        assert exists(mkv_file)
        assert sorted(os.listdir(temp_dir)) == ["next.mkv", "next.mp4"]
        read_meta = mm_mkv.get_info_from_mkv(mkv_file)
        assert read_meta["metadata"]["title"] is None
        assert read_meta["metadata"]["artists"] == ["New"]
        assert read_meta["metadata"]["description"] == "No Title"
        assert read_meta["original"] == {}
    # Test creating from a file with subtitles and multiple audio streams
    complex_video_file = abspath(join(mm_test.PAIR_VIDEO_DIRECTORY, "A.A.mkv"))
    complex_video_json = abspath(join(mm_test.PAIR_VIDEO_DIRECTORY, "A.A.json"))
    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.copy(complex_video_file, abspath(join(temp_dir, "complex.mkv")))
        shutil.copy(complex_video_json, abspath(join(temp_dir, "complex.json")))
        assert sorted(os.listdir(temp_dir)) == ["complex.json", "complex.mkv"]
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "Multiple Streams"
        metadata["date"] = "2002-06-15"
        metadata["artists"] = ["Different"]
        mkv_file = mm_mkv.create_mkv(temp_dir, "Stream", metadata, False)
        assert exists(mkv_file)
        assert sorted(os.listdir(temp_dir)) == ["Stream.mkv", "complex.json", "complex.mkv"]
        read_meta = mm_mkv.get_info_from_mkv(mkv_file)
        assert read_meta["metadata"]["title"] == "Multiple Streams"
        assert read_meta["metadata"]["date"] == "2002-06-15"
        assert read_meta["metadata"]["artists"] == ["Different"]
        assert read_meta["original"]["title"] == "Subtitled"
        assert read_meta["original"]["other"] == 1234
        empty_file = abspath(join(temp_dir, "empty.mkv"))
        main = FFmpeg().input(mkv_file).output(empty_file, map=["0", "v:0", "a:1", "s:0"], c="copy")
        main.execute()
    # Test creating MKV while deleting old files
    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.copy(basic_video_file, abspath(join(temp_dir, "basic.mp4")))
        shutil.copy(basic_video_json, abspath(join(temp_dir, "basic.json")))
        assert sorted(os.listdir(temp_dir)) == ["basic.json", "basic.mp4"]
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "Deleting"
        mkv_file = mm_mkv.create_mkv(temp_dir, "delete", metadata, True)
        assert exists(mkv_file)
        assert sorted(os.listdir(temp_dir)) == ["delete.mkv"]
        read_meta = mm_mkv.get_info_from_mkv(mkv_file)
        assert read_meta["metadata"]["title"] == "Deleting"
        assert read_meta["original"]["title"] == "BasicVideo"
        assert read_meta["original"]["date"] == "2000-01-02"
        assert read_meta["original"]["other"] == "thing"
    # Test if directory contains no videos or more than one video
    with tempfile.TemporaryDirectory() as temp_dir:
        text_file = abspath(join(temp_dir, "text.txt"))
        mm_file_tools.write_text_file(text_file, "Text.")
        assert mm_mkv.create_mkv(temp_dir, "None", metadata) is None
        shutil.copy(basic_video_file, abspath(join(temp_dir, "basic.mp4")))
        shutil.copy(basic_video_file, abspath(join(temp_dir, "basic2.mp4")))
        assert mm_mkv.create_mkv(temp_dir, "None", metadata) is None
    # Test if the video file is invalid
    with tempfile.TemporaryDirectory() as temp_dir:
        text_file = abspath(join(temp_dir, "text.mp4"))
        mm_file_tools.write_text_file(text_file, "Text.")
        assert mm_mkv.create_mkv(temp_dir, "None", metadata) is None
    # Test creating MKV with no metadata or invalid metadata
    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.copy(basic_video_file, abspath(join(temp_dir, "no_meta.mp4")))
        assert sorted(os.listdir(temp_dir)) == ["no_meta.mp4"]
        assert mm_mkv.create_mkv(temp_dir, None, None) is None
        assert mm_mkv.create_mkv(temp_dir, None, {"thing":"wrong"}) is None

def test_get_info_from_mkv():
    """
    Tests the get_info_from_mkv function.
    """
    # Test getting metadata from mkv with both original json and video metadata
    metadata = mm_mkv.get_info_from_mkv(abspath(join(mm_test.ARCHIVE_MKV_DIRECTORY, "full.MKV")))
    json_metadata = metadata["original"]
    assert json_metadata == {"artist":"Person", "date":"2020-01-01", "title":"Video Title"}
    video_metadata = metadata["metadata"]
    assert video_metadata["title"] == "Videó"
    assert video_metadata["artists"] == ["Director", "Other"]
    assert video_metadata["date"] == "2014-01-30"
    assert video_metadata["url"] == "/non/existant/vpage"
    assert video_metadata["description"] == "Video Description"
    assert video_metadata["publisher"] == "DVK"
    # Test getting metadata from mkv with only video metadata
    metadata = mm_mkv.get_info_from_mkv(abspath(join(mm_test.ARCHIVE_MKV_DIRECTORY, "nojson.mkv")))
    assert metadata["original"] == {}
    video_metadata = metadata["metadata"]
    assert video_metadata["title"] == "No JSON Included"
    assert video_metadata["artists"] == ["Person"]
    assert video_metadata["date"] == "2020-03-24"
    assert video_metadata["url"] == "/page/url/"
    assert video_metadata["description"] == "Basic Words"
    assert video_metadata["publisher"] == "DeviantArt"
    # Test getting metadata from mkv where no metadata exists
    metadata = mm_mkv.get_info_from_mkv(abspath(join(mm_test.ARCHIVE_MKV_DIRECTORY, "empty.mkv")))
    assert metadata["original"] == {}
    video_metadata = metadata["metadata"]
    assert video_metadata["title"] is None
    assert video_metadata["artists"] is None
    assert video_metadata["date"] is None
    assert video_metadata["url"] is None
    assert video_metadata["description"] is None
    assert video_metadata["publisher"] is None
    # Test if the file is not a video file
    metadata = mm_mkv.get_info_from_mkv(abspath(join(mm_test.ARCHIVE_CBZ_DIRECTORY, "basic.CBZ")))
    assert metadata["original"] == {}
    video_metadata = metadata["metadata"]
    assert video_metadata["title"] is None
    assert video_metadata["artists"] is None
    assert video_metadata["date"] is None
    assert video_metadata["url"] is None
    assert video_metadata["description"] is None
    assert video_metadata["publisher"] is None

def test_update_mkv_info():
    """
    Tests the update_mkv_info function.
    """
    # Test updating MKV without original JSON file
    with tempfile.TemporaryDirectory() as temp_dir:
        base_mkv_file = abspath(join(mm_test.ARCHIVE_MKV_DIRECTORY, "nojson.mkv"))
        mkv_file = abspath(join(temp_dir, "video.mkv"))
        shutil.copy(base_mkv_file, mkv_file)
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "New Title"
        metadata["writers"] = ["New", "Writers"]
        mm_mkv.update_mkv_info(mkv_file, metadata)
        read_meta = mm_mkv.get_info_from_mkv(mkv_file)
        assert read_meta["original"] == {}
        assert read_meta["metadata"]["title"] == "New Title"
        assert read_meta["metadata"]["writers"] == ["New", "Writers"]
        assert read_meta["metadata"]["description"] is None
    # Test that original JSON metadata is not affected when updating metadata
    with tempfile.TemporaryDirectory() as temp_dir:
        base_mkv_file = abspath(join(mm_test.ARCHIVE_MKV_DIRECTORY, "full.MKV"))
        mkv_file = abspath(join(temp_dir, "video.mkv"))
        shutil.copy(base_mkv_file, mkv_file)
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "Updated"
        metadata["artists"] = ["Different"]
        mm_mkv.update_mkv_info(mkv_file, metadata)
        read_meta = mm_mkv.get_info_from_mkv(mkv_file)
        assert read_meta["original"]["title"] == "Video Title"
        assert read_meta["original"]["artist"] == "Person"
        assert read_meta["original"]["date"] == "2020-01-01"
        assert read_meta["metadata"]["title"] == "Updated"
        assert read_meta["metadata"]["artists"] == ["Different"]
        assert read_meta["metadata"]["writers"] is None
    # Test updating MKV with no metadata at all
    with tempfile.TemporaryDirectory() as temp_dir:
        base_mkv_file = abspath(join(mm_test.ARCHIVE_MKV_DIRECTORY, "empty.mkv"))
        mkv_file = abspath(join(temp_dir, "video.mkv"))
        shutil.copy(base_mkv_file, mkv_file)
        metadata = mm_archive.get_empty_metadata()
        metadata["title"] = "Final"
        metadata["description"] = "Words"
        mm_mkv.update_mkv_info(mkv_file, metadata)
        read_meta = mm_mkv.get_info_from_mkv(mkv_file)
        assert read_meta["original"] == {}
        assert read_meta["metadata"]["title"] == "Final"
        assert read_meta["metadata"]["description"] == "Words"
        assert read_meta["metadata"]["writers"] == None

def test_remove_all_mkv_metadata():
    """
    Tests the remove_all_mkv_metadata function.
    """
    # Test stripping all metadata from an MKV file
    with tempfile.TemporaryDirectory() as temp_dir:
        base_mkv_file = abspath(join(mm_test.ARCHIVE_MKV_DIRECTORY, "full.MKV"))
        mkv_file = abspath(join(temp_dir, "video.mkv"))
        shutil.copy(base_mkv_file, mkv_file)
        mm_mkv.remove_all_mkv_metadata(mkv_file)
        metadata = mm_mkv.get_info_from_mkv(mkv_file)
        assert metadata["original"] == {}
        assert metadata["metadata"] == mm_archive.get_empty_metadata()
        test_mkv = abspath(join(temp_dir, "test.mkv"))
        main = FFmpeg().input(mkv_file).output(test_mkv, map=["0", "-0:t"], c="copy")
        main.execute()
        assert exists(test_mkv)
        os.remove(test_mkv)
        try:
            main = FFmpeg().input(mkv_file).output(test_mkv, map=["0", "1:t"], c="copy")
            main.execute()
            assert 0 == "STILL CONTAINS ATTATCHMENTS"
        except FFmpegError: pass
    # Test if the file is not an mkv file
    with tempfile.TemporaryDirectory() as temp_dir:
        text_file = abspath(join(temp_dir, "text.txt"))
        mm_file_tools.write_text_file(text_file, "Text!")
        mm_mkv.remove_all_mkv_metadata(text_file)
        assert mm_file_tools.read_text_file(text_file) == "Text!"
        text_file = abspath(join(temp_dir, "text.mkv"))
        mm_file_tools.write_text_file(text_file, "Fake video")
        mm_mkv.remove_all_mkv_metadata(text_file)
        assert mm_file_tools.read_text_file(text_file) == "Fake video"
