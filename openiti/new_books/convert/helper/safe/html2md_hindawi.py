"""Convert Hindawi library html to OpenITI mARkdown.

This script subclasses the generic MarkdownConverter class
from the html2md module (based on python-markdownify,
https://github.com/matthewwithanm/python-markdownify),
which uses BeautifulSoup to create a flexible converter.
The subclass in this module, HindawiConverter,
adds methods specifically for the conversion of books from
the Hindawi library to OpenITI mARkdown:
* special treatment of <h4> heading tags
* div classes "poetry_container", "section", "footnote" and "subtitle"
* span class "quran"

The easiest way to use this is to simply feed the html (as string)
to the markdownify() function, which will create an instance
of the HindawiConverter class and return the converted string.

Examples (doctests):

    Headings: h1 (from superclass html2md.MarkdownConverter)

    >>> import html2md_hindawi
    >>> h = '<h1>abc</h1>'
    >>> html2md_hindawi.markdownify(h)
    '\\n\\n### | abc\\n\\n'

    NB: heading style is OpenITI mARkdown style by default,
        but can be set to other styles as well:

    >>> h = '<h1>abc</h1>'
    >>> html2md_hindawi.markdownify(h, md_style=UNDERLINED)
    '\\n\\nabc\\n===\\n\\n'

    >>> h = '<h1>abc</h1>'
    >>> html2md_hindawi.markdownify(h, md_style=ATX)
    '\\n\\n# abc\\n\\n'

    Headings: <h4>
    
    NB: in the Hindawi library, <h4> tag is used for section headings
        on all levels but the highest one.
        The section level must be derived from the id of the parent div. 

    >>> h = '<div class="section" id="sect2_4"><h4>abc</h4></div>'
    >>> html2md_hindawi.markdownify(h)
    '\\n\\n### ||| abc\\n\\n'

    >>> h = '<div class="section" id="sect5_2"><h4>abc</h4></div>'
    >>> html2md_hindawi.markdownify(h)
    '\\n\\n### |||||| abc\\n\\n'


    Poetry div, single-line:
    
    >>> h = '\
    <div class="poetry_container line">\
      <div>\
        <div>hemistich1</div>\
        <div>hemistich2</div>\
      </div>\
    </div>'
    >>> html2md_hindawi.markdownify(h)
    '\\n# hemistich1 %~% hemistich2\\n'
    
    Poetry div, multiple line:

    >>> h = '\
    abc\
    <div class="poetry_container">\
      <div>\
        <div>hemistich1</div>\
        <div>hemistich2</div>\
      </div>\
      <div>\
        <div>hemistich3</div>\
        <div>hemistich4</div>\
      </div>\
    </div>\
    def'
    >>> html2md_hindawi.markdownify(h)
    ' abc\\n# hemistich1 %~% hemistich2\\n# hemistich3 %~% hemistich4\\ndef'
    
    Section div without heading:
    
    >>> h = 'abc\
             <div class="section" id="sect2_9">def</div>\
             ghi'
    >>> html2md_hindawi.markdownify(h)
    'abc\\n\\n### |||\\ndef\\n\\nghi'

    Section div with heading (handled by h4):
    
    >>> h = 'abc\
             <div class="section" id="sect2_9">\
               <h4>title</h4>\
               <p>def</p>\
             </div>\
             ghi'
    >>> html2md_hindawi.markdownify(h)
    'abc\\n\\n### ||| title\\n\\n# def\\n\\nghi'

    Footnote divs:
    
    >>> h = '<div class="footnote"><sup>1 </sup>footnotetext</div>'
    >>> html2md_hindawi.markdownify(h)
    '\\n\\nFOOTNOTE1 footnotetext\\n\\n'

    NB: FOOTNOTE is a tag that will be used to extract all footnotes
        in a next step.

    Subtitle divs:

    >>> h = '<h1>Title text</h1><div class="subtitle">Subtitle text</div>'
    >>> html2md_hindawi.markdownify(h)
    '\\n\\n### | Title text Subtitle text\\n\\n'

    Divs without class or with an unsupported class are simply stripped:
    
    >>> h = 'abc\
             <div>def</div>\
             ghi'
    >>> html2md_hindawi.markdownify(h)
    'abc def ghi'
        
    >>> h = 'abc\
             <div class="unknown_div_class">def</div>\
             ghi'
    >>> html2md_hindawi.markdownify(h)
    'abc def ghi'

    Spans with class "quran":

    >>> h = 'abc <span class="quran">def ghi</span> jkl'
    >>> html2md_hindawi.markdownify(h)
    'abc @QUR02 def ghi jkl'

    # the latter is a result of post-processing;
    # the function itself will produce: 
    # 'abc @QUR@ def ghi\\njkl'

    Spans without class or with an unsupported class are stripped:
    
    >>> h = 'abc <span>def</span> ghi'
    >>> html2md_hindawi.markdownify(h)
    'abc def ghi'
    
    >>> h = 'abc <span class="unknown_span_class">def</span> ghi'
    >>> html2md_hindawi.markdownify(h)
    'abc def ghi'


    Links: 

    >>> h = '<a href="a/b/c">abc</a>'
    >>> html2md_hindawi.markdownify(h)
    '[abc](a/b/c)'

    
    Unordered lists: 

    >>> h = '<ul><li>item1</li><li>item2</li></ul>'
    >>> html2md_hindawi.markdownify(h)
    '\\n* item1\\n* item2\\n\\n'
    
    Ordered lists:

    >>> h = '<ol><li>item1</li><li>item2</li></ol>'
    >>> html2md_hindawi.markdownify(h)
    '\\n1. item1\\n2. item2\\n\\n'

    Nested lists:
    
    >>> h = '<ol><li>item1</li><li>item2:<ul><li>item3</li><li>item4</li></ul></li></ol>'
    >>> html2md_hindawi.markdownify(h)
    '\\n1. item1\\n2. item2:\\n\\n\\t* item3\\n\\t* item4\\n\\t\\n\\n'


    Italics (<i> and <em> tags):

    >>> h = 'abc <em>def</em> ghi'
    >>> html2md_hindawi.markdownify(h)
    'abc *def* ghi'

    >>> h = 'abc <i>def</i> ghi'
    >>> html2md_hindawi.markdownify(h)
    'abc *def* ghi'


    Bold (<b> and <strong> tags):

    >>> h = 'abc <b>def</b> ghi'
    >>> html2md_hindawi.markdownify(h)
    'abc **def** ghi'

    >>> h = 'abc <strong>def</strong> ghi'
    >>> html2md_hindawi.markdownify(h)
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
    >>> html2md_hindawi.markdownify(h)
    '\\n\\n| th1aaa | th2 |\\n| ------ | --- |\\n| td1    | td2 |\\n\\n'

"""
import re


