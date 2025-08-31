"""Generic converter that converts an Epub to OpenITI mARkdown.

Examples:
    Generic epub conversion::
    
        >>> from epub_converter_generic import GenericEpubConverter
        >>> gen_converter = GenericEpubConverter(dest_folder="test/converted")
        >>> gen_converter.VERBOSE = False
        >>> folder = r"test"
        >>> fn = r"Houellebecq 2019 - serotonine.epub"
        >>> gen_converter.convert_file(os.path.join(folder, fn))
        >>> gen_converter.convert_files_in_folder(folder, ["epub",])

    Sub-class to create a converter specific to epubs from the Hindawi library::
    
        # >>> HindawiConverter = GenericEpubConverter("test/converted")
        # >>> HindawiConverter.VERBOSE = False
        # >>> from helper import html2md_hindawi
        # >>> HindawiConverter.convert_html2md = html2md_hindawi.markdownify  # (1)
        # >>> HindawiConverter.toc_fn = "nav.xhtml"  # (2)
        # >>> folder = r"test"
        # >>> fn = r"26362727.epub"
        # >>> HindawiConverter.convert_file(os.path.join(folder, fn))
    
        # (1) overwrite the convert_html2md function
        # (2) specify the filename of the table of contents in Hindawi epub files

An Epub file is in fact a zipped archive.
The most important element of the archive for conversion purposes
are the folders that contain the html files with the text.
Some Epubs have a table of contents that defines the order
in which these html files should be read.

The GenericEpubConverter is a subclass of the GenericConverter
from the generic_converter module:

GenericConverter
    \_ GenericEpubConverter

GenericEpubConverter's main methods are inherited from the GenericConverter:

* convert_file(source_fp): basic procedure for converting an epub file.
* convert_files_in_folder(source_folder): convert all epub files in the folder
    (calls convert_file)

Methods of both classes:
(methods of GenericConverter are inherited by GenericEpubConverter;
methods of GenericConverter with the same name
in GenericEpubConverter are overwritten by the latter)

=========================== ========================
GenericConverter            GenericEpubConverter
=========================== ========================
__init__                    __init__
convert_files_in_folder     (inherited)
convert_file                (inherited)
make_dest_fp                (inherited - generic!)
get_metadata                (inherited - generic!)
get_data                    get_data
pre_process                 (inherited)
add_page_numbers            (inherited - generic!)
add_structural_annotations  (inherited - generic!)
remove_notes                remove_notes
reflow                      (inherited)
add_milestones              (inherited)
post_process                (inherited - generic!)
compose                     (inherited)
save_file                   (inherited)
                            inspect_epub
                            sort_html_files_by_toc
                            add_unique_tags
=========================== ========================

To create a converter for a specific type of epubs,
subclass the GenericEpubConverter and overwrite
some of its methods:

GenericConverter
    \_ GenericEpubConverter
            \_ HindawiEpubConverter
            \_ ShamelaEpubConverter
            \_ ...
"""

import codecs
import os
import re
import zipfile
import time

from bs4 import BeautifulSoup


if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.new_books.convert.generic_converter import GenericConverter
from openiti.new_books.convert.helper import html2md



class GenericEpubConverter(GenericConverter):

    def __init__(self, dest_folder=None, overwrite=True):
        """Initialize the class and its super-class."""
        super().__init__(dest_folder=dest_folder, overwrite=overwrite)
        self.root_tag_string = "soup.html.body"
        self.unique_tags = dict()
        if dest_folder == None:
            self.dest_folder = "converted"
        else:
            self.dest_folder = dest_folder
        self.VERBOSE = True


