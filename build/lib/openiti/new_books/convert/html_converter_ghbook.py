"""Converter that converts HTML files from the Ghbook library
to OpenITI mARkdown.

The converter has two main functions:
* convert_file: convert a single html file.
* convert_files_in_folder: convert all html files in a given folder

Usage examples:
    >>> from html_converter_Ghbook import convert_file
    >>> folder = r"test/Ghbook/"
    >>> convert_file(folder+"10584.html", dest_fp=folder+"converted/10584")
    >>> from html_converter_Ghbook import convert_files_in_folder
    >>> convert_files_in_folder(folder, dest_folder=folder+"converted")  

Both functions use the GhbookHtmlConverter class to do the heavy lifting.
The GhbookHtmlConverter is a subclass of GenericHtmlConverter,
which in its turn inherits many functions from the GenericConverter.

GenericConverter
    \_ GenericHtmlConverter
            \_ EShiaHtmlConverter
            \_ GhbookHtmlConverter
            \_ ...

Overview of the methods of these classes:
(methods of GenericConverter are inherited by GenericHtmlConverter;
and methods of GenericHtmlConverter are inherited by GhbookHtmlConverter.
Methods of the superclass with the same name
in the subclass are overwritten by the latter)

================================== ========================== ==========================
GenericConverter                   GenericHtmlConverter       GhbookHtmlConverter
================================== ========================== ==========================
__init__                           __init__                   (inherited)
convert_files_in_folder            (inherited)                (inherited)
convert file                       (inherited)                (inherited)
make_dest_fp                       (inherited - generic!)     (inherited - generic!)
get_metadata (dummy)               (inherited - dummy!)       get_metadata
get_data                           get_data                   (inherited)
pre_process                        (inherited)                pre_process
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

The GhbookHtmlConverter's add_structural_annotations method uses html2md_Ghbook,
an adaptation of the generic html2md (based on markdownify)
to convert the html tags to OpenITI annotations. 

Examples:
    >>> from html_converter_Ghbook import GhbookHtmlConverter
    >>> conv = GhbookHtmlConverter()
    >>> conv.dest_folder = r"test/Ghbook/converted"
    >>> conv.VERBOSE = False
    >>> folder = r"test/Ghbook/"
    >>> conv.convert_file(folder+"10584.html")
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
from openiti.new_books.convert.helper import html2md_Ghbook


def convert_file(fp, dest_fp=None):
    """Convert one file to OpenITI format.

    Args:
        source_fp (str): path to the file that must be converted.
        dest_fp (str): path to the converted file. Defaults to None
            (in which case, the converted folder will be put in a folder
            named "converted" in the same folder as the source_fp)

    Returns:
        None
    """
    conv = GhbookHtmlConverter() 
    conv.convert_file(fp, dest_fp=dest_fp)

def convert_files_in_folder(src_folder, dest_folder=None,
                            extensions=["html"], exclude_extensions=["yml"],
                            fn_regex=None):
    """Convert all files in a folder to OpenITI format.\
    Use the `extensions` and `exclude_extensions` lists to filter\
    the files to be converted.

    Args:
        src_folder (str): path to the folder that contains
            the files that must be converted.
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
    conv = GhbookHtmlConverter()
    conv.convert_files_in_folder(src_folder, dest_folder=dest_folder,
                                 extensions=extensions,
                                 exclude_extensions=exclude_extensions,
                                 fn_regex=fn_regex)


################################################################################