if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.new_books.convert import html2md
from openiti.new_books.convert.html2md import *

class HindawiConverter(html2md.MarkdownConverter):
    """Convert Hindawi library html to OpenITI mARkdown."""

    def __init__(self, **options):
        super().__init__(**options)
        self.class_dict = dict()
        self.class_dict["quran"] = '@QUR@ {text}\n'
        self.class_dict["subtitle"] = 'DELETE_PREVIOUS_BLANKLINES {text}\n\n'
        self.class_dict["footnote"] = '\n\nFOOTNOTE{text}\n\n'

##    def process_Quran(self, match):
##        """Reformat Quran quote matches to mARkdown named entity standard."""
##        
##        prec_char = match.group(0)[0]
##        if prec_char == "\n":
##            prec_char = "\n\n# "
##        foll_char = match.group(0)[-1]
##        quote = match.group(0)[7:-2]
##        quote_words = len(re.findall(" +|\n", quote)) + 1
##        #print(match.group(0))
##        #print(quote)
##        return "{}@QUR0{} {}{}".format(prec_char, quote_words, quote, foll_char)
##
##
##    def post_process_md(self, text):
##        """Appends to the MarkdownConverter.post_process_md() method."""
##        # remove blank lines marked with "DELETE_PREVIOUS_BLANKLINES" tag
##        text = re.sub(r"\n+DELETE_PREVIOUS_BLANKLINES", "", text)
##        text = re.sub(".@QUR@ .+?\n[^~]", self.process_Quran, text,
##                      flags=re.DOTALL)
##        text = super().post_process_md(text)
##        return text

    def get_section_level(self, el):
        """Gets the level of the current section (or its parent)."""
        sect_level = 8
        try:
            if "section" in el["class"]:
                sectID = el["id"]
                sect_level, sect_no = re.findall("\d+", sectID)
                sect_level = int(sect_level)
                #print(sect_level)
            else:
                try:
                    sect_level = self.get_section_level(el.parent)
                except:
                    pass
        except:
                try:
                    sect_level = self.get_section_level(el.parent)
                except:
                    pass
        return sect_level

    #------------------------------------------------------------------------
    # new conversion methods 
    # (and adaptations of conversion methods from the super-class)

    def convert_a(self, el, text):
        """Converts html links.

        Overwrites the MarkdownConverter.post_process_md() method.
        Introduces an exception for links between footnote markers
        and footnootes. 

        Example:
            >>> import html2md_hindawi
            >>> h = '<a href="a/b/c">abc</a>'
            >>> html2md_hindawi.markdownify(h)
            '[abc](a/b/c)'

            >>> import html2md_hindawi
            >>> h = 'abc <a href="ftn1">1</a>'
            >>> html2md_hindawi.markdownify(h)
            'abc [1]'
        """
        href = el.get('href')
        if "ftn" in href or "fn" in href:
            # do not include a link for footnotes:
            return '[%s]' % text
        else:
            # return a markdown representation of a link: [text](href)
            return super().convert_a(el, text)

    def convert_div(self, el, text):
        """Converts html <div> tags, depending on their class.

        In the MarkdownConverter class, div tags are simply stripped away.
        
        Examples:
        
            # no div class: tags are stripped off
            
            >>> import html2md_hindawi
            >>> h = 'abc\
                     <div>def</div>\
                     ghi'
            >>> html2md_hindawi.markdownify(h)
            'abc def ghi'
            
            # unknown div class: tags are stripped off
            
            >>> import html2md_hindawi
            >>> h = 'abc\
                     <div class="unknown_div_class">def</div>\
                     ghi'
            >>> html2md_hindawi.markdownify(h)
            'abc def ghi'
            
            # poetry single-line:
            
            >>> h = '\
            <div class="poetry_container line">\
              <div>\
                <div>hemistich1</div>\
                <div>hemistich2</div>\
              </div>\
            </div>'
            >>> html2md_hindawi.markdownify(h)
            '\\n# hemistich1 %~% hemistich2\\n'
            
            # poetry multiple line:

            >>> h = '\
            abc\
            <div class="poetry_container">\
              <div>\
                <div>hemistich1</div>\
                <div>hemistich2</div>\
              </div>\
              <div>\
                <div>hemistich3</div>\
                <div>hemistich4</div>\
              </div>\
            </div>\
            def'
            >>> html2md_hindawi.markdownify(h)
            ' abc\\n# hemistich1 %~% hemistich2\\n# hemistich3 %~% hemistich4\\ndef'
            
            # section without heading:
            
            >>> h = 'abc\
                     <div class="section" id="sect2_9">def</div>\
                     ghi'
            >>> html2md_hindawi.markdownify(h)
            'abc\\n\\n### |||\\ndef\\n\\nghi'

            # section with heading (handled by h4):
            
            >>> h = 'abc\
                     <div class="section" id="sect2_9">\
                       <h4>title</h4>\
                       <p>def</p>\
                     </div>\
                     ghi'
            >>> html2md_hindawi.markdownify(h)
            'abc\\n\\n### ||| title\\n\\n# def\\n\\nghi'

            # footnote:
            
            >>> h = '<div class="footnote"><sup>1 </sup>footnotetext</div>'
            >>> html2md_hindawi.markdownify(h)
            '\\n\\nFOOTNOTE1 footnotetext\\n\\n'

            Paragraph block (similar to <p>):

            >>> h = '<div class="paragraph-block">abc def ghi</div>'
            >>> html2md_hindawi.markdownify(h)
            '\\n\\n# abc def ghi\\n\\n'

            >>> h = '<div class="paragraph-block"><p>abc def ghi</p></div>'
            >>> html2md_hindawi.markdownify(h)
            '\\n\\n# abc def ghi\\n\\n'

            >>> h = '<div class="paragraph-block"></div>'
            >>> html2md_hindawi.markdownify(h)
            ''

            >>> h = '<div class="paragraph-block"><div class="paragraph-block">abc</div></div>'
            >>> html2md_hindawi.markdownify(h)
            '\\n\\n# abc\\n\\n'

        """
        try:
            el["class"]
        except:
            return text
        if "poetry_container" in el["class"]:
            t = []
            for div in el.find_all("div", recursive=False):
                div_list = [x.text for x in div.find_all("div", recursive=False)]
                t.append(" %~% ".join(div_list))
            return "\n# {}\n".format("\n# ".join(t))
        elif "section" in el["class"]:
            # deal with untitled sections: 
            if not el.find(re.compile("h\d")):
                section_level = self.get_section_level(el)+1
                pipes = "|"*section_level
                return '\n\n### %s \n%s\n\n' % (pipes, text)
            #else: handled by convert_hn
        elif "paragraph-block" in el["class"]:
            if not el.find("p"):
                if not el.find("div"):
                    return '\n\n# %s\n\n' % text if text else ''
        else:
            for c in el["class"]:
                if c in self.class_dict:
                    return self.class_dict[c].format(text=text, el=el, c=c) 
           
        return text

    def convert_hn(self, n, el, text):
        """Converts headings in the usual way except h4 headings.

        In the Hindawi library, <h4> tags
        are used for subsections on any level.
        The section level must be derived from the id of the parent div.
        
        Example:
            >>> import html2md_hindawi
            >>> h = '<h1>abc</h1>'
            >>> html2md_hindawi.markdownify(h)
            '\\n\\n### | abc\\n\\n'

            >>> h = '<h3>abc</h3>'
            >>> html2md_hindawi.markdownify(h)
            '\\n\\n### ||| abc\\n\\n'

            >>> h = '<div class="section" id="sect5_2"><h4>abc</h4></div>'
            >>> html2md_hindawi.markdownify(h)
            '\\n\\n### |||||| abc\\n\\n'
        """

        if n == 4:
            return self.convert_h4(el, text)
        else:
            return super().convert_hn(n, el, text)
            
    def convert_h4(self, el, text):
        """Converts <h4> header tags.

        In the Hindawi library, <h4> tags are used
        for subsections on any level.
        The section level must be taken from the id of the parent div.
        NB: the ### | level in Hindawi is 0.

        Example:
            >>> import html2md_hindawi
            >>> h = '<div class="section" id="sect2_4"><h4>abc</h4></div>'
            >>> html2md_hindawi.markdownify(h)
            '\\n\\n### ||| abc\\n\\n'

            >>> h = '<div class="section" id="sect5_2"><h4>abc</h4></div>'
            >>> html2md_hindawi.markdownify(h)
            '\\n\\n### |||||| abc\\n\\n'
        """
        
        section_level = self.get_section_level(el)
        hashes = "#"*(section_level+1)
        style = self.options['md_style']
        if style == ATX_CLOSED:
            return '\n\n#%s %s %s\n\n' % (hashes, text, hashes)
        elif style == ATX:
            return '\n\n%s %s\n\n' % (hashes, text)
        elif style == OPENITI:
            return '\n\n### %s %s\n\n' % ("|"*(section_level+1), text)
        return '\n\n%s %s\n\n' % (hashes, text)

    def convert_span(self, el, text):
        """Converts html <span> tags, depending on their class attribute.

        Supported span classes should be stored in self.span_dict
        (key: span class (str); value: formatting string)

        Example:
            >>> import html2md_hindawi
            >>> h = 'abc <span>def</span> ghi'
            >>> html2md_hindawi.markdownify(h)
            'abc def ghi'
            
            >>> h = 'abc <span class="unknown_span_class">def</span> ghi'
            >>> html2md_hindawi.markdownify(h)
            'abc def ghi'
            
            >>> h = 'abc <span class="quran">def  ghi</span> jkl'
            >>> html2md_hindawi.markdownify(h)
            'abc @QUR02 def ghi jkl'

            # the latter is a result of post-processing;
            # the function itself will produce: 
            # 'abc @QUR@ def ghi\\njkl'
        """
        try:
            for c in el["class"]:
                if c in self.class_dict:
                    if text:
                        return self.class_dict[c].format(text=text, el=el, c=c)
                    else:
                        return ''
        except Exception as e:
            #print(e)
            pass
        return text



