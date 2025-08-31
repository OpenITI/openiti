"""Converter that converts HTML files from the eShia library to OpenITI mARkdown.

The converter has two main functions:
* convert_file: convert a single html file.
* convert_files_in_folder: convert all html files in a given folder

Usage examples:
    >>> from html_converter_eShia import convert_file
    >>> folder = r"test/eShia/"
    >>> convert_file(folder+"86596.html", dest_fp=folder+"converted/86596")
    >>> from html_converter_eShia import convert_files_in_folder
    >>> convert_files_in_folder(folder, dest_folder=folder+"converted")  

Both functions use the EShiaHtmlConverter class to do the heavy lifting.
The EShiaHtmlConverter is a subclass of GenericHtmlConverter,
which in its turn inherits many functions from the GenericConverter.

GenericConverter
    \_ GenericHtmlConverter
            \_ EShiaHtmlConverter
            \_ NoorlibHtmlConverter
            \_ ...

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
get_data                           (inherited)                (inherited)
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
    >>> folder = r"test/eShia/"
    >>> conv.convert_file(folder+"86596.html")
    >>> conv.convert_files_in_folder(folder, extensions=["html"])
"""

from bs4 import BeautifulSoup
import re
import os

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.new_books.convert.html_converter_generic import GenericHtmlConverter
from openiti.new_books.convert.helper import html2md_eShia
from openiti.helper.funcs import natural_sort


def combine_html_files_in_folder(folder, dest_fp="temp"):
    text = []
    for fn in natural_sort(os.listdir(folder)):
        fp = os.path.join(folder, fn)
        with open(fp, mode="r", encoding="utf-8") as file:
            html = file.read()
##        # Beautiful soup has problems correctly parsing some eShia books
##        # (parsers tested: no parser, "lxml", "html", "xml", "html.parser")
##        # - "html.parser" leaves out some footnotes!
##        # - "xml" doesn't parse some pages at all
##        # - "lxml" and "html" move the closing </span> tag of the footnote section
##        # this issue seems not linked to the <hr> tag above it
##        # html = re.sub("</?hr[^>]*>", "", html)  # does not influence the results.
##        soup = BeautifulSoup(html, "html")
##        text.append(soup.find_all("td", class_="book-page-show")[0].prettify())
##        print(soup.find_all("td", class_="book-page-show")[0].prettify())
##        print("---")
##        print(soup.find_all("td", class_="book-page-show")[0])
##        print("***")
##        input()
        text.append(re.findall('<td[^>]+class="book-page-show"[\s\S]+?(?=\<td)', html)[0])
        page = int(fp[:-5].split("_")[-1])
        vol = int(fp[:-5].split("_")[-2])
        text.append("PageV{:02d}P{:03d}".format(vol, page))
        
    with open(dest_fp, mode="w", encoding="utf-8") as file:
        file.write("\n\n".join(text))
    #convert_file("temp", dest_fp)
        

def convert_file(fp, dest_fp=None, verbose=False):
    """Convert one file to OpenITI format.

    Args:
        source_fp (str): path to the file that must be converted.
        dest_fp (str): path to the converted file.

    Returns:
        None
    """
    conv = EShiaHtmlConverter()
    conv.VERBOSE = verbose
    conv.convert_file(fp, dest_fp=dest_fp)

def convert_files_in_folder(src_folder, dest_folder=None,
                            extensions=["html"], exclude_extensions=["yml"],
                            fn_regex=None, verbose=False):
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
    conv = EShiaHtmlConverter()
    conv.VERBOSE = verbose
    conv.convert_files_in_folder(src_folder, dest_folder=dest_folder,
                                 extensions=extensions,
                                 exclude_extensions=exclude_extensions,
                                 fn_regex=fn_regex)


################################################################################


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
        soup = BeautifulSoup(text, features="lxml")
        meta_td = soup.find("td") # metadata is in first td tag
        
        # remove footnotes from metadata page:
        [x.extract() for x in meta_td.find_all("span", "footnotes")]
        [x.extract() for x in meta_td.find_all("footnote")]
        [x.extract() for x in meta_td.find_all("FootNote")]

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
        if re.findall("PageV\d+P\d+", text):
            return text
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
            else:
