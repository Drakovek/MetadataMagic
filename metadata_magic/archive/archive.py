#!/usr/bin/env python3

import os
import re
import math
import argparse
import html_string_tools.html
import python_print_tools.printer
import easy_text_to_image.color as etti_color
import easy_text_to_image.text_to_image as etti
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.meta_finder as mm_meta_finder
import metadata_magic.meta_reader as mm_meta_reader
import metadata_magic.archive.epub as mm_epub
import metadata_magic.archive.comic_archive as mm_comic_archive
from PIL import Image, ImageDraw
from os.path import abspath, isdir, exists

SUPPORTED_IMAGES = [".png", ".jpeg", ".jpg"]
SUPPORTED_TEXT = [".txt", ".html", ".htm"]

def get_directory_archive_type(directory:str) -> str:
    """
    Returns what kind of media archive the files in a given directory can be converted into.
    Returns "epub" if the directory contains text media.
    Returns "cbz" if the directory contains image media.
    Returns None if the directory contains no compatable media.

    :param directory: Directory to search for media within
    :type directory: str, required
    :return: Type of archive the directory's contents are suitable for
    :rtype: str
    """
    # Return "epub" if the directory contains text files
    if mm_file_tools.directory_contains(directory, SUPPORTED_TEXT, False):
        return "epub"
    # Return "cbz" if the directory contains image files
    if mm_file_tools.directory_contains(directory, SUPPORTED_IMAGES, True):
        return "cbz"
    # Return None if no appropriate archive format could be found
    return None

def get_empty_metadata() -> dict:
    """
    Returns a dictionary with keys for multiple metadata fields, populated as None.
    This dict structure is used as a framework for metadata in media archive formats.
    """
    meta_dict = dict()
    meta_dict["title"] = None
    meta_dict["series"] = None
    meta_dict["series_number"] = None
    meta_dict["series_total"] = None
    meta_dict["description"] = None
    meta_dict["date"] = None
    meta_dict["writers"] = None
    meta_dict["artists"] = None
    meta_dict["cover_artists"] = None
    meta_dict["publisher"] = None
    meta_dict["tags"] = None
    meta_dict["url"] = None
    meta_dict["age_rating"] = None
    meta_dict["score"] = None
    return meta_dict

def get_info_from_jsons(path:str) -> dict:
    """
    Extracts the data to be put into archive metadata from a JSON file in a given directory.
    Extracts data from the first JSON file found in directory when alphanumerically sorted.
    Searches sub-directories as well.
    
    :param path: Directory in which to search for JSON files
    :type path: str, required
    :return: Dictionary containing the metadata info
    :rtype: dict
    """
    # Get all the JSON pairs
    pairs = mm_meta_finder.get_pairs(path, print_info=False)
    # Read all JSON metadata
    json_metas = []
    for pair in pairs:
        json_metas.append(mm_meta_reader.load_metadata(pair["json"], pair["media"]))
    # Get first instance of JSON metadata
    try:
        main_meta = json_metas[0]
        extension = html_string_tools.html.get_extension(pairs[0]["media"])
    except IndexError: return get_empty_metadata()
    # Get most metadata from first JSON
    metadata = get_empty_metadata()
    metadata["title"] = main_meta["title"]
    metadata["date"] = main_meta["date"]
    metadata["publisher"] = main_meta["publisher"]
    metadata["url"] = main_meta["url"]
    # Get artists and writers
    metadata["artists"] = None
    metadata["writers"] = None
    if main_meta["artists"] is not None:
        metadata["artists"] = ",".join(main_meta["artists"])
    if main_meta["writers"] is not None:
        metadata["writers"] = ",".join(main_meta["writers"])
    metadata["cover_artists"] = metadata["artists"]
    # Get description metadata
    description = main_meta["description"]
    if description is not None:
        description = html_string_tools.html.replace_entities(description)
        description = re.sub(r"<a [^<>]*>|<\/a[^<>]*>|<b>|<i>|<\/b>|<\/i>", "", description)
        description = re.sub("<[^<>]*>", " ", description)
        description = re.sub(r"\s+", " ", description)
        description = description.strip()
    metadata["description"] = description
    # Get tag metadata
    tags = main_meta["tags"]
    if tags is not None and tags is not []:
        tag_string = tags[0]
        for i in range(1, len(tags)):
            tag_string = f"{tag_string},{tags[i]}"
        metadata["tags"] = tag_string
    # Get highest age rating in list of JSON metadata
    highest_age = "Unknown"
    for json_meta in json_metas:
        if json_meta["age_rating"] == "X18+":
            highest_age = "X18+"
            continue
        elif json_meta["age_rating"] == "Mature 17+" and not highest_age == "X18+":
            highest_age = "Mature 17+"
            continue
        elif json_meta["age_rating"] == "Teen" and (highest_age == "Everyone" or highest_age == "Unknown"):
            highest_age = "Teen"
            continue
        elif json_meta["age_rating"] == "Everyone" and highest_age == "Unknown":
            highest_age = "Everyone"
    metadata["age_rating"] = highest_age
    # Return metadata
    return metadata

