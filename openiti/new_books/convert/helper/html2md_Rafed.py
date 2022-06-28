"""Convert Rafed library html to OpenITI mARkdown.

This script subclasses the generic MarkdownConverter class
from the html2md module (based on python-markdownify,
https://github.com/matthewwithanm/python-markdownify),
which uses BeautifulSoup to create a flexible converter.

The subclass in this module, RafedHtmlConverter,
adds methods specifically for the conversion of books from
the eShia library to OpenITI mARkdown:

* Span, div and p conversion: span, div and p classes needed to be converted
    are defined in self.class_dict.


Inheritance schema of the RafedHtmlConverter:

======================== ==========================
MarkdownConverter        RafedHtmlConverter
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
convert_tr               convert_tr
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


class RafedHtmlConverter(html2md.MarkdownConverter):
    """Convert Rafed library html to OpenITI mARkdown.

    Examples:
        >>> import html2md_Rafed
        >>> h = '<img class="libimages" src="/images/books/86596/01/cover.jpg">'
        >>> html2md_Rafed.markdownify(h)
        '![](img/86596/01/cover.jpg)'

        >>> import html2md_Rafed
        >>> h = 'abc <a href="www.example.com">def</a> ghi'
        >>> html2md_Rafed.markdownify(h)
        'abc def ghi'
    """

    def __init__(self, **options):
        super().__init__(**options)
        self.class_dict = dict()
        self.class_dict["rfdAie"] = "@QUR@ {}\n"                  # <span class> / <p class> 
        self.class_dict["footnote"] = "{}\n"                      # <div class>
        self.class_dict["Heading1Center"] = "\n### | {}\n"        # <p class>
        self.class_dict["Heading2Center"] = "\n### || {}\n"       # <p class>
        self.class_dict["Heading3Center"] = "\n### ||| {}\n"      # <p class>
        self.class_dict["Heading4Center"] = "\n### |||| {}\n"     # <p class>
        self.class_dict["Heading5Center"] = "\n### ||||| {}\n"    # <p class>
        self.class_dict["rfdCenterBold1"] = "\n### ||| * {}\n"    # <p class>
        self.class_dict["rfdCenterBold2"] = "\n### |||| * {}\n"   # <p class>
        self.class_dict["rfdBold1"] = "\n### ||| ** {}\n"         # <p class>
        self.class_dict["rfdBold2"] = "\n### |||| ** {}\n"        # <p class>
        self.options["image_link_regex"] = "Books"
        self.options["image_folder"] = "https://books.rafed.net/Books"
        #self.options["strip"] = ["a", "img"]
        self.options["strip"] = ["a"]

    def convert_span(self, el, text):
        """Converts html <span> tags, depending on their class attribute.

        Supported span classes should be stored in self.class_dict
        (key: span class (str); value: formatting string)
        E.g., {"quran": "@QUR@ {}\\n"}

        Example:
            >>> import html2md_Rafed
            >>> h = 'abc <span>def</span> ghi'
            >>> html2md_Rafed.markdownify(h)
            'abc def ghi'

            >>> h = 'abc <span class="unknown_span_class">def</span> ghi'
            >>> html2md_Rafed.markdownify(h)
            'abc def ghi'

            #>>> h = 'abc <span class="Aya">def  ghi</span> jkl'
            #>>> html2md_Rafed.markdownify(h)
            #'abc @QUR02 def ghi jkl'

            # the @QUR@ example outputs are a result of post-processing;
            # the function itself will produce:
            # 'abc @QUR@ def ghi\\njkl'
            
            >>> h = '<span class="rightpome">abc def</span><span class="leftpome">ghi jkl</span>'
            >>> html2md_Rafed.markdownify(h)
            '\\n# abc def %~% ghi jkl'
        """
        try:  # will fail if el has no class attribute
            for c in el["class"]:
                #print(c)
                if c in self.class_dict:
                    return self.class_dict[c].format(text) if text else ''
##                elif c == "rfdAlaem":
##                    # remove zero-width non joiner
##                    #(this doesn't work since the text has been normalized by this point):
##                    zwnj = "‌"
##                    text = re.sub(zwnj, " ", text)
##                    return text

        except Exception as e:
            pass
        return text


    def convert_div(self, el, text):
        """Converts html <div> tags, depending on their class attribute.

        Supported div classes should be stored in self.class_dict
        (key: div class (str); value: formatting string)

        Example:
            >>> import html2md_Rafed
            >>> h = 'abc <div>def</div> ghi'
            >>> html2md_Rafed.markdownify(h)
            'abc def ghi'

            >>> h = 'abc <div class="unknown_div_class">def</div> ghi'
            >>> html2md_Rafed.markdownify(h)
            'abc def ghi'

            >>> h = '<div class="ClssDivMeesage">Page Is Empty</div>'
            >>> html2md_Rafed.markdownify(h)
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
            >>> import html2md_Rafed
            >>> h = "<p>abc</p>"
            >>> html2md_Rafed.markdownify(h)
            '\\n\\n# abc\\n\\n'

            >>> h = "<p>abc</p>"
            >>> html2md_Rafed.markdownify(h, md_style=ATX)
            '\\n\\nabc\\n\\n'

            >>> h = "<p></p>"
            >>> html2md_Rafed.markdownify(h, md_style=ATX)
            ''
        """
        try:  # will fail if el has no class attribute
            for c in el["class"]:
                #print(c)
                if c in self.class_dict:
                    return self.class_dict[c].format(text) if text else ''

        except Exception as e:
            pass
        if self.options['md_style'] == OPENITI:
            return '\n\n# %s\n\n' % text if text else ''
        else:
            return '\n\n%s\n\n' % text if text else ''

    def convert_sup(self, el, text):
        """Converts <sup> tags (used for footnote markers)."""
        return "({})".format(text.strip())

    def convert_table(self, el, text):
        """Wrap tables between double new lines.

        NB: conversion of the tables takes place on the tr level."""
        #print("CONVERTING TABLE")
        if el.find_all("p", class_="rfdPoem"):
            return text
        return '\n\n' + text + '\n\n'

    def convert_tr(self, el, text):
        """Convert table rows.

        NB: rows are processed before the table tag is.
        Spaces to fill out columns are added in post-processing!

        Examples:
            >>> import html2md_Rafed
            >>> h = '\
            <table>\
              <tr>\
                <th>th1aaa</th><th>th2</th>\
              </tr>\
              <tr>\
                <td>td1</td><td>td2</td>\
              </tr>\
            </table>'
            >>> html2md.markdownify(h)
            '\\n\\n| th1aaa | th2 |\\n| ------ | --- |\\n| td1    | td2 |\\n\\n'

            i.e.:
                | th1aaa | th2 |
                | td1    | td2 |

            >>> import html2md_Rafed
            >>> h = '\
            <table>\
              <tr>\
                <td>\
                    <p class="rfdPoem">hemistych1</p>\
                </td>\
                <td>\
                    <p class="rfdPoem">::after</p>\
                </td>\
                <td>\
                    <p class="rfdPoem">hemistych2</p>\
                </td>\
              </tr>\
            </table>'



        """
        # poetry stored in table format:
        poetry = el.find_all("p", class_="rfdPoem")
        if poetry:
            t = [p.text.strip() for p in poetry if p.text.strip()]
            t = [re.sub("[\r\n ]+", " ", el) for el in t]
            return " %~% ".join(t) + "\n"
                
        # other tables:
        t = []
        if el.find('th'): # headers:
            for th in el.find_all('th'):
                #t.append(wrap_cell_text(th.text))
                t.append(th.text)
            t = "|".join(t)
            return '|{}|\n|{}|\n'.format(t, self.create_underline_line(t, '-'))
        else:
            for td in el.find_all('td'):
                #t.append(wrap_cell_text(td.text))
                t.append(td.get_text(" ", strip=True))
            return '|{}|\n'.format("|".join(t))


def markdownify(html, **options):
    """Shortcut to the convert method of the HindawiConverter class."""
    return RafedHtmlConverter(**options).convert(html)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