##                # this doesn't work because none of the BeautifulSoup parsers parses the page correctly;
##                # some move the closing </span> tag of the footnote section to after the first footnote;
##                # others even leave out all except the first footnote
##                if "FootNote" in t:  
##                    soup = BeautifulSoup(t.strip(), 'lxml')
##                    note_nodes = soup.find_all("span", class_="FootNote")
##                    notes = ""
##                    for note in note_nodes:
##                        notes += note.prettify() + "\n"
##                    try:
##                        notes = "Notes to {}:<br/>{}".format(split_text[i+1], notes)
##                    except:
##                        notes = "Notes to [NO PAGE]:<br/>{}".format(notes)
##                    print(t)
##                    print("----")
##                    print(notes)
##                    input()
##                    # remove footnotes:
##                    [x.extract() for x in soup.find_all("span", class_="FootNote")]
##                    text.append(t)
##                else: # check if the horizontal line splitting apparatus off is there
                # check if the horizontal line splitting apparatus off is there
                spl = re.split("<hr */? *>", t)
                if len(spl) == 1: # no footnotes separated by line
                    text.append(t)
                    notes = None
                else:
                    if "مقدمه صفحه" in t:
                        #print("*"*60)
                        #print("MUQADDIMA!")
                        page_text = ['<td class="book-page-show">\n']
                        for el in re.split("(<\w+>\s*مقدمه صفحه \d+\s*</\w+>)", t):
                            #print(el)
                            
                            if re.findall("مقدمه صفحه", el):
                                page_no = re.findall("\d+", el)
                                print(page_no)
                            elif "book-page-show" in el:
                                continue
                            else:
                                spl = re.split("<hr */? *>", el)
                                fmt = '</td>\nPageV00P{:03d}\n<td class="book-page-show">\n'
                                #print("x"*15)
                                #print("\n---\n".join(spl))
                                #print("o"*15)
                                if len(spl) == 1: # no footnotes separated by line
                                    page_text.append(el)
                                    try:
                                        page_text.append(fmt.format(int(page_no[-1])))
                                    except:
                                        pass
                                else:
                                    try:
                                        page_text.append(spl[0])
                                        page_text.append(fmt.format(int(page_no[-1])))
                                        page_no = "PageV00P{:03d}".format(int(page_no[-1]))
                                        notes = "Notes to {}:<br/>{}".format(page_no, spl[-1])
                                    except:
                                        notes = "Notes to [NO PAGE]:<br/>{}".format(spl[-1])
                            #print("-------------------")
                        text.append("\n\n".join(page_text))
                    else:
                        try:
                            notes = "Notes to {}:<br/>{}".format(split_text[i+1], spl[-1])
                        except:
                            notes = "Notes to [NO PAGE]:<br/>{}".format(spl[-1])
                        text.append("\n\n".join(spl[:-1]))
                if notes:
                    notes = html2md_eShia.markdownify(notes) 
                    footnotes.append(notes)
                

        text = "\n\n".join(text)
        notes = "\n\n".join(footnotes)
        notes = re.sub("\n+#* *\n+", "\n\n", notes)
        notes = self.endnote_splitter + notes
        return text, notes 
                    
    #def convert_html2md(self, html):
    def add_structural_annotations(self, html):
        """Convert html to mARkdown text using a html2md converter."""
        #text = html2md_eShia.markdownify(html)
        text = []

        for i, p in enumerate(re.split("(\n+PageV\d+P\d+\n+)", html)):
            if re.findall("PageV\d+P\d+", p):
                text.append(p)
            else:
                soup = BeautifulSoup(p, features="lxml")
                try:
                    t = html2md_eShia.markdownify(soup.td.prettify())
                except:
                    print("no <td> tag on this page:")
                    print(soup.prettify())
                    html2md_eShia.markdownify(soup.prettify())
                text.append(t)
        text = "".join(text)
        return text             

    def post_process(self, text):
        print("post_processing")
        empty = """ *اين صفحه در كتاب اصلي بدون متن است / هذه الصفحة فارغة في النسخة المطبوعة *"""
        text = re.sub(empty, "\n", text)
        text = super().post_process(text)
        # convert kalematekhass tags at the beginning of a line to headers:
        text = re.sub("# \*\* (.+)\*\*", r"### || \1", text)
        text = re.sub("# \*\*\* (.+)\*\*\*", r"### ||| \1", text)
        # add footnotes after a title to same line as the title:
        text = re.sub("(### \|+ .+)[\r\n]+# (\[\d+\][\r\n]+)", r"\1 \2", text)
        # format poetry (was formatted as tables):
        #prev_line = r"((?:شعر|شاعر|نشذ|%~%).+\n+)"
        pattern = r"(?<=\n)#? ?\|([^|\n]+)\|\|([^|\n]+)\| *(?=\n)"
        text = re.sub(pattern, r"# \1 %~% \2", text)
        # remove floating hashtags and pipes
        text = re.sub("[\r\n]+# *([\r\n]+)", r"\1", text)
        text = re.sub("[\r\n]+\|+ *([\r\n]+)", r"\1", text)
        
        #
        text = re.sub("([^\r\n .!؟][\r\n]+PageV[^P]+P\d+[\r\n]+)# ", r"\1~~", text)
        return text

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    input("Passed all tests. Continue?")
    
    conv = EShiaHtmlConverter()
    folder = r"G:\London\OpenITI\new\eShia"
    import os
    conv.convert_file(os.path.join(folder, "10461.html"))

    conv.convert_files_in_folder(folder)
