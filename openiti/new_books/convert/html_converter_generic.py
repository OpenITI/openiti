"""Generic converter that converts HTML files to OpenITI mARkdown.

This generic converter forms the basis for specific converters
tailored to libraries whose texts are in html format.

Examples:
    Generic html conversion:
    >>> from html_converter_generic import GenericHtmlConverter
    >>> gen_converter = GenericHtmlConverter(dest_folder="test/converted")
    >>> gen_converter.VERBOSE = False
    >>> folder = r"test/eShia"
    >>> fn = "86596.html"
    >>> gen_converter.convert_file(os.path.join(folder, fn))
    >>> gen_converter.convert_files_in_folder(folder, extensions=[".html"])

    Sub-class to create a converter specific to htmls from the eShia library:
    >>> eShiaConv = GenericHtmlConverter("test/converted")
    >>> eShiaConv.VERBOSE = False
    >>> from helper import html2md_eShia
    >>> eShiaConv.add_structural_annotations = html2md_eShia.markdownify  # (1)
    >>> folder = r"test/eShia"
    >>> fn = "86596.html"
    >>> eShiaConv.convert_file(os.path.join(folder, fn))
    
    # (1) overwrite the add_structural_annotations method with another function

The GenericHtmlConverter is a subclass of the GenericConverter
from the generic_converter module:

GenericConverter
    \_ GenericEpubConverter
    \_ GenericHtmlConverter

GenericHtmlConverter's main methods are inherited from the GenericConverter:

* convert_file(source_fp): basic procedure for converting an html file.
* convert_files_in_folder(source_folder): convert all html files in the folder
    (calls convert_file)

Methods of both classes:
(methods of GenericConverter are inherited by GenericHtmlConverter;
methods of GenericConverter with the same name
in GenericHtmlConverter are overwritten by the latter)

=================================== ==========================
GenericConverter                    GenericHtmlConverter
=================================== ==========================
__init__                            __init__
convert_files_in_folder             (inherited)
convert file                        (inherited)
make_dest_fp                        (inherited - generic!)
get_metadata (dummy)                (inherited - dummy!)
get_data                            get_data
pre_process                         (inherited)
add_page_numbers (dummy)            (inherited - dummy!)
add_structural_annotations (dummy)  add_structural_annotations
remove_notes (dummy)                remove_notes
reflow                              (inherited)
add_milestones (dummy)              (inherited - dummy!)
post_process                        (inherited - generic!)
compose                             (inherited)
save_file                           (inherited)
                                    inspect_tags_in_html
                                    inspect_tags_in_folder
                                    find_example_of_tag
=================================== ==========================

The main difference between the two converters
is the add_structural_annotations method.
GenericHtmlConverter uses here the html2md converter
that converts or strips html tags.

To create a converter for a specific type of html files,
subclass the GenericHtmlConverter and overwrite
some of its methods that are dependent on the structure of the data, esp.:

- get_metadata
- add_page_numbers
- remove_notes
- add_structural_annotation (subclass the generic html2md converter for this,
  and create a html2md converter specific to the files you need to convert)

GenericConverter
    \_ GenericHtmlConverter
            \_ eShiaHtmlConverter
            \_ NoorlibHtmlConverter
            \_ ...

In addition to the conversion methods, the GenericHtmlConverter
contains a number of useful methods that help with deciding which
html tags need to be converted:

- inspect_tags_in_html
- inspect_tags_in_folder
- find_example_of_tag

"""

import codecs
import html
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
import html



class GenericHtmlConverter(GenericConverter):

    def __init__(self, dest_folder=None, overwrite=True):
        """Initialize the class and its super-class."""
        super().__init__(dest_folder=dest_folder, overwrite=overwrite)
        self.root_tag_string = "soup"
        self.unique_tags = dict()
##        if dest_folder == None:
##            self.dest_folder = "converted"
##        else:
##            self.dest_folder = dest_folder
        self.VERBOSE = False
        self.extension = ""


            
