import re
import unicodedata
import urllib
import doctest

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
ar_chars = [x.split("\t")[0] for x in ar_chars.splitlines()]
#ar_chars = "ذ١٢٣٤٥٦٧٨٩٠ّـضصثقفغعهخحجدًٌَُلإإشسيبلاتنمكطٍِلأأـئءؤرلاىةوزظْلآآ"
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
                       ـ   | # Taṭwīl / Kashīda
                       ٖ    | # ARABIC SUBSCRIPT ALEF
                       ٗ    | # ARABIC INVERTED DAMMA
                       ۡ    | # ARABIC SMALL HIGH DOTLESS HEAD OF KHAH = Qur'anic sukūn
                       ۤ      # ARABIC SMALL HIGH MADDA
                   """, re.VERBOSE)

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




def denoise(text):
    """Remove non-consonantal characters from Arabic text.

    Examples:
        >>> denoise("وَالَّذِينَ يُؤْمِنُونَ بِمَا أُنْزِلَ إِلَيْكَ وَمَا أُنْزِلَ مِنْ قَبْلِكَ وَبِالْآخِرَةِ هُمْ يُوقِنُونَ")
        'والذين يؤمنون بما أنزل إليك وما أنزل من قبلك وبالآخرة هم يوقنون'
        >>> denoise(" ْ ً ٌ ٍ َ ُ ِ ّ ۡ ࣰ ࣱ ࣲ ٰ ")
        '              '
    """
    return re.sub(noise, "", text)


deNoise = denoise


def normalize(text, replacement_tuples=[]):
    """Normalize Arabic text by replacing complex characters by simple ones.
    The function is used internally to do batch replacements. Also, it can be called externally
     to run custom replacements with a list of tuples of (character/regex, replacement).

    Args:
        text (str): the string that needs to be normalized
        replacement_tuples (list of tuple pairs): (character/regex, replacement)

    Examples:
        >>> normalize('AlphaBet', [("A", "a"), ("B", "b")])
        'alphabet'
    """
    for pat, repl in replacement_tuples:
        text = re.sub(pat, repl, text)
    return text


def normalize_per(text):
    """Normalize Persian strings by converting Arabic chars to related Persian unicode chars.
    fixing Alifs, Alif Maqsuras, hamzas, ta marbutas, kaf, ya، Fathatan, kasra;

    Args:
        text (str): user input string to be normalized

    Examples:
        >>> normalize_per("سياسي")
        'سیاسی'
        >>> normalize_per("مدينة")
        'مدینه'
        >>> normalize_per("درِ باز")
        'در باز'
        >>> normalize_per("حتماً")
        'حتما'
        >>> normalize_per("مدرك")
        'مدرک'
        >>> normalize_per("أسماء")
        'اسما'
        >>> normalize_per("دربارۀ")
        'درباره'

    """

    repl = [
        ('ك', 'ک'),
        ('[أاإٱ]', 'ا'),
        ('[يى]ء?', 'ی'),
        ('ؤِ', 'و'),
        ('ئ', 'ی'),
        ('[ءًِ]', ''),
        ('[ۀة]', 'ه')
    ]

    return normalize(text, repl)


def normalize_ara_light(text):
    """Lightly normalize Arabic strings:
    fixing only Alifs, Alif Maqsuras; Persian ya's and kafs;
    replacing hamzas on carriers with standalone hamzas

    Args:
        text (str): the string that needs to be normalized

    Examples:
        >>> normalize_ara_light("ألف الف إلف آلف ٱلف")
        'الف الف الف الف الف'
        >>> normalize_ara_light("يحيى")
        'يحيي'
        >>> normalize_ara_light("مقرئ فيء")
        'مقرء فء'
        >>> normalize_ara_light("قهوة")
        'قهوة'
        
    """
    text = normalize_composites(text)
    repl = [("أ", "ا"), ("ٱ", "ا"), ("آ", "ا"), ("إ", "ا"),    # alifs
            ("ى", "ي"),                                        # alif maqsura
            ("يء", "ء"), ("ىء", "ء"), ("ؤ", "ء"), ("ئ", "ء"),  # hamzas
            ("ک", "ك"), ("ی", "ي"), ("ۀ", "ه"),                # Persian letters
            ]
    return normalize(text, repl)
    

def normalize_ara_heavy(text):
    """Normalize Arabic text by simplifying complex characters:
    alifs, alif maqsura, hamzas, ta marbutas

    Examples:
        >>> normalize_ara_heavy("ألف الف إلف آلف ٱلف")
        'الف الف الف الف الف'
        >>> normalize_ara_heavy("يحيى")
        'يحيي'
        >>> normalize_ara_heavy("مقرئ فيء")
        'مقر في'
        >>> normalize_ara_heavy("قهوة")
        'قهوه'
    """
    text = normalize_composites(text)
    repl = [("أ", "ا"), ("ٱ", "ا"), ("آ", "ا"), ("إ", "ا"),  # alifs
            ("ى", "ي"),                                      # alif maqsura
            ("ؤ", ""), ("ئ", ""), ("ء", ""),                 # hamzas
            ("ک", "ك"), ("ی", "ي"),                          # Persian letters
            ("ة", "ه"), ("ۀ", "ه"),                          # ta marbuta/ha
            ]
    return normalize(text, repl)


def normalize_composites(text, method="NFKC"):
    """Normalize composite characters and ligatures\
    using unicode normalization methods.

    Composite characters are characters that consist of
    a combination of a letter and a diacritic (e.g.,
    ؤ "U+0624 : ARABIC LETTER WAW WITH HAMZA ABOVE",
    آ "U+0622 : ARABIC LETTER ALEF WITH MADDA ABOVE").
    Some normalization methods (NFD, NFKD) decompose
    these composite characters into their constituent characters,
    others (NFC, NFKC) compose these characters
    from their constituent characters.

    Ligatures are another type of composite character:
    one unicode point represents one or more letters (e.g.,
    ﷲ "U+FDF2 : ARABIC LIGATURE ALLAH ISOLATED FORM",
    ﰋ "U+FC0B : ARABIC LIGATURE TEH WITH JEEM ISOLATED FORM").
    Such ligatures can only be decomposed (NFKC, NFKD)
    or kept as they are (NFC, NFD); there are no methods
    that compose them from their constituent characters.
    
    Finally, Unicode also contains code points for the
    different contextual forms of a letter (isolated,
    initial, medial, final), in addition to the code point
    for the general letter. E.g., for the letter ba':

    * general:	0628	ب
    * isolated:	FE8F	ﺏ
    * final:  	FE90	ﺐ
    * medial: 	FE92	ﺒ
    * initial: 	FE91	ﺑ
    
    Some methods (NFKC, NFKD)
    replace those contextual form code points by the
    equivalent general code point. The other methods
    (NFC, NFD) keep the contextual code points as they are.
    There are no methods that turn general letter code points
    into their contextual code points.

    ====== ========== ========= ================
    method composites ligatures contextual forms
    ====== ========== ========= ================
    NFC    join       keep      keep
    NFD    split      keep      keep
    NFKC   join       decompose generalize
    NFKD   split      decompose generalize
    ====== ========== ========= ================
    
    For more details about Unicode normalization methods,
    see https://unicode.org/reports/tr15/

    Args:
        text (str): the string to be normalized
        method (str): the unicode method to be used for normalization
            (see https://docs.python.org/3.5/library/unicodedata.html).
            Default: NFKC, which is most suited for Arabic. 

    Examples:
        >>> len("ﷲ") # U+FDF2: ARABIC LIGATURE ALLAH ISOLATED FORM
        1
        >>> len(normalize_composites("ﷲ"))
        4
        >>> [char for char in normalize_composites("ﷲ")]
        ['ا', 'ل', 'ل', 'ه']
        
        >>> len("ﻹ") # UFEF9: ARABIC LIGATURE LAM WITH ALEF WITH HAMZA BELOW ISOLATED FORM
        1
        >>> len(normalize_composites("ﻹ"))
        2

        alif+hamza written with 2 unicode characters:
        U+0627 (ARABIC LETTER ALEF) + U+0654 (ARABIC HAMZA ABOVE):
        
        >>> a = "أ"
        >>> len(a)
        2
        >>> len(normalize_composites(a))
        1
    """
    return unicodedata.normalize(method, text)


def denormalize(text):
    """Replace complex characters with a regex covering all variants.

    Examples:
        >>> denormalize("يحيى")
        'يحي[يى]'
        >>> denormalize("هوية")
        'هوي[هة]'
        >>> denormalize("مقرئ")
        'مقر(?:[ؤئ]|[وي]ء)'
        >>> denormalize("فيء")
        'في(?:[ؤئ]|[وي]ء)'
    """
    alifs = '[إأٱآا]'
    alif_maqsura = '[يى]\\b'
    alif_maqsura_reg = '[يى]'
    ta_marbuta = '[هة]\\b'
    ta_marbuta_reg = '[هة]'
    hamzas = '[ؤئء]'
    hamzas_reg = '(?:{}|{}ء)'.format('[ؤئ]', '[وي]')
    # Applying deNormalization
    text = re.sub(alifs, alifs, text)
    text = re.sub(alif_maqsura, alif_maqsura_reg, text)
    text = re.sub(ta_marbuta, ta_marbuta_reg, text)
    text = re.sub(hamzas, hamzas_reg, text)
    return text


#def ar_ch_len(fp):
def ar_cnt_file(fp, mode="token", incl_editor_sections=True):
    """Count the number of Arabic characters/tokens in a text, given its pth

    Args:
        fp (str): url / path to a file
        mode (str): either "char" for count of Arabic characters,
                    or "token" for count of Arabic tokens
        incl_editor_sections (bool): if False, the sections marked as editorial
            (### |EDITOR|) will be left out of the token/character count.
            Default: True (editorial sections will be counted)

    Returns:
        (int): Arabic character/token count 
    """
    splitter = "#META#Header#End#"
    try:
        with urllib.request.urlopen(fp) as f:
            book = f.read().decode('utf-8')
    except:
        with open(fp, mode="r", encoding="utf-8") as f:
            book = f.read()

    if splitter in book:
        text = book.split(splitter)[-1]
    else:
        text = book
        msg = "This text is missing the splitter!\n{}".format(fp)
        #raise Exception(msg)
    if not incl_editor_sections:
        text = re.sub(r"### \|EDITOR.+?(### |\Z)", r"\1", text,
                      flags = re.DOTALL)

    # count the number of Arabic letters or tokens:
    
    if mode == "char":
        return ar_ch_cnt(text)
    else:
        return ar_tok_cnt(text)



def ar_ch_cnt(text):
    """
    Count the number of Arabic characters in a string

    :param text: text
    :return: number of the Arabic characters in the text

    Examples:
        >>> a = "ابجد ابجد اَبًجٌدُ"
        >>> ar_ch_cnt(a)
        16
    """
    return len(ar_char.findall(text))


def ar_tok_cnt(text):
    """
    Count the number of Arabic tokens in a string

    :param text: text
    :return: number of Arabic tokens in the text

    Examples:
        >>> a = "ابجد ابجد اَبًجٌدُ"
        >>> ar_tok_cnt(a)
        3
    """
    return len(ar_tok.findall(text))


def tokenize(text, token_regex=ar_tok):
    """Tokenize a text into tokens defined by `token_regex`

    NB: make sure to remove the OpenITI header from the text

    Args:
        text (str): full text with OpenITI header removed,
            cleaned of order marks ("\u202a", "\u202b", "\u202c")
        token_regex (str): regex that defines a token
        
    Returns:
        tuple (tokens (list): list of all tokens in the text,
               tokenStarts (list): list of start index of each token
               tokenEnds (list): list of end index of each token
               )
    Examples:
        >>> a = "ابجد ابجد اَبًجٌدُ"
        >>> tokens, tokenStarts, tokenEnds = tokenize(a)
        >>> tokens
        ['ابجد', 'ابجد', 'اَبًجٌدُ']
        >>> tokenStarts
        [0, 5, 10]
        >>> tokenEnds
        [4, 9, 18]
    """
    #find matches
    tokens = [m for m in re.finditer(token_regex,text)]

    #extract tokens and start,end positions
    tokenStarts = [m.start() for m in tokens]
    tokenEnds = [m.end() for m in tokens]
    tokens = [m.group() for m in tokens]

    return tokens, tokenStarts, tokenEnds


def decode_unicode_name(s):
    """Convert unicode names into the characters they refer to.

    Args:
        s (str): input string
    
    Returns:
        str

    Examples:
        >>> decode_unicode_name("ARABIC LETTER ALEF_ARABIC LETTER YEH")
        'اي'

        >>> decode_unicode_name("ARABIC LETTER ALEF_*")
        'ا*'
    """
    new_s = ""
    for x in s.split("_"):
        try:
            new_s += unicodedata.lookup(x)
        except:
            new_s += x
    return new_s

if __name__ == "__main__":
    doctest.testmod()
