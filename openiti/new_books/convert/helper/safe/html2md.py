"""Convert html to Markdown.

This program is an adaptation of python-markdownify
(https://github.com/matthewwithanm/python-markdownify)
to output OpenITI mARkdown.
It also adds methods for tables and images,
and a post-processing method.

You can use this class as a base class and subclass it
to add methods, adapt the post-processing method etc.

E.g.:
    class Hindawi_converter(html2md.MarkdownConverter):
        def post_process_md(self, text):
            text = super().post_process_md(text)
            # remove blank lines marked with "DELETE_PREVIOUS_BLANKLINES" tag
            text = re.sub(r"\n+DELETE_PREVIOUS_BLANKLINES", "", text)
            # replace placeholders for spaces in tables:
            text = re.sub("ç", " ", text)
            return text


Examples (doctests):

    Headings: h1

    >>> import html2md
    >>> h = '<h1>abc</h1>'
    >>> html2md.markdownify(h)
    '\\n\\n### | abc\\n\\n'

    NB: heading style is OpenITI mARkdown style by default,
        but can be set to other styles as well:

    >>> h = '<h1>abc</h1>'
    >>> html2md.markdownify(h, md_style=UNDERLINED)
    '\\n\\nabc\\n===\\n\\n'

    >>> h = '<h1>abc</h1>'
    >>> html2md.markdownify(h, md_style=ATX)
    '\\n\\n# abc\\n\\n'

    Paragraphs (<p>):

    >>> h = "<p>abc</p>"
    >>> html2md.markdownify(h)
    '\\n\\n# abc\\n\\n'

    >>> h = "<p>abc</p>"
    >>> html2md.markdownify(h, md_style=ATX)
    '\\n\\nabc\\n\\n'


    Divs without class or with an unsupported class are stripped:

    >>> h = 'abc\
             <div>def</div>\
             ghi'
    >>> html2md.markdownify(h)
    'abc def ghi'

    >>> h = 'abc\
             <div class="unknown_div_class">def</div>\
             ghi'
    >>> html2md.markdownify(h)
    'abc def ghi'


    Spans without class or with an unsupported class are stripped:

    >>> h = 'abc <span>def</span> ghi'
    >>> html2md.markdownify(h)
    'abc def ghi'

    >>> h = 'abc <span class="unknown_span_class">def</span> ghi'
    >>> html2md.markdownify(h)
    'abc def ghi'


    Links:

    >>> h = '<a href="a/b/c">abc</a>'
    >>> html2md.markdownify(h)
    '[abc](a/b/c)'


    Unordered lists:

    >>> h = '<ul><li>item1</li><li>item2</li></ul>'
    >>> html2md.markdownify(h)
    '\\n* item1\\n* item2\\n\\n'

    Ordered lists:

    >>> h = '<ol><li>item1</li><li>item2</li></ol>'
    >>> html2md.markdownify(h)
    '\\n1. item1\\n2. item2\\n\\n'

    Nested lists:

    >>> h = '<ol><li>item1</li><li>item2:<ul><li>item3</li><li>item4</li></ul></li></ol>'
    >>> html2md.markdownify(h)
    '\\n1. item1\\n2. item2:\\n\\n\\t* item3\\n\\t* item4\\n\\t\\n\\n'

    Italics (<i> and <em> tags):

    >>> h = 'abc <em>def</em> ghi'
    >>> html2md.markdownify(h)
    'abc *def* ghi'

    >>> h = 'abc <i>def</i> ghi'
    >>> html2md.markdownify(h)
    'abc *def* ghi'


    Bold (<b> and <strong> tags):

    >>> h = 'abc <b>def</b> ghi'
    >>> html2md.markdownify(h)
    'abc **def** ghi'

    >>> h = 'abc <strong>def</strong> ghi'
    >>> html2md.markdownify(h)
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
    >>> html2md.markdownify(h)
    '\\n\\n| th1aaa | th2 |\\n| ------ | --- |\\n| td1    | td2 |\\n\\n'

    # i.e.,
    # | th1aaa | th2 |
    # | td1    | td2 |
"""

