"""Convert Epubs from the Masaha Hurra library to OpenITI mARkdown.

The converter has two main functions:
* convert_file: convert a single epub file.
* convert_files_in_folder: convert all epub files in a given folder

Usage examples:
    >>> folder = "test/masaha/epub/"
    >>> meta_fp = "test/masaha/all_books/meta/all_metadata.json"
    >>> from epub_converter_masaha import convert_file, convert_files_in_folder
    >>> src_fp = folder+"000008.epub"
    >>> convert_file(src_fp, meta_fp, dest_fp=folder+"converted/Masaha000008")
    >>> convert_files_in_folder(folder, meta_fp, dest_folder=folder+"converted")
    Converting all files in folder test/masaha/epub with extensions ['epub']

Both functions use the MasahaEpubConverter class to do the heavy lifting.
The MasahaEpubConverter is a subclass of the GenericEpubConverter,
which in turn is a subclass of the GenericConverter
from the generic_converter module:

GenericConverter
    \_ GenericEpubConverter
            \_ MasahaEpubConverter

Methods of both classes:

(methods of GenericConverter are inherited by GenericEpubConverter;
methods of GenericConverter with the same name
in GenericEpubConverter are overwritten by the latter)

=========================== ========================= =======================
generic_converter           epub_converter_generic    epub_converter_masaha 
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
post_process                (inherited - generic!)    post_process
compose                     (inherited)               (inherited)
save_file                   (inherited)               (inherited)
                            convert_html2md           convert_html2md
                            inspect_epub              (inherited)
                            sort_html_files_by_toc    sort_html_files_by_toc
                            add_unique_tags           (inherited)
=========================== ========================= =======================


Examples:
    >>> from epub_converter_masaha import MasahaEpubConverter
    >>> from helper.yml2json import yml2json
    >>> folder = "test/"
    >>> fn = "26362727.epub"
    >>> hc = MasahaEpubConverter(dest_folder="test/converted")
    >>> hc.VERBOSE = False
    >>> meta_fp = "masaha/all_books/meta/all_metadata.json"
    >>> hc.metadata_file = meta_fp
    >>> hc.convert_file(folder+fn)

    #>>> hc.convert_files_in_folder(folder)

"""

import os
import json
import shutil
import re

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.new_books.convert.epub_converter_generic import GenericEpubConverter
from openiti.new_books.convert.helper import html2md_masaha
from openiti.new_books.convert.helper.yml2json import yml2json


def convert_file(fp, meta_fp, dest_fp=None, verbose=False, overwrite=False):
    """Convert one file to OpenITI format.

    Args:
        fp (str): path to the file that must be converted.
        meta_fp (str): path to the yml file containing the Masaha metadata
        dest_fp (str): path to the converted file.

    Returns:
        None
    """
    conv = MasahaEpubConverter(overwrite=overwrite)
    conv.VERBOSE = verbose
    with open(meta_fp, mode="r", encoding="utf-8") as file:
        d = json.load(file)
        conv.metadata_dic = {int(item["book_id"]): item for item in d}
    conv.metadata_file = meta_fp
    conv.convert_file(fp, dest_fp=dest_fp)

##def convert_multifile_text(folder, meta_fp, dest_folder, verbose=False):
##    for i, fn in enumerate(os.listdir(folder)):
##        if i == 0:
##            dest_fp = os.path.join(dest_folder, os.path.splitext(fn)[0])
##        
        

