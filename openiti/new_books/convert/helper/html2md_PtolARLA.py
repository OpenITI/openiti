"""Convert GRAR library html to OpenITI mARkdown.

This script subclasses the generic MarkdownConverter class
from the html2md module (based on python-markdownify,
https://github.com/matthewwithanm/python-markdownify),
which uses BeautifulSoup to create a flexible converter.
The subclass in this module, PtolHtmlConverter,
adds methods specifically for the conversion of books from
the GRAR library to OpenITI mARkdown:

* span conversion: the GRAR html seems to be a conversion of tei xml;
    the tei data is often embedded inside the id of a span.

Inheritance schema of the PtolHtmlConverter:

======================== ==========================
MarkdownConverter        PtolHtmlConverter
======================== ==========================
Options                  (inherited)
DefaultOptions           (inherited)
__init__                 (inherited)
__getattr__              (inherited)
convert                  (inherited)
process_tag              (inherited)
process_text             (inherited)
fill_out_columns         (inherited)
post_process_md          (inherited)
should_convert_tag       (inherited)
indent                   (inherited)
underline                (inherited)
create_underline_line    (inherited)
convert_a                convert_a
convert_b                (inherited)
convert_blockquote       (inherited)
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
                         convert_editor
                         convert_small
                         convert_span
                         convert_u
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


class PtolHtmlConverter(html2md.MarkdownConverter):
    """Convert GRAR library html to OpenITI mARkdown."""

##    def __init__(self, **options):
##        super().__init__(**options)
##        self.class_dict = dict()
##        self.class_dict["linebreak"] = '\n'


    def convert_a(self, el, text):
        """Convert html links to markdown-style links.

        Example:
            >>> import html2md
            >>> h = '<a href="a/b/c">abc</a>'
            >>> html2md.markdownify(h)
            '[abc](a/b/c)'
        """
        class_ = el.attrs.get('class', None) or ''
        href = el.attrs.get('href', None) or ''
        title = el.attrs.get('title', None) or ''
        if "pagina" in class_:
            p, side = re.findall("(\d+)([vr]*)", el["id"])[0]
            print(el["id"], p, side)
            return "PageBegV00P{0:03d}{1}".format(int(p), side)
        if href.startswith(("#", "intus")):
            return text
        if self.options['autolinks'] and text == href and not title:
            # Shortcut syntax
            return '<%s>' % href
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ''
        return '[%s](%s%s)' % (text or '', href, title_part) if href else text or ''

    def convert_editor(self, el, text):
        return "### |EDITOR|\n%s\n### | \n\n" % text

    def convert_small(self, el, text):
        class_ =  el.get("class")
        if "note" in class_:
            return " (¬{}) ".format(el["data-sign"])
        else:
            return ""

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
        class_ = el.attrs.get('class', None) or ''
        id_ = el.attrs.get('id', None) or ''
        if class_ == "note":
            return ""
        elif "pagina" in class_:
            p, side = re.findall("(\d+)([vr]*)", id_)[0]
            print(id_, p, side)
            return "PageBegV00P{0:03d}{1}".format(int(p), side)
        return text

    def convert_u(self, el, text):
        #return ' @NUM@ %s\n' % text.strip() if text else ''
        return ' _NUM_ %s' % text.strip() if text else ''



def markdownify(html, **options):
    """Shortcut to the convert method of the HindawiConverter class."""
    return PtolHtmlConverter(**options).convert(html)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
