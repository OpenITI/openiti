"""Converter that converts HTML files from the eShia library to OpenITI mARkdown.

The eShiaHtmlConverter is a subclass of GenericHtmlConverter,
which in its turn inherits many functions from the GenericConverter.

GenericConverter
    \_ GenericHtmlConverter
            \_ EShiaHtmlConverter
            \_ NoorlibHtmlConverter
            \_ ...

EShiaHtmlConverter's main methods are inherited from the GenericConverter:

* convert_file(source_fp): basic procedure for converting an html file.
* convert_files_in_folder(source_folder): convert all html files in the folder
    (calls convert_file)

Overview of the methods of these classes:
(methods of GenericConverter are inherited by GenericHtmlConverter;
and methods of GenericHtmlConverter are inherited by EShiaHtmlConverter.
Methods of the superclass with the same name
in the subclass are overwritten by the latter)

================================== ========================== ==========================
GenericConverter                   GenericHtmlConverter       EShiaHtmlConverter
================================== ========================== ==========================
__init__                           __init__                   (inherited)
convert_files_in_folder            (inherited)                (inherited)
convert file                       (inherited)                (inherited)
make_dest_fp                       (inherited - generic!)     (inherited - generic!)
get_metadata (dummy)               (inherited - dummy!)       get_metadata
get_data                           get_data                   (inherited)
pre_process                        (inherited)                (inherited)
add_page_numbers (dummy)           (inherited - dummy!)       add_page_numbers
add_structural_annotations (dummy) add_structural_annotations add_structural_annotations
remove_notes (dummy)               remove_notes               remove_notes
reflow                             (inherited)                (inherited)
add_milestones (dummy)             (inherited - dummy!)       (inherited - dummy!)
post_process                       (inherited - generic!)     post_process
compose                            (inherited)                (inherited)
save_file                          (inherited)                (inherited)
                                   inspect_tags_in_html       (inherited)
                                   inspect_tags_in_folder     (inherited)
                                   find_example_of_tag        (inherited)
================================== ========================== ==========================

The EShiaHtmlConverter's add_structural_annotations method uses html2md_eShia,
an adaptation of the generic html2md (based on markdownify)
to convert the html tags to OpenITI annotations. 

Examples:
    >>> from html_converter_eShia import EShiaHtmlConverter
    >>> conv = EShiaHtmlConverter()
    >>> conv.VERBOSE = False
    >>> folder = r"test/"
    >>> conv.convert_file(folder+"86596.html")
    >>> conv.convert_files_in_folder(folder, ["html"])
"""

from bs4 import BeautifulSoup
import re

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.new_books.convert.html_converter_generic import GenericHtmlConverter
from openiti.new_books.convert.helper import html2md_eShia


class EShiaHtmlConverter(GenericHtmlConverter):

##    # moved this function to the generic_converter!
##    def pre_process(self, text):
##        text = super().pre_process(text)
##        # attach separated wa- and a- prefixes to the following word: 
##        text = re.sub(r"\b([وأ])[\s~]+", r"\1", text)
##        return text

    def get_metadata(self, text):
        """Gets the metadata from the first td in the html.

        The metadata in eShia texts are in the first td
        (which represents the title page of the book).
        In some cases, the metadata is nicely parsed
        (p tags with ids like "author", "translator", ...);
        more often, they are simply in h, p or other tags,
        or only divided with <br/> tags.

        This function removes the footnotes from the title page
        and then adds the #META# tag before each line in the title page.        

        Args:
            text (str): text of the file that contains both data and metadata

        Returns:
            metadata (str): metadata formatted in OpenITI format
                (including the magic value and the header splitter)
        """
        soup = BeautifulSoup(text)
        meta_td = soup.find("td") # metadata is in first td tag
        
        # remove footnotes from metadata page:
        [x.extract() for x in meta_td.find_all("span", "footnotes")]
        [x.extract() for x in meta_td.find_all("footnote")]

        # remove all tags in the metadata page and add #META# tags: 
        metadata = re.sub("<[^>]+> *", "\n", str(meta_td))
        metadata = re.sub("\n+", "\n#META# ", metadata)

        # remove superfluous #META# tags:
        metadata = re.sub("\n* *#META# *(?:\n+|\Z)", "\n", metadata)

        # add magic value and header splitter: 
        metadata = self.magic_value + metadata + self.header_splitter
        return metadata

    def add_page_numbers(self, text, source_fp):
        """Convert the page numbers in the text into OpenITI mARkdown format"""
        try:
            vol_no = int(re.findall("V(\d+)", source_fp)[0])
            vol_no = "PageV{:02d}P{}".format(vol_no, "{:03d}")
        except:
            vol_no = "PageV01P{:03d}"
        def fmt_match(match):
            r = match.group(1) + vol_no.format(int(match.group(2)))
            return r + match.group(3)
        end = '<td class="book-page-show">|\Z'
        text = re.sub(r'(</td>)[^<\d]*(\d+)[^<]*({})'.format(end),
                      fmt_match, text)
        return text

    def remove_notes(self, text):
        """Remove footnotes from text, and format them as endnotes

        Footnotes are indicated in different ways in eShia texts;
        the only communality seems to be that a <hr/> tag
        splits off the critical apparatus from the text.
        We will use this feature to split off the text from the footnotes.
        """
        split_text = re.split("(PageV\d+P\d+)", text)
        text = []
        footnotes = []
        for i, t in enumerate(split_text):
            if re.match("PageV\d+P\d+", t):
                text.append(t)
            else: # check if the horizontal line splitting apparatus off is there
                spl = re.split("<hr */? *>", t)
                if len(spl) == 1: # no footnotes
                    text.append(t)
                else:
                    try:
                        notes = "Notes to {}:<br/>{}".format(split_text[i+1], spl[-1])
                    except:
                        notes = "Notes to [NO PAGE]:<br/>{}".format(spl[-1])
                    notes = html2md_eShia.markdownify(notes) 
                    footnotes.append(notes)
                    text.append("\n\n".join(spl[:-1]))

        text = "\n\n".join(text)
        notes = "\n\n".join(footnotes)
        notes = re.sub("\n+#* *\n+", "\n\n", notes)
        notes = self.endnote_splitter + notes
        return text, notes 
                    
    #def convert_html2md(self, html):
    def add_structural_annotations(self, html):
        """Convert html to mARkdown text using a html2md converter."""
        text = html2md_eShia.markdownify(html)
        return text             

    def post_process(self, text):
        empty = """ *اين صفحه در كتاب اصلي بدون متن است / هذه الصفحة فارغة في النسخة المطبوعة *"""
        text = re.sub(empty, "\n", text)
        text = super().post_process(text)
        return text

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    input("Passed all tests. Continue?")
    
    conv = EShiaHtmlConverter()
    folder = r"G:\London\OpenITI\new\eShia"

    conv.convert_files_in_folder(folder)
