"""Convert TEI xml to Markdown.

This program contains a sub-class of html2md.MarkdownConverter,
which in turn is an adaptation of python-markdownify
(https://github.com/matthewwithanm/python-markdownify)
to output OpenITI mARkdown.

IMPORTANT: since TEI indicates page beginning (<pb/>)
and OpenITI mARkdown page numbers are at the bottom of a page,
page numbers should be pre-processed in a text
before feeding it to the markdownify function.
The tei2md.preprocess_page_numbers function can be used for this. 


You can use the tei2md.TeiConverter class as a base class
and subclass it to add methods, adapt the post-processing method etc.

E.g.:
    def Class GRAR_converter(tei2md.TeiConverter):   
        def post_process_md(self, text):
            text = super().post_process_md(text)
            # remove blank lines marked with "DELETE_PREVIOUS_BLANKLINES" tag
            text = re.sub(r"\n+DELETE_PREVIOUS_BLANKLINES", "", text)
            # replace placeholders for spaces in tables: 
            text = re.sub("ç", " ", text)
            return text

This table shows the methods and classes the TeiConverter
inherits from html2md.MarkdownConverter,
which methods it overwrites,
and which methods it adds: 

=========================== ==========================
html2md.MarkdownConverter   tei2md.TeiConverter
=========================== ==========================
class DefaultOptions        (inherited)
class Options               (inherited)
__init__                    (inherited)
convert                     convert
process_tag                 (inherited)
process_text                (inherited)
fill_out_columns            (inherited)
post_process_               (inherited)
__getattr__                 (inherited)
should_convert_tag          (inherited)
indent                      (inherited)
create_underline_line       (inherited)
underline                   (inherited)
convert_a                   (inherited)
convert_b                   (inherited)
convert_blockquote          (inherited)
convert_br                  (inherited)
convert_em                  (inherited)
convert_hn                  (inherited)
convert_i                   (inherited)
convert_img                 (inherited)
convert_list                (inherited)
convert_li                  (inherited)
convert_p                   (inherited)
convert_strong              (inherited)
convert_table               (inherited)
convert_tr                  (inherited)
                            convert_div1
                            convert_div2
                            convert_div3
                            convert_div
                            convert_head
                            convert_lg
                            find_heading_level (dummy)
=========================== ==========================


Examples (doctests):

    Specific tei-related tags: 

    >>> import tei2md
    >>> h = 'abc\
             <div1 type="book" n="0" name="Preface">def</div1>\
             ghi'
    >>> tei2md.markdownify(h)
    'abc\\n\\n### | [book 0: Preface]\\n\\ndef\\n\\nghi'

    >>> h = 'abc\
             <div2 type="section" n="1">def</div1>\
             ghi'
    >>> tei2md.markdownify(h)
    'abc\\n\\n### || [section 1]\\n\\ndef\\n\\nghi'

    >>> h = 'abc\
             <div3 type="Aphorism">def</div1>\
             ghi'
    >>> tei2md.markdownify(h)
    'abc\\n\\n### ||| [Aphorism]\\n\\ndef\\n\\nghi'

    Divs without type are stripped:
    
    >>> h = 'abc\
             <div>def</div>\
             ghi'
    >>> tei2md.markdownify(h)
    'abc def ghi'

    <head> tags are converted to level-3 mARkdown headers by default:

    >>> h = 'abc\
             <head>def</head>\
             ghi'
    >>> tei2md.markdownify(h)
    'abc\\n\\n### ||| def\\n\\nghi'

    >>> h = 'abc\
             <lb/>def\
             <lb/>ghi'
    >>> tei2md.markdownify(h)
    'abc\\ndef\\nghi'

    >>> h = '\
    abc\
    <lg>\
      <l>line1</l>\
      <l>line2</l>\
      <l>line3</l>\
      <l>line4</l>\
    </lg>\
    def'
    >>> tei2md.markdownify(h)
    ' abc\\n# line1\\n# line2\\n# line3\\n# line4\\n\\ndef'


    In addition to these TEI tags, the converter also inherits methods
    from html2md.MarkdownConverter that deal with more standard html tags: 

    Headings: h1

    >>> import tei2md
    >>> h = '<h1>abc</h1>'
    >>> tei2md.markdownify(h)
    '\\n\\n### | abc\\n\\n'

    NB: heading style is OpenITI mARkdown style by default,
        but can be set to other styles as well:

    >>> h = '<h1>abc</h1>'
    >>> tei2md.markdownify(h, md_style=UNDERLINED)
    '\\n\\nabc\\n===\\n\\n'

    >>> h = '<h1>abc</h1>'
    >>> tei2md.markdownify(h, md_style=ATX)
    '\\n\\n# abc\\n\\n'

    Paragraphs (<p>):
    
    >>> h = "<p>abc</p>"
    >>> tei2md.markdownify(h)
    '\\n\\n# abc\\n\\n'

    >>> h = "<p>abc</p>"
    >>> tei2md.markdownify(h, md_style=ATX)
    '\\n\\nabc\\n\\n'


    Divs without type are stripped:
    
    >>> h = 'abc\
             <div>def</div>\
             ghi'
    >>> tei2md.markdownify(h)
    'abc def ghi'



    Spans without class or with an unsupported class are stripped:
    
    >>> h = 'abc <span>def</span> ghi'
    >>> tei2md.markdownify(h)
    'abc def ghi'
    
    >>> h = 'abc <span class="unknown_span_class">def</span> ghi'
    >>> tei2md.markdownify(h)
    'abc def ghi'


    Links: 

    >>> h = '<a href="a/b/c">abc</a>'
    >>> tei2md.markdownify(h)
    '[abc](a/b/c)'

    
    Unordered lists: 

    >>> h = '<ul><li>item1</li><li>item2</li></ul>'
    >>> tei2md.markdownify(h)
    '\\n* item1\\n* item2\\n\\n'
    
    Ordered lists:

    >>> h = '<ol><li>item1</li><li>item2</li></ol>'
    >>> tei2md.markdownify(h)
    '\\n1. item1\\n2. item2\\n\\n'

    Nested lists:
    
    >>> h = '<ol><li>item1</li><li>item2:<ul><li>item3</li><li>item4</li></ul></li></ol>'
    >>> tei2md.markdownify(h)
    '\\n1. item1\\n2. item2:\\n\\n\\t* item3\\n\\t* item4\\n\\t\\n\\n'

    Italics (<i> and <em> tags):

    >>> h = 'abc <em>def</em> ghi'
    >>> tei2md.markdownify(h)
    'abc *def* ghi'

    >>> h = 'abc <i>def</i> ghi'
    >>> tei2md.markdownify(h)
    'abc *def* ghi'


    Bold (<b> and <strong> tags):

    >>> h = 'abc <b>def</b> ghi'
    >>> tei2md.markdownify(h)
    'abc **def** ghi'

    >>> h = 'abc <strong>def</strong> ghi'
    >>> tei2md.markdownify(h)
    'abc **def** ghi'

    Tables:
    
    >>> h = '\
    <table>\
      <tr>\
        <th>th1aaa</th><th>th2</th>\
      </tr>\
      <tr>\
        <td>td1</td><td>td2</td>\
      </tr>\
    </table>'
    >>> tei2md.markdownify(h)
    '\\n\\n| th1aaa | th2 |\\n| ------ | --- |\\n| td1    | td2 |\\n\\n'
            
    # i.e.,
    # | th1aaa | th2 |
    # | td1    | td2 |
"""

