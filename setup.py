#!/usr/bin/env python3

"""Setuptools setup file."""

import setuptools

console_scripts = [
    "meta-missing-media = metadata_magic.main.error_finding.missing_media:main",
    "meta-missing-metadata = metadata_magic.main.error_finding.missing_metadata:main",
    "meta-rename = metadata_magic.main.rename.rename_jsons:main"]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Metadata-Magic",
    version="0.1.1",
    author="Drakovek",
    author_email="DrakovekMail@gmail.com",
    description="Utility for managing metadata.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Drakovek/MetadataMagic",
    packages=setuptools.find_packages(),
    install_requires=["tqdm", "HTML-String-Tools", "Python-Print-Tools"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.0',
    entry_points={"console_scripts": console_scripts}
)
