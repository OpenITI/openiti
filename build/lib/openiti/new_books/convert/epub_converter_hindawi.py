"""Convert Epubs from the Hindawi library to OpenITI mARkdown.

Examples:
    >>> from epub_converter_hindawi import HindawiEpubConverter
    >>> from yml2json import yml2json
    >>> folder = "test"
    >>> fn = "26362727.epub"
    >>> hc = HindawiEpubConverter(dest_folder="test/converted")
    >>> meta_fp = "test/hindawi_metadata_man.yml"
    >>> hc.metadata = yml2json(meta_fp, container = {})
    >>> hc.convert_file(os.path.join(folder, fn))
    >>> hc.convert_files_from_folder(folder)

An Epub file is in fact a zipped archive.
The most important element of the archive for conversion purposes
are the folders that contain the html files with the text.
Some Epubs have a table of contents that defines the order
in which these html files should be read.

The HindawiEpubConverter is a subclass of the GenericEpubConverter,
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

| *generic_converter*        | *epub_converter_hindawi* | *epub_converter_hindawi*
|----------------------------|--------------------------|-------------------------
| __init__                   | __init__                 | __init__ 
| convert_files_in_folder    | (inherited)              | (inherited)
| convert file               | (inherited)              | (inherited)
| make_dest_fp               | (inherited - generic!)   | (inherited - generic!)
| get_metadata               | (inherited - generic!)   | get_metadata
| get_data                   | get_data                 | (inherited)
| pre_process                | (inherited)              | (inherited)
| add_page_numbers           | (inherited - generic!)   | (inherited - generic!)
| add_structural_annotations | (inherited - generic!)   | (inherited - generic!) 
| remove_notes               | remove_notes             | (inherited)
| reflow                     | (inherited)              | (inherited)
| add_milestones             | (inherited)              | (inherited)
| post_process               | (inherited - generic!)   | (inherited - generic!) 
| compose                    | (inherited)              | (inherited)
| save_file                  | (inherited)              | (inherited)
|                            | convert_html2md          | convert_html2md
|                            | inspect_epub             | (inherited)
|                            | sort_html_files_by_toc   | (inherited)
|                            | add_unique_tags          | (inherited)


"""

import os

from epub_converter_generic import GenericEpubConverter
import html2md_hindawi
from yml2json import yml2json



class HindawiEpubConverter(GenericEpubConverter):
    def __init__(self, dest_folder=None):
        super().__init__(dest_folder)
        self.toc_fn = "nav.xhtml"

    def convert_html2md(self, html):
        """Use custom html to mARKdown function for Hindawi epubs."""
        text = html2md_hindawi.markdownify(html)
        return text

    def get_metadata(self, source_fp):
        """Custom method to get the metadata of the Hindawi epub file."""
        bookID = os.path.split(source_fp)[1]
        bookID = os.path.splitext(bookID)[0]
        meta_dic = self.metadata[bookID]
        meta = ["#META# {}: {}".format(k,v) for k,v in sorted(meta_dic.items())]
        return self.magic_value + "\n".join(meta) + self.header_splitter


if __name__== "__main__":
    hc = HindawiEpubConverter(dest_folder="test/converted")

    # identify the location of the yml file containing the metadata:
    meta_fp = r"test\hindawi_metadata_man.yml"
    hc.metadata = yml2json(meta_fp, container={})
    
    fp = r"test\26362727.epub"
    hc.convert_file(fp)
    print("converted Hindawi epub", fp)

    hc.convert_files_in_folder("test/hindawi")
    print("converted all epub files in folder", "test/hindawi")