from bs4 import BeautifulSoup
import re
import six

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.new_books.convert import html2md
from openiti.new_books.convert.html2md import UNDERLINED, FRAGMENT_ID, ATX


class TeiConverter(html2md.MarkdownConverter):

    def convert(self, xml):
        """Convert xml to markdown.

        # We want to take advantage of the html5 parsing, but we don't actually
        # want a full document. Therefore, we'll mark our fragment with an id,
        # create the document, and extract the element with the id.
        """
        xml = html2md.wrapped % xml
        soup = BeautifulSoup(xml, "xml")
        #print(soup)
        text = self.process_tag(soup.find(id=FRAGMENT_ID), children_only=True)
        return self.post_process_md(text)

        

    #-----------------------------------------------------------

    # Additional conversion functions for specific tags (in alphabetic order):

    def convert_div1(self, el, text):
        """Converts tei xml <div1> tags to headings.

        Examples:
            >>> import tei2md
            >>> h = 'abc\
                     <div1 type="book" n="0" name="Preface">def</div1>\
                     ghi'
            >>> tei2md.markdownify(h)
            'abc\\n\\n### | [book 0: Preface]\\n\\ndef\\n\\nghi'
        """
        text = self.convert_div(el, text, n=1)
        return text

    def convert_div2(self, el, text):
        """Converts tei xml <div1> tags to headings.

        Examples:
            >>> import tei2md
            >>> h = 'abc\
                     <div2 type="book" n="0" name="Preface">def</div1>\
                     ghi'
            >>> tei2md.markdownify(h)
            'abc\\n\\n### || [book 0: Preface]\\n\\ndef\\n\\nghi'
        """
        text = self.convert_div(el, text, n=2)
        return text

    def convert_div3(self, el, text):
        """Converts tei xml <div1> tags to headings.

        Examples:
            >>> import tei2md
            >>> h = 'abc\
                     <div3 type="book" n="0" name="Preface">def</div1>\
                     ghi'
            >>> tei2md.markdownify(h)
            'abc\\n\\n### ||| [book 0: Preface]\\n\\ndef\\n\\nghi'
        """
        text = self.convert_div(el, text, n=3)
        return text

    def convert_div(self, el, text, n=None):
        """Converts tei xml <div> tags, depending on their type.
        
        Examples:
            >>> import tei2md
            >>> h = 'abc\
                     <div1 type="book" n="0" name="Preface">def</div1>\
                     ghi'
            >>> tei2md.markdownify(h)
            'abc\\n\\n### | [book 0: Preface]\\n\\ndef\\n\\nghi'

            >>> h = 'abc\
                     <div2 type="section" n="1">def</div1>\
                     ghi'
            >>> tei2md.markdownify(h)
            'abc\\n\\n### || [section 1]\\n\\ndef\\n\\nghi'

            >>> h = 'abc\
                     <div3 type="Aphorism">def</div1>\
                     ghi'
            >>> tei2md.markdownify(h)
            'abc\\n\\n### ||| [Aphorism]\\n\\ndef\\n\\nghi'

            Divs without type are stripped:
            
            >>> h = 'abc\
                     <div>def</div>\
                     ghi'
            >>> tei2md.markdownify(h)
            'abc def ghi'
        """
        if n == None:
            return text
            
        tag = "### " + "|"*n
        details ={"type": "", "n": "", "name": ""}
        for d in details:
            try:
                details[d] = el[d]
            except:
                pass
        title = "{} {}: {}".format(details["type"], details["n"], details["name"])
        title = re.sub("  |: $", " ", title).strip()
        return "\n\n{} [{}]\n\n{}\n\n".format(tag, title, text)

    def find_heading_level(self, el, text, level=None):
            return
        
    def convert_head(self, el, text, level=None):
        """Convert <head> tags to OpenITI mARkdown headings.

        NB: no general rule was found to define the heading level
        of the head tags. A default heading level of 3 has been assigned.
        For specific tei texts, a find_heading_level method
        could be defined to specify the heading level.        

        Examples:
            >>> import tei2md
            >>> h = 'abc\
                     <head>def</head>\
                     ghi'
            >>> tei2md.markdownify(h)
            'abc\\n\\n### ||| def\\n\\nghi'
        """
        if level == None:
            level = self.find_heading_level(el, text)
        if level == None:
            return "\n\n### ||| {}\n\n".format(text)
        else:
            return "\n\n### {} {}\n\n".format("|"*level, text)

    def convert_lb(self, el, text):
        """Convert tei <lb/> (line beginning) tags to newlines.

        Examples:
            >>> import tei2md
            >>> h = 'abc\
                     <lb/>def\
                     <lb/>ghi'
            >>> tei2md.markdownify(h)
            'abc\\ndef\\nghi'
        """
        return '\n~~'

    def convert_lg(self, el, text):
        """Convert TEI line groups (<lg>), which contain <l> elements.

        Examples:
            >>> import tei2md
            >>> h = '\
            abc\
            <lg>\
              <l>line1</l>\
              <l>line2</l>\
              <l>line3</l>\
              <l>line4</l>\
            </lg>\
            def'
            >>> tei2md.markdownify(h)
            ' abc\\n# line1\\n# line2\\n# line3\\n# line4\\n\\ndef'

        """
        lines = el.find_all("l", recursive=False)
        lines = [line.text for line in lines]
        return "\n# {}\n\n".format("\n# ".join(lines))
        
