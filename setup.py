#!/usr/bin/env python3

"""Setuptools setup file."""

import setuptools

console_scripts = [
    "mm-archive = metadata_magic.archive:main",
    "mm-bulk-archive = metadata_magic.archive.bulk_archive:main",
    "mm-update = metadata_magic.archive.update:main",
    "mm-error = metadata_magic.error:main",
    "mm-rename = metadata_magic.rename:main",
    "mm-series = metadata_magic.archive.series:main"]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Metadata-Magic",
    version="0.14.1",
    author="Drakovek",
    author_email="DrakovekMail@gmail.com",
    description="Utility for managing metadata.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Drakovek/MetadataMagic",
    packages=setuptools.find_packages(),
    package_data={"": ["*.json"]},
    install_requires=["CoverGenerator>=0.2.1", "html5lib>=1.1", "HTML-String-Tools>=0.4.0",
            "pillow>=8.0.0", "Python-Print-Tools>=0.2.2", "python-ffmpeg>=2.0.0", "tqdm>=4.64.1"],
    classifiers=["Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent"],
    python_requires='>=3.7',
    entry_points={"console_scripts": console_scripts}
)
