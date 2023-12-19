# MetadataMagic

MetadataMagic is a command line utility for managing media and their respective metadata. This includes cleaning up naming for `.json` metadata as downloaded by applications such as [gallery-dl](https://github.com/mikf/gallery-dl) and [yt-dlp](https://github.com/yt-dlp/yt-dlp), as well as packaging media and metadata together into archive formats such as `.cbz` and `epub`.

- [Installation](#installation)
- [Scripts](#scripts)

# Installation

MetadataMagic can be downloaded from it's PyPI package using pip:

    pip3 install Metadata-Magic

If you are installing from source, the following python packages are required:
* [Chardet](https://github.com/chardet/chardet)
* [Easy-Text-To-Image](https://github.com/Drakovek/EasyTextToImage)
* [HTML-String-Tools](https://github.com/Drakovek/HTML-String-Tools)
* [lxml](https://github.com/lxml/lxml)
* [Pillow](https://github.com/python-pillow/Pillow)
* [Python-Print-Tools](https://github.com/Drakovek/Python-Print-Tools)
* [tqdm](https://pypi.org/project/tqdm/)

# Scripts

All scripts contain a [directory] field, which tells the script which directory to search.
If left empty, [directory] defaults to the current working directoy.

- [mm-archive](#mm-archive)
- [mm-bulk-archive](#mm-bulk-archive)
- [mm-update](#mm-update)
- [mm-series](#mm-series)
- [mm-rename](#mm-rename)
- [mm-error](#mm-error)

## mm-archive

The `mm-archive` command can be used to archive the media files and `.json` metadata in a directory into a single media archive. Currently, the `mm-archive` command supports `.cbz` and `.epub` formatting. If the given directory contains `.txt` or `.html` files, these text files will be archived and converted into the `.epub` ebook file. If the given directory contains only `.png` or `.jpeg`/`.jpg` image files and no text, the files will be archived into a `.cbz` comic book archive file.

    mm-archive [directory] [OPTIONS]

Metadata for the archive will be pulled from existing `.json` metadata contained in the given directory, and you will be prompted for any metadata fields that could not be found in the existing `.json` files. Additionally, the you can choose to override the automatic metadata generation for any field and enter metadata fields manually using the following options.

    -s, --summary    Manually input the media's summary/description
    -d, --date       Manually input the media's publication date
    -a, --artists    Manually input the artist(s), cover artist(s), and writer(s)
    -p, --publisher  Manually input the media's publisher
    -u, --url        Manually input the media's source URL
    -t, --tags       Manually input the media tags
    -r, --rating     Manually input the age rating for the media
    -g, --grade      Manually input the grade/user score

### Options specific to .epub

When creating an `.epub` ebook out of text files, you will be prompted with the option to edit how each of the original files will be structured within the new ebook. By default, each of the original files will be treated as its own section with an entry in the table of contents, with a title based on the original filename. You can then choose to alter this structure for your own needs:

    ENTRY     TITLE           FILES                   
    -----------------------------------------------
    001       cover           [01] cover.html
    002       contents        [02] contents.html
    003       ch1-1           [03] ch1-1.txt
    004       illustration    [04] illustration.png
    005       ch1-2           [05] ch1-2.txt
    006       ch2             [06] ch2.txt
    
    * - Not Included in Table of Contents

    OPTIONS:
    T - Edit Chapter Title
    C - Toggle Inclusion in Contents
    G - Group Files
    S - Separate Files
    W - Commit Changes

Firstly, you can edit the title of any given entry, which will be the title used for that entry in the table of contents.

You can also toggle whether to include an entry in the table of contents. Any entry with this flag will still be included in the ebook, but it will not be listed as a separate entry in the contents.

Finally, you can choose to group entries together so they will be included as one entry in the final ebook. This is useful if for example, you want to include an illustration at the start of a chapter, but don't want the image to be treated as a separate page.

After altertering the structure, it may look like this:
    
    ENTRY     TITLE        FILES                   
    ----------------------------------------------------------------------------
    001       Cover        [01] cover.html
    002*      Contents     [02] contents.html
    003       Chapter 1    [03] ch1-1.txt, [04] illustration.png, [05] ch1-2.txt
    004       Chapter 2    [06] ch2.txt
    
    * - Not Included in Table of Contents

    OPTIONS:
    T - Edit Chapter Title
    C - Toggle Inclusion in Contents
    G - Group Files
    S - Separate Files
    W - Commit Changes

You will also be prompted to generate a cover image:
    
    Generate Cover Image? (Y/N):

If you choose YES, a generic cover image will be generated for the ebook including the book's title and author, based on the metadata.

## mm-bulk-archive

The `mm-bulk-archive` command is used to bulk archive or extract a large number of files.

### Bulk Archiving

    mm-bulk-archive [directory]

This will archive every eligable file in a given directory into `.cbz` comic archives for images and `.epub` ebooks for text, replacing the original files. Files will only be archived if they have a corresponding `.json` metadata file, and that metadata will be used for the metadata of the newly created archives. Each individual text and image file will be turned into its own archive file.

### Bulk Extracting

    mm-bulk-archive --extract [directory]

This will read every `.cbz` and `.ebub` archive file in the given directory and extract the files within, replacing the archives. You will be prompted on whether to preserve the structure of the archive:

    Remove archive structure? (Y/[N])

If you choose to remove the structure, only the original files used to create the archive will be extracted (images/text and `.json` metadata), and all other files and folders will be discarded. The original files will be extracted directly into the given directory with no containing folder.

If you choose NOT to remove the structure, all the files of the archive will be extracted, including metadata and structural files for the `.cbz` and `epub` formats. The files for each archive will be contained in their own folders, extracted into the given directory.

## mm-update

    mm-update [path] --cover

The `mm-update` command allows you to update the metadata fields of `.cbz` and `.epub` archives. If you enter a directory as the filepath, every media archive in that directory and its subdirectories will be updated with the new metadata. Otherwise if you enter a filepath for a specific `.cbz` or `.epub` file, only that single archive will be updated. You will be prompted to give metadata for several fields, which can either be altered or left blank. The archive metadata for any field left blank will not be altered, and while fields you responded to will be updated to match your response.

If the `--cover` option is added, any auto-generated cover images for the archive(s) will be regenerated. Manually created or existing cover images that weren't auto-generated by MetadataMagic will not be affected.

## mm-series

    mm-series [directory]

The `mm-series` command allows you to add metadata to `.cbz` and `.epub` archives indicating their place in a book/comic series. All the files in the given directory should be part of the same series and in alpha-numerical order. You will then be prompted to give a series title and edit the placement in the series for each of the archive files:

    ENTRY    FILE                       
    ----------------------------------------
    1.0      [01A] Example Vol 1.cbz
    2.0      [01B] Example Special Issue.cbz  
    3.0      [02] Example Vol 2.epub       

    [E] Edit
    [R] Reset
    [W] Write Series Info
    [Q] Quit Without Saving

By default, archives will be given series entry numbers starting at 1.0 and incrementing by 1 with each entry. If any of the archives already contain series information, that order will be given priority first, but the order can be reset to being ordered alpha-numerically.

The user can choose to edit the series number for eny entry, including using decimals, useful for special issues and side-entries that don't fit the normal mainline numbering of a series. When you edit an entry, all subsequent entries will automatically be altered to come after the edited entry.

After altering the series numbering, it may look like this:

    ENTRY    FILE                       
    ----------------------------------------
    1.0      [01A] Example Vol 1.cbz
    2.5      [01B] Example Special Issue.cbz  
    2.0      [02] Example Vol 2.epub       

    [E] Edit
    [R] Reset
    [W] Write Series Info
    [Q] Quit Without Saving

### Single Series

Some comic and ebook readers don't play well with one-shot comics that contain no metadata about being part of a series. For these readers, it can be useful to mark standalone comics and books instead as being part of a series that only has one entry. For these standalone archives, you can use the `--standalone` option for the `mm-series` command:

    mm-series --standalone [directory]

With this command the `.cbz` and `.epub` files in the given directory will be marked as being entry one of one in their own series, with their series titles being the same as the archive titles.

## mm-rename

The `mm-rename` command allows you to easily bulk rename `.cbz` and `.epub` archives, as well media files with associated `.json` metadata. For media files with a separate metadata file, the `mm-rename` commands will rename both the media and `.json` file together so they keep the same filename and continue being associated with each other.

### Sort Rename

    mm-rename --sort-rename [directory]

The `--sort-rename` option allows you to rename all the files in a directory to share one template filename with the only differences being an index number indicating what order the files should appear in. The files should already be in alpha-numerical order before being renamed.

This is useful for preparing image files (with or without `.json` metadata) for being archived into a `.cbz` comic book archive. Files in a `.cbz` file are ordered alphabetically, and while `Metadata-Magic` can sort more irregularly formatted filenames alphanumerically, many comic book readers use extremely simple sorting that can order "1" after "10" or get confused if one file contains an extra space character.

When using `--sort-rename` you will first be prompted for a template:

    Sort Rename Template (Default is "Example"):

This is for the base template that files will be renamed to. By default, the index number will be appended to the end of the template, but you can also indicate where you want the index number to appear using "#" characters. Additionally the index number for each file will be padded with zeros to match the number of "#" characters in the template (Again, useful for simple `.cbz` sorting). 

For example, a template of "Title! (Page ###)" will result in files "Title! (Page 001).jpg", "Title! (Page 002).jpg", "Title! (Page 003).png", etc.

Next, you will be prompted for an starting index number:

    Starting Index (Default is "1"):

This is just the starting index number that will be used in place of the index number in the template. You will almost always leave this at 1, but it can be useful if you want the file order to start with 0 for example. You CAN start with indexes less than zero, but that isn't recommended, as most programs won't sort negative numbers properly.

### Metadata Rename

    mm-rename --metadata-rename [directory]
    
The `--metadata-rename` option allows you to bulk rename files in a given directory based on their metadata. This can be either embedded metadata as in `.cbz` and `.epub` archives, or associated metadata in a separate `.json` metadata file. Any files that do not have embedded or associated metadata will be ignored. When running this command, you will be prompted on what template to use:

    Rename in the format "[options] title"
    A - Artist
    D - Date

    Options or "C" for Custom:

You are given the option of using the default template which names files based on the "title" field in the metadata as well as the "artist" and/or "date" fields in the metadata. Inputing nothing will just name files based on the title, while inputting "AD" would include the artist and date as well, resulting in filenames like "\[2020-01-01 - Person\] Example.epub", "\[2020-01-02 - Person\] Title.cbz", etc.

Additionally, you can also input "C" to use a custom template, and you will be prompted to enter one:

    Include Metadata Fields in format "{key}"
    Template: 

With this, you can format the files any way you wish, using any metadata fields you wish. Keys for metadata fields you wish to include are put between "{}", and all other characters will be used as is. For example, if you wanted to name files based on their title and publisher, you could use the template "<{publisher}>_{title}", resulting in filenames like "\<BookCo\>_Example.epub", "\<ArtCo\> Title.cbz", etc.

If the metadata for a file does not contain metadata for one of the fields requested in the template, that file will be ignored and not renamed.

## mm-error

The `mm-error` command allows you to search for errors and abnormalities with files and their metadata.

### Missing Media

    mm-error --missing-media [directory]

The `--missing-media` option allows you to search a given directory and subdirectory for `.json` metadata files that don't match with any associated media, and lists the orphaned `.json` in the terminal. Useful for finding cases where the media and metadata have been seperated or the media file failed to download in the first place.

### Missing JSON

    mm-error --missing-json [directory]

The `--missing-json` option allows you to search for the opposite of the `--missing-media` option, searching for media files that do not have an associated `.json` metadata files. This will NOT list media files in directories that contain no `.json` files at all, as the command will assume that this is a directory containing files with embedded metadata or no metadata to begin with. This will only list media files with missing `.json` metadata in directories where otherwise, all other files DO have `.json` metadata.

### Missing Fields

    mm-error --missing-fields [directory]

The `--missing-fields` allows you to search for `.cbz` and `.epub` archives that do not contain information for a specific metadata field. When you run this command, you will be prompted for which metadata field to search for:

    [T] Missing title
    [A] Missing artist
    [D] Missing date
    [S] Missing summary
    [P] Missing publisher
    [U] Missing URL
    [R] Missing Age Rating
    [G] Missing Grade/Score
    [L] Missing Labels/Tags
    [C] Missing Chain/Series
    Which Missing Metadata Field?:

After your response, the command will list every media archive missing information for the particular field in question. This is useful for checking for fields you may have forgotten to add manually or checking which archives you haven't reviewed and scored yet, for example.