class GhbookHtmlConverter(GenericHtmlConverter):

    def pre_process(self, text):
        """Remove superfluous elements from the html file before processing."""

        def remove_html_elements(soup, tag_name, class_=None, contains_str=None):
            """Remove all html elements with tag `tag` and class `class_` \
            if they contain `contains_str`
            
            Args:
                soup (BeautifulSoup object): BeautifulSoup representation
                    of the html file
                tag_name (str): name of the tag that needs to be removed
                    (e.g., "p", "div", "span"). 
                class_ (str): class of the tag that needs to be removed.
                    Defaults to None. If None, all `tag_name` elements
                    will be removed, regardless of their class.
                contains_str (str): defaults to None. If not None,
                    `tag_name` tags will only be removed if the text within them
                    contains the `contains_str` string.
            """
            if class_:
                elements = soup.find_all(tag_name, class_=class_)
            else:
                elements = soup.find_all(tag_name)
            for el in elements:
                if contains_str:
                    if contains_str in el.text:
                        el.extract()
                else:
                    el.extract()
        
        text = super().pre_process(text)
        
        # attach separated wa- and a- prefixes to the following word: 
        text = re.sub(r"\b([وأ])[\s~]+", r"\1", text)

        # remove superfluous html elements: 
        soup = BeautifulSoup(text)
        remove_html_elements(soup, "STYLE")
        remove_html_elements(soup, "TITLE")

        for fn_line in soup.find_all("hr", class_="content_hr"):
            fn_line.insert_after("FOOTNOTES")
        text = soup.prettify()
        
        return text


    def add_page_numbers(self, text, source_fp):
        """Convert the page numbers in the text into OpenITI mARkdown format

        In Ghbook texts, the page numbers are in the page header
        (<div class="PageHead">).
        Volume numbers are not mentioned in the html files,
        but every volume is a different html file
        and volume numbers should be marked in the file names as VOLxxx.

        The script gets the volume number from the file name
        and the page number from the page header,
        joins these together in the OpenITI page number format PageVxxPxxx
        and adds this into the html at the end of the page.

        It also deletes the page header after extracting the page number.
        """

        # try to get the volume number from the filename:
        try:
            vol_no = int(re.findall("VOL(\d+)", source_fp)[0])
            vol_no = "PageV{:02d}P{}".format(vol_no, "{:03d}")
        except:
            vol_no = "PageV01P{:03d}"

        # add the page number
        soup = BeautifulSoup(text)
        for span in soup.find_all("SPAN", class_="content_text"):
            span_text = span.text.strip()
            if span_text.startswith("ص:"):
                page_no = re.findall("\d+", span_text)[0]
                page_no = vol_no.format(int(page_no))
                span.insert_after(page_no)
                span.extract()
        return soup.prettify()


    def remove_notes(self, text):
        """Remove footnotes from text, and format them as endnotes.

        Footnotes in Ghbook html files are below a horizontal line
        (<HR class=content_hr>), located just below the page number
        (<P class=content_paragraph><SPAN class=content_text>ص:45</SPAN></P></DIV></DIV>)
        each footnote in a <DIV id=content_note_PAGE_NOTENUMBER class=content_note>(footnote text)</DIV>
        
        This function extracts the footnotes from the texts
        and turns them into endnotes.
        The markers that indicate the location of the notes
        within the text are not removed.
        """
        split_text = re.split("(PageV\d+P\d+)", text)
        text = []
        footnotes = []
        for i, t in enumerate(split_text):
            if re.match("PageV\d+P\d+", t):
                text.append(t)
            else:
                notes = re.findall("content_note>([^<]+)", t)
                if notes:
                    try:
                        notes = "\n".join(notes) + "\n" +  split_text[i-1] + "\n\n"
                    except:
                        notes = "\n".join(notes) + "\n" + "PageV00P000\n\n"
                    footnotes.append(notes)
                    
                text.append(re.sub("<DIV [^>]+? class=content_note>[^<]+?</DIV>", "", t))

        text = "\n\n".join(text)
        notes = "\n\n".join(footnotes)
        notes = re.sub("\n+#* *\n+", "\n\n", notes)
        notes = self.endnote_splitter + notes
        return text, notes 
                    

    def add_structural_annotations(self, html):
        """Convert html to mARkdown text using a html2md converter."""
        text = html2md_Ghbook.markdownify(html)
        return text             


    def post_process(self, text):
        """Deal with formatting probles introduced during the conversion process."""
        text = super().post_process(text)

        # remove page numbers of empty pages:
        text = re.sub("(PageV\d+P\d+)\s*PageV\d+P\d+", r"\1", text)

        # remove empty paragraphs:
        text = re.sub(r"[\r\n]+# *[\r\n]+", "\n", text)

        # adjust spacing after closing brackets and punctuation:
        fmt = ")»،؛:.!؟\-"
        fmt2 = fmt + "\d\s"
        text = re.sub("([{}]+)([^{}])".format(fmt, fmt2), r"\1 \2", text)
        text = re.sub("\) ([{}])".format(fmt), r")\1", text)

        # adjust spacing before opening brackets:
        text = re.sub("(\w)([(«])", r"\1 \2", text)

        # remove superfluous new lines before a new paragraph/page number
        text = re.sub("[\r\n]+(# |Page)", r"\n\1", text)

        return text


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    input("Passed all tests. Continue?")


