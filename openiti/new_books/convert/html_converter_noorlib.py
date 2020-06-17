"""Converter that converts HTML files from the eShia library to OpenITI mARkdown.

The NoorlibHtmlConverter is a subclass of GenericHtmlConverter,
which in its turn inherits many functions from the GenericConverter.

GenericConverter
    \_ GenericHtmlConverter
            \_ EShiaHtmlConverter
            \_ NoorlibHtmlConverter
            \_ ...

NoorlibHtmlConverter's main methods are inherited from the GenericConverter:

* convert_file(source_fp): basic procedure for converting an html file.
* convert_files_in_folder(source_folder): convert all html files in the folder
    (calls convert_file)

Overview of the methods of these classes:
(methods of GenericConverter are inherited by GenericHtmlConverter;
and methods of GenericHtmlConverter are inherited by EShiaHtmlConverter.
Methods of the superclass with the same name
in the subclass are overwritten by the latter)

================================== ========================== ==========================
GenericConverter                   GenericHtmlConverter       NoorlibHtmlConverter
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

The EShiaHtmlConverter's add_structural_annotations method uses html2md_noorlib,
an adaptation of the generic html2md (based on markdownify)
to convert the html tags to OpenITI annotations. 

Examples:
    >>> from html_converter_noorlib import NoorlibHtmlConverter
    >>> conv = NoorlibHtmlConverter()
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
from openiti.new_books.convert.helper import html2md_noorlib


class NoorlibHtmlConverter(GenericHtmlConverter):

    def pre_process(self, text):
        def remove_html_elements(soup, tag, class_=None, contains_str=None):
            """Remove all html elements with tag `tag` and class `class_`"""
            if class_:
                elements = soup.find_all(tag, class_=class_)
            else:
                elements = soup.find_all(tag)
            for el in elements:
                if contains_str:
                    if contains_str in el.text:
                        el.extract()
                else:
                    el.extract()
        text = super().pre_process(text)
        # attach separated wa- and a- prefixes to the following word: 
        text = re.sub(r"\b([وأ])[\s~]+", r"\1", text)
        soup = BeautifulSoup(text)
        remove_html_elements(soup, "style")
        remove_html_elements(soup, "title")
        remove_html_elements(soup, "div", class_="imageArea")
        remove_html_elements(soup, "span", class_="PageTitle")
        remove_html_elements(soup, "span", class_="magsImg")
        #remove_html_elements(soup, "span", class_="OriginalDigit")
        remove_html_elements(soup, "a", class_="ayah-outer-link")
        remove_html_elements(soup, "div", class_="PageText",
                             contains_str="Page Is Empty")
        # remove metadata page:
        soup.find("div", class_="textArea").extract()
        for fn_line in soup.find_all("hr", class_="footnoteLine"):
            fn_line.insert_after("FOOTNOTES")
        text = soup.prettify()
        
        
        return text

    def get_metadata(self, text):
        """Gets the metadata from the first td in the html.

        The metadata in eShia texts are in the first div with class 'textArea'
        (which represents the title page of the book).
        The only relevant metadata are title and publisher,
        which are in a <p> element. 

        Args:
            text (str): text of the file that contains both data and metadata

        Returns:
            metadata (str): metadata formatted in OpenITI format
                (including the magic value and the header splitter)
        """
        soup = BeautifulSoup(text)
        meta_div = soup.find("div", class_="textArea") # metadata is in first textArea div
        meta = [line.strip() for line in re.split("<br ?/?>", meta_div.prettify())]
        #print(meta)
        title = [re.sub(".+?</b>", "", line, flags=re.DOTALL) for line in meta \
                 if "Book title" in line or "عنوان کتاب" in line or "اسم الكتاب" in line][0].strip()
        publisher = [re.sub(".+?</b>", "", line, flags=re.DOTALL) for line in meta \
                     if "Publisher" in line or "نام ناشر" in line or "اسم الناشر" in line][0].strip()
        #print("title:", title)
        #print("publisher:", publisher)
        #input("Continue?")

        metadata =  "#META# 020.BookTITLE\t:: {}\n".format(title)
        metadata += "#META# 043.EdPUBLISHER\t:: {}\n".format(publisher)

        # add magic value and header splitter: 
        metadata = self.magic_value + metadata + self.header_splitter
        return metadata

    def add_page_numbers(self, text, source_fp):
        """Convert the page numbers in the text into OpenITI mARkdown format"""
        try:
            vol_no = int(re.findall("VOL(\d+)", source_fp)[0])
            vol_no = "PageV{:02d}P{}".format(vol_no, "{:03d}")
        except:
            vol_no = "PageV01P{:03d}"

        soup = BeautifulSoup(text)
        for page in soup.find_all("div", class_="PageText"):
            try:
                page_head = page.find("div", class_="PageHead")
            except:
                print("no page head found")
                page_head = None
            if page_head:
                page_no = re.findall("\d+", page_head.text)[0]
                page_no = vol_no.format(int(page_no))
                page_head.extract()
                page.insert_after(page_no)
        return soup.prettify()


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
                spl = re.split("#? ?FOOTNOTES", t)
                if len(spl) == 1: # no footnotes
                    text.append(t)
                else:
                    try:
                        notes = "Notes to {}:<br/>{}".format(split_text[i+1], spl[-1])
                    except:
                        notes = "Notes to [NO PAGE]:<br/>{}".format(spl[-1])
                    notes = html2md_noorlib.markdownify(notes) 
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
        text = html2md_noorlib.markdownify(html)
        return text             

    def post_process(self, text):
        #empty = """ *اين صفحه در كتاب اصلي بدون متن است / هذه الصفحة فارغة في النسخة المطبوعة *"""
        #text = re.sub(empty, "\n", text)
        text = re.sub("(PageV\d+P\d+)\s*PageV\d+P\d+", r"\1", text)
        text = super().post_process(text)
        text = re.sub(r"[\r\n]+# *[\r\n]+", "\n", text)
        fmt = ")»،؛:.!؟\-"
        fmt2 = fmt + "\d\s"
        text = re.sub("([{}]+)([^{}])".format(fmt, fmt2), r"\1 \2", text)
        text = re.sub("(\w)([(«])", r"\1 \2", text)
        text = re.sub("\) ([{}])".format(fmt), r")\1", text)
        #text = re.sub("(# [^%]+%~%.+)[\r\n]+(# [^%]+%~%.+)", r"\1\n\2", text)
        text = re.sub("[\r\n]+(# |Page)", r"\n\1", text)
        return text

if __name__ == "__main__":
    #import doctest
    #doctest.testmod()
    #input("Passed all tests. Continue?")
    import os

    errors = [#r"G:\London\OpenITI\new\NoorLib\2020-06-16\0872IdrisCimadDin\0872IdrisCimadDin.CuyunAkhbar\0872IdrisCimadDin.CuyunAkhbar.Noorlib0020423-ara1_VOL6.html", # error: if "Book title" in line][0].strip() IndexError: list index out of range
              #r"G:\London\OpenITI\new\NoorLib\2020-06-16\0872IdrisCimadDin\0872IdrisCimadDin.CuyunAkhbar\0872IdrisCimadDin.CuyunAkhbar.Noorlib0007954-ara1_VOL5.html", # error: if "Book title" in line][0].strip() IndexError: list index out of range
              #r"G:\London\OpenITI\new\NoorLib\2020-06-16\0411HamidDinKirmani\0411HamidDinKirmani.RahatCaql.Noorlib0023925-ara1.html", # line 219, in add_structural_annotations : text = html2md_eShia.markdownify(html) error:  File "C:\Python34\lib\site-packages\openiti\new_books\convert\helper\html2md.py", line 234, in process_tag : for el in node.children: RuntimeError: maximum recursion depth exceeded
              #r"G:\London\OpenITI\new\NoorLib\2020-06-16\Anon.KitabHaftWaAzilla\Anon.KitabHaftWaAzilla.NoorLb0015842-ara1.html", # # error: if "Book title" in line][0].strip() IndexError: list index out of range
              #r"G:\London\OpenITI\new\NoorLib\2020-06-16\0000DaciQarmatiCabdan\converted\0000DaciQarmatiCabdan.ShajaratYaqin.Noorlib0035479-ara1_html", # error: meta = [line.strip() for line in re.split("<br ?/?>", meta_div.prettify())] : AttributeError: 'NoneType' object has no attribute 'prettify'
              #r"G:\London\OpenITI\new\NoorLib\2020-06-16\0612CaliIbnWalidYamani\0612CaliIbnWalidYamani.DamighBatil_VOLS\CaliIbnWalidYamani.DamighBatil.Noorlib0005343-ara1_VOL2.html", # error: if "Book title" in line][0].strip() IndexError: list index out of range
              #r"G:\London\OpenITI\new\NoorLib\2020-06-16\0612CaliIbnWalidYamani\0612CaliIbnWalidYamani.DamighBatil_VOLS\CaliIbnWalidYamani.DamighBatil.Noorlib0005343-ara1_VOL1.html", # error: if "Book title" in line][0].strip() IndexError: list index out of range
              ]
    
    conv = NoorlibHtmlConverter()
    folder = r"G:\London\OpenITI\new\NoorLib\2020-06-16"
    conv.dest_folder = os.path.join(folder, "converted")
    conv.convert_file(r"G:\London\OpenITI\new\NoorLib\2020-06-16\0411HamidDinKirmani\0411HamidDinKirmani.RahatCaql.Noorlib0023925-ara1.html")
    input("CONTINUE?")
    for root, dirs, files in os.walk(folder):
        for fn in files:
            fp = os.path.join(root, fn)
            if fp.endswith("html"):
                print("converting", fp)
                if fp not in errors:
                    conv.convert_file(fp)
    for fp in errors:
        conv.convert_file(fp)
#NB: all converted files are in G:\London\OpenITI\new\NoorLib\2020-06-16\0557IbrahimBinHusaynHamidi\converted
    #conv.convert_files_in_folder(folder)
