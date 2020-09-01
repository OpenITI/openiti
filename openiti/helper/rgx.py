"""This module provides useful regular expression patterns for OpenITI texts.
"""

# NB: "(?s)" = inline flag (to be put at the start of a regex pattern)
# that forces the regex module to consider the dot as representing any
# character including newline (= using flag re.DOTALL while compiling a regex)
dotall = (?s)

# 1. Characters, words and spaces

ar_char = re.compile("""
    ء	| # ARABIC LETTER HAMZA
    آ	| # ARABIC LETTER ALEF WITH MADDA ABOVE
    أ	| # ARABIC LETTER ALEF WITH HAMZA ABOVE
    ؤ	| # ARABIC LETTER WAW WITH HAMZA ABOVE
    إ	| # ARABIC LETTER ALEF WITH HAMZA BELOW
    ئ	| # ARABIC LETTER YEH WITH HAMZA ABOVE
    ا	| # ARABIC LETTER ALEF
    ب	| # ARABIC LETTER BEH
    ة	| # ARABIC LETTER TEH MARBUTA
    ت	| # ARABIC LETTER TEH
    ث	| # ARABIC LETTER THEH
    ج	| # ARABIC LETTER JEEM
    ح	| # ARABIC LETTER HAH
    خ	| # ARABIC LETTER KHAH
    د	| # ARABIC LETTER DAL
    ذ	| # ARABIC LETTER THAL
    ر	| # ARABIC LETTER REH
    ز	| # ARABIC LETTER ZAIN
    س	| # ARABIC LETTER SEEN
    ش	| # ARABIC LETTER SHEEN
    ص	| # ARABIC LETTER SAD
    ض	| # ARABIC LETTER DAD
    ط	| # ARABIC LETTER TAH
    ظ	| # ARABIC LETTER ZAH
    ع	| # ARABIC LETTER AIN
    غ	| # ARABIC LETTER GHAIN
    ـ	| # ARABIC TATWEEL
    ف	| # ARABIC LETTER FEH
    ق	| # ARABIC LETTER QAF
    ك	| # ARABIC LETTER KAF
    ل	| # ARABIC LETTER LAM
    م	| # ARABIC LETTER MEEM
    ن	| # ARABIC LETTER NOON
    ه	| # ARABIC LETTER HEH
    و	| # ARABIC LETTER WAW
    ى	| # ARABIC LETTER ALEF MAKSURA
    ي	| # ARABIC LETTER YEH
    ً	| # ARABIC FATHATAN
    ٌ	| # ARABIC DAMMATAN
    ٍ	| # ARABIC KASRATAN
    َ	| # ARABIC FATHA
    ُ	| # ARABIC DAMMA
    ِ	| # ARABIC KASRA
    ّ	| # ARABIC SHADDA
    ْ	| # ARABIC SUKUN
    ٠	| # ARABIC-INDIC DIGIT ZERO
    ١	| # ARABIC-INDIC DIGIT ONE
    ٢	| # ARABIC-INDIC DIGIT TWO
    ٣	| # ARABIC-INDIC DIGIT THREE
    ٤	| # ARABIC-INDIC DIGIT FOUR
    ٥	| # ARABIC-INDIC DIGIT FIVE
    ٦	| # ARABIC-INDIC DIGIT SIX
    ٧	| # ARABIC-INDIC DIGIT SEVEN
    ٨	| # ARABIC-INDIC DIGIT EIGHT
    ٩	| # ARABIC-INDIC DIGIT NINE
    ٮ	| # ARABIC LETTER DOTLESS BEH
    ٰ	| # ARABIC LETTER SUPERSCRIPT ALEF
    ٹ	| # ARABIC LETTER TTEH
    پ	| # ARABIC LETTER PEH
    چ	| # ARABIC LETTER TCHEH
    ژ	| # ARABIC LETTER JEH
    ک	| # ARABIC LETTER KEHEH
    گ	| # ARABIC LETTER GAF
    ی	| # ARABIC LETTER FARSI YEH
    ے	| # ARABIC LETTER YEH BARREE
    ۱	| # EXTENDED ARABIC-INDIC DIGIT ONE
    ۲	| # EXTENDED ARABIC-INDIC DIGIT TWO
    ۳	| # EXTENDED ARABIC-INDIC DIGIT THREE
    ۴	| # EXTENDED ARABIC-INDIC DIGIT FOUR
    ۵	| # EXTENDED ARABIC-INDIC DIGIT FIVE
    """, re.VERBOSE)
##‌        | # ZERO WIDTH NON-JOINER
##‍        | # ZERO WIDTH JOINER
##    """, re.VERBOSE)
ar_tok = ar_char + "+"  # regex for one Arabic token

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
space_word = "(?:{}{})".format(space, ar_tok)

