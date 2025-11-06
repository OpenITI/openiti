"""Templates for OpenITI yml files, readme files, etc.

Templates:

* MAGIC_VALUE
* HEADER_SPLITTER
* HTML_HEADER
* HTML_FOOTER
* author_yml_template
* book_yml_template
* version_yml_template
* readme_template
* text_questionnaire_template
"""

MAGIC_VALUE = "######OpenITI#"
HEADER_SPLITTER = "#META#Header#End#"

HTML_HEADER = """\
<html>
  <head>
    <style>
      .entry-title {
        font-size: 20px;
      }
    </style>
  </head>
  <body>
"""

HTML_FOOTER = """\
  </body>
</html>"""

author_yml_template = """\
00#AUTH#URI######: 
10#AUTH#ISM####AR: Fulān
10#AUTH#KUNYA##AR: Abū Fulān, Abū Fulānaŧ
10#AUTH#LAQAB##AR: Fulān al-dīn, Fulān al-dawlaŧ
10#AUTH#NASAB##AR: b. Fulān b. Fulān b. Fulān b. Fulān
10#AUTH#NISBA##AR: al-Fulānī, al-Fāʿil, al-Fulānī, al-Mufaʿʿil
10#AUTH#SHUHRA#AR: Ibn Fulān al-Fulānī
20#AUTH#BORN#####: URIs from Althurayya, comma separated
20#AUTH#DIED#####: URIs from Althurayya, comma separated
20#AUTH#RESIDED##: URIs from Althurayya, comma separated
20#AUTH#VISITED##: URIs from Althurayya, comma separated
30#AUTH#BORN###AH: YEAR-MON-DA (X+ for unknown)
30#AUTH#DIED###AH: YEAR-MON-DA (X+ for unknown)
40#AUTH#STUDENTS#: AUTH_URI from OpenITI, comma separated
40#AUTH#TEACHERS#: AUTH_URI from OpenITI, comma separated
70#AUTH#EXTID####: viaf@id, wikidata@id, src@id
80#AUTH#BIBLIO###: src@id, src@id, src@id, src@id, src@id
90#AUTH#COMMENT##: a free running comment here; you can add as many
    lines as you see fit; the main goal of this comment section is to have a
    place to record valuable information, which is difficult to formalize
    into the above given categories."""

book_yml_template = """\
00#BOOK#URI######: 
10#BOOK#GENRES###: src@keyword, src@keyword, src@keyword
10#BOOK#TITLEA#AR: Kitāb al-Muʾallif
10#BOOK#TITLEB#AR: Risālaŧ al-Muʾallif
20#BOOK#WROTE####: URIs from Althurayya, comma separated
30#BOOK#WROTE##AH: YEAR-MON-DA (X+ for unknown)
40#BOOK#RELATED##: URI of a book from OpenITI, or [Author's Title],
    followed by abbreviation for relation type between brackets (see
    book_relations repo). Only include relations with older books. Separate
    related books with semicolon.
70#BOOK#EXTID####: viaf@id, wikidata@id, src@id
80#BOOK#EDITIONS#: permalink, permalink, permalink
80#BOOK#LINKS####: permalink, permalink, permalink
80#BOOK#MSS######: permalink, permalink, permalink
80#BOOK#STUDIES##: permalink, permalink, permalink
80#BOOK#TRANSLAT#: permalink, permalink, permalink
90#BOOK#COMMENT##: a free running comment here; you can add as many
    lines as you see fit; the main goal of this comment section is to have a
    place to record valuable information, which is difficult to formalize
    into the above given categories."""

version_yml_template = """\
00#VERS#LENGTH###:
00#VERS#CLENGTH##:
00#VERS#URI######: 
80#VERS#BASED####: permalink, permalink, permalink
80#VERS#COLLATED#: permalink, permalink, permalink
80#VERS#LINKS####: all@id, vol1@id, vol2@id, vol3@id, volX@id
90#VERS#ANNOTATOR: the name of the annotator (latin characters; please
    use consistently)
90#VERS#COMMENT##: a free running comment here; you can add as many
    lines as you see fit; the main goal of this comment section is to have a
    place to record valuable information, which is difficult to formalize
    into the above given categories.
90#VERS#DATE#####: YYYY-MM-DD
90#VERS#ISSUES###: formalized issues, separated with commas"""

readme_template = """
Please, copy-paste questions from `text_questionnaire.md`
into this file and answer the questions.
If you have done so, please check if `text_questionnaire.md`
has been updated and has new questions.
"""

