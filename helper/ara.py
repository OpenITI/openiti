import re


def deNoise(text):
    """Remove non-consonantal characters from Arabic text.

    Examples:
        >>> deNoise("وَالَّذِينَ يُؤْمِنُونَ بِمَا أُنْزِلَ إِلَيْكَ وَمَا أُنْزِلَ مِنْ قَبْلِكَ وَبِالْآخِرَةِ هُمْ يُوقِنُونَ")
        'والذين يؤمنون بما أنزل إليك وما أنزل من قبلك وبالآخرة هم يوقنون'
        >>> deNoise(" ْ ً ٌ ٍ َ ُ ِ ّ ۡ ࣰ ࣱ ࣲ ٰ ")
        '              '
    """
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


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
