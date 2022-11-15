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


class LALHtmlConverter(html2md.MarkdownConverter):
    """Convert LAL library html to OpenITI mARkdown."""

##    def __init__(self, **options):
##        super().__init__(**options)
##        self.class_dict = dict()
##        self.class_dict["linebreak"] = '\n'

    def convert_div(self, el, text):
        """Convert div tags (structural markup)"""
        def alpha2num(s):
            alpha = re.findall("[a-zA-Z]+$", s)
            if not alpha:
                return s
            alphabet = "abcdefghijklmnopqrstuvwxyz"
            num = [alphabet.index(c.lower())+1 for c in alpha[0]]
            sum_num = 0
            for i,n in enumerate(num[::-1]):
                sum_num += (26**i)*n
            return s[:-len(alpha[0])] + str(sum_num)

        if "type" in el.attrs and "prelim" in el["type"]:
            return "\n### |PARATEXT|" + text
        
        try:
            n = el["n"]
        except:
            # use xml:id (e.g., xml:id="ARA.section.4.1.2") to get the section number
            xml_id = el["xml:id"]
            xml_id = re.sub("\.(\d+)([a-zA-Z]+)$", r".\1.\2", xml_id)            
            #n = ".".join(xml_id.split(".")[2:])
            n = re.findall("(?:\d\.)*[\da-zA-Z]+$", xml_id)[0]
        n = alpha2num(n)
        level = len(n.split("."))
        header = ""
        for i, c in enumerate(el.findChildren()):
            if c.name == "head":
                header += " " + c.text.strip()
            elif c.name in ("div", "p") or i > 4:
                break
        #if not header:
        #    return "\n[{}]{}".format(n, text)
        #else:
        if "type" in el.attrs and el["type"] != "section":
            #return "\n### {} {}{}{}".format(level*"|", n.split(".")[-1], header, text)
            return "\n### {} {}{}".format(level*"|", header, text)
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
        return " @QUR@ {} \n".format(quote)

    def convert_p(self, el, text):
        """Convert p tags (paragraphs)"""
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