text_questionnaire_template = """
# Please, answer the following questions about the text that you work on

[[Last update: August 15, 2016]]

Copy-paste these questions into the README.md file and answer them.

## 1. Describe why you chose this specific version of the text. Why others, in your opinion, are worse?

Type your response here.

## 2. Which edition you used for collation? How close the text to the edition? Is pagination the same?

Type your response here.

## 3. Have you noticed any typos? If yes, how many? (Guesstimate is fine)

Type your response here.

## 4. Add any comments on the text

Type your response here

## 5. ...

## Comments by : [Firstname Lastname]
"""

# TEMPLATES FOR MANUSCRIPT / DOCUMENT FILES:

location_yml_template = """\
00#LOC#URI#######: 
10#LOC#CITY#AR###: name of the city, in Arabic [one-to-one transcription]
10#LOC#CITY#EN###: name of the city, in English
10#LOC#INST#AR###: name of the institution, in Arabic [one-to-one transcription]
10#LOC#INST#EN###: name of the institution, in English
70#LOC#EXTID#####: wikidata@id, src@id
80#LOC#CATALOGS##: permalink, permalink, permalink [worldcat or other]
80#LOC#LINKS#####: WEBSITE@permalink, CATALOGUE@permalink, permalink
90#LOC#COMMENT###: a free running comment here; you can add as many
    lines as you see fit; the main goal of this comment section is to have a
    place to record valuable information, which is difficult to formalize
    into the above given categories."""

manuscript_yml_template = """\
00#MS#URI########: 
00#MS#SHELFM#####: shelfmark, shelfmark 
    [in one-to-one transcription]
10#MS#TITLE#AR###: title(s) on the front page and/or of parts
    [in one-to-one transcription; replace language code if needed;
    semicolon-separated]
30#MS#DATE#AH####: date of copy in hijri era: DD-MM-YYYY, 
    DD-MM-YYYY@page, DD-MM-YYYY@page_range
30#MS#PLACE######: place of copy: place, URI@page
30#MS#PERSONS####: COPYIST@URI, AUTHOR@URI, PATRON@URI, READER@URI
30#MS#INSTITUT###: institutions mentioned
30#MS#SCRIPT#####: Maghribi/Naskh/Nastacliq/Hebrew/...
40#MS#INCIPIT####: first 5 lines (max.) of transcription
40#MS#EXPLICIT###: last 5 lines (max.) of transcription
40#MS#COLOPHON###: transcription of colophon
40#MS#HEIGHT#MM##: height, in mm (if needed replace MM by CM/IN/...)
40#MS#WIDTH#MM###: width, in mm (if needed replace MM by CM/IN/...)
40#MS#INK########: color, color
40#MS#LINESPP####: lines per page: n, n@page_range
40#MS#BINDING####: description of the binding
40#MS#STAMPS#####: seals and stamps: URI@page
40#MS#HANDS######: description of the different hands in the ms.
40#MS#DECO#######: description of the decorations in the ms.
40#MS#COLUMNS####: number of columns in the manuscript: n, n@page_range
40#MS#PARTS######: URI@page_range, URI@page_range
40#MS#VOLS#######: X of Y
70#MS#EXTID######: wikidata@id, src@id
80#MS#LINKS######: SOURCE@permalink, IIIF@permalink, PDF@permalink, 
    IMAGES@permalink, BIBTEX@permalink
80#MS#CATREF#####: reference to a manuscript catalogue 
90#MS#COMMENT####: a free running comment here; you can add as many
    lines as you see fit; the main goal of this comment section is 
    to have a place to record valuable information, which is 
    difficult to formalize into the above given categories.
90#MS#ISSUES#####: comma-separated list of issues:
    INCORRECT_FOLIO_ORDER, CORRECTED_FOLIO_ORDER,
    NO_FOLIO_NUMBERS, INCOMPLETE, FRAGMENT"""

transcription_yml_template = """\
00#TRNS#CLENGTH##: number of characters
00#TRNS#LENGTH###: number of tokens
00#TRNS#URI######: 
40#TRNS#PAGES####: pages transcribed: page_range
80#TRNS#LINEMODEL: segmentation model used for line segmentation
    (name and/or URL)
80#TRNS#REGMODEL#: segmentation model used for region segmentation
    (name and/or URL)
80#TRNS#RECMODEL#: recognition model used for transcription
    (name and/or URL)
80#TRNS#LINKS####: SOURCE@permalink, IIIF@permalink, PDF@permalink, 
    BIBTEX@permalink
90#TRNS#CONTRIB##: TRANSCRIPTION@name, CORRECTION@name
   (latin characters; please use consistently)
90#TRNS#COMMENT##: a free running comment here; you can add as many
    lines as you see fit; the main goal of this comment section is to have a
    place to record valuable information, which is difficult to formalize
    into the above given categories.
90#TRNS#DATE#####: YYYY-MM-DD
90#TRNS#ISSUES###: comma-separated list of issues: UNCORRECTED_OCR, 
    TRANSCRIPTION_ERRORS, INCOMPLETE_TRANSCRIPTION"""
