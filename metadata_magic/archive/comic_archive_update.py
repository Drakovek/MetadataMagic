#!/usr/bin/env python3

import os
import tqdm
import argparse
import python_print_tools.printer
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.meta_reader as mm_meta_reader
import metadata_magic.archive.comic_archive as mm_comic_archive
from os.path import abspath, exists, join

def mass_update_cbzs(directory:str, metadata:dict):
    """
    Updates all the cbz files in a given directory to use new metadata.
    Uses artist, writer, cover_artist, publisher, age_rating, and score keys in a metadata dictionary.
    Any metadata fields with a value of None will be unaltered from the orignal cbz file.
    
    :param directory: Directory in which to look for cbz files, including subdirectories
    :type directory: str, required
    :param metadata: Metadata to update the cbz files with
    :type metadata: dict, required
    """
    # Get list of cbz files in the directory
    cbz_files = mm_file_tools.find_files_of_type(directory, ".cbz")
    for cbz_file in tqdm.tqdm(cbz_files):
        # Get the existing info for the cbz file
        new_metadata = mm_comic_archive.get_info_from_cbz(cbz_file)
        # Update the metadata
        if metadata["artist"] is not None:
            new_metadata["artist"] = metadata["artist"]
        if metadata["writer"] is not None:
            new_metadata["writer"] = metadata["writer"]
        if metadata["cover_artist"] is not None:
            new_metadata["cover_artist"] = metadata["cover_artist"]
        if metadata["publisher"] is not None:
            new_metadata["publisher"] = metadata["publisher"]
        if metadata["age_rating"] is not None:
            new_metadata["age_rating"] = metadata["age_rating"]
        if metadata["score"] is not None:
            new_metadata["score"] = metadata["score"]
        # Update the cbz file with the new metadata
        mm_comic_archive.update_cbz_info(cbz_file, new_metadata)

def user_mass_update_cbzs(path:str,
                rp_artists:bool=False,
                rp_publisher:bool=False,
                rp_age:bool=False,
                rp_score:bool=False):
    """
    Updates all the cbz files in a given directory from user-provided values.
    
    :param path: Path to the directory in which to update cbz files
    :type path: str, required
    :param rp_artist: Whether to update artist values, defaults to false
    :type rp_artist: bool, optional
    :param rp_publisher: Whether to update publisher values, defaults to false
    :type rp_publisher: bool, optional
    :param rp_age: Whether to update age rating values, defaults to false
    :type rp_age: bool, optional
    :param rp_score: Whether to update scores/grades, defaults to false
    :type rp_score: bool, optional
    """
    metadata = mm_meta_reader.get_empty_metadata()
    # Get Artists
    artist = None
    if rp_artists:
        # Get the main Artist
        artist = str(input("Artist: "))
        if not artist == "":
            metadata["artist"] = artist
        # Get the Cover Artist
        cover = str(input(f"Cover Artist (Default is \"{artist}\"): "))
        if not cover == "":
            metadata["cover_artist"] = cover
        elif not artist == "":
            metadata["cover_artist"] = artist
        # Get the Writer
        writer = str(input(f"Writer (Default is \"{artist}\"): "))
        if not writer == "":
            metadata["writer"] = writer
        elif not artist == "":
            metadata["writer"] = artist
    # Get the Publisher
    if rp_publisher:
        publisher = str(input("Publisher: "))
        if not publisher == "":
            metadata["publisher"] = publisher
    # Get age rating
    while rp_age and metadata["age_rating"] is None:
        print("0) Unknown\n1) Everyone\n2) Teen\n3) Mature 17+\n4) X18+")
        age = str(input("Age Rating: "))
        if age == "0":
            metadata["age_rating"] = "Unknown"
        if age == "1":
            metadata["age_rating"] = "Everyone"
        if age == "2":
            metadata["age_rating"] = "Teen"
        if age == "3":
            metadata["age_rating"] = "Mature 17+"
        if age == "4":
            metadata["age_rating"] = "X18+"
    # Get score
    if rp_score:
        score = str(input("Score (Range 0-5): "))
        if not score == "":
            metadata["score"] = score
    # Update cbz files
    mass_update_cbzs(path, metadata)

def main():
    """
    Sets up the parser for creating a comic archive.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "path",
            help="Path to directory or existing .cbz file.",
            nargs="?",
            type=str,
            default=str(os.getcwd()))
    parser.add_argument(
            "-a",
            "--artists",
            help="Replace the artist values.",
            action="store_true")
    parser.add_argument(
            "-p",
            "--publisher",
            help="Replace the publisher values.",
            action="store_true")
    parser.add_argument(
            "-r",
            "--rating",
            help="Replace the age ratings.",
            action="store_true")
    parser.add_argument(
            "-g",
            "--grade",
            help="Replace the grades/scores.",
            action="store_true")
    args = parser.parse_args()
    # Check that directory is valid
    path = abspath(args.path)
    if not exists(path):
        python_print_tools.printer.color_print("Invalid path.", "red")
    else:
        # Create the comic archive
        user_mass_update_cbzs(path,
                rp_artists=args.artists,
                rp_publisher=args.publisher,
                rp_age=args.rating,
                rp_score=args.grade)
