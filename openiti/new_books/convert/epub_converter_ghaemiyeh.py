"""Convert Epubs from the Ghbook / Ghaemiyeh (Qaimiyya) library \
to OpenITI mARkdown.

The converter has two main functions:
* convert_file: convert a single epub file.
* convert_files_in_folder: convert all epub files in a given folder

Usage examples:
    >>> folder = "test/ghaemiyeh/epub/"
    >>> meta_fp = "test/ghaemiyeh/all_books/meta/all_metadata.json"
    >>> from epub_converter_ghaemiyeh import convert_file, convert_files_in_folder
    >>> src_fp = folder+"000008.epub"
    >>> convert_file(src_fp, meta_fp, dest_fp=folder+"converted/ghaemiyeh000008")
    >>> convert_files_in_folder(folder, meta_fp, dest_folder=folder+"converted")
    Converting all files in folder test/ghaemiyeh/epub with extensions ['epub']

Both functions use the ghaemiyehEpubConverter class to do the heavy lifting.
The ghaemiyehEpubConverter is a subclass of the GenericEpubConverter,
which in turn is a subclass of the GenericConverter
from the generic_converter module:

GenericConverter
    \_ GenericEpubConverter
            \_ ghaemiyehEpubConverter

Methods of both classes:

(methods of GenericConverter are inherited by GenericEpubConverter;
methods of GenericConverter with the same name
in GenericEpubConverter are overwritten by the latter)

=========================== ========================= =======================
generic_converter           epub_converter_generic    epub_converter_ghaemiyeh 
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
    >>> from epub_converter_ghaemiyeh import ghaemiyehEpubConverter
    >>> from helper.yml2json import yml2json
    >>> folder = "test/"
    >>> fn = "26362727.epub"
    >>> hc = ghaemiyehEpubConverter(dest_folder="test/converted")
    >>> hc.VERBOSE = False
    >>> meta_fp = "ghaemiyeh/all_books/meta/all_metadata.json"
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
from openiti.new_books.convert.helper import html2md_ghaemiyeh
from openiti.new_books.convert.helper.yml2json import yml2json


def load_metadata(meta_fp):
    with open(meta_fp, mode="r", encoding="utf-8") as file:
        meta = file.read().splitlines()
    header = meta.pop(0).split("\t")
    id_col = header.index("book_id")
    d = dict()
    for row in meta:
        try:
            row = row.split("\t")
            book_id = int(row[id_col])
        except:
            print("no book_id found!")
            continue
        d[book_id] = dict()
        for i, key in enumerate(header):
            d[book_id][key] = row[i]
            
    return d
    

def convert_file(fp, meta_fp, dest_fp=None, verbose=False, overwrite=False):
    """Convert one file to OpenITI format.

    Args:
        fp (str): path to the file that must be converted.
        meta_fp (str): path to the yml file containing the ghaemiyeh metadata
        dest_fp (str): path to the converted file.

    Returns:
        None
    """
    conv = ghaemiyehEpubConverter(overwrite=overwrite)
    conv.VERBOSE = verbose
    conv.metadata_file = meta_fp
    conv.metadata_dic = load_metadata(meta_fp)
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
        meta_fp (str): path to the yml file containing the ghaemiyeh metadata
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
    conv = ghaemiyehEpubConverter(overwrite=overwrite)
    conv.VERBOSE = verbose
    conv.metadata_dic = load_metadata(meta_fp)
    conv.metadata_file = meta_fp
    conv.convert_files_in_folder(src_folder, dest_folder=dest_folder,
                                 extensions=extensions,
                                 exclude_extensions=exclude_extensions,
                                 fn_regex=fn_regex)


################################################################################




class ghaemiyehEpubConverter(GenericEpubConverter):
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
            #self.inspect_epub(fp)
            #print(fp)
            try:
                self.convert_file(fp)
                #print("converted!")
            except Exception as e:
                print(fp)
                print("  >> ERROR:", e)
                failed.append((fp, e))
                

        # deal with multivolume texts:
        print("checking multivolume texts")
        all_book_ids = [os.path.splitext(os.path.split(fp)[-1])[0] for fp in fp_list]
        multivol_book_ids = dict()
        for book_id in all_book_ids:
            if len(book_id) > 7:
                main_id = re.sub("^10+(\d+)\d\d\d$", r"\1", book_id)
                if not main_id in multivol_book_ids:
                    multivol_book_ids[main_id] = []
                multivol_book_ids[main_id].append(book_id)
        for main_id in multivol_book_ids:
            combined = ""
            endnotes = []
            outfp = os.path.join(self.dest_folder, main_id + ".automARkdown")
            if os.path.exists(outfp):  # if a file exists containing all volumes, don't join separate volumes
                continue
            outfp = re.sub("\.automARkdown", "Vols.automARkdown", outfp)
            if os.path.exists(outfp):  # if a file exists containing all volumes, don't join separate volumes
                continue
            print("joining", main_id)
            for i, book_id in enumerate(sorted(multivol_book_ids[main_id])):
                fp = os.path.join(self.dest_folder, book_id + ".automARkdown")
                try:
                    with open(fp, mode="r", encoding="utf-8") as file:
                        text = file.read()
                except:
                    print("file does not exist:", fp)
                    continue
                if i != 0:
                    text = re.split("#META#Header#End#", text)[-1]
                    text = re.sub("PageV01", "PageV{0:02d}".format(i+1), text)
                if re.findall("### \|EDITOR\|[ \r\n]+ENDNOTES:?", text):
                    text, notes = re.split("### \|EDITOR\|[ \r\n]+ENDNOTES:?", text)
                    endnotes.append(notes)
                combined += text
                
            if endnotes:
                combined += "\n\n### |EDITOR|\nENDNOTES:\n\n" + "\n\n".join(endnotes)
            
            if combined:
                with open(outfp, mode="w", encoding="utf-8") as file:
                    file.write(combined)
            else:
                print("No contents for", outfp)


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
        """Use custom html to mARKdown function for ghaemiyeh epubs."""
        text = html2md_ghaemiyeh.markdownify(html)
        return text

    def remove_notes(self, text):
        """Remove the footnotes from the text.

        Args:
            text (str)

        Returns:
            text_without_notes (str): text from which the notes were removed.
            notes (str): the footnotes converted to endnotes
                (if there are endnotes: add the endnote_splitter before them)
        """
        print("REMOVING NOTES")
        text_without_notes = ""
        notes = ""
        spl = re.split("(FOOTNOTE.*\n+)", text)
        spl = [x for x in spl if x != ""]
        i = 0
        #last_text_fragm = 0
        for t in spl:
            if not t.strip().startswith("FOOTNOTE"):
                text_without_notes += t
                #last_text_fragm = i
            else:
                fn_text = t.strip()[8:]
                if spl[i-1].strip().startswith("FOOTNOTE"):
                    notes += "{}\n\n".format(fn_text)
                else:
                    #p = re.findall("PageV\d+P\d+", spl[last_text_fragm])
                    #p = re.findall("PageV\d+P\d+", spl[i-1])
                    p = re.findall("# ص *: *(\d+)", spl[i-1])
                    if p:
                        notes += "PageV01P{:03d}:\n\n{}\n\n".format(int(p[-1]), fn_text)
                    else:
                        section_rgx = "(### [\|$]+) (.*)"
                        #sections = re.findall(section_rgx, spl[last_text_fragm])
                        sections = re.findall(section_rgx, spl[i-1])
                        if sections:
                            msg = "Notes on section ({})"
                            msg +=  "(no page numbers):\n\n{}\n\n"
                            notes += msg.format(sections[0][1], fn_text)
                        else:
                            notes += "(no page number):\n\n{}\n\n".format(fn_text)
            i += 1
        if notes:
            notes = self.endnote_splitter + notes
        return text_without_notes, notes

    def get_metadata(self, metadata_fp):
        """Custom method to get the metadata of the ghaemiyeh epub file."""
        source_fp = self.source_fp
        bookID = os.path.split(source_fp)[1]
        bookID = int(os.path.splitext(bookID)[0])
        meta_dic = self.metadata_dic[bookID]
        meta = ["#META# {}: {}".format(k,v) for k,v in sorted(meta_dic.items())]
        return self.magic_value + "\n".join(meta) + self.header_splitter

    def post_process(self, text):
        """Custom post-processing for ghaemiyeh texts"""
        
        text = re.sub("# ص *: *(\d+)", r"PageV01P\1", text)
        text = re.sub("#(?! \d).+ج *(\d+)[، ]*ص *: *(\d+)", r"PageV\1P\2", text)
        text = re.sub("PageV(\d)P", r"PageV0\1P", text)
        text = re.sub("PageV01P(\d)(?!\d)", r"PageV01P00\1", text)
        text = re.sub("PageV01P(\d\d)(?!\d)", r"PageV01P0\1", text)
        processed = super().post_process(text)
        return processed
        


if __name__== "__main__":
    #import doctest
    #doctest.testmod()
    #input("Testing finished. Continue?")

    # identify the location of the yml file containing the metadata:
    meta_fp = r"H:\OpenITI\new_books\Ghbook\books_AR_FA_UR_cleaned.tsv"
    src_folder = r"H:\OpenITI\new_books\Ghbook\epub\AR"
    dest_folder = r"H:\OpenITI\new_books\Ghbook\converted"
    convert_files_in_folder(src_folder, meta_fp, dest_folder=dest_folder,
                            verbose=False, overwrite=False)
##    hc.metadata = yml2json(meta_fp, container={})
    
##    fp = r"test\26362727.epub"
##    hc.convert_file(fp)
##    print("converted ghaemiyeh epub", fp)
##
##    hc.convert_files_in_folder("test/ghaemiyeh")
##    print("converted all epub files in folder", "test/ghaemiyeh")