from bs4 import BeautifulSoup, NavigableString, Comment
import re
import six


convert_heading_re = re.compile(r'convert_h(\d+)')
line_beginning_re = re.compile(r'^', re.MULTILINE)
whitespace_re = re.compile(r'[\r\n\s\t ]+')
FRAGMENT_ID = '__MARKDOWNIFY_WRAPPER__'
wrapped = '<div id="%s">%%s</div>' % FRAGMENT_ID



# Heading styles
ATX = 'atx'
ATX_CLOSED = 'atx_closed'
UNDERLINED = 'underlined'
OPENITI = 'OpenITI'
SETEXT = UNDERLINED


def escape(text):
##    if not text:
##        return ''
##    return text.replace('_', r'\_')
    return text


def _todict(obj):
    return dict((k, getattr(obj, k)) for k in dir(obj) if not k.startswith('_'))


class MarkdownConverter(object):
    class DefaultOptions:
        strip = None
        convert = None
        autolinks = True
        md_style = OPENITI
        bullets = '*+-'  # An iterable of bullet types.
        image_link_regex = ""  # e.g., "images/books"
        image_folder = "img"

    class Options(DefaultOptions):
        pass

    def __init__(self, **options):
        # Create an options dictionary. Use DefaultOptions as a base so that
        # it doesn't have to be extended.
        self.options = _todict(self.DefaultOptions)
        self.options.update(_todict(self.Options))
        self.options.update(options)
        if self.options['strip'] is not None and self.options['convert'] is not None:
            raise ValueError('You may specify either tags to strip or tags to'
                             ' convert, but not both.')


    def convert(self, html):
        """Convert html to markdown.

        # We want to take advantage of the html5 parsing, but we don't actually
        # want a full document. Therefore, we'll mark our fragment with an id,
        # create the document, and extract the element with the id.
        """

        html = wrapped % html
        soup = BeautifulSoup(html, 'html.parser')
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

    def process_tag(self, node, children_only=False):
        """Process each tag and its children.
        """
        #print(node.name, node.attrs)
        text = ''

        # Convert the children first
        for el in node.children:

            if isinstance(el, NavigableString):
                if not isinstance(el, Comment):  # remove html comments
                    text += self.process_text(six.text_type(el))
            else:
                text += self.process_tag(el)


        if not children_only:
            convert_fn = getattr(self, 'convert_%s' % node.name, None)
            if convert_fn and self.should_convert_tag(node.name):
                #print("text is now:")
                #input(text)
                text = convert_fn(node, text)
        return text

    def process_text(self, text):
        #return escape(whitespace_re.sub(' ', text or ''))
        if whitespace_re.sub('', text or ''):
            return whitespace_re.sub(' ', text)
        return ""

    def fill_out_columns(self, match):
        """Find the longest cell in a column; add spaces to shorter columns."""

        # split the table into a list of lists:

        table = match.group(1)
        #print(table)
        if "|--" in table:
            header = True
        else:
            header = False
        table = table.splitlines()
        if header:
            del table[1]  # remove horizontal lines separating header from body
        table = [(row.split("|"))[1:] for row in table]  # remove empty string

        # get length of longest cell per column:

        column_length = dict()
        for row in table:
            for i, cell in enumerate(row):
                try:
                    if len(cell) > column_length[i]:
                        column_length[i] = len(cell)
                except:
                    column_length[i] = len(cell)

        # fill out shorter cells:

        new_table = []
        for row in table:
            new_row = []
            for i, cell in enumerate(row):
                new_cell = cell + " "*(column_length[i]-len(cell))
                new_cell = new_cell + (" " * len(re.findall("لا|لأ|لإ", new_cell)))
                #combining = re.findall("[ؐ-ًؚ-ٰٟۖ-ۜ۟-۪ۤۧۨ-ۭ]", new_cell)
                #new_cell = re.sub(" {%s}" % len(combining), "", new_cell)
                new_row.append(new_cell)
            new_table.append(new_row)

        # re-build the table:

        new_table = [" | ".join(row).strip() for row in new_table]
        if header:
            lines = " | ".join(["-" * v for k,v in column_length.items()])
            new_table = [new_table[0], lines.strip()]+new_table[1:]
        new_table = "\n| ".join(new_table)
        new_table = "\n\n| {}\n\n".format(new_table)

        #print("new_table: ")
        #print(new_table)
        return new_table


    def post_process_named_entities(self, match):
        """Reformat named entity matches to mARkdown named entity standard.

        Named entities should be marked with @TAG@ tags in the converter
        (3 capital letters between ampersands), and end with a new line.
        This post-processing step then converts these temporary tags
        into OpenITI mARkdown format @TAG\d\d+:
        * The first number after the @QUR tag refers to the number of letters
          following the tag that do not belong to the named entity
          (in this automatic step, this number will always be set to 0);
        * the following number(s) refer(s) to the length of the entity in tokens

        Examples:
            >>> import html2md
            >>> conv = html2md.MarkdownConverter()
            >>> conv.post_process_md("abc @QUR@ def ghi\\njkl")
            'abc @QUR02 def ghi jkl'
            >>> conv.post_process_md("abc @QUR@ def ghi\\n~~jkl\\nmno")
            'abc @QUR03 def ghi\\n~~jkl mno'
        """

        foll_char = match.group(3)
        entity = match.group(2)
        ent_words = len(re.findall("[\n\r ]+", entity)) + 1
        code = match.group(1)
        return "@{}0{} {} {}".format(code, ent_words, entity, foll_char)


    def post_process_md(self, text):

        # post-process named entity tags:
        text = re.sub("@([A-Z]+)@ +(.+?)\n([^~]|Z)",
                      self.post_process_named_entities, text,
                      flags=re.DOTALL)
        # remove blank lines marked with "DELETE_PREVIOUS_BLANKLINES" tag
        text = re.sub(r"\n+DELETE_PREVIOUS_BLANKLINES", "", text)

        # remove leading and trailing spaces in lines:
        text = re.sub(r" *(\n+) *", r"\1", text)
        # remove unwanted additional spaces and lines:
        text = re.sub(r"\n{3,}", r"\n\n", text)
        text = re.sub(r" +", r" ", text)
        # fill out columns in tables:
        text = re.sub("\n\n(\|.+?)\n\n", self.fill_out_columns, text, flags=re.DOTALL)
        return text

    def __getattr__(self, attr):
        # Handle headings
        m = convert_heading_re.match(attr)
        if m:
            n = int(m.group(1))

            def convert_tag(el, text):
                return self.convert_hn(n, el, text)

            convert_tag.__name__ = 'convert_h%s' % n
            setattr(self, convert_tag.__name__, convert_tag)
            return convert_tag

        raise AttributeError(attr)

    def should_convert_tag(self, tag):
        """Check whether a tag should be converted or simply stripped"""
        tag = tag.lower()
        strip = self.options['strip']
        convert = self.options['convert']
        if strip is not None:
            return tag not in strip
        elif convert is not None:
            return tag in convert
        else:
            return True

    def indent(self, text, level):
        """Add tab indentation before text."""
        return line_beginning_re.sub('\t' * level, text) if text else ''

    def create_underline_line(self, text, pad_char):
        """Create a sequence of pad_char characters the same lenght as text."""
        return pad_char * len(text) if text else ''

    def underline(self, text, pad_char):
        """Underline text with pad_char characters (-, =, or +).

        Args:
            text (str): the text within a tag, to be underlined
            pad_char (str): the character used for the line (-, =, or +)

        Returns:
            an underlined line of text

        Example:
            >>> import html2md
            >>> html2md.MarkdownConverter().underline("123456789", "=")
            '123456789\\n========='
            >>> html2md.MarkdownConverter().underline("123456789  ", "=")
            '123456789\\n========='
        """
        text = (text or '').rstrip()
        line = self.create_underline_line(text, pad_char)
        return "{}\n{}".format(text, line)


    #-----------------------------------------------------------

    # Conversion functions for specific tags (in alphabetic order):

    def convert_a(self, el, text):
        """Convert html links.

        Example:
            >>> import html2md
            >>> h = '<a href="a/b/c">abc</a>'
            >>> html2md.markdownify(h)
            '[abc](a/b/c)'
        """
        href = el.get('href')
        title = el.get('title')
        if self.options['autolinks'] and text == href and not title:
            # Shortcut syntax
            return '<%s>' % href
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ''
        return '[%s](%s%s)' % (text or '', href, title_part) if href else text or ''

    def convert_b(self, el, text):
        return self.convert_strong(el, text)

    def convert_blockquote(self, el, text):
        return '\n' + line_beginning_re.sub('> ', text) if text else ''

    def convert_br(self, el, text):
        return '  \n'

    def convert_em(self, el, text):
        return '*%s*' % text if text else ''

    def convert_hn(self, n, el, text):
        style = self.options['md_style']
        text = text.rstrip()
        if style == OPENITI:
            return '\n\n### %s %s\n\n' % ("|"*n, text)
        if style == UNDERLINED and n <= 2:
            line = '=' if n == 1 else '-'
            return '\n\n%s\n\n' % self.underline(text, line)
        hashes = '#' * n
        if style == ATX_CLOSED:
            return '\n\n%s %s %s\n\n' % (hashes, text, hashes)
        return '\n\n%s %s\n\n' % (hashes, text)

    def convert_i(self, el, text):
        return self.convert_em(el, text)

    def convert_img(self, el, text):
        """
        Examples:
            >>> import html2md
            >>> h = '<div><img class="figure" src="../Images/figure1.png" /></div>'
            >>> html2md.markdownify(h)
            '![](../Images/figure1.png)'
            
            >>> html2md.markdownify(h, image_link_regex="../Images", image_folder="img")
            '![](img/figure1.png)'
        """

        alt = el.attrs.get('alt', None) or ''
        src = el.attrs.get('src', None) or ''
        title = el.attrs.get('title', None) or ''
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ''

        # replace the online address with the local path to the image:
        if self.options['image_link_regex']:
            src = re.sub(self.options['image_link_regex'],
                         self.options['image_folder'], src)

        return '![%s](%s%s)' % (alt, src, title_part)

    def convert_list(self, el, text):
        """Convert ordered and unordered html lists (<ul> and <ol> tags).

        Examples:
            # unordered lists:
            >>> import html2md
            >>> h = '<ul><li>item1</li><li>item2</li></ul>'
            >>> html2md.markdownify(h)
            '\\n* item1\\n* item2\\n\\n'

            # ordered lists:
            >>> import html2md
            >>> h = '<ol><li>item1</li><li>item2</li></ol>'
            >>> html2md.markdownify(h)
            '\\n1. item1\\n2. item2\\n\\n'

            # nested lists:
            ###### TEST FAILS FOR UNKNOWN REASONS
            ##>>> import html2md
            ##>>> h = '<ol><li>item1</li><li>item2:<ul><li>item3</li><li>item4</li></ul></li></ol>'
            ##>>> html2md.markdownify(h)
            ##'\\n1. item1\\n2. item2:\\n\\n\\t* item3\\n\\t* item4\\n\\t\\n\\n'
        """
        nested = False
        while el:
            if el.name == 'li':
                nested = True
                break
            el = el.parent
        if nested:
            text = '\n' + self.indent(text, 1)
        return '\n' + text + '\n'


    def convert_li(self, el, text):
        """Convert list element tags <li>."""
        parent = el.parent
        if parent is not None and parent.name == 'ol':
            bullet = '%s.' % (parent.index(el) + 1)
        else:
            depth = -1
            while el:
                if el.name == 'ul':
                    depth += 1
                el = el.parent
            bullets = self.options['bullets']
            bullet = bullets[depth % len(bullets)]
        return '%s %s\n' % (bullet, text or '')

    convert_ol = convert_list


    def convert_p(self, el, text):
        """Converts <p> tags.

        Examples:
            >>> import html2md
            >>> h = "<p>abc</p>"
            >>> html2md.markdownify(h)
            '\\n\\n# abc\\n\\n'

            >>> h = "<p>abc</p>"
            >>> html2md.markdownify(h, md_style=ATX)
            '\\n\\nabc\\n\\n'

            >>> h = "<p></p>"
            >>> html2md.markdownify(h, md_style=ATX)
            ''
        """
        if self.options['md_style'] == OPENITI:
            return '\n\n# %s\n\n' % text if text else ''
        else:
            return '\n\n%s\n\n' % text if text else ''


    def convert_table(self, el, text):
        """Wrap tables between double new lines.

        NB: conversion of the tables takes place on the tr level."""
        #print("CONVERTING TABLE")
        return '\n\n' + text + '\n\n'

    def convert_tr(self, el, text):
        """Convert table rows.

        NB: rows are processed before the table tag is.
        Spaces to fill out columns are added in post-processing!

        Examples:
            >>> import html2md
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

            # i.e.,
            # | th1aaa | th2 |
            # | td1    | td2 |
        """
