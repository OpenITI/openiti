"""Convert Wuerzburg Latin-Arabic library html to OpenITI mARkdown.

This script subclasses the generic MarkdownConverter class
from the html2md module (based on python-markdownify,
https://github.com/matthewwithanm/python-markdownify),
which uses BeautifulSoup to create a flexible converter.
The subclass in this module, GRARHtmlConverter,
adds methods specifically for the conversion of books from
the GRAR library to OpenITI mARkdown:

* span conversion: the GRAR html seems to be a conversion of tei xml;
    the tei data is often embedded inside the id of a span.

Inheritance schema of the GRARHtmlConverter:

======================== ==========================
MarkdownConverter        WuerzburgHtmlConverter
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
                         convert_span
                         convert_head
                         convert_lb
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


class WuerzburgHtmlConverter(html2md.MarkdownConverter):
    """Convert GRAR library html to OpenITI mARkdown."""

##    def __init__(self, **options):
##        super().__init__(**options)
##        self.class_dict = dict()
##        self.class_dict["linebreak"] = '\n'


    def convert_page(self, el, text):
        """Convert page tags"""
        return " "+text+" "

    def convert_head(self, el, text):
        """Convert <head> tags"""
        return "\n### | {}\n".format(el.get_text(" ", strip=True))

    def convert_lb(self, el, text):
        return "\n~~"


def markdownify(html, **options):
    """Shortcut to the convert method of the HindawiConverter class."""
    return WuerzburgHtmlConverter(**options).convert(html)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