##    def convert_file(self, source_fp):
##        """Convert one file to OpenITI format.
##
##        Args:
##            source_fp (str): path to the file that must be converted.
##
##        Returns:
##            None
##        """
##        if self.VERBOSE:
##            print("converting", source_fp)
##        dest_fp = self.make_dest_fp(source_fp)
##        metadata = self.get_metadata(source_fp)
##
##        text = self.get_data(source_fp)
##        #print(1, text)
##        text = self.pre_process(text)
##        #print(2, text)
##
##        text = self.add_page_numbers(text, source_fp)
##        
##        text, notes = self.remove_notes(text)
##        #print(5, text)
##        
##        text = self.convert_html2md(text)
##        #text = self.add_structural_annotations(text)
##        #print(4, text)
##        text = self.reflow(text)
##        #print(6, text)
##        #text = self.add_milestones(text)
##        #print(7, text)
##
##        text = self.post_process(text)
##        #print(8, text)
##
##        text = self.compose(metadata, text, notes)
##        #print(9, text)
##        
##
##        self.save_file(text, dest_fp)
##        #print("saved text to", dest_fp)

    def post_process(self, text):
        # replace html entities:
        text = text.replace("&nbsp;", " ") # otherwise it will be replaced with \xa0
        text = html.unescape(text)

        text = super().post_process(text)

        return text


    #def convert_html2md(self, html):
    def add_structural_annotations(self, text):
        """Convert the html to mARkdown text.

        *** USING A GENERIC HTML TO MARKDOWN CONVERTER HERE.
        OVERWRITE THIS FUNCTION IN THE SUB-CLASS
        TO CONVERT THE LIBRARY'S SPECIFIC HTML FLAVOUR TO MARKDOWN ***
        """
        text = html2md.markdownify(text)
        return text

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



    def inspect_tags_in_html(self, html_str,
                             header_tag="",
                             only_tag_names=True,
                             strip_attr=["id", "href"],
                             print_tags=True):
        """Extracts a set of all tags used in an html string html_str.

        Args:
            html_str (str): a string in html format. Does not need to be well-formed.
            header_tag (str): the name of the tag that includes the header (e.g., "header");
                if defined, the tags within the header tag will not be taken into account.
                Defaults to an empty string (=> all tags in the file will be extracted)
            only_tag_names (bool): if set to True, only the tag names will be extracted,
                not the tag attributes. If set to False, the full tags including their
                attributes will be extracted. Defaults to True.
            strip_attr (list): the tag attributes in the strip_attr list will be
                stripped of their values.
                By default, the values of the "id" and "href" attributes will be stripped.
            print_tags(bool): if set to True, all single tags used in the folder will be printed.

        Returns:
            tags (set): a set of all tags that comply with the user's parameters.
        """
        if header_tag:
            header_tag = re.sub("\W", "", header_tag)
            html_str = re.sub(".+</{}>".format(header_tag), "", html_str,
                          count=1, flags=re.DOTALL)        
        if only_tag_names:
            tags = set(re.findall("<[^/][^ >]+", html_str))
        else:
            tags = set(re.findall("<[^/][^>]*>", html_str))

        if strip_attr and not only_tag_names:
            regex = '({})="[^"]+"'.format("|".join(strip_attr))
            stripped_tags = [re.sub(regex, r'\1=""', tag) for tag in tags]
            tags = set(stripped_tags)

        if print_tags:
            print("list of tags:")
            for tag in sorted(tags):
                print("    ", tag)
        return tags


    def inspect_tags_in_folder(self, folder,
                               extensions=[],
                               exclude_extensions=[],
                               header_tag="",
                               only_tag_names=True,
                               strip_attr=["id", "href"],
                               print_tags=True,
                               within_tag=None):
        """Extracts a set of all tags used in the texts in a folder.

        Args:
            folder (str): path to the folder from which the tags must be extracted.
            extensions (list): if defined, tags will be extracted
                only from files with one of these extensions.
                Defaults to an empty list (=> tags will be extracted from all files)
            exclude_extensions (list): if defined (and no extensions list is defined),
                tags will be extracted only from files without one of these extensions
                Defaults to an empty list (=> tags will be extracted from all files)
            header_tag (str): the name of the tag that includes the header (e.g., "header");
                if defined, the tags within the header tag will not be taken into account.
                Defaults to an empty string (=> all tags in the file will be extracted)
            only_tag_names (bool): if set to True, only the tag names will be extracted,
                not the tag attributes. If set to False, the full tags including their
                attributes will be extracted. Defaults to True.
            strip_attr (list): the tag attributes in the strip_attr list will be
                stripped of their values.
                By default, the values of the "id" and "href" attributes will be stripped.
            print_tags(bool): if set to True, all single tags used in the folder will be printed.

        Returns:
            tags (set): a set of all tags that comply with the user's parameters.
        """
        tags = set()
        fp_list = self.filter_files_in_folder(folder, extensions,
                                               exclude_extensions)
        for fp in fp_list: 
            print(fp)
            with open(fp, mode="r", encoding="utf-8") as file:
                text = file.read()
                if within_tag:
                    soup = BeautifulSoup(text)
                    text = soup.find(within_tag[0], attrs=within_tag[1]).prettify()
            fp_tags = self.inspect_tags_in_html(text, header_tag, only_tag_names, strip_attr,
                                                print_tags=False)
            tags = tags.union(fp_tags)

        if print_tags:
            print("list of tags:")
            for tag in sorted(tags):
                print("    ", tag)
        return tags

    def find_example_of_tag(self, folder, tag_name, attr={}, n=5, incl_parent=False,
                            extensions=[], exclude_extensions=[]):
        """Find an example of a specific tag from a file in the folder \
        with the required extension

        Args:
            folder (str): the path to the folder in which the files reside
            tag_name (str): the name of the tag for which an example is desired
            attr (dictionary): attribute of the tag for which an example is desired
                (key: attribute_name, value: attribute_value).
                E.g., {"class": "footnote"}
            n (int): number of examples wished
            incl_parent (bool): if True, the parent and siblings of the desired tag
                will be included.
            extensions (list): if defined, tags will be extracted
                only from files with one of these extensions.
                Defaults to an empty list (=> tags will be extracted from all files)
            exclude_extensions (list): if defined (and no extensions list is defined),
                tags will be extracted only from files without one of these extensions
                Defaults to an empty list (=> tags will be extracted from all files)
        """
        
        fp_list = self.filter_files_in_folder(folder, extensions=extensions,
                                              exclude_extensions=exclude_extensions)
        tags = []
        for fp in fp_list:
            with open(fp, mode="r", encoding="utf-8") as file:
                text = file.read()
            soup = BeautifulSoup(text)
            if attr:
                text_tags = soup.find_all(tag_name, attrs=attr)
            else:
                text_tags = soup.find_all(tag_name)
            if text_tags:
                print(fp)
            tags += text_tags
            if len(tags) >= n:
                break

        for t in tags[:n]:
            if incl_parent:
                t = t.parent
            print(t.prettify())
            print()
        return text_tags[:n]
        

if __name__ == "__main__":
    import doctest
    #doctest.testmod()
    #print("Passed all tests.")

    conv = GenericHtmlConverter()
    folder = r"G:\London\OpenITI\new\Rafed\test"
##    conv.inspect_tags_in_folder(folder,
##                                extensions=["html"],
##                                only_tag_names=False,
##                                strip_attr=["name", "href", "title"],
##                                print_tags=True,
##                                within_tag=("div", {"id": "content1"}))

    conv.find_example_of_tag(folder, "p", attr={"class", "rfdCenterBold2"},
                             n=15, incl_parent=True, extensions=["html"])
    
##    conv.convert_files_in_folder(folder)



