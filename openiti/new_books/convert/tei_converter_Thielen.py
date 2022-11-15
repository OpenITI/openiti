"""A converter for converting Jan Thielen's tei xml files into OpenITI format.

The converter has two main functions:
* convert_file: convert a single html file.
* convert_files_in_folder: convert all html files in a given folder

Usage examples:
    >>> from tei_converter_Thielen import convert_file, convert_files_in_folder
    >>> folder = r"test/Thielen/"
    >>> convert_file(folder+"Thielen000070.xml", dest_fp=folder+"converted/Thielen000070")
    >>> convert_files_in_folder(folder, dest_folder=folder+"converted")

Both functions use the ThielenConverter class to do the heavy lifting.



The ThielenConverter (which is sub-classed from tei_converter_generic.TeiConverter)
converts both the tei xml files and the html files.
It uses the generic TeiConverter's tei2md.TeiConverter for the xml files,
and for the html files the html2md_Thielen.ThielenHtmlConverter
(which is a modified version (sub-class) of the html2md.MarkdownConverter).

Schema representing the method inheritance in the ThielenConverter:

=========================== ========================== =========================
GenericConverter            TeiConverter               ThielenConverter
=========================== ========================== =========================
__init__                    __init__ (appended)        (inherited)
convert_files_in_folder     (inherited)                convert_files_in_folder
convert file                convert_file               convert_file
make_dest_fp                (inherited)                (inherited)
get_metadata (dummy)        get_metadata               (inherited - for tei xml)
get_data                    (inherited)                (inherited - for tei xml)
pre_process                 pre_process                pre-process (appended)
add_page_numbers (dummy)    (inherited - not used)     (inherited - not used)
add_structural_annotations  add_structural_annotations (inherited - for tei xml)
remove_notes (dummy)        (inherited - generic!)     (inherited - generic!)
reflow                      (inherited)                (inherited)
add_milestones (dummy)      (inherited - dummy)        (inherited - not used)
post_process                post_process               post-process (appended)
compose                     (inherited)                (inherited)
save_file                   (inherited)                (inherited)
                            preprocess_page_numbers    (inherited)
                            preprocess_wrapped_lines   (inherited)
                                                       get_html_data
                                                       get_html_metadata
                                                       format_html_metadata
=========================== ========================== =========================

##Examples:
##    >>> from tei_converter_Thielen import ThielenConverter
##    >>> conv = ThielenConverter(dest_folder="test/Thielen/converted")
##    >>> conv.VERBOSE = False
##    >>> folder = r"test/Thielen"
##    >>> fn = r"Thielen000070.xml"
##    >>> conv.convert_file(os.path.join(folder, fn))

"""
import os
import re
from bs4 import BeautifulSoup

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.new_books.convert.tei_converter_generic import TeiConverter
from openiti.new_books.convert.helper import html2md_Thielen



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
    conv = ThielenConverter() 
    conv.convert_file(fp, dest_fp=dest_fp)

