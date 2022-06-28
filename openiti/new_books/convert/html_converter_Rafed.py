"""Converter that converts HTML files from the Rafed library
to OpenITI mARkdown.

The converter has two main functions:
* convert_file: convert a single html file.
* convert_files_in_folder: convert all html files in a given folder

Usage examples:
    >>> from html_converter_Rafed import convert_file
    >>> folder = r"test/Rafed/"
    >>> convert_file(folder+"10584.html", dest_fp=folder+"converted/10584")
    >>> from html_converter_Rafed import convert_files_in_folder
    >>> convert_files_in_folder(folder, dest_folder=folder+"converted")  

Both functions use the RafedHtmlConverter class to do the heavy lifting.
The RafedHtmlConverter is a subclass of GenericHtmlConverter,
which in its turn inherits many functions from the GenericConverter.

GenericConverter
    \_ GenericHtmlConverter
            \_ EShiaHtmlConverter
            \_ RafedHtmlConverter
            \_ ...

Overview of the methods of these classes:
(methods of GenericConverter are inherited by GenericHtmlConverter;
and methods of GenericHtmlConverter are inherited by RafedHtmlConverter.
Methods of the superclass with the same name
in the subclass are overwritten by the latter)

================================== ========================== ==========================
GenericConverter                   GenericHtmlConverter       RafedHtmlConverter
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

The RafedHtmlConverter's add_structural_annotations method uses html2md_Rafed,
an adaptation of the generic html2md (based on markdownify)
to convert the html tags to OpenITI annotations. 

Examples:
    >>> from html_converter_Rafed import RafedHtmlConverter
    >>> conv = RafedHtmlConverter()
    >>> conv.dest_folder = r"test/Rafed/converted"
    >>> conv.VERBOSE = False
    >>> folder = r"test/Rafed/"
    >>> conv.convert_file(folder+"Rafed_3943.html")
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
from openiti.new_books.convert.helper import html2md_Rafed


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
    conv = RafedHtmlConverter() 
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
    conv = RafedHtmlConverter()
    conv.convert_files_in_folder(src_folder, dest_folder=dest_folder,
                                 extensions=extensions,
                                 exclude_extensions=exclude_extensions,
                                 fn_regex=fn_regex)


################################################################################


class RafedHtmlConverter(GenericHtmlConverter):

    def get_metadata(self, text):
        soup = BeautifulSoup(text)
        meta_div = soup.find_all("div", class_="bookinfo")[0]
        meta = html2md_Rafed.markdownify(meta_div)
        meta = [line.strip() for line in meta.splitlines() if len(line) > 3]
        meta = "#META# " + ("\n#META# ".join(meta))
        meta = self.magic_value + meta + self.header_splitter
        return meta
        

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
            soup = BeautifulSoup(text)
            soup = soup.find("div", {"id": "content1"})
            if class_:
                elements = soup.find_all(tag_name, class_=class_)
                #print(len(elements), tag_name, "elements with class", class_, "will be removed")
            else:
                elements = soup.find_all(tag_name)
            for el in elements:
                if contains_str:
                    if contains_str in el.text:
                        el.extract()
                else:
                    el.extract()
            return soup.prettify()
        
        text = super().pre_process(text)
        
        # attach separated wa- and a- prefixes to the following word: 
        text = re.sub(r"\b([وأ])[\s~]+", r"\1", text)

        # remove superfluous html elements: 
        #soup = BeautifulSoup(text)
        text = remove_html_elements(text, "p", class_="rfdLine")
        text = remove_html_elements(text, "script")
##        remove_html_elements(soup, "TITLE")
##
##        for fn_line in soup.find_all("hr", class_="content_hr"):
##            fn_line.insert_after("FOOTNOTES")
##        text = soup.prettify()
        
        return text


    def add_page_numbers(self, text, source_fp, vol=None):
        """Convert the page numbers in the text into OpenITI mARkdown format

        In Rafed texts, the page numbers are at the bottom of the page,
        in a div with class="pgnum">.
        Volume numbers are not mentioned in the html files,
        but every volume is a different html file.

        It also deletes the page header after extracting the page number.
        """

        # try to get the volume number from the filename:
        try:
            vol_no = "PageV{:02d}P{}".format(vol, "{:03d}")
        except:
            vol_no = "PageV01P{:03d}"

        # add the page number
        soup = BeautifulSoup(text)
        for div in soup.find_all("div", class_="pgnum"):
            div_text = div.text.strip()
            page_no = re.findall("\d+", div_text)[-1]
            # add the page number string to the text:
            div.insert_after(vol_no.format(int(page_no)))
            # remove the original page number div:
            div.extract()
        return soup.prettify()


    def remove_notes(self, text):
        """Remove footnotes from text, and format them as endnotes.

        Footnotes in Rafed html files are below a horizontal line
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
                page = re.findall('<div class="pgcontent">.+', t, flags=re.DOTALL)
                if not page:
                    #print("NO PAGE CONTENT FOUND!")
                    #print(t)
                    continue
                soup = BeautifulSoup(page[0])
                #print(page)
                #print(soup.prettify())
                note_ps = soup.find_all("p", class_="rfdFootnote0")
                #print(len(note_ps))
                notes = []
                if note_ps:
                    #print("removing notes")
                    for note in note_ps:
                        notes.append(note.text.strip())
                        # remove the note from the html string:
                        note.extract()
                    try:
                        notes = "\n".join(notes) + "\n" +  split_text[i-1] + "\n\n"
                    except:
                        notes = "\n".join(notes) + "\n" + "PageV00P000\n\n"
                    footnotes.append(notes)
                
                #input("CONTINUE?")
                text.append(soup.prettify())

        text = "\n\n".join(text)
        notes = "\n\n".join(footnotes)
        notes = re.sub("\n+#* *\n+", "\n\n", notes)
        notes = self.endnote_splitter + notes
        return text, notes 
                    

    def add_structural_annotations(self, html):
        """Convert html to mARkdown text using a html2md converter."""
        text = html2md_Rafed.markdownify(html)
        return text             


    def post_process(self, text):
        """Deal with formatting problems introduced during the conversion process."""
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

        # restore the formatting of urls:
        def restore_url_formatting(m):
            descr = m.group(1)
            link = m.group(2)
            link = re.sub(" |~~|\r|\n", "", link)
            return "!"+descr+link
        text = re.sub("(?:# )*! (\[[^\]]*\]) *(\([^\)]+\))", restore_url_formatting, text)

        # adjust spacing before opening brackets:
        text = re.sub("(\w)([(«])", r"\1 \2", text)

        # restore formulae that had zwnj in between them:
        d = {
            "صلىاللهعليهوسلم": "صلى الله عليه وسلم",
            "صلىاللهعليهاوسلم": "صلى الله عليها وسلم",
            "صلىاللهعليهموسلم": "صلى الله عليهم وسلم",
            "صلىاللهعليهماوسلم": "صلى الله عليهما وسلم",
            "رحمهالله": "رحمه الله",
            "رحمهاالله": "رحمها الله",
            "رحمهمالله": "رحمهم الله",
            "رحمهماالله": "رحمهما الله",
            "عليهالسلام": "عليه السلام",
            "عليهمالسلام": "عليهم السلام",
            "عليهماالسلام": "عليهما السلام",
            "عليهاالسلام": "عليها السلام",
            "عزوجل": "عز وجل",
            "صلىاللهعليهوآلهوسلم": "صلى الله عليه وآله وسلم",
            "صلىاللهعليهوآله": "صلى الله عليه وآله",
            }
        formula_regex = "|".join(d.keys())
        text = re.sub(formula_regex, lambda m: d.get(m.group(0)), text)

        # remove superfluous new lines before a new paragraph/page number
        text = re.sub("[\r\n]+(# |Page)", r"\n\1", text)

        return text


if __name__ == "__main__":
    folder = r"test/Rafed/"
    conv = RafedHtmlConverter()
    #conv.convert_file(folder+"Rafed_3943.html")
    convert_files_in_folder(folder)
    input("DONE")
    import doctest
    doctest.testmod()
    input("Passed all tests. Continue?")


