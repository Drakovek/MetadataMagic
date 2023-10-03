#!/usr/bin/env python3

"""Setuptools setup file."""

import setuptools

console_scripts = [
    "meta-missing-media = metadata_magic.error.missing_media:main",
    "meta-missing-metadata = metadata_magic.error.missing_metadata:main",
    "meta-missing-fields = metadata_magic.error.missing_fields:main",
    "meta-rename = metadata_magic.rename.meta_rename:main",
    "sort-rename = metadata_magic.rename.sort_rename:main",    
    "archive-comic = metadata_magic.archive.comic_archive:main",
    "archive-series = metadata_magic.archive.series_info:main",
    "update-comic-archives = metadata_magic.archive.comic_archive_update:main",
    "archive-all-comics = metadata_magic.archive.archive_all:main",
    "extract-all-comics = metadata_magic.archive.extract_all:main",
    "archive-book = metadata_magic.archive.epub:main"]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Metadata-Magic",
    version="0.7.5",
    author="Drakovek",
    author_email="DrakovekMail@gmail.com",
    description="Utility for managing metadata.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Drakovek/MetadataMagic",
    packages=setuptools.find_packages(),
    install_requires=["lxml", "tqdm", "HTML-String-Tools", "Pillow", "Python-Print-Tools"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.9',
    entry_points={"console_scripts": console_scripts}
)
