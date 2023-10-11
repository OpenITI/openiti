"""A converter for converting LAL tei xml files into OpenITI format.

(LAL = Library of Arabic Literature)

The converter has two main functions:
* convert_file: convert a single html file.
* convert_files_in_folder: convert all html files in a given folder

Usage examples:
    >>> from tei_converter_LAL import convert_file, convert_files_in_folder
    >>> folder = r"test/LAL/"
    >>> convert_file(folder+"LAL000070.xml", dest_fp=folder+"converted/LAL000070")
    >>> convert_files_in_folder(folder, dest_folder=folder+"converted")

Both functions use the LALConverter class to do the heavy lifting.



The LALConverter (which is sub-classed from tei_converter_generic.TeiConverter)
converts both the tei xml files and the html files.
It uses the generic TeiConverter's tei2md.TeiConverter for the xml files,
and for the html files the html2md_LAL.LALHtmlConverter
(which is a modified version (sub-class) of the html2md.MarkdownConverter).

Schema representing the method inheritance in the LALConverter:

=========================== ========================== =========================
GenericConverter            TeiConverter               LALConverter
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
##    >>> from tei_converter_LAL import LALConverter
##    >>> conv = LALConverter(dest_folder="test/LAL/converted")
##    >>> conv.VERBOSE = False
##    >>> folder = r"test/LAL"
##    >>> fn = r"LAL000070.xml"
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
from openiti.new_books.convert.helper import html2md_LAL
from openiti.helper.ara import deNoise



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
    conv = LALConverter() 
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
    conv = LALConverter()
    conv.convert_files_in_folder(src_folder, dest_folder=dest_folder,
                                 extensions=extensions,
                                 exclude_extensions=exclude_extensions,
                                 fn_regex=fn_regex)


################################################################################






class LALConverter(TeiConverter):


    def extract_meta_item(self, tei_header, tag_name, labels_d, meta):
        """Extract author, title, editor from teiHeader"""
        items = tei_header.titleStmt.find_all(tag_name)
        for item in items:
            #lang = item["xml:lang"]
            lang = item["xml:id"].split(".")[0]
            try:
                label = labels_d[tag_name][lang]
            except:
                label = tag_name[0].upper() + tag_name[1:]
            try:
                meta += "#META# {}: {}\n".format(label, item.text.strip())
            except Exception as e:
                print(tag_name, "not found:", e)
                pass
        return meta

    def extract_publ_stmt(self, tei_header, meta):
        """Extract the publicationStmt info from the teiHeader"""
        try:
            isbn = tei_header.publicationStmt.idno
            meta += "#META# ISBN: {}\n".format(isbn.text.strip())
        except Exception as e:
            print("isbn not found:", e)
            pass
        try:
            publisher = tei_header.publicationStmt.publisher
            meta += "#META# Publisher: {}\n".format(publisher.text.strip())
        except Exception as e:
            print("Publisher not found:", e)
            pass
        try:
            pubPlace = tei_header.publicationStmt.pubPlace
            meta += "#META# Place of publication: {}\n".format(pubPlace.text.strip())
        except Exception as e:
            print("pubPlace not found:", e)
            pass
        return meta

    def extract_witnesses(self, tei_header, meta):
        """Extract witness data from the teiHeader"""
        # try:
        #     witnesses = tei_header.sourceDesc.listBibl
        # except Exception as e:
        #     try: 
        #         witnesses = tei_header.sourceDesc
        #     except:
        #         print("witnesses not found:", e)
        #         return meta
        # for w in witnesses.find_all("bibl"):
        #     w = w.text.strip()
        #     meta += "#META# Witness: {}\n".format(w)
        try:
            witnesses = tei_header.sourceDesc.listBibl
            for w in witnesses.find_all("bibl"):
                w = w.text.strip()
                meta += "#META# Witness: {}\n".format(w)
            return meta
        except:
            pass

        for ref in tei_header.find_all("bibl"):
            if "xml:id" in ref.attrs and "wit" in ref["xml:id"]:
                w = ref.text.strip()
                meta += "#META# Witness: {}\n".format(w)
        return meta
                
    def extract_ed_decl(self, tei_header, meta):
        """Extract the editorial declaration from the teiHeader"""
        try:
            decl = tei_header.editorialDecl
            for p in decl.find_all("p"):
                p = re.sub("[\r\n]+", " ", p.text.strip())
                meta += "#META# Editorial declaration: {}\n".format(p)
        except Exception as e:
            print("editorial declaration not found:", e)
            pass
        return meta    

    def get_metadata(self, text):
        """Extracts the metadata from the text.


        Args:
            text (str): text of the file that contains data + metadata

        Returns:
            metadata (str): metadata formatted in OpenITI format
                (including the magic value and the header splitter)
        """
        soup = BeautifulSoup(text, "xml")
        labels_d = {
            "title":  {"ARA": "العنوان", "ENG": "Title (EN)"},
            "author": {"ARA": "المؤلف", "ENG": "Author"},
            "editor": {"ARA": "المحقق", "ENG": "Editor"},
            }
        meta = ""
        tei_header = soup.teiHeader
        meta = self.extract_meta_item(tei_header, "title", labels_d, meta)
        meta = self.extract_meta_item(tei_header, "author", labels_d, meta)
        meta = self.extract_meta_item(tei_header, "editor", labels_d, meta)
        meta = self.extract_publ_stmt(tei_header, meta)
        meta = self.extract_witnesses(tei_header, meta)
        meta = self.extract_ed_decl(tei_header, meta)
        meta = re.sub("([a-z])([A-Z])", r"\1 \2", meta)
        meta = re.sub("\n+(?!#META#)", " ", meta)
        meta = "######OpenITI#\n\n" + meta + "\n\n#META#Header#End#\n\n"
        
        return meta

    def pre_process(self, text):
        text = super().pre_process(text)
        # remove zero-width joiner:
        text = re.sub(r"‌", "", text)
        text = re.sub(" *<caesura/> *", " %~% ", text)
        text = re.sub("[\r\n]+", " ", text)
##        soup = BeautifulSoup(text, "xml")
##        # remove the front page:
##        soup.extract("front")
##        # remove notes:
##        soup.extract("note")
##        # convert caesura tags into OpenITI poetry tags:
##        for caesura in soup.find_all("caesura"):
##            caesura.replace_with(" %~% ")
##        text = soup.prettify()
        return text


##    def convert_files_in_folder(self, folder):
##        for fn in os.listdir(folder):
##            fp = os.path.join(folder, fn)
##            if os.path.isfile(fp) and fn.endswith("ara1"):
##                self.convert_file(fp)

    def add_structural_annotations(self, text, **options):
        soup = BeautifulSoup(text, "xml")
        text_soup = soup.find("body")
        text = html2md_LAL.markdownify(str(text_soup), **options)
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
        self.metadata = self.get_metadata(text)
        text = self.add_structural_annotations(text, strip=["front", "note"])

        # notes already removed by stripping <note> elements:
        notes = ""
        #text, notes = self.remove_notes(text)
        
        text = deNoise(text)

        soup = BeautifulSoup(text, "xml")
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
        text = re.sub("(### \|PARATEXT\|(?:\n# .+)+)\n### \|PARATEXT\|", r"\1", text)
        # fix sections without headers:
        text = re.sub("(### \|+)([\r\n]+)", r"\1 \2", text)
        # put poems always on one line:
        text = re.sub(r"(%~%.+)[\r\n]+~~", r"\1 ", text)
        # remove waṣlas:
        text = re.sub("ٱ", "ا", text)
        # Format the paragraph numbers as page number:
        # (this proved to be the wrong approach: some text have a number for every line)
        # temp = ""
        # current_p = ""
        # for p in re.split("(\[[\d.]+\])", text):
        #     if p.startswith("["):
        #         split_p = p[1:-1].split(".")
        #         if len(split_p) == 2:
        #             v, p = split_p
        #         elif len(split_p) > 2:
        #             v = split_p[0]
        #             p = "0".join(split_p[1:])
        #             print(split_p)
        #         else:
        #             v = 0
        #             p = split_p[0]
        #         current_p = "PageV{:02d}P{:03d}".format(int(v), int(p))
        #     else:
        #         temp += p + current_p
        # text = re.sub("\[(\d)\]", r"PageV00P00\1", temp)
        # text = re.sub("\[(\d\d)\]", r"PageV00P0\1", text)
        # text = re.sub("\[(\d\d+)\]", r"PageV00P\1", text)

        return text



###########################################################################


def list_all_tags(folder, header_end_tag="</teiHeader>"):
    """
    Extracts a list of all tags used in the texts in a folder:


    """
    tags = []
    full_tags = []
    for fn in os.listdir(folder):
        fp = os.path.join(folder, fn)
        #if not fn.endswith("yml") and not fn.endswith("py"):
        if fn.endswith("xml"):
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
##    conv = LALConverter(dest_folder="test/converted")
##    conv.VERBOSE = False
##    folder = r"test"
##    fn = r"LAL000070"
##    conv.convert_file(os.path.join(folder, fn))
##    input("passed test")
    import doctest
    doctest.testmod()

    #input("Passed tests. Press Enter to start converting")
  

    folder = r"C:\Users\peter\Downloads\LAL"
    conv = LALConverter(os.path.join(folder, "converted"))
    #fn = "al-Quḍāʿī (ed. Qutbuddin) A Treasury of Virtues.xml"
    #conv.convert_file(os.path.join(folder, fn))
    #input("CONTINUE?")
    conv.extension = ""
    conv.VERBOSE = True
    conv.convert_files_in_folder(folder)
