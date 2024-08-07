#!/usr/bin/env python3

"""Setuptools setup file."""

import setuptools

console_scripts = [
    "mm-archive = metadata_magic.archive.archive:main",
    "mm-bulk-archive = metadata_magic.archive.bulk_archive:main",
    "mm-update = metadata_magic.archive.update:main",
    "mm-error = metadata_magic.error:main",
    "mm-rename = metadata_magic.rename:main",
    "mm-series = metadata_magic.archive.series:main"]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Metadata-Magic",
    version="0.11.3",
    author="Drakovek",
    author_email="DrakovekMail@gmail.com",
    description="Utility for managing metadata.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Drakovek/MetadataMagic",
    packages=setuptools.find_packages(),
    install_requires=["Easy-Text-To-Image", "HTML-String-Tools",
            "html5lib", "Pillow", "Python-Print-Tools", "tqdm"],
    classifiers=["Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent"],
    python_requires='>=3.8',
    entry_points={"console_scripts": console_scripts}
)
