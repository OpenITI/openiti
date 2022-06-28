"""Convert Ghaemiyeh library html to OpenITI mARkdown.

This script subclasses the generic MarkdownConverter class
from the html2md module (based on python-markdownify,
https://github.com/matthewwithanm/python-markdownify),
which uses BeautifulSoup to create a flexible converter.

The subclass in this module, QaemiyehConverter,
adds methods specifically for the conversion of books from
the Qaemiyeh library to OpenITI mARkdown.

There do not seem to be many special cases in Ghaemiyeh texts, 
only footnotes: <div class="calibre1" id="content_note_12_1">1 footnotetext</div>

The easiest way to use this is to simply feed the html (as string)
to the markdownify() function, which will create an instance
of the QaemiyehConverter class and return the converted string.

Examples (doctests):

    Headings: h1 (from superclass html2md.MarkdownConverter)

    >>> import html2md_Qaemiyeh
    >>> h = '<h1>abc</h1>'
    >>> html2md_Qaemiyeh.markdownify(h)
    '\\n\\n### | abc\\n\\n'

    NB: heading style is OpenITI mARkdown style by default,
        but can be set to other styles as well:

    >>> h = '<h1>abc</h1>'
    >>> html2md_Qaemiyeh.markdownify(h, md_style=UNDERLINED)
    '\\n\\nabc\\n===\\n\\n'

    >>> h = '<h1>abc</h1>'
    >>> html2md_Qaemiyeh.markdownify(h, md_style=ATX)
    '\\n\\n# abc\\n\\n'


    Footnote divs:
    
    >>> h = '<div class="calibre1" id="content_note_12_1">1 footnotetext</div>'
    >>> html2md_Qaemiyeh.markdownify(h)
    '\\n\\nFOOTNOTE1 footnotetext\\n\\n'

    NB: FOOTNOTE is a tag that will be used to extract all footnotes
        in a next step.

    Divs without class or with an unsupported class are simply stripped:
    
    >>> h = 'abc\
             <div>def</div>\
             ghi'
    >>> html2md_Qaemiyeh.markdownify(h)
    'abc def ghi'
        
    >>> h = 'abc\
             <div class="unknown_div_class">def</div>\
             ghi'
    >>> html2md_Qaemiyeh.markdownify(h)
    'abc def ghi'

    Spans without class or with an unsupported class are stripped:
    
    >>> h = 'abc <span>def</span> ghi'
    >>> html2md_Qaemiyeh.markdownify(h)
    'abc def ghi'
    
    >>> h = 'abc <span class="unknown_span_class">def</span> ghi'
    >>> html2md_Qaemiyeh.markdownify(h)
    'abc def ghi'


    Links: 

    >>> h = '<a href="a/b/c">abc</a>'
    >>> html2md_Qaemiyeh.markdownify(h)
    '[abc](a/b/c)'

    
    Unordered lists: 

    >>> h = '<ul><li>item1</li><li>item2</li></ul>'
    >>> html2md_Qaemiyeh.markdownify(h)
    '\\n* item1\\n* item2\\n\\n'
    
    Ordered lists:

    >>> h = '<ol><li>item1</li><li>item2</li></ol>'
    >>> html2md_Qaemiyeh.markdownify(h)
    '\\n1. item1\\n2. item2\\n\\n'

    Nested lists:
    
    >>> h = '<ol><li>item1</li><li>item2:<ul><li>item3</li><li>item4</li></ul></li></ol>'
    >>> html2md_Qaemiyeh.markdownify(h)
    '\\n1. item1\\n2. item2:\\n\\n\\t* item3\\n\\t* item4\\n\\t\\n\\n'


    Italics (<i> and <em> tags):

    >>> h = 'abc <em>def</em> ghi'
    >>> html2md_Qaemiyeh.markdownify(h)
    'abc *def* ghi'

    >>> h = 'abc <i>def</i> ghi'
    >>> html2md_Qaemiyeh.markdownify(h)
    'abc *def* ghi'


    Bold (<b> and <strong> tags):

    >>> h = 'abc <b>def</b> ghi'
    >>> html2md_Qaemiyeh.markdownify(h)
    'abc **def** ghi'

    >>> h = 'abc <strong>def</strong> ghi'
    >>> html2md_Qaemiyeh.markdownify(h)
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
    >>> html2md_Qaemiyeh.markdownify(h)
    '\\n\\n| th1aaa | th2 |\\n| ------ | --- |\\n| td1    | td2 |\\n\\n'

"""
import re