##        def wrap_cell_text(cell_text):
##            while len(cell_text) < self.max_len:
##                cell_text += "ç" # placeholder; will be replaced by spaces later
##            return cell_text
##
##        try:
##            self.max_len
##        except:
##            self.max_len = 0
##        if self.max_len == 0:
##            max_len = 0
##            for desc in el.find_all():
##                if len(desc.text) > max_len:
##                    max_len = len(desc.text)
##            if max_len>30:
##                max_len = 30
##            self.max_len = max_len

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
                t.append(td.text)
            return '|{}|\n'.format("|".join(t))

    convert_ul = convert_list

    def convert_strong(self, el, text):
        """Convert <b> and <strong> tags.

        NB: convert_b refers to this same function

        Examples:
            >>> import html2md
            >>> h = 'abc <strong>def</strong> ghi'
            >>> html2md.markdownify(h)
            'abc **def** ghi'

            >>> import html2md
            >>> h = 'abc <b>def</b> ghi'
            >>> html2md.markdownify(h)
            'abc **def** ghi'
        """
        return '**%s**' % text if text else ''




def markdownify(html, **options):
    return MarkdownConverter(**options).convert(html)


if __name__ == "__main__":
    test_html = """
    <?xml version="1.0" encoding="UTF-8"?>
    <html xml:lang="ar" lang="ar" dir="rtl" xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
    <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="initial-scale=2.3, user-scalable=no" />
    <title>TITLE</title>
    <link rel="stylesheet" type="text/css" href="../Style/epub.css" />
    </head>
    <body>
    <div dir="rtl" id="1">
      <h1 dir="rtl" class="title center">H1 TITLE</h1>
      <div dir="rtl" class="subtitle" id="2">SUBTITLE DIV
      </div>
      <div dir="rtl" class="section" id="sect1_34">
        <h4 dir="rtl" class="title center">H4 SECTION TITLE</h4>
        <div class="center" id="4">
          <p>P BLA <span class="quran">QURAN QUOTE</span> P BLABLA</p>
        </div>
      </div>
      <div dir="rtl" class="section" id="sect1_35">
        <h4 dir="rtl" class="title">H4 SECTION TITLE</h4>
        <p>P1

        </p>
        <p>
                            P2
                        P2b

        </p>
        <div dir="rtl" class="section" id="sect2_3">
          <h4 dir="rtl" class="title">H4 SUBSECTION2_3 TITLE</h4>
          <p>SUBSECTION2_3 PARAGRAPH</p>
        </div>
      </div>
    </div>
    </body>
    </html>
    """

    import doctest
    doctest.testmod()

    soup = BeautifulSoup(test_html)
    text_div = soup.html.body.div
    #print(text_div)
    #text=markdownify(text_div, md_style=ATX)
    #print("*"*40)
    #print(text)