##    def convert_pb(self, el, text):
##        """Page beginnings are taken care of in a preprocessing step"""
##        pass

    def convert_quote(self, el, text):
        """Quotes are currently not converted"""
        return text


#######################################################################"

def preprocess_page_numbers(s):
    """Turn page beginnings into page endings.

    TEI xml indicates the beginning of a page, while OpenITI mARkdown
    indicates the end of a page.
    """
    try:
        s, tail = re.split("</body>", s)
    except:
        tail = ""
    s = re.split('<pb n="(\d+)"/?>', s)
    page_numbers = [it for it in s if s.index(it)%2]
    page_texts = [it for it in s if not s.index(it)%2]
    if page_texts[0] != "":
        page_numbers = ["0"] + page_numbers
    else:
        page_texts = page_texts[1:]
    text = ""
    for i, it in enumerate(page_texts):
        text += it
        text += "\n\nPageV00P{:03d}\n".format(int(page_numbers[i]))
    if tail:
        return text + "</body>" + tail
    else:
        return text
    
def preprocess_wrapped_lines(s):
    s = re.sub("-[\n\r]+~~", "", s)
    return re.sub("[\n\r]+~~", " ", s)


def markdownify(xml_str, **options):
    return TeiConverter(**options).convert(xml_str)


if __name__ == "__main__":
    test_xml = """
<?xml version="1.0" encoding="utf-8"?>
<TEI.2>
 <teiHeader>
 <fileDesc>
 <titleStmt>
 <title>Kitāb al-fihrist</title>
 <author>Ibn al-Nadīm</author>
 <editor>Gustav Flügel</editor>
 <funder>Andrew W. Mellon Foundation</funder>
 </titleStmt>
 <sourceDesc>
 <biblStruct>
 <monogr>
 <author>Ibn al-Nadīm</author>
 <title>Kitâb al-Fihrist</title>
 <editor>Gustav Flügel</editor>
 <imprint>
 <pubPlace>Leipzig</pubPlace>
 <publisher>Maktabat al-nahḍah al-miṣrīyah</publisher>
 <biblScope unit="vol">1</biblScope>
 <biblScope unit="pp" from="2" to="360">2-360</biblScope>
 <date>1871-1872</date>
 </imprint>
 </monogr>
 </biblStruct>
 </sourceDesc>
 </fileDesc>
 <encodingDesc>
 <editorialDecl default="NO">
 <correction status="high" default="NO" method="silent">
 <p>Data Entry</p>
 </correction>
 </editorialDecl>
 <refsDecl n="text=1" doctype="TEI.2">
 <state unit="text"/>
 <state unit="book"/>
 <state unit="chapter" n="chunk"/>
 </refsDecl>
 </encodingDesc>
 <profileDesc>
 <langUsage default="NO">
 <language id="arabic">Arabic</language>
 </langUsage>
 </profileDesc>
 </teiHeader>

<text lang="arabic" id="perseus0001.perseus001.alpheios-text-ara1">
<body>

<pb n="2"/>

<div1 type="book" n="1">
<div2 type="chapter" n="0" name="Preface">
<head>
الجزء الاول
من
كتاب الفهرست
</head>
<p>
بسم الله الرحمن الرحيم
</p>
<p>
رب يسر برحمتك النفوس تشراب الى النتائج دون المقدمات وترتاح الى الغرض المقصود
دون التطويل فى العبارات فلذلك اقتصرنا على هذه الكلمات فى صدر كتابنا هذه اذ كانت
دالة على ما قصدناه فى تاليفه ان شاء الله فنقول وبالله نستعين واياه نسئل الصلوة على
جميع انبيائه وعباده المخلصين فى طاعته ولا حول ولا قوة الا بالله العلى العظيم
</p>
<p>
هذا فهرست كتب جميع الامم من العرب والعجم الموجود منها بلغة العرب وقلمها
فى اصناف العلوم واخبار مصنفيها وطبقات مولفليها وانسابهم وتاريخ مواليدهم ومبلغ
اعمارهم واوقات وفاتهم واماكن بلدانهم ومناقبهم ومثالبهم منذ ابتاداء كل علم اخترع
الى عصرنا هذا وهو سنة سبع وسبعين وثلثمائة للهجرة
</p>
<head>
اقتصاص
ما يحتوى عليه الكتاب وهو عشر مقالات
</head>
<p>
المقالة الاولى وهى ثلثة فنون الفن الاول فى وصف لغات الامم من العرب
~~والعجم ونعوت
اقلامها وانواع خطوطها واشكال كتاباتها الفن الثانى فى اسماء كتب الشرائع
~~المنزلة على
مذاهب المسلمين ومذاهب اهلها الفن الثالث فى نعت الكتاب الذى لا ياتيه الباطل
من بين يديه ولا من خلفه تنزيل من حكيم حميد واسماء الكتب المصنفة فى علومه
واخبار القراء واسماء رواتهم والشواذ من قراءتهم
</p>

<pb n="3"/>

<p>
المقالة الثانية وهى ثلثة فنون فى النحويين واللغويين الفن الاول فى ابتداء
~~النحو واخبار
النحويين البصريين وفصحاء الاعراب واسماء كتبهم الفن الثانى فى اخبار النحويين
واللغويين من الكوفيين واسماء كتبهم الفن الثالث فى ذكر قوم من النحويين خلطوا
المذهبين واسماء كتبهم
</p>
</div2></div1></body></text></TEI.2>"""

    import doctest
    doctest.testmod()

    test_xml = preprocess_wrapped_lines(test_xml)
    test_xml = preprocess_page_numbers(test_xml)

    soup = BeautifulSoup(test_xml, "xml")
##    print(soup)
##    input()
##    print(soup.find_all("head"))
##    input()
    text_div = str(soup.find("text"))
##    print(text_div)
    text=markdownify(text_div, md_style="OpenITI")
##    print("*"*40)
    print(text)
