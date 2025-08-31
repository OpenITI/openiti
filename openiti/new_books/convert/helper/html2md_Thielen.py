"""Convert GRAR library html to OpenITI mARkdown.

This script subclasses the generic MarkdownConverter class
from the html2md module (based on python-markdownify,
https://github.com/matthewwithanm/python-markdownify),
which uses BeautifulSoup to create a flexible converter.
The subclass in this module, GRARHtmlConverter,
adds methods specifically for the conversion of books from
the GRAR library to OpenITI mARkdown:

* span conversion: the GRAR html seems to be a conversion of tei xml;
    the tei data is often embedded inside the id of a span.

Inheritance schema of the ThielenHtmlConverter:

======================== ==========================
MarkdownConverter        ThielenHtmlConverter
======================== ==========================
Options                  (inherited)
DefaultOptions           (inherited)
__init__                 (inherited)
__getattr__              (inherited)
convert                  (inherited)
process_tag              (inherited)
process_text             (inherited)
fill_out_columns         (inherited)
post_process_md          post_process_md (appended)
should_convert_tag       (inherited)
indent                   (inherited)
underline                (inherited)
create_underline_line    (inherited)
convert_a                (inherited)
convert_b                (inherited)
convert_blockquote       convert_blockquote
convert_br               (inherited)
convert_em               (inherited)
convert_hn               (inherited)
convert_i                (inherited)
convert_img              (inherited)
convert_list             (inherited)
convert_li               (inherited)
convert_ol               (inherited)
convert_p                (inherited)
convert_table            (inherited)
convert_tr               (inherited)
convert_ul               (inherited)
convert_strong           (inherited)
                         convert_span
======================== ==========================

"""
import re

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(path.dirname(root_folder)))
    sys.path.append(root_folder)

from openiti.new_books.convert.helper import html2md
from openiti.new_books.convert.helper.html2md import *  # import all constants!


class ThielenHtmlConverter(html2md.MarkdownConverter):
    """Convert GRAR library html to OpenITI mARkdown."""

##    def __init__(self, **options):
##        super().__init__(**options)
##        self.class_dict = dict()
##        self.class_dict["linebreak"] = '\n'

    def post_process_md(self, text):
        """Appends to the MarkdownConverter.post_process_md() method."""
        # remove blank lines marked with "DELETE_PREVIOUS_BLANKLINES" tag
        text = re.sub("\n*(PageV\d+P\d+) *@QUOTE@", r"\n\n\1\n\n# ", text)
        text = re.sub("[\r\n]@QUOTE@", "\n#", text)
        text = re.sub("@QUOTE@", "", text)
        text = re.sub(" *\n~~ *\n", "\n", text)
        text = super().post_process_md(text)
        return text

    def convert_blockquote(self, el, text):
        """Convert blockquote tags to mARkdown

        NB: the @QUOTE@ tag is a temporary tag that will be removed
        in the post-processing step.
        
        Examples:
            >>> import html2md_GRAR
            >>> h = 'abc <blockquote>def</blockquote> ghi'
            >>> html2md_GRAR.markdownify(h)
            'abc def ghi'

            >>> h = 'abc <span id="pb-21"/><blockquote>def</blockquote> ghi jkl'
            >>> html2md_GRAR.markdownify(h)
            'abc\\n\\nPageV00P020\\n\\n# def ghi jkl'


        """
        return "@QUOTE@"+text

    def convert_page(self, el, text):
        """Convert page tags"""
        return " "+text+" "

    def convert_head(self, el, text):
        """Convert <head> tags"""
        if "rendition" in el.attrs:
            try:
                n = int(el["rendition"][-1])
            except:
                n = 1
            return "\n### {} {}\n".format("|" * n, text or "")
        else:
            return "\n### ||| "

    def convert_lb(self, el, text):
        return "\n~~"
    
    def convert_span(self, el, text):
        """Converts html <span> tags, depending on their id attribute.

        Example:
            >>> import html2md_GRAR
            >>> h = 'abc <span>def</span> ghi'
            >>> html2md_GRAR.markdownify(h)
            'abc def ghi'

            >>> h = 'abc <span class="unknown_span_class">def</span> ghi'
            >>> html2md_GRAR.markdownify(h)
            'abc def ghi'

            Page numbers (NB: mARkdown uses page end instead of page beginning)

            >>> h = 'abc <span id="pb-21"/>def  ghi jkl'
            >>> html2md_GRAR.markdownify(h)
            'abc PageV00P020 def ghi jkl'

            Sections: 

            >>> h = 'abc <span class="book" id="part-2 div1-2"/>def  ghi jkl'
            >>> html2md_GRAR.markdownify(h)
            'abc\\n\\n### | [book 2]\\n\\ndef ghi jkl'

            >>> h = 'abc <span class="chapter" id="part-2 div2-1"/>def  ghi jkl'
            >>> html2md_GRAR.markdownify(h)
            'abc\\n\\n### || [chapter 1]\\n\\ndef ghi jkl'

            >>> h = 'abc <span class="chapter" id="part-2 div2-1" title="Intro"/>def  ghi jkl'
            >>> html2md_GRAR.markdownify(h)
            'abc\\n\\n### || [chapter 1: Intro]\\n\\ndef ghi jkl'

        """
        try:
            if "pb" in el["id"]:
                #print(el["id"])
                page_no = re.findall("\d+", el["id"])[-1]
                #print(page_no)
                page_no = int(page_no) - 1
                return "PageV00P{:03d} ".format(page_no)
            elif "div"  in el["id"]:
                no = int(re.findall("div(1|2)", el["id"])[0])
                #print("div1 or div2?", no)
                div_no = re.findall("\d+", el["id"])[-1]
                #print("div no:", div_no)
                try:
                    return "\n\n### {} [{} {}: {}]\n\n".format(\
                        "|"*no, el["class"][0], div_no, el["title"])
                except:
                    #print("\n\n### {} [{} {}]\n\n".format(\
                    #    "|"*no, el["class"][0], div_no))
                    return "\n\n### {} [{} {}]\n\n".format(\
                        "|"*no, el["class"][0], div_no)
        except Exception as e:
            #print(e)
            #input()
            pass
        try:
            if el["title"] == "linebreak":
                return "\n~~"
        except:
            pass
        return text


def markdownify(html, **options):
    """Shortcut to the convert method of the HindawiConverter class."""
    return ThielenHtmlConverter(**options).convert(html)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