def get_info_from_archive(file:str) -> dict:
    """
    Attempts to get metadata information from any of the supported media archive formats.
    Currently supports EPUB and CBZ.
    
    :param file: Path to media archive file
    :type file: str, required
    :return: Dictionary containing metadata as formatted in get_empty_metadata function
    :rtype: dict
    """
    # Try getting info from a CBZ file
    metadata = mm_comic_archive.get_info_from_cbz(file)
    if not metadata == get_empty_metadata():
        return metadata
    # Try getting info from an EPUB file
    metadata = mm_epub.get_info_from_epub(file)
    if not metadata == get_empty_metadata():
        return metadata
    # Return empty metadata
    return get_empty_metadata()

def format_title(text:str) -> dict:
    """
    Attempts to format title to add capitalization and remove page numbers from a given text value.
    
    :param text: Text to format as title
    :type text: str, required
    :return: Text with the page number text removed
    :rtype: str
    """
    # Return None if the text is None
    if text is None:
        return None
    # Reduce spaces
    altered = re.sub(r"\s+", " ", text)
    # Remove references to page number
    regex = r"(?:\s*-\s*)?(?:\b(?:p[gt]?\.?\s*|page\s*|part\s*))?(?:#\s*)?(?:[0-9]+\s*(?:[\/-]|of)\s*)?[0-9]+\s*$"
    regex = regex + r"|\[\s*(?:\b(?:p[gt]?\.?\s*|page\s*|part\s*))?(?:#\s*)?(?:[0-9]+\s*(?:[\/-]|of)\s*)?[0-9]+\s*\]\s*$"
    regex = regex + r"|\(\s*(?:\b(?:p[gt]?\.?\s*|page\s*|part\s*))?(?:#\s*)?(?:[0-9]+\s*(?:[\/-]|of)\s*)?[0-9]+\s*\)\s*$"
    regex = regex + r"|^\[[^\[\]]*\]\s+"
    altered = re.sub(regex, "", altered, flags=re.IGNORECASE).strip()
    # Set the title case
    regex = r"^[a-z]|\s[a-z]|[\[(][a-z]"
    while len(re.findall(regex, altered)) > 0:
        altered = re.sub(regex, lambda x:x[0].upper(), altered, count=1)
    regex = r"\sOf\s|\sFor\s|\sA\s|\sAn\s|\sAnd\s|\sThe\s|\sTo\s"
    while len(re.findall(regex, altered)) > 0:
        altered = re.sub(regex, lambda x:x[0].lower(), altered, count=1)
    # Check if the altered text is valid
    if not altered == "":
        return altered
    # Return the original text if altered text is empty
    return text

def update_archive_info(archive_file:str, metadata:dict, update_cover:bool=False):
    """
    Replaces the metadata in a given archive file with the given metadata.
    Supports CBZ and EPUB files.
    
    :param archive_file: Path of the archive file to update
    :type archive_file: str, required
    :param metadata: Metadata to use for the new metadata
    :type metadata: dict
    :param update_cover: Whether to regenerate cover images, defaults to False
    :type update_cover: bool, optional
    """
    extension = html_string_tools.html.get_extension(archive_file).lower()
    if extension == ".epub":
        mm_epub.update_epub_info(archive_file, metadata, update_cover=update_cover)
    if extension == ".cbz":
        mm_comic_archive.update_cbz_info(archive_file, metadata)

