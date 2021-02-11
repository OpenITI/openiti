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
ar_chars = [x.split("\t")[0] for x in ar_chars.splitlines()]
#ar_chars = "ذ١٢٣٤٥٦٧٨٩٠ّـضصثقفغعهخحجدًٌَُلإإشسيبلاتنمكطٍِلأأـئءؤرلاىةوزظْلآآ"
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
                   """, re.VERBOSE)

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
        >>> normalize_per_light("سياسي")
        'سیاسی'
        >>> normalize_per_light("مدينة")
        'مدینه'
        >>> normalize_per_light("درِ باز")
        'در باز'
        >>> normalize_per_light("حتماً")
        'حتما'
        >>> normalize_per_light("مدرك")
        'مدرک'
        >>> normalize_per_light("أسماء")
        'اسما'
        >>> normalize_per_light("دربارۀ")
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
    """Lighlty normalize Arabic strings:
    fixing only Alifs, Alif Maqsuras;
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
            ("ة", "ه")                                       # ta marbuta
            ]
    return normalize(text, repl)


def normalize_composites(text, method="NFKC"):
    """Normalize composite characters and ligatures

    Ligatures like "Allah" will be broken into their components,
    while combining characters like alif + hamza above will be joined
    into one character. 

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


if __name__ == "__main__":
    doctest.testmod()

