# MetadataMagic

MetadataMagic is a command line utility for managing media and their respective metadata. This includes cleaning up naming for `.json` metadata as downloaded by applications such as [gallery-dl](https://github.com/mikf/gallery-dl) and [yt-dlp](https://github.com/yt-dlp/yt-dlp), as well as packaging media and metadata together into archive formats such as `.cbz`.

- [Installation](#installation)
- [Scripts](#scripts)

# Installation

MetadataMagic can be downloaded from it's PyPI package using pip:

    pip3 install Metadata-Magic

If you are installing from source, the following python packages are required:
* [HTML-String-Tools](https://github.com/Drakovek/HTML-String-Tools)
* [Python-Print-Tools](https://github.com/Drakovek/Python-Print-Tools)
* [tqdm](https://pypi.org/project/tqdm/)

# Scripts

All scripts contain a [directory] field, which tells the script which directory to search.
If left empty, [directory] defaults to the current working directoy.

- [meta-missing-media](#meta-missing-media)
- [meta-missing-metadata](#meta-missing-metadata)
- [meta-rename](#meta-rename)
- [sort-rename](#sort-rename)
- [archive-comic](#archive-comic)
- [archive-series](#archive-series)

## Finding Missing files

Scripts for finding media with missing metadata or vise versa.

### meta-missing-media
    meta-missing-media [directory]

Prints a list of `.json` metadata files in \[directory\] that do not have a corresponding media file to link to.
Linked media should have the same base name as the `.json` metadata with a different extension.
Includes files in subdirectories.

### meta-missing-metadata
    meta-missing-metadata [directory]

Prints a list of all files in \[directory\] that do not have a corresponding `.json` metadata file.
Linked media should have the same base name as the `.json` metadata with a different extension.
Includes files in subdirectories.

## Rename Files

Scripts for renaming files and metadata.

### meta-rename
    meta-rename [directory] [-i, --id]

Renames all media files and their corresponding `.json` metadata files in a given directory, based on the title provided by the `.json` metadata.

If the `-i, --id` option is included, file names will also include the media ID tag provided by the `.json` metadata as well.
This command renames files in main directory and subdirectories

### sort-rename
    sort-rename [directory] [OPTIONS]

Renames all media files and corresponing `.json` metadata files in given directory to a standard filename with numbers designating their order.
This command does NOT rename files in subdirectories.

Options:

    -n, --name [NAME]       The base filename that will be used when renaming files. "\#" characters will be replaced with the index number.
    -i, --index [INDEX]     The index number to start with when renaming files. Defaults to "1".

## Comic Archives

Scripts for creating and managing comic archives in `.cbz` format.

### archive-comic
    archive-comic [path] [OPTIONS]

Either creates a `.cbz` comic archive or updates an existing `.cbz` archive. Path can either lead to a directory, or an existing `.cbz` file. The program will attempt to get metadata from an existing `.cbz`, a standalone `ComicInfo.xml` file, or `.json` metadata files when creating the `ComicInfo.xml` file for the archive. The program will prompt the user for any metadata that could not be gatherered.

If the user wishes to override any existing metadata when creating the archive, they can use the following options:

    -s, --summary       Override the summary
    -d, --date          Override the date
    -a, --artists       Override the artists
    -p, --publisher     Override the publisher
    -u, --url           Override the URL
    -t, --tags          Override the tags
    -r, --rating        Override the age rating
    -g, --grade         Override the score/grade

### archive-series
    archive-series [directory] [-s, --single]

Updates existing `.cbz` comic archives in a given directory to include series info. The program prompts the user for the series title and the series number of each archive when run.

If the `-s, --single` option is included, all comic archives in the given directory will be set as being book 1 of 1 in a series. This option is intended for indicating that a collection of comic archives are all considered single comics or one-shots.

## EPUB

Scripts for creating and managing ebooks in the `.epub` format.

### archive-book
    archive-book [path] [OPTIONS]

Creates a `.epub` ebook based on the text files in a given directory. The program will attempt to get metadata from `.json` metadata files. The program will prompt the user for any metadata that could not be gathered.

If the user wishes to override any existing metadata when creating the ebook, they can use the following options:

    -s, --summary       Override the summary
    -d, --date          Override the date
    -a, --artists       Override the artists/writers
    -p, --publisher     Override the publisher
    -u, --url           Override the URL
    -t, --tags          Override the tags
    -g, --grade         Override the score/grade