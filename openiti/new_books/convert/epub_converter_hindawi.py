"""Convert Epubs from the Hindawi library to OpenITI mARkdown.

The converter has two main functions:
* convert_file: convert a single epub file.
* convert_files_in_folder: convert all epub files in a given folder

Usage examples:
    >>> folder = r"test/hindawi/"
    >>> meta_fp = folder+"hindawi_metadata_man.yml"
    >>> from epub_converter_hindawi import convert_file, convert_files_in_folder
    >>> src_fp = folder+"26362727.epub"
    >>> convert_file(src_fp, meta_fp, dest_fp=folder+"converted/26362727")
    >>> convert_files_in_folder(folder, meta_fp, dest_folder=folder+"converted")
    Converting all files in folder test/hindawi/ with extensions ['epub']

Both functions use the HindawiEpubConverter class to do the heavy lifting.
The HindawiEpubConverter is a subclass of the GenericEpubConverter,
which in turn is a subclass of the GenericConverter
from the generic_converter module:

GenericConverter
    \_ GenericEpubConverter
            \_ HindawiEpubConverter

Methods of both classes:

(methods of GenericConverter are inherited by GenericEpubConverter;
methods of GenericConverter with the same name
in GenericEpubConverter are overwritten by the latter)

=========================== ========================= =======================
generic_converter           epub_converter_generic    epub_converter_hindawi 
=========================== ========================= =======================
__init__                    __init__                  __init__ 
convert_files_in_folder     (inherited)               (inherited)
convert file                (inherited)               (inherited)
make_dest_fp                (inherited - generic!)    (inherited - generic!)
get_metadata                (inherited - generic!)    get_metadata
get_data                    get_data                  (inherited)
pre_process                 (inherited)               (inherited)
add_page_numbers            (inherited - generic!)    (inherited - generic!)
add_structural_annotations  (inherited - generic!)    (inherited - generic!) 
remove_notes                remove_notes              (inherited)
reflow                      (inherited)               (inherited)
add_milestones              (inherited)               (inherited)
post_process                (inherited - generic!)    (inherited - generic!) 
compose                     (inherited)               (inherited)
save_file                   (inherited)               (inherited)
                            convert_html2md           convert_html2md
                            inspect_epub              (inherited)
                            sort_html_files_by_toc    (inherited)
                            add_unique_tags           (inherited)
=========================== ========================= =======================


Examples:
    >>> from epub_converter_hindawi import HindawiEpubConverter
    >>> from helper.yml2json import yml2json
    >>> folder = "test/"
    >>> fn = "26362727.epub"
    >>> hc = HindawiEpubConverter(dest_folder="test/converted")
    >>> hc.VERBOSE = False
    >>> meta_fp = "test/hindawi/hindawi_metadata_man.yml"
    >>> hc.metadata_dic = yml2json(meta_fp, container = {})
    >>> hc.metadata_file = meta_fp
    >>> hc.convert_file(folder+fn)

    #>>> hc.convert_files_in_folder(folder)

"""

import os

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.new_books.convert.epub_converter_generic import GenericEpubConverter
from openiti.new_books.convert.helper import html2md_hindawi
from openiti.new_books.convert.helper.yml2json import yml2json

##from epub_converter_generic import GenericEpubConverter
##import html2md_hindawi
##from yml2json import yml2json


def convert_file(fp, meta_fp, dest_fp=None, verbose=False):
    """Convert one file to OpenITI format.

    Args:
        fp (str): path to the file that must be converted.
        meta_fp (str): path to the yml file containing the Hindawi metadata
        dest_fp (str): path to the converted file.

    Returns:
        None
    """
    conv = HindawiEpubConverter()
    conv.VERBOSE = verbose
    try:
        conv.metadata_dic = yml2json(meta_fp, container = {})
    except:
        conv.metadata_dic = dict()
        print("No metadata found")
    conv.metadata_file = meta_fp
    conv.convert_file(fp, dest_fp=dest_fp)

def convert_files_in_folder(src_folder, meta_fp, dest_folder=None, verbose=False,
                            extensions=["epub"], exclude_extensions=["yml"],
                            fn_regex=None):
    """Convert all files in a folder to OpenITI format.\
    Use the `extensions` and `exclude_extensions` lists to filter\
    the files to be converted.

    Args:
        src_folder (str): path to the folder that contains
            the files that must be converted.
        meta_fp (str): path to the yml file containing the Hindawi metadata
        dest_folder (str): path to the folder where converted files
            will be stored.
        extensions (list): list of extensions; if this list is not empty,
            only files with an extension in the list should be converted.
        exclude_extensions (list): list of extensions;
            if this list is not empty,
            only files whose extension is not in the list will be converted.
        fn_regex (str): regular expression defining the filename pattern
            e.g., "-(ara|per)\d". If `fn_regex` is defined,
            only files whose filename matches the pattern will be converted.

    Returns:
        None
    """
    msg = "Converting all files in folder {} with extensions {}"
    print(msg.format(src_folder, extensions))
    conv = HindawiEpubConverter()
    conv.VERBOSE = verbose
    try:
        conv.metadata_dic = yml2json(meta_fp, container = {})
    except:
        conv.metadata_dic = dict()
        print("No metadata found")
    conv.metadata_file = meta_fp
    conv.convert_files_in_folder(src_folder, dest_folder=dest_folder,
                                 extensions=extensions,
                                 exclude_extensions=exclude_extensions,
                                 fn_regex=fn_regex)


################################################################################




class HindawiEpubConverter(GenericEpubConverter):
    def __init__(self, dest_folder=None):
        super().__init__(dest_folder)
        self.toc_fn = "nav.xhtml"
        self.metadata_file = None

    def convert_html2md(self, html):
        """Use custom html to mARKdown function for Hindawi epubs."""
        text = html2md_hindawi.markdownify(html)
        return text

    def get_metadata(self, metadata_fp):
        """Custom method to get the metadata of the Hindawi epub file."""
        source_fp = self.source_fp
        bookID = os.path.split(source_fp)[1]
        bookID = os.path.splitext(bookID)[0]
        try:
            meta_dic = self.metadata_dic[bookID]
        except:
            meta_dic = dict()

        meta = ["#META# {}: {}".format(k,v) for k,v in sorted(meta_dic.items())]
        return self.magic_value + "\n".join(meta) + self.header_splitter


if __name__== "__main__":
    import doctest
    doctest.testmod()
    input("Testing finished. Continue?")

    hc = HindawiEpubConverter(dest_folder="test/converted")

    # identify the location of the yml file containing the metadata:
    meta_fp = r"test\hindawi_metadata_man.yml"
    hc.metadata = yml2json(meta_fp, container={})
    
    fp = r"test\26362727.epub"
    hc.convert_file(fp)
    print("converted Hindawi epub", fp)

    hc.convert_files_in_folder("test/hindawi")
    print("converted all epub files in folder", "test/hindawi")

