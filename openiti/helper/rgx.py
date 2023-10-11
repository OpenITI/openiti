"""This module provides useful regular expression patterns for OpenITI texts.

The patterns are roughly divided into the following sections:

# 1. Characters, words and spaces
# 2. OpenITI URIs and filenames
# 3. OpenITI mARkdown tags


See also:

* https://alraqmiyyat.github.io/mARkdown/
* https://docs.python.org/3/library/re.html
* https://pypi.org/project/regex/

"""

import re

# NB: "(?s)" = inline flag (to be put at the start of a regex pattern)
# that forces the regex machine to consider the dot as representing any
# character including newline (= using flag re.DOTALL while compiling a regex)
dotall = "(?s)"

# 1. Characters, words and spaces

ar_chars = """\
ء	ARABIC LETTER HAMZA
آ	ARABIC LETTER ALEF WITH MADDA ABOVE
أ	ARABIC LETTER ALEF WITH HAMZA ABOVE
ؤ	ARABIC LETTER WAW WITH HAMZA ABOVE
إ	ARABIC LETTER ALEF WITH HAMZA BELOW
ئ	ARABIC LETTER YEH WITH HAMZA ABOVE
ا	ARABIC LETTER ALEF
ب	ARABIC LETTER BEH
ة	ARABIC LETTER TEH MARBUTA
ت	ARABIC LETTER TEH
ث	ARABIC LETTER THEH
ج	ARABIC LETTER JEEM
ح	ARABIC LETTER HAH
خ	ARABIC LETTER KHAH
د	ARABIC LETTER DAL
ذ	ARABIC LETTER THAL
ر	ARABIC LETTER REH
ز	ARABIC LETTER ZAIN
س	ARABIC LETTER SEEN
ش	ARABIC LETTER SHEEN
ص	ARABIC LETTER SAD
ض	ARABIC LETTER DAD
ط	ARABIC LETTER TAH
ظ	ARABIC LETTER ZAH
ع	ARABIC LETTER AIN
غ	ARABIC LETTER GHAIN
ـ	ARABIC TATWEEL
ف	ARABIC LETTER FEH
ق	ARABIC LETTER QAF
ك	ARABIC LETTER KAF
ل	ARABIC LETTER LAM
م	ARABIC LETTER MEEM
ن	ARABIC LETTER NOON
ه	ARABIC LETTER HEH
و	ARABIC LETTER WAW
ى	ARABIC LETTER ALEF MAKSURA
ي	ARABIC LETTER YEH
ً	ARABIC FATHATAN
ٌ	ARABIC DAMMATAN
ٍ	ARABIC KASRATAN
َ	ARABIC FATHA
ُ	ARABIC DAMMA
ِ	ARABIC KASRA
ّ	ARABIC SHADDA
ْ	ARABIC SUKUN
٠	ARABIC-INDIC DIGIT ZERO
١	ARABIC-INDIC DIGIT ONE
٢	ARABIC-INDIC DIGIT TWO
٣	ARABIC-INDIC DIGIT THREE
٤	ARABIC-INDIC DIGIT FOUR
٥	ARABIC-INDIC DIGIT FIVE
٦	ARABIC-INDIC DIGIT SIX
٧	ARABIC-INDIC DIGIT SEVEN
٨	ARABIC-INDIC DIGIT EIGHT
٩	ARABIC-INDIC DIGIT NINE
ٮ	ARABIC LETTER DOTLESS BEH
ٰ	ARABIC LETTER SUPERSCRIPT ALEF
ٹ	ARABIC LETTER TTEH
پ	ARABIC LETTER PEH
چ	ARABIC LETTER TCHEH
ژ	ARABIC LETTER JEH
ک	ARABIC LETTER KEHEH
گ	ARABIC LETTER GAF
ی	ARABIC LETTER FARSI YEH
ے	ARABIC LETTER YEH BARREE
۱	EXTENDED ARABIC-INDIC DIGIT ONE
۲	EXTENDED ARABIC-INDIC DIGIT TWO
۳	EXTENDED ARABIC-INDIC DIGIT THREE
۴	EXTENDED ARABIC-INDIC DIGIT FOUR
۵	EXTENDED ARABIC-INDIC DIGIT FIVE"""
##‌	ZERO WIDTH NON-JOINER
##‍	ZERO WIDTH JOINER"""
ar_chars = "".join([x.split("\t")[0] for x in ar_chars.splitlines()])
ar_char = "[{}]".format(ar_chars) # regex for one Arabic character
ar_tok = "[{}]+".format(ar_chars) # regex for one Arabic token

