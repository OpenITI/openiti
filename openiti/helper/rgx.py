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
dotall = r"(?s)"

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
"""
##‌	ZERO WIDTH NON-JOINER
##‍	ZERO WIDTH JOINER"""
ar_chars = "".join([x.split("\t")[0] for x in ar_chars.splitlines()])

ar_nums = """
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
۰	EXTENDED ARABIC-INDIC DIGIT ZERO
۱	EXTENDED ARABIC-INDIC DIGIT ONE
۲	EXTENDED ARABIC-INDIC DIGIT TWO
۳	EXTENDED ARABIC-INDIC DIGIT THREE
۴	EXTENDED ARABIC-INDIC DIGIT FOUR
۵	EXTENDED ARABIC-INDIC DIGIT FIVE
۶	EXTENDED ARABIC-INDIC DIGIT SIX
۷	EXTENDED ARABIC-INDIC DIGIT SEVEN
۸	EXTENDED ARABIC-INDIC DIGIT EIGHT
۹	EXTENDED ARABIC-INDIC DIGIT NINE
"""
ar_nums = [x.split("\t")[0] for x in ar_nums.splitlines()]


#ar_char = "[{}]".format(ar_chars) # regex for one Arabic character
#ar_tok = "[{}]+".format(ar_chars) # regex for one Arabic token
ar_char = re.compile("[{}]".format("".join(ar_chars))) # regex for one Arabic character
ar_tok = re.compile("[{}]+".format("".join(ar_chars))) # regex for one Arabic token

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
                       ٖ    | # ARABIC SUBSCRIPT ALEF
                       ٗ    | # ARABIC INVERTED DAMMA
                       ۡ    | # ARABIC SMALL HIGH DOTLESS HEAD OF KHAH = Qur'anic sukūn
                       ۤ      # ARABIC SMALL HIGH MADDA
                   """, re.VERBOSE)

any_unicode_letter = r"[^\W\d_]"
any_word = any_unicode_letter + "+"

###### regex module (alternative to re module):
#any_unicode_letter = "\p{L}"
#any_unicode_diacritic = "\p{M}"

space = r"(?: |[\r\n]+~~|PageV[^P]+P\d+)+"
space = r"(?:\W|PageV[^P]+P\d+)+" # also takes care of commas etc.
space_word = r"(?:{}{})".format(space, ar_tok)

# regex patterns to ignore tokens that contain letters and numbers
# but should not be counted as tokens:
not_tok_regexes = [
    # structural tags like ### |EDITOR|, ### |PARATEXT|:
    r"[|$][A-Z]+[|$]",
    # semantic tags:
    r"@",
    r"\bY[A-Z]?\d+\b",
    # page number tags:
    r"(?:Folio|Page)(?:Beg|Beginning|End)?V",
    # milestone tags:
    r"\bms[A-Z]?\d+",
    # markdown image links and urls:
    r"!?\[[^\]]*\]\([^)]*\)",
    # numbers only should be counted as token,
    # but not number+non-letter character (e.g., 1., (1), ...):
    r"^\W*\d+\W+$"
    ]
do_not_count = "|".join(not_tok_regexes)

# regular expression to split the text into tokens:
# NB: "|" is used for "### |PARATEXT|"-style tags and for markdown tables
tok_splitter = r"((?:\|[A-Z]+\|)|[\s~#|]+)"

# Whitelist of characters that are allowed in OpenITI texts:

allowed_chars = """\
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
ٹ	ARABIC LETTER TTEH
پ	ARABIC LETTER PEH
چ	ARABIC LETTER TCHEH
ڈ	ARABIC LETTER DDAL
ڑ	ARABIC LETTER RREH
ژ	ARABIC LETTER JEH
ک	ARABIC LETTER KEHEH
ݣ	ARABIC LETTER KEHEH WITH THREE DOTS ABOVE
ڭ	ARABIC LETTER NG
گ	ARABIC LETTER GAF
ۀ	ARABIC LETTER HEH WITH YEH ABOVE
ہ	ARABIC LETTER HEH GOAL
ۂ	ARABIC LETTER HEH GOAL WITH HAMZA ABOVE
ی	ARABIC LETTER FARSI YEH
ے	ARABIC LETTER YEH BARREE
ۓ	ARABIC LETTER YEH BARREE WITH HAMZA ABOVE
ھ	ARABIC LETTER HEH DOACHASHMEE
ە	ARABIC LETTER AE
ں	ARABIC LETTER NOON GHUNNA
ٮ   ARABIC LETTER DOTLESS BEH
ٯ   ARABIC LETTER DOTLESS QAF
ڡ   ARABIC LETTER DOTLESS FEH
ڤ	ARABIC LETTER VEH
ڨ	ARABIC LETTER QAF WITH THREE DOTS ABOVE
ڣ   ARABIC LETTER FEH WITH DOT BELOW
ټ	ARABIC LETTER TEH WITH RING
‌	ZERO WIDTH NON-JOINER
ٔ	ARABIC HAMZA ABOVE (needed for the Farsi izafeh)
#	NUMBER SIGN
%	PERCENT SIGN
(	LEFT PARENTHESIS
)	RIGHT PARENTHESIS
.	FULL STOP
/	SOLIDUS
0	DIGIT ZERO
1	DIGIT ONE
2	DIGIT TWO
3	DIGIT THREE
4	DIGIT FOUR
5	DIGIT FIVE
7	DIGIT SEVEN
8	DIGIT EIGHT
9	DIGIT NINE
:	COLON
|	VERTICAL LINE
~	TILDE
؟	ARABIC QUESTION MARK
،	ARABIC COMMA
!	EXCLAMATION MARK
$	DOLLAR SIGN
*	ASTERISK
-	HYPHEN-MINUS
_	LOW LINE (i.e., underscore)
«	LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
»	RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
؛	ARABIC SEMICOLON
!	EXCLAMATION MARK
"	QUOTATION MARK
,	COMMA
=	EQUALS SIGN
?	QUESTION MARK
“	LEFT DOUBLE QUOTATION MARK
”	RIGHT DOUBLE QUOTATION MARK
’	RIGHT SINGLE QUOTATION MARK
&   AMPERSAND
§   SECTION SIGN
¶	PILCROW SIGN
¬	NOT SIGN
•	BULLET
<	LESS-THAN SIGN
>	GREATER-THAN SIGN
{	LEFT CURLY BRACKET
}	RIGHT CURLY BRACKET
+	PLUS SIGN
;	SEMICOLON
@	COMMERCIAL AT
ְ	HEBREW POINT SHEVA
ֳ	HEBREW POINT HATAF QAMATS
ִ	HEBREW POINT HIRIQ
ֵ	HEBREW POINT TSERE
ֶ	HEBREW POINT SEGOL
ַ	HEBREW POINT PATAH
ָ	HEBREW POINT QAMATS
ֹ	HEBREW POINT HOLAM
ּ	HEBREW POINT DAGESH OR MAPIQ
א	HEBREW LETTER ALEF
ב	HEBREW LETTER BET
ג	HEBREW LETTER GIMEL
ד	HEBREW LETTER DALET
ה	HEBREW LETTER HE
ו	HEBREW LETTER VAV
ז	HEBREW LETTER ZAYIN
ח	HEBREW LETTER HET
ט	HEBREW LETTER TET
י	HEBREW LETTER YOD
ך	HEBREW LETTER FINAL KAF
כ	HEBREW LETTER KAF
ל	HEBREW LETTER LAMED
ם	HEBREW LETTER FINAL MEM
מ	HEBREW LETTER MEM
ן	HEBREW LETTER FINAL NUN
נ	HEBREW LETTER NUN
ס	HEBREW LETTER SAMEKH
ע	HEBREW LETTER AYIN
ף	HEBREW LETTER FINAL PE
פ	HEBREW LETTER PE
ץ	HEBREW LETTER FINAL TSADI
צ	HEBREW LETTER TSADI
ק	HEBREW LETTER QOF
ר	HEBREW LETTER RESH
ש	HEBREW LETTER SHIN
ת	HEBREW LETTER TAV
І	CYRILLIC CAPITAL LETTER BYELORUSSIAN-UKRAINIAN I
А	CYRILLIC CAPITAL LETTER A
Б	CYRILLIC CAPITAL LETTER BE
В	CYRILLIC CAPITAL LETTER VE
Г	CYRILLIC CAPITAL LETTER GHE
Д	CYRILLIC CAPITAL LETTER DE
Е	CYRILLIC CAPITAL LETTER IE
Ж	CYRILLIC CAPITAL LETTER ZHE
З	CYRILLIC CAPITAL LETTER ZE
И	CYRILLIC CAPITAL LETTER I
Й	CYRILLIC CAPITAL LETTER SHORT I
К	CYRILLIC CAPITAL LETTER KA
Л	CYRILLIC CAPITAL LETTER EL
М	CYRILLIC CAPITAL LETTER EM
Н	CYRILLIC CAPITAL LETTER EN
О	CYRILLIC CAPITAL LETTER O
П	CYRILLIC CAPITAL LETTER PE
Р	CYRILLIC CAPITAL LETTER ER
С	CYRILLIC CAPITAL LETTER ES
Т	CYRILLIC CAPITAL LETTER TE
У	CYRILLIC CAPITAL LETTER U
Ф	CYRILLIC CAPITAL LETTER EF
Х	CYRILLIC CAPITAL LETTER HA
Ц	CYRILLIC CAPITAL LETTER TSE
Ч	CYRILLIC CAPITAL LETTER CHE
Ш	CYRILLIC CAPITAL LETTER SHA
Щ	CYRILLIC CAPITAL LETTER SHCHA
Ъ	CYRILLIC CAPITAL LETTER HARD SIGN
Ы	CYRILLIC CAPITAL LETTER YERU
Ь	CYRILLIC CAPITAL LETTER SOFT SIGN
Э	CYRILLIC CAPITAL LETTER E
Ю	CYRILLIC CAPITAL LETTER YU
Я	CYRILLIC CAPITAL LETTER YA
а	CYRILLIC SMALL LETTER A
б	CYRILLIC SMALL LETTER BE
в	CYRILLIC SMALL LETTER VE
г	CYRILLIC SMALL LETTER GHE
д	CYRILLIC SMALL LETTER DE
е	CYRILLIC SMALL LETTER IE
ж	CYRILLIC SMALL LETTER ZHE
з	CYRILLIC SMALL LETTER ZE
и	CYRILLIC SMALL LETTER I
й	CYRILLIC SMALL LETTER SHORT I
к	CYRILLIC SMALL LETTER KA
л	CYRILLIC SMALL LETTER EL
м	CYRILLIC SMALL LETTER EM
н	CYRILLIC SMALL LETTER EN
о	CYRILLIC SMALL LETTER O
п	CYRILLIC SMALL LETTER PE
р	CYRILLIC SMALL LETTER ER
с	CYRILLIC SMALL LETTER ES
т	CYRILLIC SMALL LETTER TE
у	CYRILLIC SMALL LETTER U
ф	CYRILLIC SMALL LETTER EF
х	CYRILLIC SMALL LETTER HA
ц	CYRILLIC SMALL LETTER TSE
ч	CYRILLIC SMALL LETTER CHE
ш	CYRILLIC SMALL LETTER SHA
щ	CYRILLIC SMALL LETTER SHCHA
ъ	CYRILLIC SMALL LETTER HARD SIGN
ы	CYRILLIC SMALL LETTER YERU
ь	CYRILLIC SMALL LETTER SOFT SIGN
э	CYRILLIC SMALL LETTER E
ю	CYRILLIC SMALL LETTER YU
я	CYRILLIC SMALL LETTER YA
і	CYRILLIC SMALL LETTER BYELORUSSIAN-UKRAINIAN I
Ѣ	CYRILLIC CAPITAL LETTER YAT
ѣ	CYRILLIC SMALL LETTER YAT
Ѳ	CYRILLIC CAPITAL LETTER FITA
̇	COMBINING DOT ABOVE
̈	COMBINING DIAERESIS
Α	GREEK CAPITAL LETTER ALPHA
Β	GREEK CAPITAL LETTER BETA
Γ	GREEK CAPITAL LETTER GAMMA
Δ	GREEK CAPITAL LETTER DELTA
Ε	GREEK CAPITAL LETTER EPSILON
Ζ	GREEK CAPITAL LETTER ZETA
Η	GREEK CAPITAL LETTER ETA
Θ	GREEK CAPITAL LETTER THETA
Ι	GREEK CAPITAL LETTER IOTA
Κ	GREEK CAPITAL LETTER KAPPA
Λ	GREEK CAPITAL LETTER LAMDA
Μ	GREEK CAPITAL LETTER MU
Ν	GREEK CAPITAL LETTER NU
Ξ	GREEK CAPITAL LETTER XI
Ο	GREEK CAPITAL LETTER OMICRON
Π	GREEK CAPITAL LETTER PI
Ρ	GREEK CAPITAL LETTER RHO
Σ	GREEK CAPITAL LETTER SIGMA
Τ	GREEK CAPITAL LETTER TAU
Υ	GREEK CAPITAL LETTER UPSILON
Φ	GREEK CAPITAL LETTER PHI
Χ	GREEK CAPITAL LETTER CHI
Ψ	GREEK CAPITAL LETTER PSI
Ω	GREEK CAPITAL LETTER OMEGA
ά	GREEK SMALL LETTER ALPHA WITH TONOS
έ	GREEK SMALL LETTER EPSILON WITH TONOS
ή	GREEK SMALL LETTER ETA WITH TONOS
ί	GREEK SMALL LETTER IOTA WITH TONOS
Ω	GREEK CAPITAL LETTER OMEGA
α	GREEK SMALL LETTER ALPHA
β	GREEK SMALL LETTER BETA
γ	GREEK SMALL LETTER GAMMA
δ	GREEK SMALL LETTER DELTA
ε	GREEK SMALL LETTER EPSILON
ζ	GREEK SMALL LETTER ZETA
η	GREEK SMALL LETTER ETA
θ	GREEK SMALL LETTER THETA
ι	GREEK SMALL LETTER IOTA
κ	GREEK SMALL LETTER KAPPA
λ	GREEK SMALL LETTER LAMDA
μ	GREEK SMALL LETTER MU
ν	GREEK SMALL LETTER NU
ξ	GREEK SMALL LETTER XI
ο	GREEK SMALL LETTER OMICRON
π	GREEK SMALL LETTER PI
ρ	GREEK SMALL LETTER RHO
ς	GREEK SMALL LETTER FINAL SIGMA
σ	GREEK SMALL LETTER SIGMA
τ	GREEK SMALL LETTER TAU
υ	GREEK SMALL LETTER UPSILON
φ	GREEK SMALL LETTER PHI
χ	GREEK SMALL LETTER CHI
ψ	GREEK SMALL LETTER PSI
ω	GREEK SMALL LETTER OMEGA
ϊ	GREEK SMALL LETTER IOTA WITH DIALYTIKA
ϋ	GREEK SMALL LETTER UPSILON WITH DIALYTIKA
ΰ	GREEK SMALL LETTER UPSILON WITH DIALYTIKA AND TONOS
ό	GREEK SMALL LETTER OMICRON WITH TONOS
ώ	GREEK SMALL LETTER OMEGA WITH TONOS
ύ	GREEK SMALL LETTER UPSILON WITH TONOS
ἐ	GREEK SMALL LETTER EPSILON WITH PSILI
ἔ	GREEK SMALL LETTER EPSILON WITH PSILI AND OXIA
ἷ	GREEK SMALL LETTER IOTA WITH DASIA AND PERISPOMENI
ὐ	GREEK SMALL LETTER UPSILON WITH PSILI
ὰ	GREEK SMALL LETTER ALPHA WITH VARIA
ὲ	GREEK SMALL LETTER EPSILON WITH VARIA
ὶ	GREEK SMALL LETTER IOTA WITH VARIA
ὸ	GREEK SMALL LETTER OMICRON WITH VARIA
ᾶ	GREEK SMALL LETTER ALPHA WITH PERISPOMENI
ῦ	GREEK SMALL LETTER UPSILON WITH PERISPOMENI
ἀ	GREEK SMALL LETTER ALPHA WITH PSILI
ἄ	GREEK SMALL LETTER ALPHA WITH PSILI AND OXIA
ἅ	GREEK SMALL LETTER ALPHA WITH DASIA AND OXIA
Ἀ	GREEK CAPITAL LETTER ALPHA WITH PSILI
Ἔ	GREEK CAPITAL LETTER EPSILON WITH PSILI AND OXIA
ἠ	GREEK SMALL LETTER ETA WITH PSILI
ἡ	GREEK SMALL LETTER ETA WITH DASIA
ἥ	GREEK SMALL LETTER ETA WITH DASIA AND OXIA
ἦ	GREEK SMALL LETTER ETA WITH PSILI AND PERISPOMENI
ἰ	GREEK SMALL LETTER IOTA WITH PSILI
ἱ	GREEK SMALL LETTER IOTA WITH DASIA
ἴ	GREEK SMALL LETTER IOTA WITH PSILI AND OXIA
ἶ	GREEK SMALL LETTER IOTA WITH PSILI AND PERISPOMENI
Ἰ	GREEK CAPITAL LETTER IOTA WITH PSILI
Ἱ	GREEK CAPITAL LETTER IOTA WITH DASIA
ὀ	GREEK SMALL LETTER OMICRON WITH PSILI
ὁ	GREEK SMALL LETTER OMICRON WITH DASIA
ὃ	GREEK SMALL LETTER OMICRON WITH DASIA AND VARIA
ὄ	GREEK SMALL LETTER OMICRON WITH PSILI AND OXIA
ὅ	GREEK SMALL LETTER OMICRON WITH DASIA AND OXIA
ὑ	GREEK SMALL LETTER UPSILON WITH DASIA
ὕ	GREEK SMALL LETTER UPSILON WITH DASIA AND OXIA
ὖ	GREEK SMALL LETTER UPSILON WITH PSILI AND PERISPOMENI
ὗ	GREEK SMALL LETTER UPSILON WITH DASIA AND PERISPOMENI
ὠ	GREEK SMALL LETTER OMEGA WITH PSILI
ὡ	GREEK SMALL LETTER OMEGA WITH DASIA
ὥ	GREEK SMALL LETTER OMEGA WITH DASIA AND OXIA
ὴ	GREEK SMALL LETTER ETA WITH VARIA
ὺ	GREEK SMALL LETTER UPSILON WITH VARIA
ὼ	GREEK SMALL LETTER OMEGA WITH VARIA
ᾧ	GREEK SMALL LETTER OMEGA WITH DASIA AND PERISPOMENI AND YPOGEGRAMMENI
ᾳ	GREEK SMALL LETTER ALPHA WITH YPOGEGRAMMENI
ῃ	GREEK SMALL LETTER ETA WITH YPOGEGRAMMENI
ῄ	GREEK SMALL LETTER ETA WITH OXIA AND YPOGEGRAMMENI
ῆ	GREEK SMALL LETTER ETA WITH PERISPOMENI
ῇ	GREEK SMALL LETTER ETA WITH PERISPOMENI AND YPOGEGRAMMENI
ῖ	GREEK SMALL LETTER IOTA WITH PERISPOMENI
ῳ	GREEK SMALL LETTER OMEGA WITH YPOGEGRAMMENI
ῶ	GREEK SMALL LETTER OMEGA WITH PERISPOMENI
ῷ	GREEK SMALL LETTER OMEGA WITH PERISPOMENI AND YPOGEGRAMMENI
Ϛ	GREEK LETTER STIGMA
ϛ	GREEK SMALL LETTER STIGMA
ⲁ	COPTIC SMALL LETTER ALFA
ⲅ	COPTIC SMALL LETTER GAMMA
ⲇ	COPTIC SMALL LETTER DALDA
ⲉ	COPTIC SMALL LETTER EIE
ⲋ	COPTIC SMALL LETTER SOU
ⲏ	COPTIC SMALL LETTER HATE
Ⲓ	COPTIC CAPITAL LETTER IAUDA
ⲓ	COPTIC SMALL LETTER IAUDA
ⲕ	COPTIC SMALL LETTER KAPA
ⲗ	COPTIC SMALL LETTER LAULA
ⲙ	COPTIC SMALL LETTER MI
ⲛ	COPTIC SMALL LETTER NI
ⲝ	COPTIC SMALL LETTER KSI
ⲟ	COPTIC SMALL LETTER O
ⲡ	COPTIC SMALL LETTER PI
ⲣ	COPTIC SMALL LETTER RO
ⲥ	COPTIC SMALL LETTER SIMA
ⲧ	COPTIC SMALL LETTER TAU
ⲭ	COPTIC SMALL LETTER KHI
ⲱ	COPTIC SMALL LETTER OOU
ϥ	COPTIC SMALL LETTER FEI
ϧ	COPTIC SMALL LETTER KHEI
ϫ	COPTIC SMALL LETTER GANGIA
ϭ	COPTIC SMALL LETTER SHIMA
Ϯ	COPTIC CAPITAL LETTER DEI
ϯ	COPTIC SMALL LETTER DEI
⳱	COPTIC COMBINING SPIRITUS LENIS
܀	SYRIAC END OF PARAGRAPH
ܐ	SYRIAC LETTER ALAPH
ܒ	SYRIAC LETTER BETH
ܓ	SYRIAC LETTER GAMAL
ܕ	SYRIAC LETTER DALATH
ܗ	SYRIAC LETTER HE
ܘ	SYRIAC LETTER WAW
ܙ	SYRIAC LETTER ZAIN
ܚ	SYRIAC LETTER HETH
ܛ	SYRIAC LETTER TETH
ܝ	SYRIAC LETTER YUDH
ܟ	SYRIAC LETTER KAPH
ܠ	SYRIAC LETTER LAMADH
ܡ	SYRIAC LETTER MIM
ܢ	SYRIAC LETTER NUN
ܥ	SYRIAC LETTER E
ܦ	SYRIAC LETTER PE
ܨ	SYRIAC LETTER SADHE
ܩ	SYRIAC LETTER QAPH
ܪ	SYRIAC LETTER RISH
ܫ	SYRIAC LETTER SHIN
ܬ	SYRIAC LETTER TAW
Â	LATIN CAPITAL LETTER A WITH CIRCUMFLEX
Œ	LATIN CAPITAL LIGATURE OE
Å	LATIN CAPITAL LETTER A WITH RING ABOVE
Æ	LATIN CAPITAL LETTER AE
Ì	LATIN CAPITAL LETTER I WITH GRAVE
Ø	LATIN CAPITAL LETTER O WITH STROKE
Þ	LATIN CAPITAL LETTER THORN
ß	LATIN SMALL LETTER SHARP S
â	LATIN SMALL LETTER A WITH CIRCUMFLEX
å	LATIN SMALL LETTER A WITH RING ABOVE
æ	LATIN SMALL LETTER AE
ì	LATIN SMALL LETTER I WITH GRAVE
í	LATIN SMALL LETTER I WITH ACUTE
ð	LATIN SMALL LETTER ETH
õ	LATIN SMALL LETTER O WITH TILDE
ø	LATIN SMALL LETTER O WITH STROKE
þ	LATIN SMALL LETTER THORN
ÿ	LATIN SMALL LETTER Y WITH DIAERESIS
ć	LATIN SMALL LETTER C WITH ACUTE
ĉ	LATIN SMALL LETTER C WITH CIRCUMFLEX
ď	LATIN SMALL LETTER D WITH CARON
ė	LATIN SMALL LETTER E WITH DOT ABOVE
ģ	LATIN SMALL LETTER G WITH CEDILLA
į	LATIN SMALL LETTER I WITH OGONEK
Ľ	LATIN CAPITAL LETTER L WITH CARON
ľ	LATIN SMALL LETTER L WITH CARON
ł	LATIN SMALL LETTER L WITH STROKE
ń	LATIN SMALL LETTER N WITH ACUTE
ņ	LATIN SMALL LETTER N WITH CEDILLA
Ň	LATIN CAPITAL LETTER N WITH CARON
ŏ	LATIN SMALL LETTER O WITH BREVE
Ő	LATIN CAPITAL LETTER O WITH DOUBLE ACUTE
ő	LATIN SMALL LETTER O WITH DOUBLE ACUTE
œ	LATIN SMALL LIGATURE OE
ŕ	LATIN SMALL LETTER R WITH ACUTE
Ŗ	LATIN CAPITAL LETTER R WITH CEDILLA
ŗ	LATIN SMALL LETTER R WITH CEDILLA
ř	LATIN SMALL LETTER R WITH CARON
Ś	LATIN CAPITAL LETTER S WITH ACUTE
ś	LATIN SMALL LETTER S WITH ACUTE
ŝ	LATIN SMALL LETTER S WITH CIRCUMFLEX
Ş	LATIN CAPITAL LETTER S WITH CEDILLA
ş	LATIN SMALL LETTER S WITH CEDILLA
ũ	LATIN SMALL LETTER U WITH TILDE
Ű	LATIN CAPITAL LETTER U WITH DOUBLE ACUTE
ű	LATIN SMALL LETTER U WITH DOUBLE ACUTE
ż	LATIN SMALL LETTER Z WITH DOT ABOVE
ƃ	LATIN SMALL LETTER B WITH TOPBAR
ș	LATIN SMALL LETTER S WITH COMMA BELOW
`	GRAVE ACCENT
¡	INVERTED EXCLAMATION MARK
£	POUND SIGN
©	COPYRIGHT SIGN
®	REGISTERED SIGN
°	DEGREE SIGN
±	PLUS-MINUS SIGN
·	MIDDLE DOT
¿	INVERTED QUESTION MARK
"""
allowed_chars = [x.split("\t")[0] for x in allowed_chars.splitlines()]
allowed_chars = [c for c in allowed_chars if c not in ("-", ".")]

# In addition to the above characters, also include Latin script, whitespace and punctuation:
transcription_chars = "0-9a-zA-ZāĀăĂēĒĕĔṭṬṯṮūŪīĪĭĬİıōŌṣṢšŠḍḌḏḎǧǦġĠğĞḫḪḥḤḳḲẓẒžŽčČçÇñÑãÃáÁàÀäÄéÉèÈêÊëËïÏîÎôÔóÓòÒōÕöÖüÜûÛúÚùÙʿʾ' "
escaped_chars = r"\"\n\t\[\]\.\-\\"

# build a regex to match all allowed characters (and all those that are not allowed):
allowed_chars_regex = re.compile(r"[{}{}{}]+".format("".join(allowed_chars), transcription_chars, escaped_chars))
unwanted_chars_regex = re.compile(r"[^{}{}{}]+".format("".join(allowed_chars), transcription_chars, escaped_chars))


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
book = auth + r"\.[A-Z][a-zA-Z]+"
#version = book + r"\.\w+(?:Vols)?(?:BK\d+|[A-Z])*-(?:%s)+\d+" % "|".join(language_codes)
version = book + r"\.\w+(?:Vols)?(?:BK\d+|[A-Z])*-(?:[a-z]{3}\d+)+"
author_uri = auth
book_uri = book
version_uri = version

loc = r"MS\d{4}[A-Z][a-zA-Z]+"
manuscr = loc + r"\.[A-Z][a-zA-Z_0-9]+"
transcr = manuscr + r"\.\w+-(?:[a-z]{3}\d+)+"
location_uri = loc
manuscript_uri = manuscr
transcription_uri = transcr

# OpenITI text file names:
extensions = ["inProgress", "completed", "mARkdown"]
ext_regex = r"(?:\.{}|(?= |\n|\r|\Z))".format(r"|\.".join(extensions))
version_file = version+ext_regex
version_fp = r"%s[/\\]%s[/\\]%s" % (auth, book, version_file)

# OpenITI yml file names:
yml = r"\.yml"
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
vol_page = r"Page(?:Beg|End)?V[^P]+P\d+[ABab]?"
vol_no = r"Page(?:Beg|End)?V([^P]+)P\d+[ABab]?"
page_no = r"Page(?:Beg|End)?V[^P]+P(\d+[ABab]?)"
vol_page_3 = r"Page(?:Beg|End)?V[^P]{2}P\d{3}[ABab]?"
vol_page_4 = r"Page(?:Beg|End)?V[^P]{2}P\d{4}[ABab]?"
page = dotall + r"(?:(?<={})|(?<={})|(?<={})).+?(?:{}|\Z)".format(vol_page_3,
                    vol_page_4, header_splitter, vol_page)

# Hierarchical section tags:
section_tag = r"### \|\d*\|* "
section_title = section_tag + r"([^\r\n]*)"
section = dotall + section_tag + r".+?(?=###|\Z)"
section_text = dotall + section_tag + r"[^\r\n]*[\r\n]+(.+?)(?=###|\Z)"

# biographies
bio_tag = r"### (?:\|+ )?\$+ "
bio = dotall + bio_tag + r"[^\r\n]*[\r\n]+.+?(?=###|\Z)"
bio_title = bio_tag + r"([^\r\n]*)"
bio_text = dotall + bio_tag + r"[^\r\n]*[\r\n]+(.+?)(?=###|\Z)"

bio_man_tag = r"### (?:\|+ )?\$ "
bio_man = dotall + bio_man_tag + r"[^\r\n]*[\r\n]+.+?(?=###|\Z)"
bio_man_title = bio_man_tag + r"([^\r\n]*)"
bio_man_text = dotall + bio_man_tag + r"[^\r\n]*[\r\n]+(.+?)(?=###|\Z)"

bio_woman_tag = r"### (?:\|+ )?\$\$ "
bio_woman = dotall + bio_woman_tag + r"[^\r\n]*[\r\n]+.+?(?=###|\Z)"
bio_woman_title = bio_woman_tag + r"([^\r\n]*)"
bio_woman_text = dotall + bio_woman_tag + r"[^\r\n]*[\r\n]+(.+?)(?=###|\Z)"

# editorial sections:
editorial_tag = r"### \|EDITOR\|"
editorial = dotall + editorial_tag + r"[^\r\n]*[\r\n]+.+?(?=###|\Z)"
editorial_text = dotall + editorial_tag + r"[^\r\n]*[\r\n]+(.+?)(?=###|\Z)"

# paratext sections:
paratext_tag = r"### \|PARATEXT\|"
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
anal_tag = r"(?:@[A-Z]{3})?[@#][A-Z]{3}(?:\$[\w+\-]+)?(?:@?\d\d+)?"
tag_range = r"|".join([str(i)+"%(w)s{"+str(i)+"}" for i in range(1,21)])
tag_range = r"@?(?:\d\W*?(?:" + tag_range % {"w": space_word} + "))?"
anal_tag_text = r"(?:@[A-Z]{3})?[@#][A-Z]{3}(?:\$[\w+\-]+)?" + tag_range

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

