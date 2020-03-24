"""
Replace markdown tags by html tags.

TO DO:
* replace ### \|+ headers not by <hx> but by <div><hx>title</hx>content</div>?
"""
import re
from bs4 import BeautifulSoup

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.new_books.convert.generic_converter import GenericConverter
from openiti.helper.templates import HTML_HEADER, HTML_FOOTER


##HTML_HEADER = """<html>
##<head>
##<style>
##  .entry-title {
##      font-size: 20px;
##  }
##</style>
##</head>
##<body>"""
##
##HTML_FOOTER = "</body></html>"

def header(text):
    return re.sub(".+?#META#HEADER#END", HTML_HEADER, text)

def unwrap(text):
    return re.sub("\n~~", " ", text)


def paragraphs(text):
    regex = r"\n# (.+?)(?=\n#|\n<p|\n<h|\n?</div>|\n\||$)"
    return re.sub(regex, r"\n<p>\1</p>", text, flags=re.DOTALL)


def poetry(text):
    p = r'<p class="verse"><span class="hemistych1">\1</span>'
    p += r' <span class="hemistych2">\2</span></p>'
    #text = re.sub("# (.+?) %~% (.+)", p, text)
    text = re.sub("<p>(.+?) %~% (.+?)</p>", p, text)
    return text


def editorials(text):
    r = r'<div class="editorial">\n\1\n</div>'
    return re.sub(r"### \|EDITOR\| ?\n(.+?)(?=$|\n###)", r, text,
                  flags=re.DOTALL)

def titles(text):
    def title_tag(match):
        level = len(match.group(1))
        cont = match.group(2)
        return '<h{}>{}</h{}>'.format(level, cont, level)
    return re.sub("### (\|+) (.+)", title_tag, text)

def dict_units(text):
    """Replace dictionary units mARkdown tags with html tags.

    Examples:
        >>> import md2html
        >>> md2html.dict_units("### $DIC_NIS$ Name of the entry")
        '<div class="entry descr-name"><span class="entry-title">Name of the entry</span>\\n</div>\\n'
        >>> md2html.dict_units("### $DIC_TOP$ Name of the place")
        '<div class="entry toponym"><span class="entry-title">Name of the place</span>\\n</div>\\n'
        >>> md2html.dict_units("### $DIC_LEX$ Word")
        '<div class="entry lexical"><span class="entry-title">Word</span>\\n</div>\\n'
        >>> md2html.dict_units("### $DIC_BIB$ Book title")
        '<div class="entry book"><span class="entry-title">Book title</span>\\n</div>\\n'
        >>> md2html.dict_units("### $BIO_MAN$ Name of the man")
        '<div class="entry man"><span class="entry-title">Name of the man</span>\\n</div>\\n'
        >>> md2html.dict_units("### $BIO_WOM$ Name of the woman")
        '<div class="entry woman"><span class="entry-title">Name of the woman</span>\\n</div>\\n'
        >>> md2html.dict_units("### $BIO_REF$ Cross-reference to a person")
        '<div class="entry cross-ref"><span class="entry-title">Cross-reference to a person</span>\\n</div>\\n'
        >>> md2html.dict_units("### $BIO_NLI$ List of names")
        '<div class="entry name-list"><span class="entry-title">List of names</span>\\n</div>\\n'
        >>> md2html.dict_units("### $CHR_EVE$ Event description")
        '<div class="entry event"><span class="entry-title">Event description</span>\\n</div>\\n'
        >>> md2html.dict_units("### $CHR_RAW$ Events description")
        '<div class="entry events-batch"><span class="entry-title">Events description</span>\\n</div>\\n'
        >>> md2html.dict_units("### $ Name of the man")
        '<div class="entry man"><span class="entry-title">Name of the man</span>\\n</div>\\n'
        >>> md2html.dict_units("### $$ Name of the woman")
        '<div class="entry woman"><span class="entry-title">Name of the woman</span>\\n</div>\\n'
        >>> md2html.dict_units("### $$$ Cross-reference to a person")
        '<div class="entry cross-ref"><span class="entry-title">Cross-reference to a person</span>\\n</div>\\n'
        >>> md2html.dict_units("### $$$$ List of names")
        '<div class="entry name-list"><span class="entry-title">List of names</span>\\n</div>\\n'
    """
    def dict_tag(match):
        tag_dict = {"WOM": "woman",
                    "MAN": "man",
                    "REF": "cross-ref",
                    "NLI": "name-list",
                    "EVE": "event",
                    "RAW": "events-batch",
                    "NIS": "descr-name",
                    "TOP": "toponym",
                    "LEX": "lexical",
                    "BIB": "book"}
        tag = match.group(1).strip()
        title = match.group(2).strip()
        cont = match.group(3).strip()
        if tag in tag_dict:
            tag = tag_dict[tag]
        else:
            tag = tag.lower()
        if title:
            title_span_tag = '<span class="entry-title">'
            if cont:
                fmt = '<div class="entry {}">{}{}</span>\n{}\n</div>\n'
                return fmt.format(tag, title_span_tag, title, cont)
            else:
                fmt = '<div class="entry {}">{}{}</span>\n</div>\n'
                return fmt.format(tag, title_span_tag, title)
        else:
            fmt = '<div class="entry {}">{}\n</div>\n'
            return fmt.format(tag, cont)

    def bio_tag(match):
        type_index = len(match.group(1))-1
        types = "man woman cross-ref name-list".split()
        title = match.group(2).strip()
        cont = match.group(3).strip()
        if cont:
            if title:
                fmt = '<div class="entry {}"><span class="entry-title">{}</span>\n{}\n</div>\n'
                return fmt.format(types[type_index], title, cont)
            else:
                fmt = '<div class="entry {}">{}\n</div>\n'
                return fmt.format(types[type_index], cont)
        else:
            fmt = '<div class="entry {}"><span class="entry-title">{}</span>\n</div>\n'
            return fmt.format(types[type_index], title)

    #regex = r"### \$[A-Z]{3}_([A-Z]{3})\$([^\n]*\n)(.*?)(?=###|<div>|$)"
    tag = "### \$[A-Z]{3}_([A-Z]{3})\$"
    title = "( ?[^\n]*)"
    cont = "((?:\n.*?)?)(?=###|<div|$)"
    regex = tag + title + cont
    text = re.sub(regex, dict_tag, text, flags=re.DOTALL)