if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(path.dirname(root_folder)))
    sys.path.append(root_folder)

from openiti.new_books.convert.helper import html2md
from openiti.new_books.convert.helper.html2md import *  # import all constants!

import re


class QaemiyehConverter(html2md.MarkdownConverter):
    """Convert Qaemiyeh library html to OpenITI mARkdown."""

    def __init__(self, **options):
        super().__init__(**options)
        self.class_dict = dict()
        #self.class_dict["quran"] = '@QUR@ {text}\n'
        #self.class_dict["hadith"] = '@HAD@ {text}\n'
        #self.class_dict["subtitle"] = 'DELETE_PREVIOUS_BLANKLINES {text}\n\n'


    #------------------------------------------------------------------------
    # new conversion methods 
    # (and adaptations of conversion methods from the super-class)

    def convert_a(self, el, text):
        """Converts html links.

        Overwrites the MarkdownConverter.post_process_md() method.
        Introduces an exception for links between footnote markers
        and footnootes. 

        Example:
            >>> import html2md_Qaemiyeh
            >>> h = '<a href="a/b/c">abc</a>'
            >>> html2md_Qaemiyeh.markdownify(h)
            '[abc](a/b/c)'

            >>> import html2md_Qaemiyeh
            >>> h = 'abc <a href="ftn1">1</a>'
            >>> html2md_Qaemiyeh.markdownify(h)
            'abc [1]'
        """
        href = el.get('href')
        if href:
            if "content_note" in href or "fn" in href:
                # do not include a link for footnotes:
                return text
            else:
                # return a markdown representation of a link: [text](href)
                return super().convert_a(el, text)
        else:
            return super().convert_a(el, text)

    def convert_div(self, el, text):
        """Converts html <div> tags, depending on their class.

        In the MarkdownConverter class, div tags are simply stripped away.
        
        Examples:
        
            # no div class: tags are stripped off
            
            >>> import html2md_Qaemiyeh
            >>> h = 'abc\
                     <div>def</div>\
                     ghi'
            >>> html2md_Qaemiyeh.markdownify(h)
            'abc def ghi'
            
            # unknown div class: tags are stripped off
            
            >>> import html2md_Qaemiyeh
            >>> h = 'abc\
                     <div class="unknown_div_class">def</div>\
                     ghi'
            >>> html2md_Qaemiyeh.markdownify(h)
            'abc def ghi'
            

            # footnote:
            
            >>> h = '<div class="calibre1" id="content_note_24_1>1 footnotetext</div>'
            >>> html2md_Qaemiyeh.markdownify(h)
            '\\n\\nFOOTNOTE1 footnotetext\\n\\n'

        """
        
        try:
            if el["id"].startswith("content_note_"):
                return "\n\nFOOTNOTE" + text + "\n\n"
        except:
            pass
        try:
            el["class"]
            for c in el["class"]:
                if c in self.class_dict:
                    return self.class_dict[c].format(text=text, el=el, c=c) 
        except:
            return text
           
        return text

    def convert_p(self, el, text):
        """Converts html <p> tags, depending on their class attribute.

        Supported span classes should be stored in self.span_dict
        (key: span class (str); value: formatting string)

        Example:
            >>> import html2md_Qaemiyeh
            >>> h = '<p>abc def ghi</p>'
            >>> html2md_Qaemiyeh.markdownify(h)
            '# abc def ghi'
            
            >>> h = 'abc <p class="unknown_span_class">def</p> ghi'
            >>> html2md_Qaemiyeh.markdownify(h)
            'abc \n#def ghi'
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
        return "\n# " + text + "\n"


    def convert_span(self, el, text):
        """Converts html <span> tags, depending on their class attribute.

        Supported span classes should be stored in self.span_dict
        (key: span class (str); value: formatting string)

        Example:
            >>> import html2md_Qaemiyeh
            >>> h = 'abc <span>def</span> ghi'
            >>> html2md_Qaemiyeh.markdownify(h)
            'abc def ghi'
            
            >>> h = 'abc <span class="unknown_span_class">def</span> ghi'
            >>> html2md_Qaemiyeh.markdownify(h)
            'abc def ghi'
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
    """Shortcut to the convert method of the QaemiyehConverter class."""
    return QaemiyehConverter(**options).convert(html)


if __name__ == "__main__":
    import doctest
    doctest.testmod()