noise = re.compile(""" ّ    | # Tashdīd / Shadda
                       َ    | # Fatḥa
                       ً    | # Tanwīn Fatḥ / Fatḥatān
                       ُ    | # Ḍamma
                       ٌ    | # Tanwīn Ḍamm / Ḍammatān
                       ِ    | # Kasra
                       ٍ    | # Tanwīn Kasr / Kasratān
                       ْ    | # Sukūn
                       ۡ    | # Quranic Sukūn
                       ࣰ    | # Quranic Open Fatḥatān
                       ࣱ    | # Quranic Open Ḍammatān
                       ࣲ    | # Quranic Open Kasratān
                       ٰ    | # Dagger Alif
                       ـ     # Taṭwīl / Kashīda
                   """, re.VERBOSE)

any_unicode_letter = "[^\W\d_]"
any_word = any_unicode_letter + "+"

###### regex module (alternative to re module):
#any_unicode_letter = "\p{L}"
#any_unicode_diacritic = "\p{M}"

space ="(?: |[\r\n]+~~|PageV[^P]+P\d+)+"
space ="(?:\W|PageV[^P]+P\d+)+" # also takes care of commas etc.
space_word = "(?:{}{})".format(space, ar_tok)


# 2. URIs and OpenITI filenames:

# OpenITI URIs
language_codes = [        # ISO 639-2B language codes: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
    "ara", # Arabic
    "per", # Persian
    "urd", # Urdu
    "heb", # Hebrew
    "arm", # Armenian
    "ave", # Avestan
    "geo", # Georgian
    "kur", # Kurdish
    "pus", # Pashtu
    "swa", # Swahili
    ]
auth = r"\b\d{4}[A-Z][a-zA-Z]+"
book = auth + "\.[A-Z][a-zA-Z]+"
version = book + "\.\w+(?:Vols)?(?:BK\d+|[A-Z])*-(?:%s)+\d+" % "|".join(language_codes)
author_uri = auth
book_uri = book
version_uri = version

# OpenITI text file names:
extensions = ["inProgress", "completed", "mARkdown"]
ext_regex = r"(?:\.{}|(?= |\n|\r|\Z))".format("|\.".join(extensions))
version_file = version+ext_regex
version_fp = r"%s[/\\]%s[/\\]%s" % (auth, book, version_file)

# OpenITI yml file names:
yml ="\.yml"
auth_yml = auth+yml
book_yml = book+yml
version_yml = version+yml

auth_yml_fp = r"%s[/\\]%s" % (auth, auth_yml)
book_yml_fp = r"%s[/\\]%s[/\\]%s" % (auth, book, book_yml)
version_yml_fp = r"%s[/\\]%s[/\\]%s" % (auth, book, version_yml)

# 3. OpenITI mARkdown tags

magic_value = "######OpenITI#"
header_splitter = "#META#Header#End#"

# Page numbers:
vol_page = "Page(?:Beg|End)?V[^P]+P\d+[ABab]?"
vol_no = "Page(?:Beg|End)?V([^P]+)P\d+[ABab]?"
page_no = "Page(?:Beg|End)?V[^P]+P(\d+[ABab]?)"
vol_page_3 = "Page(?:Beg|End)?V[^P]{2}P\d{3}[ABab]?"
vol_page_4 = "Page(?:Beg|End)?V[^P]{2}P\d{4}[ABab]?"
page = dotall + r"(?:(?<={})|(?<={})|(?<={})).+?(?:{}|\Z)".format(vol_page_3,
                    vol_page_4, header_splitter, vol_page)

# Hierarchical section tags:
section_tag = "### \|\w*\|* "
section_title = section_tag + "([^\r\n]*)"
section = dotall + section_tag + r".+?(?=###|\Z)"
section_text = dotall + section_tag + "[^\r\n]*[\r\n]+(.+?)(?=###|\Z)"

# biographies
bio_tag = r"### (?:\|+ )?\$+ "
bio = dotall + bio_tag + "[^\r\n]*[\r\n]+.+?(?=###|\Z)"
bio_title = bio_tag + "([^\r\n]*)"
bio_text = dotall + bio_tag + "[^\r\n]*[\r\n]+(.+?)(?=###|\Z)"

