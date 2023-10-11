"""Convert LAL library html to OpenITI mARkdown.

This script subclasses the generic MarkdownConverter class
from the html2md module (based on python-markdownify,
https://github.com/matthewwithanm/python-markdownify),
which uses BeautifulSoup to create a flexible converter.
The subclass in this module, LALHtmlConverter,
adds methods specifically for the conversion of books from
the LAL library to OpenITI mARkdown:

* span conversion: the LAL html seems to be a conversion of tei xml;
    the tei data is often embedded inside the id of a span.

Inheritance schema of the LALHtmlConverter:

======================== ==========================
MarkdownConverter        LALHtmlConverter
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
convert_p                convert_p
convert_table            (inherited)
convert_tr               (inherited)
convert_ul               (inherited)
convert_strong           (inherited)
                         convert_div
                         convert_opener
                         convert_closer
                         convert_cit
                         convert_l
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
from openiti.helper.quran import normalise_quran, special_letters_regex

class LALHtmlConverter(html2md.MarkdownConverter):
    """Convert LAL library html to OpenITI mARkdown."""

##    def __init__(self, **options):
##        super().__init__(**options)
##        self.class_dict = dict()
##        self.class_dict["linebreak"] = '\n'

    def convert(self, html):
        """Convert XML to markdown.

        NB: replaces the parent class's convert method because it uses an html parser rather than xml!

        # We want to take advantage of the html5 parsing, but we don't actually
        # want a full document. Therefore, we'll mark our fragment with an id,
        # create the document, and extract the element with the id.
        """

        html = wrapped % html
        #soup = BeautifulSoup(html, 'html.parser')
        soup = BeautifulSoup(html, 'xml')
        if 'strip' in self.options and self.options["strip"]:
            for tag in self.options["strip"]:
                [t.decompose() for t in soup.find_all(tag)]
        text = self.process_tag(soup.find(id=FRAGMENT_ID), children_only=True)

##        # post-processing: remove unneeded blank lines and spaces:
##
##        # remove leading and trailing spaces in lines:
##        text = re.sub(r" *(\n+) *", r"\1", text)
##        # remove unwanted additional spaces and lines:
##        text = re.sub(r"\n{3,}", r"\n\n", text)
##        text = re.sub(r" +", r" ", text)
##        # remove blank lines marked with "DELETE_PREVIOUS_BLANKLINES" tag
##        text = re.sub(r"\n+DELETE_PREVIOUS_BLANKLINES", "", text)
##        # replace placeholders for spaces in tables:
##        text = re.sub("ç", " ", text)
##        return text
        return self.post_process_md(text)

    def convert_div(self, el, text):
        """Convert div tags (structural markup)"""
        # def alpha2num(s):
        #     """Convert alphabetical part of an ID to numerical"""
        #     # this approach doesn't work for things like 1.b.2!
        #     alpha = re.findall("[a-zA-Z]+$", s) 
        #     # no conversion needed if the ID does not contain letters:
        #     if not alpha:
        #         return s
        #     # calculate the numerical value of an alphabetic string (a=1, aa=27, ...)
        #     alphabet = "abcdefghijklmnopqrstuvwxyz"
        #     num = [alphabet.index(c.lower())+1 for c in alpha[0]]
        #     sum_num = 0
        #     for i,n in enumerate(num[::-1]):
        #         sum_num += (26**i)*n
        #     return s[:-len(alpha[0])] + str(sum_num)

        def alpha2num(s):
            """Convert alphabetical part of an ID to numerical"""
            alpha = re.findall("[a-zA-Z]", s) 
            # no conversion needed if the ID does not contain letters:
            if not alpha:
                return s
            # calculate the numerical value of an alphabetic string (a=1, aa=27, ...)
            alphabet = "abcdefghijklmnopqrstuvwxyz"
            num_s = []
            for el in s.split("."):
                if re.findall("[a-zA-Z]", el):
                    num = [alphabet.index(c.lower())+1 for c in el]
                    sum_num = 0
                    for i,n in enumerate(num[::-1]):
                        sum_num += (26**i)*n
                    num_s.append(str(sum_num))
                else:
                    num_s.append(el)
            return ".".join(num_s)

        if "type" in el.attrs and "prelim" in el["type"]:
            return "\n### |PARATEXT|" + text
        
        # use xml:id (e.g., xml:id="ARA.section.4.1.2") to get the section number
        xml_id = el["xml:id"]
        xml_id = re.sub("\.(\d+)([a-zA-Z]+)$", r".\1.\2", xml_id)            
        #n = ".".join(xml_id.split(".")[2:])
        # convert the alphabetical parts of a section ID (e.g. 4.1.b) to numbers (e.g., 4.1.2)
        #n = re.findall("(?:\d+\.)*[\da-zA-Z]+$", xml_id)[0] # this approach does not work for things like 4.b.2...
        try:
            n = ".".join(xml_id.split(".")[2:])
            n = alpha2num(n)
        except Exception as e:
            print(xml_id, e)
            n = ""
        # calculate the hierarchical level of the header (that is, the number of pipes in the ### |+ tag)
        level = len(n.split("."))
        header = ""
        for i, c in enumerate(el.findChildren()):
            if c.name == "head":
                header += " " + c.text.strip()
            elif c.name in ("div", "p") or i > 4:
                break

        if "type" in el.attrs and el["type"] != "section":
            #return "\n### {} {}{}".format(level*"|", header, text)
            #return "\n### {} {}{}{}".format(level*"|", n.split(".")[-1], header, text)
            #return "\n### {} {}{}{}".format(level*"|", n, header, text)
            if header:
                header_regex = re.sub("\s+", r"\\s*", header)
                text = re.sub(header_regex, "", text, count=1)
                return "\n### {} {} {}\n{}".format(level*"|", n, header, text)
            return "\n### {} {} {}".format(level*"|", n, text)
        else:
            return "\n[{}]{}".format(n, text)
        
    def convert_l(self, el, text):
        """Convert poetry line tags"""
        # caesuras are dealt with in preprocessing
        #for caesura in tag.find_all("caesura"):
        #    caesura.replace_with(" %~% ")
        #line = "\n# " + tag.text.strip()
        line = "\n# " + text
        if not " %~% " in line:
            line += " %~%"
        return line

    def convert_opener(self, el, text):
        """Convert opener tag (paratext)"""
        #return "\n### |PARATEXT|\n# " + tag.text.strip()
        #return "\n### |PARATEXT|\n# " + text
        return "\n# " + text  # most often, not really paratext.

    def convert_closer(self, el, text):
        """Convert closer tag (paratext)"""
        #return "\n### |PARATEXT|\n# " + tag.text.strip()
        if "rend" in el.attrs and "ornament" in el["rend"]:
            return "\n" + text
            
        return "\n### |PARATEXT|\n# " + text

    def convert_cit(self, el, text):
        """Convert cit tag (for Qur'an citations)"""
        quote = []
        for q in el.find_all("quote"):
            quote.append(q.text.strip())
        quote = " * ".join(quote)
        quote = normalise_quran(quote, post_process=True)
        qid = []
        try:    
            for pointer in el.find_all("ptr"):
                qid.append(re.sub("Q\W*", "", pointer["cref"]))
        except Exception as e:
            pass
        if qid:
            #return " @QB@{}@ {} @QE@{}@ ".format(qid, el.quote.text.strip(), qid)
            qid = "_".join(qid)
            return " @QUR_{}@ {}\n".format(qid, quote)
        #return " @QB@ {} @QE@ ".format(el.quote.text.strip())
        return " @QUR@ {}\n".format(quote)

    def convert_item(self, el, text):
        """Convert list items"""
        return "\n# * " + text

    def convert_p(self, el, text):
        """Convert p tags (paragraphs)"""
        if "n" in el.attrs:
            return "\n# " + el["n"] + " " + text
        if "rend" in el.attrs:
            if "isnad" in el["rend"]:
                #return "\n# @ISNAD@ "+tag.text.strip()
                return "\n# _ISNAD_ " + text
            elif "answer" in el["rend"]:
                pass
            elif "question" in el["rend"]:
                pass
            elif "bismillah" in el["rend"]:
                pass
            elif "no_indent"in el["rend"]:
                pass
            elif "tafsir" in el["rend"]:
                pass
            
        #return "\n# "+tag.text.strip()
        return "\n# " + text

    def post_process_md(self, text):
        """Appends to the MarkdownConverter.post_process_md() method."""
        text = re.sub(" *\n~~ *\n", "\n", text)
        text = re.sub("(### \|PARATEXT\|(?:\n# .+)+)\n### \|PARATEXT\|", r"\1", text)
        text = super().post_process_md(text)
        text = re.sub("@QUR_", "@QUR@", text)
        # fix duplicate headings:
        text = re.sub(r"(### \|+ [\w.]+) ?[\r\n]+\1", r"\1", text) # number only first
        text = re.sub(r"(### \|+ [\w.]+)( .+)[\r\n]+\1 ?[\r\n]+", r"\1\2\n", text) # header first
        
        return text


def markdownify(html, **options):
    """Shortcut to the convert method of the HindawiConverter class."""
    return LALHtmlConverter(**options).convert(html)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