##    print(text)
##    input()

#    regex = "### (\$+) ((?:.+?)?)\n((?:.+?)?)(?=\n###|\n<div>|$)"
    tag = "### (\$+)"
    title = "( ?[^\n]*)"
    cont = "((?:\n.*?)?)(?=###|<div|$)"
    #print(re.findall(tag+title+cont, text, flags=re.DOTALL))
    regex = tag + title + cont
##    for x in re.findall(regex, text, flags=re.DOTALL):
##        print(x)
##    input()
    text = re.sub(regex, bio_tag, text, flags=re.DOTALL)
    return text

def events(text):
    def event_tag(match):
        title = match.group(2).strip()
        cont = match.group(3).strip()
        if match.group(1):
            event_class = "events-batch"
        else:
            event_class = "event"
        if title:
            if cont:
                fmt = '<div class="{}"><span class="entry-title">{}</span>{}\n</div>\n'
                return fmt.format(event_class, title, cont)
            else:
                fmt = '<div class="{}"><span class="entry-title">{}</span>\n</div>\n'
                return fmt.format(event_class, title)
        else:
            if cont:
                fmt = '<div class="{}">{}\n</div>\n'
                return fmt.format(event_class, cont)
            else:
                return '<div class="{}">\n</div>\n'.format(event_class, title)

    regex = "### @ ((?:RAW)?) ?(.+?)(?=\n###|$|\n<div)"
    tag = "### @ ((?:RAW)?)"
    title = "( ?[^\n]*)"
    cont = "((?:\n.*?)?)(?=###|<div|$)"
    #print(re.findall(tag+title+cont, text, flags=re.DOTALL))
    regex = tag + title + cont
    
    return re.sub(regex, event_tag, text, flags=re.DOTALL)

