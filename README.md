# openiti

This is a first attempt to create a Python library that combines all often-used code in the OpenITI project. 

## Description

### git

Modules to leverage git from Python.

Currently contains:

#### clone_OpenITI

#### collect_txt_files

Moves all ara1 () file from all directories into a single directory.

### helper

Frequently used functions in OpenITI. Currently contains:

#### ara

Normalization functions for Arabic text.

#### funcs

Contains a text cleaning function, an id generator, 
and Arabic character count function.

### instantiations

Contains functions used for creating instances of the OpenITI corpus.

Currently contains: 

#### genereate_imech_instantiation

#### generate_istylo_instantiation

### new_books

Modules and functions related to adding new books to the corpus: 

#### scrape

Generic tools for scraping websites, and adaptations of these generic tools 
to specific websites.

#### convert

Generic tools for converting texts in any format to OpenITI format, 
and adaptations of these generic tools to specific websites.

Currently contains: 

##### generic_converter

A generic converter function that includes all steps that need to be taken 
to convert a text into an OpenITI text. 
It contains a GenericConverter class that can be subclassed to create converters
that are geared to specific file types (e.g., epub files, bok files) and 
specific sources (e.g., the Hindawi library, Shamela, etc.)

##### epub_converter_generic

A generic converter that converts epub files to OpenITI mARkdown. 

An Epub file is in fact a zipped archive.
The most important element of the archive for conversion purposes
are the folders that contain the html files with the text.
Some Epubs have a table of contents that defines the order
in which these html files should be read.

The GenericEpubConverter is a subclass of the GenericConverter
from the generic_converter module:

    GenericConverter
        |_ GenericEpubConverter

GenericEpubConverter's main methods are inherited from the GenericConverter:

* convert_file(source_fp): basic procedure for converting an epub file.
* convert_files_in_folder(source_folder): convert all epub files in the folder
    (calls convert_file)

Methods of both classes:
(methods of GenericConverter are inherited by GenericEpubConverter;
methods of GenericConverter with the same name
in GenericEpubConverter are overwritten by the latter)

| **GenericConverter**          | **GenericEpubConverter**
|-----------------------------|-----------------------
| \__init__                    | \__init__
| convert_files_in_folder     | (inherited)
| convert file                | (inherited)
| make_dest_fp                | (inherited)
| get_metadata                | (inherited)
| get_data                    | get_data
| pre_process                 | (inherited)
| add_page_numbers            | (inherited)
| add_structural_annotations  | (inherited)
| remove_notes                | remove_notes
| reflow                      | (inherited)
| add_milestones              | (inherited)
| post_process                | (inherited)
| compose                     | (inherited)
| save_file                   | (inherited)
|                             | inspect_epub
|                             | sort_html_files_by_toc
|                             | add_unique_tags

To create a converter for a specific type of epubs,
subclass the GenericEpubConverter and overwrite
some of its methods:

    GenericConverter
        |_ GenericEpubConverter
                |_ HindawiEpubConverter
                |_ ShamelaEpubConverter
                |_ ...


##### epub_converter_hindawi

Convert Epubs from the Hindawi library to OpenITI mARkdown.

The module contains a HindawiEpubConverter class
which is a subclass of the GenericEpubConverter,
which in turn is a subclass of the GenericConverter
from the generic_converter module:

    GenericConverter
        |_ GenericEpubConverter
                |_ HindawiEpubConverter

HindawiConverter's main methods are inherited from the GenericConverter:

* convert_file(source_fp): basic procedure for converting an epub file.
* convert_files_in_folder(source_folder): convert all epub files in the folder
    (calls convert_file)

Methods of both classes:

(methods of GenericConverter are inherited by GenericEpubConverter;
methods of GenericConverter with the same name
in GenericEpubConverter are overwritten by the latter)

| *GenericConverter*          | *GenericEpubConverter*  | *HindawiEpubConverter*
|-----------------------------|-------------------------|-----------------------
| __init__                    | __init__                | __init__ 
| convert_files_in_folder     | (inherited)             | (inherited)
| convert file                | (inherited)             | (inherited)
| make_dest_fp                | (inherited)             | (inherited)
| get_metadata                | (inherited)             | get_metadata
| get_data                    | get_data                | (inherited)
| pre_process                 | (inherited)             | (inherited)
| add_page_numbers            | (inherited)             | (inherited)
| add_structural_annotations  | (inherited)             | (inherited)
| remove_notes                | remove_notes            | (inherited)
| reflow                      | (inherited)             | (inherited)
| add_milestones              | (inherited)             | (inherited)
| post_process                | (inherited)             | (inherited)
| compose                     | (inherited)             | (inherited)
| save_file                   | (inherited)             | (inherited)
|                             | convert_html2md         | convert_html2md
|                             | inspect_epub            | (inherited)
|                             | sort_html_files_by_toc  | (inherited)
|                             | add_unique_tags         | (inherited)

##### html2md

Generic conversion tool to convert html files to OpenITI mARkdown.

This module is an adaptation of python-markdownify
(https://github.com/matthewwithanm/python-markdownify)
to output OpenITI mARkdown.
It also adds methods for tables and images,
and a post-processing method.
It uses BeautifulSoup to create a flexible converter.

This module's MarkdownConverter class can be used as a base class 
and subclassed to add methods, adapt the post-processing method, etc.

The easiest way to use this is to simply feed the html (as string)
to the markdownify() function, which will create an instance
of the HindawiConverter class and return the converted string. E.g.,

    >>> h = '<div class="section" id="sect2_4"><h4>abc</h4></div>'
    >>> hindawi_html2md.markdownify(h)
    '\n\n### ||| abc\n\n'



##### html2md_hindawi

Convert html in the Hindawi library epub files to OpenITI mARkdown.

This module subclasses the generic MarkdownConverter class
from the html2md module.

The subclass in this module, HindawiConverter,
adds methods specifically for the conversion of books from
the Hindawi library to OpenITI mARkdown:

* special treatment of <h4> heading tags
* div classes "poetry_container", "section", "footnote" and "subtitle"
* span class "quran"

The easiest way to use this is to simply feed the html (as string)
to the markdownify() function, which will create an instance
of the HindawiConverter class and return the converted string. E.g.,

    >>> h = 'abc <em>def</em> ghi'
    >>> html2md.markdownify(h)
    'abc *def* ghi'
    
    >>> h = '<h1>abc</h1>'
    >>> html2md.markdownify(h)
    '\n\n### | abc\n\n'    

##### yml2json

Convert a YML metadata file to json.

The yml2json function can be used to convert a yml metadata file to

* a list of dictionaries: useful for
    - conserving the order
    - conserving comments between the records
* a dictionary of dictionaries (key: record id, val: metadata dictionary),
  useful for easy lookup by record id

#### add

Tools to add texts to the OpenITI corpus.

### release

Tools to create a new release of the OpenITI corpus.

Currently contains: 

#### collect_openITI_version

Copies all data from the XXXXAH directories to a single directory 
in order to publish a version of OpenITI.

#### collect_release_stats