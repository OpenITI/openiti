"""converter that converts an Epub from the Urdu Elibrary to OpenITI mARkdown.

Examples:
    Generic epub conversion::
    
        >>> from epub_converter_generic import UrduElibEpubConverter
        >>> converter = UrduElibEpubConverter(dest_folder="test/converted")
        >>> converter.VERBOSE = False
        >>> folder = r"test/urduElib"
        >>> fn = r"2897_Alf-Laila-wa-Laila_1.epub"
        >>> converter.convert_file(os.path.join(folder, fn))
        >>> converter.convert_files_in_folder(folder, ["epub",])

An Epub file is in fact a zipped archive.
The most important element of the archive for conversion purposes
are the folders that contain the html files with the text.

The Urdu Elibrary epub files contain two files that specify the order of
the html files that contain the text:
* OEBPS/content.opf: (Open Publication Format): xml file containing
    some metadata + a manifest describing the order of the html files
* OEPBS/toc.ncx: (Navigation Control XML): a hierarchical table of contents

The UrduElibEpubConverter is a subclass of the GenericEpubConverter,
which itself is a subclass of the GenericConverter 
from the generic_converter module:

GenericConverter
    |_ GenericEpubConverter
        |_ UrduElibEpubConverter

Methods of these classes:
(methods of GenericConverter are inherited by GenericEpubConverter;
methods of GenericConverter with the same name
in GenericEpubConverter are overwritten by the latter; and so on)

=========================== ======================== ========================
GenericConverter            GenericEpubConverter     UrduElibEpubConverter
=========================== ======================== ========================
__init__                    __init__                 __init__
convert_files_in_folder     (inherited)              (inherited)
convert_file                (inherited)              (inherited)
make_dest_fp                (inherited - generic!)   (inherited - generic!)
get_metadata                (inherited - generic!)   (inherited - generic!)
get_data                    get_data                 get_data
pre_process                 (inherited)              (inherited)
add_page_numbers            (inherited - generic!)   (inherited - generic!)
add_structural_annotations  (inherited - generic!)   (inherited - generic!)
remove_notes                remove_notes             (inherited)
reflow                      (inherited)              (inherited)
add_milestones              (inherited)              (inherited)
post_process                (inherited - generic!)   (inherited - generic!)
compose                     (inherited)              (inherited)
save_file                   (inherited)              (inherited)
                            inspect_epub             (inherited)
                            sort_html_files_by_toc   (inherited)
                            add_unique_tags          (inherited)
=========================== ======================== ========================

"""

import codecs
import os
import re
import zipfile
import time

from bs4 import BeautifulSoup


if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.new_books.convert.epub_converter_generic import GenericEpubConverter
from openiti.new_books.convert.helper import html2md



class UrduElibEpubConverter(GenericEpubConverter):

    def __init__(self, dest_folder=None, overwrite=True):
        """Initialize the class and its super-class."""
        super().__init__(dest_folder=dest_folder, overwrite=overwrite)
        self.metadata_file = None

    def get_metadata(self, src_fp):
        """We'll extract the metadata in the get_data method.
        """
        return ""
        

    def get_data(self, src_fp):
        """Converts an Epub file to an OpenITI mARkdown document.

        If a dictionary is passed as the unique_tags parameter,
        the function will keep track of all tags (and their classes)
        used in the converted Epub file.

        Args:
            src_fp (str): the path to the file currently being converted.
            dest_folder (str): the path to the folder where the converted file
                should be stored.
            conv_func (function): the function used to convert html to mARkdown.
            toc_fn (str): filename of the table of contents file within the epub.
            root_tag_string (str): the path to the BeautifulSoup element that
                contains the full text.
                Default: the body tag.
            unique_tabs (dict): a dictionary containing all tags used in the Epub.
                Default: None (tags used in the epubs will not be listed)

        Returns:
            unique_tabs (dict): a dictionary containing all tags used in the Epub.
        """
        if src_fp.endswith(".epub"):
            zp = zipfile.ZipFile(src_fp)
            if self.VERBOSE:
                fn = os.path.basename(src_fp)
##                msg = "Press Enter to convert %s to txt..." % fn
##                input(msg)

            # make a list of the html files in the epub:

            toc_fn = self.get_toc(src_fp)
            html_files = []
            for info in zp.infolist():
                if info.filename.endswith(self.toc_fn):
                    toc_fp = info.filename
                    if self.VERBOSE:
                        print("toc_fp", toc_fp)
                elif info.filename.endswith("html"):
                    html_files.append(info.filename)

            # sort the list of the html files in the correct order:

            try:
                html_files = self.sort_html_files_by_toc(zp, toc_fp, html_files)
            except:
                if self.VERBOSE:
                    print("No table of contents. Use file numbers for order.")
                html_files = html_files
            if self.VERBOSE:
                print("Table of contents of the Epub file:")
                for file in html_files:
                    print("    ", file)
                print("End of table of contents")

            # get the volume number:
            try:
                vol_no = int(re.findall("_(\d+)\.epub", src_fp)[0])
            except:
                vol_no = 1

            # Extract the text from the different html files in the epub archive:

            new_text = ""
            for fp in html_files:
                fn = os.path.split(fp)[-1]
                data = zp.read(fp)
                text = codecs.decode(data, "utf-8")
                text = re.sub(r"<br />", "\n", text)
                soup = BeautifulSoup(text)
                root_tag = eval(self.root_tag_string)
                self.add_unique_tags(root_tag, src_fp, fn)
                text = self.convert_html2md(root_tag)
                page_no = int(re.findall("\d+", fn)[-1])
                page_no = f"\n\nPageV{vol_no:02d}P{page_no:03d}"
                new_text += "\n\n\n\n" + text + page_no
            new_text = re.sub("\n{3,}", "\n\n", new_text)

            metadata_raw = zp.read("OEBPS/content.opf")
            soup = BeautifulSoup(metadata_raw)
            meta_tag = soup.find("metadata")
            metadata = ""
            for dc_tag in soup.find_all(lambda tag: tag.name.startswith("dc:")):
                key = dc_tag.name.split(":")[1]
                val = dc_tag.text
                if val.strip():
                    metadata += f"#META# {key}: {val}\n"
            metadata = self.magic_value + metadata + self.header_splitter

            new_text = metadata + new_text
            return new_text


    def post_process(self, text):
        """Custom post-processing for masaha texts"""
        # put page number at the bottom of the page:
        text = re.sub("\n(?![\n\rP~# ])", r"\n# ", text)
        processed = super().post_process(text)
        return processed
    

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    input("Testing finished. Continue?")
    
##    c = GenericEpubConverter()
##    c.make_dest_fp("a/b/c.epub")
##    print(c.dest_fp)
##    c = GenericEpubConverter("test/converted")
##    c.make_dest_fp("a/b/c.epub")
##    print(c.dest_fp)
##
##
##    input()

##    gen_converter = GenericEpubConverter("test/converted")
##    fp = r"test\Houellebecq 2019 - serotonine.epub"
##    gen_converter.convert_file(fp)
##    print("converted Houellebecq")
##    gen_converter.VERBOSE = True
##    gen_converter.convert_files_in_folder("test", ["epub",])
##    print("all files in test folder converted")
##
##    print("-"*60)

    import html2md_hindawi
    HindawiConverter = GenericEpubConverter("test/converted")
    HindawiConverter.convert_html2md = html2md_hindawi.markdownify
    HindawiConverter.toc_fn = "nav.xhtml"
    fp = r"test\26362727.epub"
    HindawiConverter.convert_file(fp)
    print("converted Hindawi text")




