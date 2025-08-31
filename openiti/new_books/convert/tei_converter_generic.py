"""A generic converter for converting tei xml files into OpenITI format.

Subclass the TeiConverter to make a converter for a new
source of scraped books in TEI xml format.

Examples:
    Generic tei conversion::
    
        >>> from tei_converter_generic import TeiConverter
        >>> conv = TeiConverter(dest_folder="test/converted")
        >>> conv.VERBOSE = False
        >>> folder = r"test"
        >>> fn = r"GRAR000070"
        >>> conv.convert_file(os.path.join(folder, fn))
        >>> conv.convert_files_in_folder(folder, extensions = [""])

    Sub-class to create a converter specific to GRAR collection tei files::
    
        #>>> class GRARConverter(TeiConverter):
        #        def post_process(self, text):
        #            text = super().post_process(text)
        #            vols = re.findall("#META#.+ vol. (\d+) pp", text)
        #            if len(vols) == 1:
        #                text = re.sub("PageV00", "PageV{:02d}".format(int(vols[0])), text)
        #            elif len(vols) == 0:
        #                text = re.sub("PageV00", "PageV01", text)
        #            return text
        #>>> conv = GRARConverter("test/converted")
        #>>> conv.VERBOSE = False
        #>>> folder = r"test"
        #>>> conv.convert_files_in_folder(folder, exclude_ext = ["py", "yml", "txt", "epub"])

================================== ==========================
GenericConverter                   TeiConverter
================================== ==========================
__init__                           __init__ (appended)
convert_files_in_folder            (inherited)
convert file                       (inherited)
make_dest_fp                       (inherited)
get_metadata (dummy)               get_metadata
get_data                           (inherited)
pre_process                        pre_process
add_page_numbers (dummy)           (inherited - not used)
add_structural_annotations (dummy) add_structural_annotations
remove_notes (dummy)               (inherited - generic!)
reflow                             (inherited)
add_milestones (dummy)             (inherited - dummy)
post_process                       post_process
compose                            (inherited)
save_file                          (inherited)
                                   preprocess_page_numbers
                                   preprocess_wrapped_lines
================================== ==========================
"""

from bs4 import BeautifulSoup
import os
import re
import textwrap

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.helper.ara import deNoise
from openiti.new_books.convert.generic_converter import GenericConverter
from openiti.new_books.convert.helper import tei2md

class TeiConverter(GenericConverter):

    def __init__(self, dest_folder=None):
        """Initialize the class and its super-class."""
        super().__init__()
        self.root_tag_string = "soup.html.body"
##        self.unique_tags = dict()



    def pre_process(self, text):
        """Remove unwanted features from the text.

        ### Overwrite this method in subclass ###

        Args:
            text (str): the text in its initial state

        Returns:
            text (str): pre-processed text
        """
        super().pre_process(text)
        text = self.preprocess_page_numbers(text)
        text = self.preprocess_wrapped_lines(text)
        return text


    def preprocess_page_numbers(self, s):
        """Turn page beginnings into page endings.

        TEI xml indicates the beginning of a page, while OpenITI mARkdown
        indicates the end of a page.
        """
        try:
            s, tail = re.split("</body>", s, 1)
        except:
            tail = ""
        spl = re.split('<pb n="(\d+)"/?>', s)
        if len(spl) < 3:
            spl = re.split('<span [^>]+pb-(\d+)[^>]+>', s)
        s = spl
        page_numbers = [it for it in s if s.index(it)%2]
        page_texts = [it for it in s if not s.index(it)%2]
        if page_texts[0] != "":
            page_numbers = ["0"] + page_numbers
        else:
            page_texts = page_texts[1:]
        text = ""
        for i, it in enumerate(page_texts):
            text += it
            text += "\n\nPageV00P{:03d}\n".format(int(page_numbers[i]))
        if tail:
            return text + "</body>" + tail
        else:
            return text

    def preprocess_wrapped_lines(self, s):
        s = re.sub("-[\n\r]+~~", "", s)
        s = re.sub("[\n\r]+~~", " ", s)
        return re.sub(" {2,}", " ", s)


    def get_metadata(self, text):
        """Extracts the metadata from the text.


        Args:
            text (str): text of the file that contains data + metadata

        Returns:
            metadata (str): metadata formatted in OpenITI format
                (including the magic value and the header splitter)
        """
        soup = BeautifulSoup(text, "xml")
        metadata = ""
        header = soup.find("teiHeader")
        file_d = ["author", "title"]
        fileDesc = header.find("fileDesc")
        for k in file_d:
            try:
                item = fileDesc.find(k).text.strip()
            except:
                item = ""
            if item:
                metadata += "#META# {}: {}\n".format(k, item)

        source_d = {"title": "", "author": "n.n.", "editor": "n.n.",
                    "pubPlace": "n.p.", "publisher": "n.n.", "date": "n.d."}
        sourceDesc = header.find("sourceDesc")
        for k in source_d:
            try:
                source_d[k] = sourceDesc.find(k).text.strip()
            except:
                pass
        p = ""
        page_info = sourceDesc.find_all("biblScope")
        for i in page_info:
            if i.has_attr("unit"):
                if i["unit"] == "vol":
                    p += "vol. {} ".format(i.text)
                if i["unit"] in ["pp", "pages"]:
                    p += "pp. {}".format(i.text)
        ed_info = "Ed. {editor} ({date}), {title}, {pubPlace}: {publisher}"
        ed_info = ed_info.format(**source_d)
        if p:
            ed_info += ", {}.".format(p)
        else:
            ed_info += "."
        metadata += "#META# ed_info: {}\n".format(ed_info)

        text_tag = soup.find("text")
        try:
            text_id = text_tag["id"]
            metadata += "#META# coll_id: {}\n".format(text_id)
        except:
            #print("no ID found in the metadata header")
            pass
        metadata = self.magic_value + metadata + self.header_splitter
        return metadata


    def add_structural_annotations(self, text, options=None):
        soup = BeautifulSoup(text, "xml")
        text_soup = soup.find("text")
        text = tei2md.markdownify(str(text_soup), options=options)
        return text


    def post_process(self, text):
        """Carry out post-processing operations on the text.

        Args:
            text (str): the text in its current conversion state

        Returns:
            processed (str): the text after post-processing operations.
        """
        text = re.sub(r"\APageV\d+P000\n*", "", text.strip())
        processed = re.sub("[\n\r]{2,}(?![#\|P])", "\n\n# ", text)
        return processed



if __name__ == "__main__":
    import doctest
    doctest.testmod()

    input("Passed tests. Press Enter to start converting")

    conv = TeiConverter()
    #conv.convert_file("test/test.txt")
    folder = r"G:\London\OpenITI\RAWrabica\RAWrabica005000\GRAR"
    conv.convert_files_in_folder(folder, exclude_ext=["yml", "py"])
##    input()
##    source_fp = r"G:\London\OpenITI\RAWrabica\RAWrabica005000\GRAR\GRAR000070"
##    conv.convert_file(source_fp)