def tables(text):
    """Replace markdown table tags with html table tags.

    Examples:
        >>> text = "# first paragraph\\n\
| table header 1 | header 2 |\\n\
|:---------------|----------|\\n\
| table row 1 col 1 | table row 1 col 2|\\n\
| table row 2 col 1 | table row 2 col 2|"
        >>> import md2html
        >>> md2html.tables(text)
        '# first paragraph\\n\
<table>\\n\
<tr>\\n<th>table header 1</th><th>header 2</th>\\n</tr>\\n\
<tr>\\n<td>table row 1 col 1</td><td>table row 1 col 2</td>\\n</tr>\\n\
<tr>\\n<td>table row 2 col 1</td><td>table row 2 col 2</td>\\n</tr>\\n\
</table>\\n'
        """
    def format_table(match):
        table = ""
        rows = match.group(1).strip().splitlines()
        #print(rows)
        if re.search("\A\| *[:\-]+", rows[1]): # if a header row is underlined
            header = rows.pop(0)
            del rows[0] # remove the underlining row
            # remove the starting and ending pipes, and wrap each cell in html tags:
            header = re.sub("\A\||\| *\Z", "", header)
            header = ["<th>" + x.strip() + "</th>" for x in header.split("|")]
            table += "<tr>\n{}\n</tr>\n".format("".join(header))
        for row in rows:
            row = re.sub("\A\||\| *\Z", "", row)
            row = ["<td>" + x.strip() + "</td>" for x in row.split("|")]
            table += "<tr>\n{}\n</tr>\n".format("".join(row))
        return "\n<table>\n{}</table>\n".format(table)
    
    text = re.sub("\n(\|.+?)(?:\n(?![~|])|$)", format_table, text, flags=re.DOTALL)  
    return text

def pages(text):
    def page_tag(match):
        return '<a class="page" n="{}.{}"></a>'.format(group(1), group(2))
    return re.sub("PageV(\d+)P(\d+)", page_tag, text)

def milestones(text):
    return re.sub("Milestone(\d+)", '<a class="milestone" n="\1">', text)

def replace_by_regex(text):
    text = header(text)
    text = unwrap(text)
    text = paragraphs(text)
    text = editorials(text)
    text = poetry(text)
    text = titles(text)
    text = dict_units(text)
    text = events(text)
    text = tables(text)
    text = pages(text)
    text = milestones(text)
    return text


def replace_by_split(text):
    # split the text on (combinations) of new lines, spaces or html tags,
    # keeping the split characters:
    spl = re.split("((?:\n| |<[^>]+>)+)", text)
    text = ""
    skip_until = 0
    for i, t in enumerate(spl):
        if i < skip_until:
            pass
        elif t.startswith("@"): # named entities
            cls, prefix, n = re.findall("@([A-Za-z@]+)(\d)(\d+)", t)[0]
            cls = " ".join(cls.split("@"))
            cont = "".join(spl[i+2:i+1+(2*int(n))])[int(prefix):]
            prefix = spl[i+2][:int(prefix)]
            fmt = '{}<span class="named-ent {}">{}</span>'
            text += fmt.format(prefix, cls, cont)
            skip_until = i + 1 + (int(n)*2)
        elif t.startswith("Y"):
            text += '<a class="{}" n="{}"></a>'.format(t[:2], t[2:])

        else:
            text += t
    return text


def convert(text):
    text = replace_by_regex(text)
    text = replace_by_split(text)
    return HTML_HEADER + text + HTML_FOOTER


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    text = """
### |EDITOR|
# Editorial line 1
# Editorial line 2
# Editorial line 3
### | Heading 1
### || Heading 2
### $$$ Dict unit 1
# paragraph 1 paragraph1
~~paragraph 1 continued
### $DIC_TOP$ Dict unit 2
# poem line 1 hemi 1 %~% poem line 1 hemi2
# paragraph 2 @TOP23 biMadinat al Salam
### $DIC_LEX$
# untitled dict unit
~~unnamed dict unit continued
### @ Event 1
### @ RAW
# Event 1
# Event 2 @PER03 Abdallah ibn Ahmad @SRC02 Kitab al-Buldan
### $$ Name of the woman
# Description of the woman's life
| table header 1 | header 2 |
|:---------------|----------|
| table row 1 col 1 | table row 1 col 2|
| table row 2 col 1 | table row 2
~~col 2|
### |EDITOR|
# Editorial 2 line 1
# Editorial 2 line 2
"""
    html = convert(text)
    #print(html.strip())
    print(BeautifulSoup(html, 'html.parser').prettify())
