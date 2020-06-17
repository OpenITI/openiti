"""Convert Noorlib library html to OpenITI mARkdown.

This script subclasses the generic MarkdownConverter class
from the html2md module (based on python-markdownify,
https://github.com/matthewwithanm/python-markdownify),
which uses BeautifulSoup to create a flexible converter.

The subclass in this module, NoorlibHtmlConverter,
adds methods specifically for the conversion of books from
the eShia library to OpenITI mARkdown:

* Span, div and p conversion: span, div and p classes needed to be converted
    are defined in self.class_dict.


Inheritance schema of the NoorlibHtmlConverter:

======================== ==========================
MarkdownConverter        NoorlibHtmlConverter
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
convert_p                convert_p
convert_table            (inherited)
convert_tr               (inherited)
convert_ul               (inherited)
convert_strong           (inherited)
                         convert_span
                         convert_div
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


class NoorlibHtmlConverter(html2md.MarkdownConverter):
    """Convert Noorlib library html to OpenITI mARkdown.

    Examples:
        >>> import html2md_noorlib
        >>> h = '<img class="libimages" src="/images/books/86596/01/cover.jpg">'
        >>> html2md_noorlib.markdownify(h)
        '![](img/86596/01/cover.jpg)'

        >>> import html2md_noorlib
        >>> h = 'abc <a href="www.example.com">def</a> ghi'
        >>> html2md_noorlib.markdownify(h)
        'abc def ghi'
    """

    def __init__(self, **options):
        super().__init__(**options)
        self.class_dict = dict()
        self.class_dict["rightpome"] = "\n# {} %~% "              # <span class>
        self.class_dict["leftpome"] = "{}\n"                      # <span class>
        self.class_dict["footnote"] = "{}\n"                      # <div class>
##        ##old:
##        self.class_dict["Titr3"] = "\n\n### ||| {}\n\n"         # <span class>
##        self.class_dict["KalamateKhas2"] = "\n\n### || {}\n\n"  # <p class>
##        self.class_dict["KalamateKhas"] = "\n\n### ||| {}\n\n"  # <p class>
##        self.class_dict["TextsStyles3"] = "\n\n### ||| {}\n\n"  # <p class>
##        self.class_dict["TextsStyles1"] = "@QUR@ {}\n"          # <span class>
##        self.class_dict["Aye"] = "@QUR@ {}\n"                   # <span class>
##        self.class_dict["tdfehrest2"] = "\t{}"                  # <td class>
##        self.class_dict["list3"] = "\t{}"                       # <div class>
##        self.class_dict["sher"] = "# {}\n"                      # <p class>
##        self.class_dict["#6C3934"] = "\n\n# {}\n\n"             # <span class>

        self.options["image_link_regex"] = "/?images/books"
##        self.options["image_folder"] = "img"
        self.options["strip"] = ["a", "img"]


    def convert_span(self, el, text):
        """Converts html <span> tags, depending on their class attribute.

        Supported span classes should be stored in self.class_dict
        (key: span class (str); value: formatting string)
        E.g., {"quran": "@QUR@ {}\\n"}

        Example:
            >>> import html2md_noorlib
            >>> h = 'abc <span>def</span> ghi'
            >>> html2md_noorlib.markdownify(h)
            'abc def ghi'

            >>> h = 'abc <span class="unknown_span_class">def</span> ghi'
            >>> html2md_noorlib.markdownify(h)
            'abc def ghi'

            #>>> h = 'abc <span class="Aya">def  ghi</span> jkl'
            #>>> html2md_noorlib.markdownify(h)
            #'abc @QUR02 def ghi jkl'

            # the @QUR@ example outputs are a result of post-processing;
            # the function itself will produce:
            # 'abc @QUR@ def ghi\\njkl'
            
            >>> h = '<span class="rightpome">abc def</span><span class="leftpome">ghi jkl</span>'
            >>> html2md_noorlib.markdownify(h)
            '\\n# abc def %~% ghi jkl'
        """
        try:  # will fail if el has no class attribute
            for c in el["class"]:
                #print(c)
                if c in self.class_dict:
                    return self.class_dict[c].format(text) if text else ''
                if c == "ayah":
                    try:
                        sura = el["surah"]
                    except:
                        sura = "0"
                    try:
                        aya = el["ayah"]
                    except:
                        aya = "0"
                    #print("@QUR{}.{}@ {}".format(sura, aya, text))
                    return "@QUR{}.{}@ {}\n".format(sura, aya, text)
        except Exception as e:
            pass
        return text


    def convert_div(self, el, text):
        """Converts html <div> tags, depending on their class attribute.

        Supported div classes should be stored in self.class_dict
        (key: div class (str); value: formatting string)

        Example:
            >>> import html2md_noorlib
            >>> h = 'abc <div>def</div> ghi'
            >>> html2md_noorlib.markdownify(h)
            'abc def ghi'

            >>> h = 'abc <div class="unknown_div_class">def</div> ghi'
            >>> html2md_noorlib.markdownify(h)
            'abc def ghi'

            >>> h = '<div class="ClssDivMeesage">Page Is Empty</div>'
            >>> html2md_noorlib.markdownify(h)
            ''
        """
        try:  # will fail if el has no class attribute
            for c in el["class"]:
                if c in self.class_dict:
                    return self.class_dict[c].format(text) if text else ''
                if c == "ClssDivMeesage":
                    return ""
        except Exception as e:
            pass
        return text

    def convert_p(self, el, text):
        """Converts <p> tags according to their class.

        Supported p classes should be stored in self.class_dict
        (key: span class (str); value: formatting string)
        E.g., {"quran": "@QUR@ {}\\n"}

        <p> tags without class attribute, or unsupported class,
        will be converted according to the markdown style
        as defined in the self.options["md_style"] value
        (from super().DefaultOptions)

        Examples:
            >>> import html2md_noorlib
            >>> h = "<p>abc</p>"
            >>> html2md_noorlib.markdownify(h)
            '\\n\\n# abc\\n\\n'

            >>> h = "<p>abc</p>"
            >>> html2md_noorlib.markdownify(h, md_style=ATX)
            '\\n\\nabc\\n\\n'

            >>> h = "<p></p>"
            >>> html2md_noorlib.markdownify(h, md_style=ATX)
            ''
        """
        if self.options['md_style'] == OPENITI:
            return '\n\n# %s\n\n' % text if text else ''
        else:
            return '\n\n%s\n\n' % text if text else ''

    def convert_sup(self, el, text):
        """Converts <sup> tags (used for footnote markers)."""
        return "({})".format(text.strip())
    


def markdownify(html, **options):
    """Shortcut to the convert method of the HindawiConverter class."""
    return NoorlibHtmlConverter(**options).convert(html)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