bio_man_tag = "### (?:\|+ )?\$ "
bio_man = dotall + bio_man_tag + "[^\r\n]*[\r\n]+.+?(?=###|\Z)"
bio_man_title = bio_man_tag + "([^\r\n]*)"
bio_man_text = dotall + bio_man_tag + "[^\r\n]*[\r\n]+(.+?)(?=###|\Z)"

bio_woman_tag = "### (?:\|+ )?\$\$ "
bio_woman = dotall + bio_woman_tag + "[^\r\n]*[\r\n]+.+?(?=###|\Z)"
bio_woman_title = bio_woman_tag + "([^\r\n]*)"
bio_woman_text = dotall + bio_woman_tag + "[^\r\n]*[\r\n]+(.+?)(?=###|\Z)"

# editorial sections:
editorial_tag = "### \|EDITOR\|"
editorial = dotall + editorial_tag + r"[^\r\n]*[\r\n]+.+?(?=###|\Z)"
editorial_text = dotall + editorial_tag + "[^\r\n]*[\r\n]+(.+?)(?=###|\Z)"

# paratext sections:
paratext_tag = "### \|PARATEXT\|"
paratext = dotall + paratext_tag + r"[^\r\n]*[\r\n]+.+?(?=###|\Z)"
paratext_text = dotall + paratext_tag + r"[^\r\n]*[\r\n]+(.+?)(?=###|\Z)"

# paragraphs:
paragraph_tag = r"(?<=[\r\n])# "
paragraph = r"(?<=[\r\n])# [^#]+"
paragraph_text = r"(?<=[\r\n]# )[^#]+"
word_in_paragraph = r"(?<=[\r\n])# [^#]+?{}[^#]+" # insert word using string formatting
word_in_paragraph_text= r"(?<=[\r\n]# )[^#]+?{}[^#]+" # insert word using string formatting

# years:
year = r"\bY[A-Z]?\d+"
year_born = r"\bYB\d+"
year_died = r"\bYD\d+"

# milestones:
ms = r"\bms[A-Z]?\d+"

# analytical tag pattern:
anal_tag = "(?:@[A-Z]{3})?[@#][A-Z]{3}(?:\$[\w+\-]+)?(?:@?\d\d+)?"
tag_range = "|".join([str(i)+"%(w)s{"+str(i)+"}" for i in range(1,21)])
tag_range = "@?(?:\d\W*?(?:" + tag_range % {"w": space_word} + "))?"
anal_tag_text = "(?:@[A-Z]{3})?[@#][A-Z]{3}(?:\$[\w+\-]+)?" + tag_range

#(this is identical to:)
#anal_tag_text = """(?x)                                 # verbose inline flag
#                   (?:@[A-Z]{3})?                       # optional personal ID
#                   [@#][A-Z]{3}                         # tag name/category
#                   (?:_[a-zA-Z]+)*                      # subcategory/ies
#                   (?:$[\w\-]+)?                        # named entity ID
#                   @?(?:\d                              # tag range: prefix
#                     (?:1%(w)s{1}|2%(w)s{2}|3%(w)s{3}|  # tag range: no. of words
#                     4%(w)s{4}|5%(w)s{5}|6%(w)s{6}|
#                     7%(w)s{7}|8%(w)s{8}|9%(w)s{9}|
#                     10%(w)s{10}|11%(w)s{11}|12%(w)s{12}|
#                     13%(w)s{13}|14%(w)s{14}|15%(w)s{15}|
#                     16%(w)s{16}|17%(w)s{17}))?""" % {"w": space_word}

# match all OpenITI mARkdown tags:
all_tags = r"|".join([
    vol_page, ms, year, 
    r"### [\$|]\w*[\$|]*",  # section headers, paratext, editor, biographies
    r"[#@]\S+",  # ampersand/hash followed by any combination of non-whitespace chars
    r"# ",
    r"~~",
    r"%~%"
    ])

# match any html tag:
html_tags = r"<[^>]+>"
html_tag_w_content = dotall + r"<\W*([a-zA-Z]+)<[^>]+>.+?<\W*/\1\W*>"

