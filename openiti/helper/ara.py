import re
import unicodedata
import urllib
import doctest

from openiti.helper.rgx import ar_chars, ar_nums, ar_char, ar_tok, noise, \
     transcription_chars, escaped_chars, allowed_chars, allowed_chars_regex, unwanted_chars_regex

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

def char_cnt(text, char_regex):
    """
    Count the number of letter characters in a string

    Args:
        text (str): text in which to count the tokens
        char_regex (obj): compiled regex pattern

    Returns: int

    Examples:
        >>> a = "ابجد ابجد اَبًجٌدُ"
        >>> ar_ch_cnt(a)
        16
    """
    return len(char_regex.findall(text))

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
    #return len(ar_char.findall(text))
    return char_cnt(text, ar_char)

def tok_cnt(text, tok_regex):
    """
    Count the number of tokens in a string

    Args:
        text (str): text in which to count the tokens
        tok_regex (obj): compiled regex pattern

    Returns: int

    Examples:
        >>> a = "ابجد ابجد اَبًجٌدُ"
        >>> tok_cnt(a, ar_tok)
        3
    """
    return len(tok_regex.findall(text))

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
    #return len(ar_tok.findall(text))
    return tok_cnt(text, ar_tok)




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