##    def make_dest_fp(self, source_fp):
##        """"""
##        source_folder = os.path.split(source_fp)[0]
##        self.dest_folder = os.path.join(source_folder, "converted")
##        self.dest_fp = super().make_dest_fp(source_fp)

    def inspect_epub(self, src_fp):
        """Print the contents of the zip archive."""
        if self.VERBOSE:
            print("-"*60)
            print("Contents of  {}:".format(src_fp))
        if src_fp.endswith(".epub"):
            zp = zipfile.ZipFile(src_fp)
            if self.VERBOSE:
                for info in zp.infolist():
                    print(info.filename)


    def convert_html2md(self, html):
        """Convert the Epub's internal html to mARkdown text.

        *** USING A GENERIC HTML TO MARKDOWN CONVERTER HERE.
        OVERWRITE THIS FUNCTION IN THE SUB-CLASS
        TO CONVERT THE EPUB'S SPECIFIC HTML FLAVOUR TO MARKDOWN ***
        """
        text = html2md.markdownify(html)
        return text


    def add_unique_tags(self, root_tag, src_fp, fn):
        """Adds tags to the unique_tags_dictionary that were not yet in it.

        Args:
            root_tag (BeautifulSoup object): html element containing the text.
            unique_tabs (dict): a dictionary containing all tags used in the
                converted texts.
            src_fp (str): the path to the file currently being converted.
            fn (str): the filename of the string currently being converted.

        Returns:
            None
        """
        all_tags = root_tag.find_all()
    ##    print("number of tags in document {}: {}".format(fn, len(all_tags)))
    ##    all_divs = root_tag.find_all("div")
    ##    print("number of divs in document {}: {}".format(fn, len(all_divs)))

        for tag in all_tags:
            if tag.name not in self.unique_tags:
                try:
                    class_ = repr(tag["class"])
                except:
                    class_ = "no class"
                self.unique_tags[tag.name]={class_: (src_fp, fn)}
            else:
                try:
                    class_ = repr(tag["class"])
                except:
                    class_ = "no class"
                if class_ not in self.unique_tags[tag.name]:
                    self.unique_tags[tag.name][class_] = (src_fp, fn)


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
        
        
        toc = []
        if toc_fp.endswith("ncx"):
            soup = BeautifulSoup(toc_data, "lxml")
            for c in soup.find_all("content"):
                fn = os.path.split(c.get("src"))[-1]
                if fn in html_files_dict:
                    toc.append(html_files_dict[fn])
        else:
            soup = BeautifulSoup(toc_data)
            toc_ol = soup.find("ol")
            for a in toc_ol.find_all("a"):
                fn = os.path.split(a.get("href"))[-1]
                if fn in html_files_dict:
                    toc.append(html_files_dict[fn])
        return toc


    def remove_notes(self, text):
        """Remove the footnotes from the text.

        Args:
            text (str)

        Returns:
            text_without_notes (str): text from which the notes were removed.
            notes (str): the footnotes converted to endnotes
                (if there are endnotes: add the endnote_splitter before them)
        """
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
                    p = re.findall("PageV\d+P\d+", spl[i-1])
                    if p:
                        notes += "{}:\n\n{}\n\n".format(p[-1], fn_text)
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

    def find_toc_fn(self,src_fp):
        """Try to find the file containing the table of contents automatically"""
        zp = zipfile.ZipFile(src_fp)
        for info in zp.infolist():
            if "toc." in info.filename:
                print(info.filename)
                return info.filename

    def get_toc(self, src_fp):
        """Get the filename of the table of contents of the epub"""
        try:
            self.toc_fn
        except:
            toc_fn = self.find_toc_fn(src_fp)
            if toc_fn:
                self.toc_fn = toc_fn
                return toc_fn
            self.inspect_epub(src_fp)
            toc_input = """\
Write the filename (with extension) of the table of contents
(if there is no table of contents, simply press Enter): """
            if self.VERBOSE:
                resp = input(toc_input)
            else:
                resp = ""
            #print(resp)
            if resp.endswith("ml"):
                self.toc_fn = resp
            else:
                self.toc_fn = "no toc"
        return self.toc_fn


    def get_data(self, src_fp):
        """Converts an Epub file to an OpenITI mARkdown document.

        If a dictionary is passed as the unique_tags parameter,
        the function will keep track of all tags (and their classes)
        used in the converted Epub file.

        Args:
            src_fp (str): the path to the file currently being converted.
            dest_folder (str): the path to the folder where the converted file
                should be stored.
            conv_func (function): the function used to convert html to mARkdown.
            toc_fn (str): filename of the table of contents file within the epub.
            root_tag_string (str): the path to the BeautifulSoup element that
                contains the full text.
                Default: the body tag.
            unique_tabs (dict): a dictionary containing all tags used in the Epub.
                Default: None (tags used in the epubs will not be listed)

        Returns:
            unique_tabs (dict): a dictionary containing all tags used in the Epub.
        """
        if src_fp.endswith(".epub"):
            zp = zipfile.ZipFile(src_fp)
            if self.VERBOSE:
                fn = os.path.basename(src_fp)
##                msg = "Press Enter to convert %s to txt..." % fn
##                input(msg)

            # make a list of the html files in the epub:

            toc_fn = self.get_toc(src_fp)
            html_files = []
            for info in zp.infolist():
                if info.filename.endswith(self.toc_fn):
                    toc_fp = info.filename
                    if self.VERBOSE:
                        print("toc_fp", toc_fp)
                elif info.filename.endswith("html"):
                    html_files.append(info.filename)

            # sort the list of the html files in the correct order:

            try:
                html_files = self.sort_html_files_by_toc(zp, toc_fp, html_files)
            except:
                if self.VERBOSE:
                    print("No table of contents. Use file numbers for order.")
                html_files = html_files
            if self.VERBOSE:
                print("Table of contents of the Epub file:")
                for file in html_files:
                    print("    ", file)
                print("End of table of contents")

            # Extract the text from the different html files in the epub archive:

            new_text = ""
            for fp in html_files:
                fn = os.path.split(fp)[-1]
                data = zp.read(fp)
                text = codecs.decode(data, "utf-8")
                text = re.sub(r"<br />", "\n", text)
                soup = BeautifulSoup(text)
                root_tag = eval(self.root_tag_string)
                self.add_unique_tags(root_tag, src_fp, fn)
                text = self.convert_html2md(root_tag)
                new_text += "\n\n\n\n" + text
            new_text = re.sub("\n{3,}", "\n\n", new_text)

            return new_text


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    input("Testing finished. Continue?")
    
##    c = GenericEpubConverter()
##    c.make_dest_fp("a/b/c.epub")
##    print(c.dest_fp)
##    c = GenericEpubConverter("test/converted")
##    c.make_dest_fp("a/b/c.epub")
##    print(c.dest_fp)
##
##
##    input()

##    gen_converter = GenericEpubConverter("test/converted")
##    fp = r"test\Houellebecq 2019 - serotonine.epub"
##    gen_converter.convert_file(fp)
##    print("converted Houellebecq")
##    gen_converter.VERBOSE = True
##    gen_converter.convert_files_in_folder("test", ["epub",])
##    print("all files in test folder converted")
##
##    print("-"*60)

    import html2md_hindawi
    HindawiConverter = GenericEpubConverter("test/converted")
    HindawiConverter.convert_html2md = html2md_hindawi.markdownify
    HindawiConverter.toc_fn = "nav.xhtml"
    fp = r"test\26362727.epub"
    HindawiConverter.convert_file(fp)
    print("converted Hindawi text")