def markdownify(html, **options):
    """Shortcut to the convert method of the HindawiConverter class."""
    return HindawiConverter(**options).convert(html)


if __name__ == "__main__":
    import doctest
    doctest.testmod()



### subclassing experiment: 
##
##import re
##
##class Html2md(object):
##    def post_process(self, text):
##        # remove leading and trailing spaces in lines:
##        text = re.sub(r" *(\n+) *", r"\1", text)
##        # remove unwanted additional spaces and lines:
##        text = re.sub(r"\n{3,}", r"\n\n", text)
##        text = re.sub(r" +", r" ", text)
##        return text
##
##class html2md_hindawi(Html2md):
##    def post_process(self, text):
##        text = super().post_process(text)
##        # remove blank lines marked with "DELETE_PREVIOUS_BLANKLINES" tag
##        text = re.sub(r"\n+DELETE_PREVIOUS_BLANKLINES", "", text)
##        # replace placeholders for spaces in tables: 
##        text = re.sub("ç", " ", text)
##        return text    
##
##    def post_process_super(self, text):
##        text = super().post_process(text)
##        return text
##
##
##test = """ab \ncd\n ef\n\n\n\ngh          ij\n\nDELETE_PREVIOUS_BLANKLINESklçççmn"""
##h1 = Html2md()
##
##h2 = html2md_hindawi()
##print(h1.post_process(test))
##print("+"*40)
##print(h2.post_process(test))
##print("+"*40)
##print(h2.post_process_super(test))




