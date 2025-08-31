"""A converter for converting Persian Digital Library
tei xml files into OpenITI format.

The converter has two main functions:
* convert_file: convert a single html file.
* convert_files_in_folder: convert all html files in a given folder

Usage examples:
    >>> from tei_converter_GRAR import convert_file, convert_files_in_folder
    >>> folder = r"test/GRAR/"
    >>> convert_file(folder+"GRAR000070.xml", dest_fp=folder+"converted/GRAR000070")
    >>> convert_files_in_folder(folder, dest_folder=folder+"converted")

Both functions use the PDLConverter class to do the heavy lifting.

The PDL GitHub page (https://github.com/PersDigUMD/PDL)
contains 114 texts transcribed in TEI xml.

Schema representing the method inheritance in the PDLConverter:

=========================== ========================== =========================
GenericConverter            TeiConverter               PDLConverter
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
=========================== ========================== =========================

##Examples:
##    >>> from tei_converter_PDL import PDLConverter
##    >>> conv = PDLConverter(dest_folder="test/PDL/converted")
##    >>> conv.VERBOSE = False
##    >>> folder = r"test/PDL"
##    >>> fn = r"PDL000070.xml"
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
from openiti.new_books.convert.helper import html2md_GRAR



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
    conv = PDLConverter() 
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
    conv = PDLConverter()
    conv.convert_files_in_folder(src_folder, dest_folder=dest_folder,
                                 extensions=extensions,
                                 exclude_extensions=exclude_extensions,
                                 fn_regex=fn_regex)


################################################################################






class PDLConverter(TeiConverter):

##    def pre_process(self, text):
##        text = super().pre_process(text)
##        text = re.sub("([\n ])[|*] ", r"\1", text)
##        return text

    def get_metadata(self, text, url=None):
        metadata = super().get_metadata(text)
        if url:
            metadata = re.sub("(\n+#META#Header#End)", "\n#META# url: " + url + r"\1", metadata)
        return metadata
        
        

    def format_lines(self, soup, include_line_numbers=True):
        """Format <l> tags"""
        text = ""
        for line in soup.find_all("l", recursive=False):
            segments = line.find_all("seg")
            if segments:
                line_text = " %~% ".join([s.text for s in segments])
            else:
                print("no segments in this line:")
                print(line)
                line_text = line.text
            if include_line_numbers and "n" in line.attrs:
                line_text = f'\n# {line["n"]} {line_text}'
            else:
                line_text = "\n# " + line_text
            text += line_text
        return text
            
            

    def format_text(self, soup):
        text = ""
        page_no = ""
        vol_no = 1
        div_types = set()
        div_subtypes = set()        
        divs = soup.find_all("div")

        n_pages = len([1 for div in divs if "subtype" in div.attrs and div["subtype"] == "page"])
        n_poems = len([1 for div in divs if "subtype" in div.attrs and div["subtype"] == "poem"])
        print(n_pages, "pages and", n_poems, "poems in this document")
        if n_pages:
            padding = len(str(n_pages))
        else:
            padding = len(str(n_poems))
        

        for div in divs:
            if "type" in div.attrs:
                div_types.add(div["type"])
            if "subtype" in div.attrs:
                div_subtypes.add(div["subtype"])
                if div["subtype"] == "chapter":
                    if "n" in div.attrs:
                        chapter_title = div["n"]
                        chapter_no = re.findall("\d+", div["n"])
                        if chapter_no:
                            vol_no = int(chapter_no[0])
                            #chapter_title = chapter_no[0] + " " + chapter_title[len(str(vol_no)):]
                            chapter_title = re.sub("(\d+)", r" \1 ", chapter_title).strip()
                        text += f'\n### | [ {chapter_title} ]'
                elif div["subtype"] == "page":
                    text += f'\n{page_no}'
                    page_no = f'PageV{vol_no:02d}P' + div["n"].zfill(padding)
                elif div["subtype"] == "poem":
                    if n_pages == 0:
                        text += f'\n{page_no}'
                        p = div["n"].zfill(padding)
                        page_no = f'PageV{vol_no}P{p}'
                    text += '\n### || '
                    if "genre" in div.attrs:
                        text += f'[genre: {div["genre"]}]'
                elif div["subtype"] == "paragraph":
                    text += "\n# " + div.text
            text += self.format_lines(div)

        if page_no:
            text += f'\n{page_no}'
        else:
            text += '\nPageV00P000'
                    
        print("div types:")
        print(div_types)
        print("div subtypes:")
        print(div_subtypes)

        

        return text
        
            
        


##    def convert_files_in_folder(self, folder):
##        for fn in os.listdir(folder):
##            fp = os.path.join(folder, fn)
##            if os.path.isfile(fp) and fn.endswith("ara1"):
##                self.convert_file(fp)

    def convert_file(self, source_fp, dest_fp=None, url=None):
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
        self.metadata = self.get_metadata(text, url=url)
        text = self.format_text(soup)
        notes = ""
        #text = self.add_structural_annotations(text)


        #text, notes = self.remove_notes(text)
        if not soup.find_all("lb") and not soup.find_all(title="linebreak") and not soup.find_all("l"):
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
        if verbose:
            print(text)
            input()
        text = re.sub("\n~~ *(PageV\d+P\d+)\n", r"\n\n\1\n", text)
        text = re.sub("\n~~ ", r"\n~~", text)
        text = re.sub("(### \|+[^#]+)\n~~", r"\1 ", text)
        text = re.sub("(### \|+ \[[^\]]+\]) *\n+### \|{3}", r"\1", text)
        text = re.sub("([^.؟])\n{2}# (PageV\d+P\d+) ?", r"\1 \2\n~~", text)
        # if a page number does not follow a dot/question mark
        text = re.sub("([^.؟])\n{2}(PageV\d+P\d+)\n+# ", r"\1 \2\n~~", text)
        text = re.sub("([^.؟])\n{2}(PageV\d+P\d+) *(?!\n)", r"\1 \2\n~~", text)
        #text = re.sub("@QUOTE@", "", text)
        # if a page number immediately follows a heading, switch order:
        text = re.sub("(### \|.+)\n(Page\w+)", r"\2\n\1", text)
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
        #output_fp = re.findall("GRAR\d+", os.path.split(folder)[-1])[0]
        output_fp = os.path.join("combined", os.path.split(folder)[-1])
    with open(output_fp, mode="w", encoding="utf-8") as file:
        file.write(comp)

def list_all_tags(folder, header_end_tag="</teiHeader>"):
    """
    Extracts a list of all tags used in the texts in a folder:

    For GRAR:

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
        if not fn.endswith("yml") and not fn.endswith("py"):
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
##    conv = PDLConverter(dest_folder="test/converted")
##    conv.VERBOSE = False
##    folder = r"test"
##    fn = r"GRAR000070"
##    conv.convert_file(os.path.join(folder, fn))
##    input("passed test")
    import doctest
    doctest.testmod()

    input("Passed tests. Press Enter to start converting")
  

    folder = r"G:\London\OpenITI\RAWrabica\RAWrabica005000\GRAR"
    conv = PDLConverter(os.path.join(folder, "converted"))
    conv.extension = ""
    conv.convert_files_in_folder(folder)
