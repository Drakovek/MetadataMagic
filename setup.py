#!/usr/bin/env python3

"""Setuptools setup file."""

import setuptools

console_scripts = [
    "meta-missing-fields = metadata_magic.main.error_finding.missing_fields:main",
    "meta-missing-media = metadata_magic.main.error_finding.missing_media:main",
    "meta-missing-metadata = metadata_magic.main.error_finding.missing_metadata:main",
    "meta-rename = metadata_magic.main.rename.meta_rename:main",
    "sort-rename = metadata_magic.main.rename.sort_rename:main",
    "archive-comic = metadata_magic.main.comic_archive.comic_archive:main",
    "archive-all-comics = metadata_magic.main.comic_archive.archive_all:main",
    "extract-all-comics = metadata_magic.main.comic_archive.extract_all:main",
    "update-comic-archives = metadata_magic.main.comic_archive.comic_archive_update:main",
    "archive-series = metadata_magic.main.comic_archive.series_info:main",
    "archive-book = metadata_magic.main.epub.epub:main"]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Metadata-Magic",
    version="0.6.1",
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