if __name__ == "__main__":
    # tests for the regex patterns involved:
    verbose=True
    def test_regex_findall(ptrn, txt, res):
        shouldbe = "Should be {}".format(res)
        if verbose:
            print(re.findall(ptrn, txt))
        assert re.findall(ptrn, txt) == res, shouldbe

    # test word/character regexes:
    
    test_regex_findall(ar_char, "كتاب kitab", ['ك', 'ت', 'ا', 'ب'])
    test_regex_findall(ar_tok, "كتاب kitab", ['كتاب'])
    res = ['ك', 'ت', 'ا', 'ب', 'k', 'i', 't', 'a', 'b']
    test_regex_findall(any_unicode_letter, "كتاب_kitab", res)
    test_regex_findall(any_word, "كتاب_kitab", ['كتاب', 'kitab'])
    txt = """الكلمة الأولى
~~السطر الثاني PageV01P003 الصفحة التالية"""
    res = [' الأولى', '\n~~السطر', ' الثاني', ' PageV01P003 الصفحة', ' التالية']
    test_regex_findall(space_word, txt, res)

    # test URI/fn regexes:
    
    fn = "0255Jahiz.Hayawan.Shamela0001234VolsBk1-ara1.completed"
    test_regex_findall(auth, fn, ["0255Jahiz"])
    test_regex_findall(book, fn, ["0255Jahiz.Hayawan"])
    test_regex_findall(version, fn,
                       ["0255Jahiz.Hayawan.Shamela0001234VolsBk1-ara1"])
    test_regex_findall(version_file, fn,
                       ["0255Jahiz.Hayawan.Shamela0001234VolsBk1-ara1.completed"])
    fn = "0255Jahiz.Hayawan.Shamela0001234-per3"
    test_regex_findall(version, fn,
                       ["0255Jahiz.Hayawan.Shamela0001234-per3"])
    test_regex_findall(version_file, fn,
                       ["0255Jahiz.Hayawan.Shamela0001234-per3"])
    fps = """
0255Jahiz/0255Jahiz.yml
0255Jahiz/0255Jahiz.Hayawan/0255Jahiz.Hayawan.yml
0255Jahiz/0255Jahiz.Hayawan/0255Jahiz.Hayawan.Shamela0001234-per3.inProgress
0255Jahiz/0255Jahiz.Hayawan/0255Jahiz.Hayawan.Shamela0001234-per3.yml
"""
    test_regex_findall(auth_yml, fps, ["0255Jahiz.yml"])
    test_regex_findall(book_yml, fps, ["0255Jahiz.Hayawan.yml"])
    test_regex_findall(version_yml, fps, ["0255Jahiz.Hayawan.Shamela0001234-per3.yml"])
    test_regex_findall(auth_yml_fp, fps,
                       ["0255Jahiz/0255Jahiz.yml"])
    test_regex_findall(book_yml_fp, fps,
                       ["0255Jahiz/0255Jahiz.Hayawan/0255Jahiz.Hayawan.yml"])
    test_regex_findall(version_yml_fp, fps,
                       ["0255Jahiz/0255Jahiz.Hayawan/0255Jahiz.Hayawan.Shamela0001234-per3.yml"])
    test_regex_findall(version_fp, fps,
                       ["0255Jahiz/0255Jahiz.Hayawan/0255Jahiz.Hayawan.Shamela0001234-per3.inProgress"])
    
    # test OpenITI mARkdown regexes:

    txt = """######OpenITI#
#META# blabla
#META#Header#End#

Text text text"""
    test_regex_findall(header_splitter, txt, ["#META#Header#End#"])
    test_regex_findall(magic_value, txt, ["######OpenITI#"])
    pages = "PageV01P001 PageV02P0002 PageVM3P003 Pagev04P004 PageV05p0005"
    test_regex_findall(vol_page, pages, ["PageV01P001", "PageV02P0002", "PageVM3P003"])
    test_regex_findall(vol_no, pages, ["01", "02", "M3"])
    test_regex_findall(page_no, pages, ["001", "0002", "003"])
    pages = "#META#Header#End#\n\npage text 1 PageV01P001 page text 2 PageV02P0002 text without page number"
    res = ['\n\npage text 1 PageV01P001', ' page text 2 PageV02P0002', ' text without page number']
    test_regex_findall(page, pages, res)
    
    txt = """### | heading 1
text section 1
### || heading 2
text section 2
text section 2"""
    test_regex_findall(section_tag, txt, ["### | ", "### || "])
    test_regex_findall(section_title, txt, ["heading 1", "heading 2"])
    test_regex_findall(section, txt, ['### | heading 1\ntext section 1\n',
                                      '### || heading 2\ntext section 2\ntext section 2'])
    test_regex_findall(section_text, txt, ['text section 1\n',
                                           'text section 2\ntext section 2'])
    
    txt = """### | biographies
text section 1
### || $ biography 1
text biography 1
### $$ biography 2
text biography 2"""
    test_regex_findall(bio_tag, txt, ["### || $ ", "### $$ "])
    test_regex_findall(bio_title, txt, ["biography 1", "biography 2"])
    test_regex_findall(bio, txt, ["### || $ biography 1\ntext biography 1\n",
                                  "### $$ biography 2\ntext biography 2"])
    test_regex_findall(bio_text, txt, ["text biography 1\n",
                                       "text biography 2"])

    
    test_regex_findall(bio_man_tag, txt, ["### || $ "])
    test_regex_findall(bio_man_title, txt, ["biography 1"])
    test_regex_findall(bio_man, txt, ["### || $ biography 1\ntext biography 1\n"])
    test_regex_findall(bio_man_text, txt, ["text biography 1\n"])
    

    test_regex_findall(bio_woman_tag, txt, ["### $$ "])
    test_regex_findall(bio_woman_title, txt, ["biography 2"])
    test_regex_findall(bio_woman, txt, ["### $$ biography 2\ntext biography 2"])
    test_regex_findall(bio_woman_text, txt, ["text biography 2"])


    txt = """
### |EDITOR|
editorial intro
### | title
main text
### |EDITOR|
editorial outro"""
    test_regex_findall(editorial_tag, txt, ["### |EDITOR|", "### |EDITOR|"])
    test_regex_findall(editorial, txt, ["### |EDITOR|\neditorial intro\n",
                                        "### |EDITOR|\neditorial outro"])
    test_regex_findall(editorial_text, txt, ["editorial intro\n",
                                             "editorial outro"])

    txt = """
### |PARATEXT|
paratext intro
### | title
main text
### |PARATEXT|
paratext outro"""
    test_regex_findall(paratext_tag, txt, ["### |PARATEXT|", "### |PARATEXT|"])
    test_regex_findall(paratext, txt, ["### |PARATEXT|\nparatext intro\n",
                                        "### |PARATEXT|\nparatext outro"])
    test_regex_findall(paratext_text, txt, ["paratext intro\n",
                                             "paratext outro"])
    
    txt = """### | section title
# paragraph 1
~~paragraph 1 continued
# paragraph 2
### | section 2
# paragraph 3"""
    test_regex_findall(paragraph_tag, txt, ["# ", "# ", "# "])
    test_regex_findall(paragraph, txt, ["# paragraph 1\n~~paragraph 1 continued\n",
                                        "# paragraph 2\n",
                                        "# paragraph 3"])
    test_regex_findall(paragraph_text, txt, ["paragraph 1\n~~paragraph 1 continued\n",
                                             "paragraph 2\n",
                                             "paragraph 3"])
    w = word_in_paragraph.format("continued")
    test_regex_findall(w, txt, ["# paragraph 1\n~~paragraph 1 continued\n"])
    w = word_in_paragraph_text.format("continued")
    test_regex_findall(w, txt, ["paragraph 1\n~~paragraph 1 continued\n"])

    txt = """wulida YB0100 sana mia wa-mata YD170 sana mia wa-sabcin"""
    test_regex_findall(year, txt, ["YB0100", "YD170"])
    test_regex_findall(year_born, txt, ["YB0100"])
    test_regex_findall(year_died, txt, ["YD170"])

    txt = "مع #PER$0310Tabari أبي جرير الطبري #PER$0279Baladhuri@12 وأحمد البلاذري"
    test_regex_findall(anal_tag, txt, ["#PER$0310Tabari", "#PER$0279Baladhuri@12"])
    test_regex_findall(anal_tag_text, txt, ["#PER$0310Tabari", "#PER$0279Baladhuri@12 وأحمد البلاذري"])


    txt = """مع @MGR@PER$0310Tabari أبي جرير الطبري @PER$0279Baladhuri@12 وأحمد\n~~البلاذري"""
    test_regex_findall(anal_tag, txt, ["@MGR@PER$0310Tabari", "@PER$0279Baladhuri@12"])
    test_regex_findall(anal_tag_text, txt, ["@MGR@PER$0310Tabari",
                                            "@PER$0279Baladhuri@12 وأحمد\n~~البلاذري"])

    txt = """قال: @QUR$1_1-2@08 ( بسم الله الرحمن الرحيم الحمد لله رب العلمين )"""
    test_regex_findall(anal_tag, txt, ["@QUR$1_1-2@08"])
    test_regex_findall(anal_tag_text, txt, ["@QUR$1_1-2@08 ( بسم الله الرحمن الرحيم الحمد لله رب العلمين"])


    print("finished testing")