def get_cover_image(title:str, authors:str, portrait:bool=True, uppercase:bool=True) -> Image:
    """
    Creates and returns a cover image based on a given title and author.
    
    :param title: Title to use for the cover image
    :type title: str, required
    :param authors: Author(s) to use for the cover image
    :type authors: str, required
    :param portrait: Wheter the image should be in portrait orientation, defaults to True
    :type portrait: bool, optional
    :param uppercase: Whether to set all text to uppercase, defaults to True
    :type uppercase: bool, optional
    :return: Cover image
    :rtype: PIL.Image
    """
    # Get the dimensions of the full cover image
    full_width = 900
    full_height = 1200
    if portrait is False:
        full_width = 1200
        full_height = 900
    # Get the colors for the image
    palette = etti_color.get_random_color_palette()
    # Create the base image
    margin = 90
    half_margin = math.floor(margin/2)
    cover = Image.new("RGBA", size=(full_width, full_height), color=palette["secondary-saturated"])
    inner = Image.new("RGBA", size=(full_width - margin, full_height), color=palette["primary-saturated"])
    cover.alpha_composite(inner, (margin, 0))
    # Get the font for the image
    system_fonts = etti.get_system_fonts()
    italic_font = etti.get_basic_font("sans-serif", system_fonts, bold=True, italic=True)
    bold_font = etti.get_basic_font("sans-serif", system_fonts, bold=True)
    # Create the text for the author
    text_width = full_width - math.floor(margin * 2.5)
    author_text = re.sub(r"\s*,\s*", " and ", str(authors))
    author_text = f"by {author_text}"
    if uppercase:
        author_text = author_text.upper()
    author_image = etti.text_image_fit_width(author_text, bold_font, image_width=text_width,
            foreground=palette["secondary-desaturated"], background="#00000000", justified="l", minimum_characters=200)
    author_height = author_image.size[1]
    cover.alpha_composite(author_image, (math.floor(margin * 1.5), full_height - (half_margin + author_height)))
    # Create the text for the title
    text_height = full_height - ((margin*3) + author_height)
    title_text = str(title)
    if uppercase:
        title_text = title_text.upper()
    title_image = etti.text_image_fit_box(title_text, italic_font, image_width=text_width, image_height=text_height,
            foreground=palette["primary-desaturated"], background="#00000000", justified="l", vertical="t", space=1)
    # Create the title framing
    top, bottom = etti.get_vertical_bounds(title_image, "#00000000")
    frame_bottom = (bottom - top) + (margin * 1.5)
    draw = ImageDraw.Draw(cover)
    draw.rounded_rectangle([(0, half_margin), (full_width-half_margin, frame_bottom)],
            fill=palette["secondary-saturated"], radius=half_margin)
    cover.alpha_composite(title_image, (math.floor(margin*1.5), margin))
    # Return the image
    return cover

def get_string_from_user(value_type:str, default_value:str=None) -> str:
    """
    Gets a string from the user with prompt generated from given value type.

    :param value_type: Name of the value user is inputting, used for the prompt
    :type value_type: str, required
    :param default_value: Default value to return, defaults to None
    :type default_value: str, optional
    :return: User value or default if the value is invalid
    :rtype: str
    """
    # Set the prompt
    prompt = value_type
    if default_value is not None:
        prompt = f"{prompt} (Default is \"{default_value}\")"
    # Get value from the user
    value = str(input(f"{prompt}: ")).strip()
    # Return user value if the value is valid
    if not value == "":
        return value
    # Return default value if user value is not valid
    return default_value

def get_list_from_user(value_type:str, default_value:str=None) -> str:
    """
    Gets a list from the user with prompt generated from given value type.

    :param value_type: Name of the value user is inputting, used for the prompt
    :type value_type: str, required
    :param default_value: Default value to return, defaults to None
    :type default_value: str, optional
    :return: User value or default if the value is invalid
    :rtype: str
    """
    # Get the string value
    value = get_string_from_user(value_type, default_value)
    if value is None: return None
    # Split value by comma
    value_list = value.split(",")
    # Remove whitespace from each value
    value = ""
    for item in value_list:
        value = f"{value}{item},"
    value = re.sub(r"\s*,+$", "", value)
    value = re.sub(r"\s*,\s*", ",", value)
    # Return the value
    return value

def user_string_default(value_type:str, default_value:str) -> str:
    """
    Gets a string from the user with prompt generated from given value type.
    Will simply return the default value without prompting the user if not None.

    :param value_type: Name of the value user is inputting, used for the prompt
    :type value_type: str, required
    :param default_value: Default value to return, defaults to None
    :type default_value: str, optional
    :return: User value or default if the value is invalid
    :rtype: str
    """
    if default_value is not None:
        return default_value
    return get_string_from_user(value_type, None)

def user_list_default(value_type:str, default_value:str) -> str:
    """
    Gets a list from the user with prompt generated from given value type.
    Will simply return the default value without prompting the user if not None.

    :param value_type: Name of the value user is inputting, used for the prompt
    :type value_type: str, required
    :param default_value: Default value to return, defaults to None
    :type default_value: str, optional
    :return: User value or default if the value is invalid
    :rtype: str
    """
    if default_value is not None:
        return default_value
    return get_list_from_user(value_type, None)