def convert_files_in_folder(src_folder, dest_folder=None,
                            extensions=[], exclude_extensions=["yml"],
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
    conv = ThielenConverter()
    conv.convert_files_in_folder(src_folder, dest_folder=dest_folder,
                                 extensions=extensions,
                                 exclude_extensions=exclude_extensions,
                                 fn_regex=fn_regex)


################################################################################






class ThielenConverter(TeiConverter):


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
        except:
            text_id = "n.n."
        metadata += "#META# coll_id: {}\n".format(text_id)
        metadata = self.magic_value + metadata + self.header_splitter
        return metadata

    def pre_process(self, text):
        def process_page(m):
            ar = ["أ", "ا", "ب", "ج", "و"]
            en = ["a", "a", "b", "j", "w"]
            soup = BeautifulSoup(m.group())
            page_no = soup.get_text().strip()
            if " " in page_no:
                vol, page_no = page_no.split(" ")
                if vol in ar:
                    vol = en[ar.index(vol)]
            else:
                vol = "00"
            page = int(page_no[:-1])
            suff = page_no[-1]
            if suff in ar:
                suff = en[ar.index(suff)]
                
            return "<page>PageBegV0{0}P{1:03d}{2}</page>".format(vol, page, suff)
            
            
        text = super().pre_process(text)
        # remove zero-width joiner:
        text = re.sub(r"‌", "", text)
        text = re.sub("([\n ])[|*] ", r"\1", text)
        text = re.sub('>', "> ", text)
        text = re.sub(" +", " ", text)
        # replace note tag for page numbers
##        text = re.sub('<note place="right[^>]+?>(.+?)</note>',
##                      process_page, text, flags=re.DOTALL)

        
        return text

    def format_html_metadata(self, meta_boxes):
        meta = {
            0: {
                "Domains": "", 
                "Title": "", 
            },
            1: {
                "Date": "", 
                "Translated from": "", 
                "Translator": "", 
                "Type": "", 
            },
            2: {
                "Author/Editor": "n.n.", 
                "Number": "", 
                "Pages": "", 
                "Publication type": "", 
                "Published": "n.d.", 
                "Publisher": "n.p.", 
                "Series": "", 
                "Title": "", 
                "Volume": "", 
            }
        }
        for i, box in enumerate(meta_boxes):
            for p in box.find_all("p"):
                #all_metadata[i].add(p.text.split(":")[0].strip())
                key = p.text.split(":")[0].strip()
                val = re.split(":", p.text, 1)[-1].strip()
                val = re.sub('English|Original| *" *|\n', "", val)
                val = re.sub(":", " :: ", val)
                meta[i][key] = val
     
        meta_strings = []
        meta_strings.append("#META# Title: {}".format(meta[0]["Title"]))
        meta_strings.append("#META# Genres: {}".format(meta[0]["Domains"]))
        for key in sorted(meta[1].keys(), reverse=True):
            if meta[1][key]:
                meta_strings.append("#META# {}: {}".format(key, meta[1][key]))
        ed_info = "#META# Ed_info: {} ({}), {}".format(meta[2]["Author/Editor"],
                                                       meta[2]["Published"],
                                                       meta[2]["Title"])
        if meta[2]["Series"]:
            ed_info += " ({} {}),".format(meta[2]["Series"], meta[2]["Volume"])
        ed_info += ", {}".format(meta[2]["Publisher"])
        if meta[2]["Volume"]:
            ed_info += ", vol. " + meta[2]["Volume"]
        if meta[2]["Pages"]:
            ed_info += ", pp. " + meta[2]["Pages"]
        meta_strings.append(ed_info)
        metadata = "\n".join(meta_strings)
        metadata = re.sub(" +", " ", metadata)
        metadata = re.sub(",+", ",", metadata)
        metadata = self.magic_value + metadata + self.header_splitter
        return metadata

    def get_html_metadata(self, soup):
        meta_boxes = soup.find_all("div", class_="boxcontent")
        return self.format_html_metadata(meta_boxes)

    def get_html_data(self, soup):
        text_soup = soup.find("body")
        c = html2md_Thielen.ThielenHtmlConverter()
        text = c.convert(text_soup)
        return text

##    def convert_files_in_folder(self, folder):
##        for fn in os.listdir(folder):
##            fp = os.path.join(folder, fn)
##            if os.path.isfile(fp) and fn.endswith("ara1"):
##                self.convert_file(fp)

    def add_structural_annotations(self, text, **options):
        soup = BeautifulSoup(text, "xml")
        text_soup = soup.find("text")
        text = html2md_Thielen.markdownify(str(text_soup), **options)
        return text

    def convert_file(self, source_fp, dest_fp=None):
        """Convert one file to OpenITI format.

        Args:
            source_fp (str): path to the file that must be converted.
            dest_fp (str): path to the converted file. Defaults to None
                (in which case, the converted folder will be put in a folder
                named "converted" in the same folder as the source_fp)

        Returns:
            None
        """
        if self.VERBOSE:
            print("converting", source_fp)
        if dest_fp == None:
            dest_fp = self.make_dest_fp(source_fp)
        with open(source_fp, mode="r", encoding="utf-8") as file:
            text = file.read()
        text = self.pre_process(text)
        soup = BeautifulSoup(text, "xml")
        self.metadata = self.get_metadata(text)
        text = self.add_structural_annotations(text, strip=["note"])

        # remove notes:
        notes = ""
        #text, notes = self.remove_notes(text)
        
        if not soup.find_all("lb") and not soup.find_all(title="linebreak"):
            text = self.reflow(text)
        text = self.post_process(text)
        text = self.compose(self.metadata, text, notes)

        self.save_file(text, dest_fp)

    def post_process(self, text, verbose=False):
        text = super().post_process(text)
        vols = re.findall("vol. (\d+) pp", self.metadata)
        #print(vols)
        if len(vols) == 1:
            text = re.sub("PageV00", "PageV{:02d}".format(int(vols[0])), text)
        elif len(vols) == 0:
            text = re.sub("PageV00", "PageV01", text)
        elif len(vols) > 1:
            print("More than one volume! adjust volume numbers manually")
        text = re.sub("# Page(V\d+P\d+)", r"Page\1\n\n#", text)

        text = re.sub("\n~~ *(PageV\d+P\d+)\n", r"\n\n\1\n", text)
        text = re.sub("\n~~ ", r"\n~~", text)
        text = re.sub("(### \|+[^#]+)\n~~", r"\1 ", text)
        text = re.sub("(### \|+ \[[^\]]+\]) *\n+### \|{3}", r"\1", text)
        text = re.sub("([^.؟])\n{2}# (PageV\d+P\d+) ?", r"\1 \2\n~~", text)
        # if a page number does not follow a dot/question mark
        text = re.sub("([^.؟])\n{2}(PageV\d+P\d+)\n+# ", r"\1 \2\n~~", text)
        text = re.sub("([^.؟])\n{2}(PageV\d+P\d+) *(?!\n)", r"\1 \2\n~~", text)
        #text = re.sub("@QUOTE@", "", text)
        return text



###########################################################################


def combine_files_in_folder(folder, output_fp=None):
    """Combine separate html files into one master html file"""
    print(folder)
    comp = HTML_HEADER
    i = 0
    for fn in os.listdir(folder):
        if fn.endswith(".html") and not fn.endswith("combined.html"):
            fp = os.path.join(folder, fn)
            with open(fp, mode="r", encoding="utf-8") as file:
                html = file.read()
            soup = BeautifulSoup(html)
            if i == 0:
                meta_boxes = soup.find_all("div", class_="boxcontent")
                meta_boxes = [str(x) for x in meta_boxes]
                metadata = """<div class="metadata">\n{}\n</div>"""
                metadata = metadata.format("\n".join(meta_boxes))
                comp += metadata
            box = soup.find("div", class_="textbox")
            comp += "\n{}\n".format(box)
            i += 1
    comp += HTML_FOOTER
    comp = BeautifulSoup(comp).prettify()
    if not output_fp:
        #output_fp = os.path.join(folder, os.path.split(folder)[-1]+"_combined.html")
        #output_fp = re.findall("Thielen\d+", os.path.split(folder)[-1])[0]
        output_fp = os.path.join("combined", os.path.split(folder)[-1])
    with open(output_fp, mode="w", encoding="utf-8") as file:
        file.write(comp)

def list_all_tags(folder, header_end_tag="</teiHeader>"):
    """
    Extracts a list of all tags used in the texts in a folder:

    For Thielen:

    <body>
    <div1 type="" n="" (name="")(/)>     # book subdivision level 1
    <div2 type="" n="" (name="")(/)>     # book subdivision level 2 
    <head>                               # title
    <lb(/)>                              # start of new line
    <milestone unit="" n=""/>            #
    <p>                                  # paragraph
    <pb (type="") n=""/>                 # start of new page
    <quote type="" (author="") (id="")>  # quotation of a source
    <text lang="" id="">                 # metadata

    # tables: 
    <table>
    <tr>
    <td>

    # line groups (e.g., for poetry):
    <lg>                                 # line group
    <l>                                  # line in line group


    div types:

    ================= =================== 
    div1              div2
    ================= ===================
    book
    books
    chapter           chapter
    folio
    sentence          sentence
                      aphorism
    ================= ===================

    pb types: primary, secondary

    quote types: lemma, commentary

    milestone units: book, ed1chapter, ed1page, ms1folio
    """
    tags = []
    full_tags = []
    for fn in os.listdir(folder):
        fp = os.path.join(folder, fn)
        #if not fn.endswith("yml") and not fn.endswith("py"):
        if fn.endswith("xml"):
            print(fn)
            with open(fp, mode="r", encoding="utf-8") as file:
                text = file.read()
    ##        orig_len = len(text)
            text = re.sub("\n~~", " ", text)
            if header_end_tag:
                text = re.sub(".+?{}".format(header_end_tag), "", text,
                              count=1, flags=re.DOTALL)
    ##        if "teiHeader" in text:
    ##            print(fn, "missing teiheader closing tag?")
    ##        if len(text) == orig_len:
    ##            print(fn, "missing teiheader?")
            text_full_tags = re.findall("<[^/][^>]*>", text)
            text_tags = re.findall("<[^/][^ >]+", text)
##            if '<milestone' in text_tags:
##                print("milestone in", fn)
##                input()
            for tag in set(text_tags):
                if tag not in tags:
                    tags.append(tag)
            for tag in set(text_full_tags):
                if tag not in full_tags:
                    full_tags.append(tag)

    stripped_tags = [re.sub('(author|lang|n|name|id)="[^"]+"', r'\1=""', tag)\
                     for tag in full_tags]
    stripped_tags = list(set(stripped_tags))

##    for tag in sorted(stripped_tags):
##        print(tag)
    for tag in sorted(full_tags):
        print(tag)


##############################################################################

if __name__ == "__main__":
##    conv = ThielenConverter(dest_folder="test/converted")
##    conv.VERBOSE = False
##    folder = r"test"
##    fn = r"Thielen000070"
##    conv.convert_file(os.path.join(folder, fn))
##    input("passed test")
    import doctest
    doctest.testmod()

    input("Passed tests. Press Enter to start converting")
  

    folder = r"G:\London\OpenITI\RAWrabica\RAWrabica005000\Thielen"
    conv = ThielenConverter(os.path.join(folder, "converted"))
    conv.extension = ""
    conv.convert_files_in_folder(folder)
