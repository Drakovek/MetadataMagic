#!/usr/bin/env python3

"""Setuptools setup file."""

import setuptools

console_scripts = [
    "mm-archive = metadata_magic.archive.archive:main",
    "mm-update = metadata_magic.archive.update:main",
    "mm-error = metadata_magic.error:main",
    "mm-rename = metadata_magic.rename:main",
    "archive-series = metadata_magic.archive.series_info:main",
    "archive-all-comics = metadata_magic.archive.archive_all:main",
    "extract-all-comics = metadata_magic.archive.extract_all:main"]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Metadata-Magic",
    version="0.8.6",
    author="Drakovek",
    author_email="DrakovekMail@gmail.com",
    description="Utility for managing metadata.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Drakovek/MetadataMagic",
    packages=setuptools.find_packages(),
    install_requires=["chardet", "lxml", "tqdm", "HTML-String-Tools", "Pillow", "Python-Print-Tools"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.9',
    entry_points={"console_scripts": console_scripts}
)