def get_metadata_from_user(metadata:dict, get_score:bool) -> dict:
    """
    Gets a list of metadata from the user.
    Will not ask the user for certain fields that already contain default metadata.
    Metadata is formatted in a dictionary as returned by get_empty_metadata.

    :param metadata: Existing metadata to not ask the user for
    :type metadata: dict, required
    :param get_score: Whether to ask the user for the score
    :type get_score: bool, required
    :return: Dictonary of metadata input by the user
    :rtype: dict
    """
    user_metadata = metadata
    # Get the title
    user_metadata["title"] = get_string_from_user("Title", format_title(user_metadata["title"]))
    # Get the date
    regex = "(19[7-9][0-9]|2[0-1][0-9]{2})\\-(0[1-9]|1[0-2])\\-(0[1-9]|[1-2][0-9]|3[0-1])"
    if user_metadata["date"] is None or len(re.findall(regex, user_metadata["date"])) == 0:
        user_metadata["date"] = get_string_from_user("Date (YYYY-MM-DD)", None)
    if user_metadata["date"] is None or len(re.findall(regex, user_metadata["date"])) == 0:
        user_metadata["date"] = None
    # Get the artists
    user_metadata["artists"] = user_list_default("Illustrator(s)", user_metadata["artists"])
    if user_metadata["cover_artists"] is None:
        user_metadata["cover_artists"] = get_list_from_user("Cover Artist(s)", user_metadata["artists"])
    if user_metadata["writers"] is None:
        user_metadata["writers"] = get_list_from_user("Writer(s)", user_metadata["artists"])
    # Get the publisher
    user_metadata["publisher"] = user_string_default("Publisher", user_metadata["publisher"])
    # Get the URL
    user_metadata["url"] = user_string_default("URL", user_metadata["url"])
    # Get the description
    user_metadata["description"] = user_string_default("Description", user_metadata["description"])
    # Get the tags
    user_metadata["tags"] = user_list_default("Tags", user_metadata["tags"])
    # Get the age rating
    age_ratings = {"0":"Unknown", "1":"Everyone", "2":"Teen", "3":"Mature 17+", "4":"X18+"}
    if user_metadata["age_rating"] is None:
        try:
            print("0) Unknown\n1) Everyone\n2) Teen\n3) Mature 17+\n4) X18+")
            value = user_string_default("Age Rating", None)
            user_metadata["age_rating"] = age_ratings[value]
        except KeyError: user_metadata["age_rating"] = None
    # Get the score
    if get_score:
        try:
            score = int(user_string_default("Score (Range 0-5)", None))
            if score > -1 and score < 6:
                user_metadata["score"] = str(score)
        except (TypeError, ValueError): user_metadata["score"] = None
    # Return the user metadata
    return user_metadata

def main():
    """
    Sets up the parser for creating a media archive.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory to encapsulate in a media archive.",
            nargs="?",
            type=str,
            default=str(os.getcwd()))
    parser.add_argument(
            "-s",
            "--summary",
            help="Use user summary instead of summary in metadata.",
            action="store_true")
    parser.add_argument(
            "-d",
            "--date",
            help="Use user date instead of date in metadata.",
            action="store_true")
    parser.add_argument(
            "-a",
            "--artists",
            help="Use user artists instead of artists in metadata.",
            action="store_true")
    parser.add_argument(
            "-p",
            "--publisher",
            help="Use user publisher instead of publisher in metadata.",
            action="store_true")
    parser.add_argument(
            "-u",
            "--url",
            help="Use user URL instead of URL in metadata.",
            action="store_true")
    parser.add_argument(
            "-t",
            "--tags",
            help="Use user tags instead of tags in metadata.",
            action="store_true")
    parser.add_argument(
            "-r",
            "--rating",
            help="Use user age rating instead of rating in metadata.",
            action="store_true")
    parser.add_argument(
            "-g",
            "--grade",
            help="Use user grade/score instead of score in metadata.",
            action="store_true")
    parser.add_argument(
            "-x",
            "--xxxxx",
            help="Deletes the original media after creating the archive.",
            action="store_true")
    args = parser.parse_args()
    # Check that directory is valid
    path = abspath(args.directory)
    if not exists(path) or not isdir(path):
        python_print_tools.printer.color_print("Invalid directory.", "red")
    else:
        # Discover the type of archive to create
        archive_type = get_directory_archive_type(path)
        if archive_type is None:
            python_print_tools.printer.color_print("Unsupported media.", "red")
        else:
            # Get existing info from a directory
            metadata = get_info_from_jsons(path)
            if metadata["title"] is None:
                metadata["title"] = ""
            # Remove default values that the user wishes to change
            if args.summary:
                metadata["description"] = None
            if args.date:
                metadata["date"] = None
            if args.artists:
                metadata["artists"] = None
                metadata["cover_artists"] = None
                metadata["writers"] = None
            if args.publisher:
                metadata["publisher"] = None
            if args.url:
                metadata["url"] = None
            if args.tags:
                metadata["tags"] = None
            if args.rating:
                metadata["age_rating"] = None
            if args.grade:
                metadata["score"] = None
            # Get  metadata values from the user
            metadata = get_metadata_from_user(metadata, args.grade)
            # Create the archive        
            if archive_type == "cbz":
                mm_comic_archive.create_cbz(path, metadata["title"], metadata, remove_files=args.xxxxx)
            if archive_type == "epub":
                chapters = mm_epub.get_chapters_from_user(path, metadata)
                mm_epub.create_epub(chapters, metadata, path)