# 2. URIs and OpenITI filenames:

# OpenITI URIs
auth = "\d{4}(?:[A-Z][a-z])+"
book = auth + "\.(?:[A-Z][a-z])+"
version = book + "\w+(?:Vols)?(?:BK\d+|[A-Z])-\w{3}\d+"

# OpenITI text file names:
extensions = ["inProgress", "completed", "mARkdown"]
ext_regex  = "(?:\.{})? ".format("|\.".join(extensions))
version_file = version+ext_regex

# OpenITI yml file names:
yml ="\.yml"
auth_yml = auth+yml
book_yml = book+yml
version_yml = version+yml

# 3. OpenITI mARkdown tags

# Page numbers:
vol_page = "PageV[^P]+P\d+"
vol_no = "PageV([^P]+)P\d+"
page_no = "PageV[^P]+P(\d+)"
page = dotall + r"(?<={}|{}).+?(?:{}|\Z)".format(vol_page, header_splitter, vol_page)

# Hierarchical section tags: 
section_tag = "### \|+ "
section_title = section_tag + "([^\r\n]*)"
section = dotall + section_tag + ".+?(?=###)"
section_text = dotall + section_tag + "[^\r\n]*[\r\n]+(.+?)(?=###)"

# biographies
bio_tag = "### (?:|+ )$+ "
bio = dotall + bio_tag + "[^\r\n]*[\r\n]+.+?(?=###)"
bio_title = bio_tag + "([^\r\n]*)"
bio_text = dotall + bio_tag + "[^\r\n]*[\r\n]+(.+?)(?=###)"

bio_man_tag = "### (?:|+ )$ "
bio_man = dotall + bio_man_tag + "[^\r\n]*[\r\n]+.+?(?=###)"
bio_man_title = bio_man_tag + "([^\r\n]*)"
bio_man_text = dotall + bio_man_tag + "[^\r\n]*[\r\n]+(.+?)(?=###)"

bio_woman_tag = "### (?:|+ )$$ "
bio_woman = dotall + bio_woman_tag + "[^\r\n]*[\r\n]+.+?(?=###)"
bio_woman_title = bio_woman_tag + "([^\r\n]*)"
bio_woman_text = dotall + bio_woman_tag + "[^\r\n]*[\r\n]+(.+?)(?=###)

# editorial sections:
editorial_tag = "### |EDITOR|"
editorial = dotall + editorial_tag + r"[^\r\n]*[\r\n]+.+?(?=###|\Z)"
editorial_text = dotall + editorial_tag + "[^\r\n]*[\r\n]+(.+?)(?=###|\Z)"

# paratext sections:
paratext_tag = "### |PARATEXT|"
paratext = dotall + paratext_tag + r"[^\r\n]*[\r\n]+.+?(?=###|\Z)"
paratext_text = dotall + paratext_tag + r"[^\r\n]*[\r\n]+(.+?)(?=###|\Z)" 

# paragraphs:
paragraph_tag = r"(?<=[\r\n])# "
paragraph = r"(?<=[\r\n])# [^#]+"
paragraph_text = r"(?<=[\r\n]# )[^#]+"
word_in_paragraph = r"(?<=[\r\n]# )[^#]+?{}[^#]+" # insert word using string formatting

# years:
year = r"\bY[A-Z]?\d+"
year_born = r"\bYB\d+"
year_died = r"\bYD\d+"

# analytical tag pattern:
anal_tag = "(?:@[A-Z]{3})?[@#][A-Z]{3}(?:$\w+)?(?:@?\d\d+)?"
tag_range = "|".join([str(i)+"%(w)s{"+str(i)+"}" for i in range(1,21)])
tag_range = "@?(?:\d(?:" + tag_range % {"w": space_word} + "))?"
anal_tag_text = "(?:@[A-Z]{3})?@[A-Z]{3}(?:$\w+)?" + tag_range
#(this is identical to:)
#anal_tag_text = """(?x)                                 # verbose inline flag
#                   (?:@[A-Z]{3})?                       # optional personal ID
#                   @[A-Z]{3}(?:$\w+)?                   # tag name
#                   (?:$\w+)?                            # optional ID
#                   @?(?:\d                              # tag range: prefix
#                     (?:1%(w)s{1}|2%(w)s{2}|3%(w)s{3}|  # tag range: no. of words
#                     4%(w)s{4}|5%(w)s{5}|6%(w)s{6}|
#                     7%(w)s{7}|8%(w)s{8}|9%(w)s{9}|
#                     10%(w)s{10}|11%(w)s{11}|12%(w)s{12}|
#                     13%(w)s{13}|14%(w)s{14}|15%(w)s{15}|
#                     16%(w)s{16}|17%(w)s{17}))?""" % {"w": space_word}