def convert_files_in_folder(src_folder, meta_fp, dest_folder=None, verbose=False,
                            extensions=["epub"], exclude_extensions=["yml"],
                            fn_regex=None, overwrite=False):
    """Convert all files in a folder to OpenITI format.\
    Use the `extensions` and `exclude_extensions` lists to filter\
    the files to be converted.

    Args:
        src_folder (str): path to the folder that contains
            the files that must be converted.
        meta_fp (str): path to the yml file containing the Masaha metadata
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
    conv = MasahaEpubConverter(overwrite=overwrite)
    conv.VERBOSE = verbose
    with open(meta_fp, mode="r", encoding="utf-8") as file:
        d = json.load(file)
        conv.metadata_dic = {int(item["book_id"]): item for item in d}
    conv.metadata_file = meta_fp
    conv.convert_files_in_folder(src_folder, dest_folder=dest_folder,
                                 extensions=extensions,
                                 exclude_extensions=exclude_extensions,
                                 fn_regex=fn_regex)


################################################################################




class MasahaEpubConverter(GenericEpubConverter):
    def __init__(self, dest_folder=None, overwrite=True):
        super().__init__(dest_folder=dest_folder, overwrite=overwrite)
        self.toc_fn = "content.opf"
        self.metadata_file = None


    def convert_files_in_folder(self, source_folder, dest_folder=None,
                                extensions=[], exclude_extensions=[],
                                fn_regex=None):
        """Convert all files in a folder to OpenITI format.\
        Use the `extensions` and `exclude_extensions` lists to filter\
        the files to be converted.

        Args:
            source_folder (str): path to the folder that contains
                the files that must be converted.
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
        failed = []
        if dest_folder:
            self.dest_folder = dest_folder
        fp_list = self.filter_files_in_folder(source_folder, extensions,
                                              exclude_extensions, fn_regex)
        for fp in fp_list:
            print(fp)
            try:
                self.convert_file(fp)
            except Exception as e:
                print("ERROR:", e)
                failed.append((fp, e))
                

        # deal with multivolume texts that are in separate folders:
        multivol_folders = [f for f in os.listdir(source_folder) if f.startswith("multivol")]
        multivol_folders = [os.path.join(source_folder, f) for f in multivol_folders]
        
        for folder in multivol_folders:
            print(folder)
            try:
                first_fn = sorted(os.listdir(folder))[0]
            except Exception as e:
                print("folder does not contain files:", e)
                failed.append((folder, e))
                continue
            outfn = re.sub("\.epub", "Vols.automARkdown", first_fn)
            outfp = os.path.join(dest_folder, outfn)
            if os.path.exists(outfp):
                print(outfp, "already exists")
                continue
            temp_folder = os.path.join(dest_folder, "temp")
            if os.path.exists(temp_folder):
                shutil.rmtree(temp_folder)
            os.makedirs(temp_folder)
            self.convert_files_in_folder(folder, dest_folder=temp_folder,
                                         extensions=extensions,
                                         exclude_extensions=exclude_extensions,
                                         fn_regex=fn_regex)
            # combine all volumes into one folder:
            combined = []
            endnotes = []
            for i, fn in enumerate(sorted(os.listdir(temp_folder))):
                fp = os.path.join(temp_folder, fn)
                if i == 0:
                    outfn = re.sub("\.", "Vols.", fn) 
                    outfp = os.path.join(dest_folder, outfn)
                with open(fp, mode="r", encoding="utf-8") as file:
                    text = file.read()
                    if i != 0:
                        text = re.split("#META#Header#End#?", text)[-1]
                        page = "PageV{:02d}P{:03d}"
                        text = re.sub("PageV\d+P(\d+)", r"PageV{:02d}P\1".format(i+1), text)
                if re.findall("### \|EDITOR\|[ \r\n]+ENDNOTES:?", text):
                    text, notes = re.split("### \|EDITOR\|[ \r\n]+ENDNOTES:?", text)
                    endnotes.append(notes)
                combined.append(text)
            with open(outfp, mode="w", encoding="utf-8") as file:
                text = "\n\n".join(combined)
                endnotes = "\n\n".join(endnotes)
                file.write(text + "\n\n### |EDITOR|\n\nENDNOTES:\n\n" + endnotes)
        print("Converting all files done")
        if failed:
            print("These files failed to convert:")
            for fp, e in failed:
                print(fp, e)
        
                

    def sort_html_files_by_toc(self, zp, toc_fp, html_files):
        """Gets the table of contents from the Epub file.

        Args:
            zp: zipfile object
            toc_fp (str): filepath to the table of contents of the epub.
            html_files(list): an unordered list of the html files in the epub.

        Returns:
            toc (list): a list of filepaths to the html files
                in the epub file, in the order specified by the
                table of contents
        """
        html_files_dict = {os.path.split(fp)[-1] : fp for fp in html_files}
        toc_data = zp.read(toc_fp)
        toc_data = codecs.decode(toc_data, "utf-8")
        soup = BeautifulSoup(toc_data)
        toc_ol = soup.find("spine")
        toc = []
        for item in toc_ol.find_all("itemref"):
            fn = os.path.split(item.get("idref"))[-1]
            if fn in html_files_dict:
                toc.append(html_files_dict[fn])
        return toc

    def convert_html2md(self, html):
        """Use custom html to mARKdown function for Masaha epubs."""
        text = html2md_masaha.markdownify(html)
        return text

    def get_metadata(self, metadata_fp):
        """Custom method to get the metadata of the Masaha epub file."""
        source_fp = self.source_fp
        bookID = os.path.split(source_fp)[1]
        bookID = int(os.path.splitext(bookID)[0])
        meta_dic = self.metadata_dic[bookID]
        meta = ["#META# {}: {}".format(k,v) for k,v in sorted(meta_dic.items())]
        return self.magic_value + "\n".join(meta) + self.header_splitter

    def post_process(self, text):
        """Custom post-processing for masaha texts"""
        # put page number at the bottom of the page:
        text = re.sub("(PageV\d+P\d+)(.+?)(?=Page|\Z)", r"\2\n\n\1\n\n", text, flags=re.DOTALL)
        processed = super().post_process(text)
        return processed
        


if __name__== "__main__":
    #import doctest
    #doctest.testmod()
    #input("Testing finished. Continue?")

    # identify the location of the yml file containing the metadata:
    meta_fp = r"test\masaha\meta\all_metadata.json"
    src_folder = "test/masaha/epub"
    convert_files_in_folder(src_folder, meta_fp, dest_folder="test/converted", verbose=False)
##    hc.metadata = yml2json(meta_fp, container={})
    
##    fp = r"test\26362727.epub"
##    hc.convert_file(fp)
##    print("converted Masaha epub", fp)
##
##    hc.convert_files_in_folder("test/masaha")
##    print("converted all epub files in folder", "test/masaha")

