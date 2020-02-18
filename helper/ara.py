import re

ar_chars = "ذ١٢٣٤٥٦٧٨٩٠ّـضصثقفغعهخحجدًٌَُلإإشسيبلاتنمكطٍِلأأـئءؤرلاىةوزظْلآآ"
ar_char = re.compile("[{}]".format(ar_chars)) # regex for one Arabic character
ar_tok = re.compile("[{}]+".format(ar_chars)) # regex for one Arabic token
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
splitter = "#META#Header#End#"


def denoise(text):
    """Remove non-consonantal characters from Arabic text.

    Examples:
        >>> denoise("وَالَّذِينَ يُؤْمِنُونَ بِمَا أُنْزِلَ إِلَيْكَ وَمَا أُنْزِلَ مِنْ قَبْلِكَ وَبِالْآخِرَةِ هُمْ يُوقِنُونَ")
        'والذين يؤمنون بما أنزل إليك وما أنزل من قبلك وبالآخرة هم يوقنون'
        >>> denoise(" ْ ً ٌ ٍ َ ُ ِ ّ ۡ ࣰ ࣱ ࣲ ٰ ")
        '              '
    """
    return re.sub(noise, "", text)


def normalize(text, replacement_tuples=[]):
    """Normalize Arabic text by replacing complex characters by simple ones.

    Args:
        text (str): the string that needs to be normalized
        replacement_tuples (list of tuple pairs): (character, replacement)

    Examples:
        >>> normalize('AlphaBet', [("A", "a"), ("B", "b")])
        'alphabet'
    """
    for char, repl in replacement_tuples:
        text = text.replace(char, repl)
    return text


def normalize_ara_light(text):
    """Lighlty normalize Arabic strings:
    fixing only Alifs, Alif Maqsuras;
    replacing hamzas on carriers with standalone hamzas

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
    repl = [("أ", "ا"), ("ٱ", "ا"), ("آ", "ا"), ("إ", "ا"),  # alifs
            ("ى", "ي"),                                      # alif maqsura
            ("ؤ", ""), ("ئ", ""), ("ء", ""),                 # hamzas
            ("ة", "ه")                                       # ta marbuta
            ]
    return normalize(text, repl)


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
def ar_cnt_file(fp, mode="token"):
    """Count the number of Arabic characters/tokens in a text, given its pth

    Args:
        fp (str): url / path to a file
        mode (str): either "char" for count of Arabic characters,
                    or "token" for count of Arabic tokens

    Returns:
        length (int): Arabic character/token count 
    """
    try:
        with url.urlopen(fp) as f:
            book = f.read().decode('utf-8')
    except:
        with open(fp, mode="r", encoding="utf-8") as f:
            book = f.read()

    if splitter in book:
        text = book.split(splitter)[1]

        # remove Editorial sections:
        
        text = re.sub(r"### \|EDITOR.+?(### |\Z)", r"\1", text,
                      flags = re.DOTALL)

        # count the number of Arabic letters or tokens:
        
        if mode == "char":
            return ar_ch_cnt(text)
        else:
            return ar_tok_cnt(text)
    else:
        print("{} is missing the splitter!".format(fp))
        return 0


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
    import doctest
    doctest.testmod()
    
    
