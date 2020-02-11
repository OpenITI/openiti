"""
Test relative speed of string.replace, re.sub replacement
and mixed replacement (using re.sub for character disjunctions
like [أاإآ] and string replace for single replacements)
for the deNoise and normalize functions.

Conclusion of the test:

With both tested strings (a 30-line fully vocalized string and a 75MB text),
string replacement is almost always significantly faster
than re.sub and mixed replacement;
Only when a single regex is used to replace many characters by an empty string,
a single re.sub operation with a compiled regex is rarely (!)
marginally faster than multiple string replace operations
in very large texts or after 100.000 loops in the short string.
(tested up to 25 string replace operations for one single regex)


Output: 

----------------------------------------
Testing functions re.sub deNoise, string replace deNoise:

Results after 100 loops, with 30 first lines of the Qur'an:
1 - string replace deNoise: 0.008388800000000002
2 - re.sub deNoise: 0.0274035
(string replace deNoise ca. 3.3 times faster than re.sub deNoise)

Results after 10000 loops, with 30 first lines of the Qur'an:
1 - string replace deNoise: 0.8215248000000002
2 - re.sub deNoise: 2.6362182
(string replace deNoise ca. 3.2 times faster than re.sub deNoise)

----------------------------------------
Testing functions re.sub deNoise, string replace deNoise:

Results after 10 loops, with large text of 75MB:
1 - re.sub deNoise: 4.5313052
2 - string replace deNoise: 6.2427817999999995
(re.sub deNoise ca. 1.4 times faster than string replace deNoise)

Results after 50 loops, with large text of 75MB:
1 - re.sub deNoise: 21.9464538
2 - string replace deNoise: 31.245985300000008
(re.sub deNoise ca. 1.4 times faster than string replace deNoise)

----------------------------------------
Testing functions re.sub normalization, string replace normalization, mixed normalization:

Results after 100 loops, with 30 first lines of the Qur'an:
1 - string replace normalization: 0.002014299999999025
2 - mixed normalization: 0.004392899999999145
3 - re.sub normalization: 0.01432450000000074
(string replace normalization ca. 2.2 times faster than mixed normalization)
(string replace normalization ca. 7.1 times faster than re.sub normalization)

Results after 10000 loops, with 30 first lines of the Qur'an:
1 - string replace normalization: 0.1923208000000045
2 - mixed normalization: 0.4523312999999973
3 - re.sub normalization: 1.357212600000011
(string replace normalization ca. 2.4 times faster than mixed normalization)
(string replace normalization ca. 7.1 times faster than re.sub normalization)

Results after 100000 loops, with 30 first lines of the Qur'an:
1 - string replace normalization: 1.9453049999999905
2 - mixed normalization: 4.5060936
3 - re.sub normalization: 18.344620699999993
(string replace normalization ca. 2.3 times faster than mixed normalization)
(string replace normalization ca. 9.4 times faster than re.sub normalization)

----------------------------------------
Testing functions re.sub normalization, string replace normalization, mixed normalization:

Results after 10 loops, with large text of 75MB:
1 - string replace normalization: 5.748965499999997
2 - mixed normalization: 11.941127800000004
3 - re.sub normalization: 34.2564823
(string replace normalization ca. 2.1 times faster than mixed normalization)
(string replace normalization ca. 6.0 times faster than re.sub normalization)

Results after 50 loops, with large text of 75MB:
1 - string replace normalization: 31.95850839999997
2 - mixed normalization: 64.00169269999998
3 - re.sub normalization: 169.95990599999996
(string replace normalization ca. 2.0 times faster than mixed normalization)
(string replace normalization ca. 5.3 times faster than re.sub normalization)

----------------------------------------
Testing functions re.sub denormalization, string replace denormalization:

Results after 100 loops, with 30 first lines of the Qur'an:
1 - string replace denormalization: 0.009504700000000001
2 - re.sub denormalization: 0.0194251
(string replace denormalization ca. 2.0 times faster than re.sub denormalization)

Results after 10000 loops, with 30 first lines of the Qur'an:
1 - string replace denormalization: 0.9411094000000002
2 - re.sub denormalization: 1.9976751000000001
(string replace denormalization ca. 2.1 times faster than re.sub denormalization)

Results after 100000 loops, with 30 first lines of the Qur'an:
1 - string replace denormalization: 9.413773800000001
2 - re.sub denormalization: 19.1022952
(string replace denormalization ca. 2.0 times faster than re.sub denormalization)

----------------------------------------
Testing functions re.sub denormalization, string replace denormalization:

Results after 10 loops, with large text of 75MB:
1 - string replace denormalization: 25.790224800000004
2 - re.sub denormalization: 43.2591982
(string replace denormalization ca. 1.7 times faster than re.sub denormalization)

Results after 50 loops, with large text of 75MB:
1 - string replace denormalization: 135.18536029999996
2 - re.sub denormalization: 222.3127232
(string replace denormalization ca. 1.6 times faster than re.sub denormalization)

----------------------------------------
Testing functions single re.sub operation, 5 string replace operations:

Results after 100 loops, with 30 first lines of the Qur'an:
1 - 5 string replace operations: 0.0032636999999999996
2 - single re.sub operation: 0.006046800000000001
(5 string replace operations ca. 1.9 times faster than single re.sub operation)

Results after 10000 loops, with 30 first lines of the Qur'an:
1 - 5 string replace operations: 0.3252406000000001
2 - single re.sub operation: 0.5332258
(5 string replace operations ca. 1.6 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 5 string replace operations:

Results after 10 loops, with large text of 75MB:
1 - 5 string replace operations: 7.272236500000002
2 - single re.sub operation: 17.459449199999998
(5 string replace operations ca. 2.4 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 6 string replace operations:

Results after 100 loops, with 30 first lines of the Qur'an:
1 - 6 string replace operations: 0.003712800000002403
2 - single re.sub operation: 0.005911600000001016
(6 string replace operations ca. 1.6 times faster than single re.sub operation)

Results after 10000 loops, with 30 first lines of the Qur'an:
1 - 6 string replace operations: 0.37006929999999727
2 - single re.sub operation: 0.5517581000000007
(6 string replace operations ca. 1.5 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 6 string replace operations:

Results after 10 loops, with large text of 75MB:
1 - 6 string replace operations: 8.367578600000002
2 - single re.sub operation: 16.8720289
(6 string replace operations ca. 2.0 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 7 string replace operations:

Results after 100 loops, with 30 first lines of the Qur'an:
1 - 7 string replace operations: 0.0044642000000010285
2 - single re.sub operation: 0.006948700000002361
(7 string replace operations ca. 1.6 times faster than single re.sub operation)

Results after 10000 loops, with 30 first lines of the Qur'an:
1 - 7 string replace operations: 0.43168089999999637
2 - single re.sub operation: 0.6184892000000062
(7 string replace operations ca. 1.4 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 7 string replace operations:

Results after 10 loops, with large text of 75MB:
1 - 7 string replace operations: 9.770164199999996
2 - single re.sub operation: 19.609205799999998
(7 string replace operations ca. 2.0 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 8 string replace operations:

Results after 100 loops, with 30 first lines of the Qur'an:
1 - 8 string replace operations: 0.005006100000002789
2 - single re.sub operation: 0.00739210000000412
(8 string replace operations ca. 1.5 times faster than single re.sub operation)

Results after 10000 loops, with 30 first lines of the Qur'an:
1 - 8 string replace operations: 0.495628300000007
2 - single re.sub operation: 0.677892600000007
(8 string replace operations ca. 1.4 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 8 string replace operations:

Results after 10 loops, with large text of 75MB:
1 - 8 string replace operations: 12.027051700000001
2 - single re.sub operation: 23.323600100000007
(8 string replace operations ca. 1.9 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 9 string replace operations:

Results after 100 loops, with 30 first lines of the Qur'an:
1 - 9 string replace operations: 0.0055399000000022625
2 - single re.sub operation: 0.007424799999995457
(9 string replace operations ca. 1.3 times faster than single re.sub operation)

Results after 10000 loops, with 30 first lines of the Qur'an:
1 - 9 string replace operations: 0.5545536999999996
2 - single re.sub operation: 0.7581914000000012
(9 string replace operations ca. 1.4 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 9 string replace operations:

Results after 10 loops, with large text of 75MB:
1 - 9 string replace operations: 12.158491499999997
2 - single re.sub operation: 25.170432899999994
(9 string replace operations ca. 2.1 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 10 string replace operations:

Results after 100 loops, with 30 first lines of the Qur'an:
1 - 10 string replace operations: 0.006212199999993118
2 - single re.sub operation: 0.007610900000003085
(10 string replace operations ca. 1.2 times faster than single re.sub operation)

Results after 10000 loops, with 30 first lines of the Qur'an:
1 - 10 string replace operations: 0.6160366999999951
2 - single re.sub operation: 0.7125027999999816
(10 string replace operations ca. 1.2 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 10 string replace operations:

Results after 10 loops, with large text of 75MB:
1 - 10 string replace operations: 14.283474799999993
2 - single re.sub operation: 23.337247899999994
(10 string replace operations ca. 1.6 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 11 string replace operations:

Results after 100 loops, with 30 first lines of the Qur'an:
1 - 11 string replace operations: 0.0067801000000144995
2 - single re.sub operation: 0.007790099999994027
(11 string replace operations ca. 1.1 times faster than single re.sub operation)

Results after 10000 loops, with 30 first lines of the Qur'an:
1 - 11 string replace operations: 0.663314999999983
2 - single re.sub operation: 0.8159454000000039
(11 string replace operations ca. 1.2 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 11 string replace operations:

Results after 10 loops, with large text of 75MB:
1 - 11 string replace operations: 14.236086099999994
2 - single re.sub operation: 29.64436070000002
(11 string replace operations ca. 2.1 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 12 string replace operations:

Results after 100 loops, with 30 first lines of the Qur'an:
1 - 12 string replace operations: 0.007327099999997699
2 - single re.sub operation: 0.00877140000000054
(12 string replace operations ca. 1.2 times faster than single re.sub operation)

Results after 10000 loops, with 30 first lines of the Qur'an:
1 - single re.sub operation: 0.8271442999999863
2 - 12 string replace operations: 0.9188682999999855
(single re.sub operation ca. 1.1 times faster than 12 string replace operations)

----------------------------------------
Testing functions single re.sub operation, 12 string replace operations:

Results after 10 loops, with large text of 75MB:
1 - 12 string replace operations: 20.162684599999977
2 - single re.sub operation: 31.15590209999999
(12 string replace operations ca. 1.5 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 13 string replace operations:

Results after 100 loops, with 30 first lines of the Qur'an:
1 - 13 string replace operations: 0.008608600000002298
2 - single re.sub operation: 0.012064600000030623
(13 string replace operations ca. 1.4 times faster than single re.sub operation)

Results after 10000 loops, with 30 first lines of the Qur'an:
1 - 13 string replace operations: 1.1774655000000394
2 - single re.sub operation: 1.7925384000000122
(13 string replace operations ca. 1.5 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 13 string replace operations:

Results after 10 loops, with large text of 75MB:
1 - 13 string replace operations: 17.298843399999953
2 - single re.sub operation: 36.47844249999997
(13 string replace operations ca. 2.1 times faster than single re.sub operation)

----------------------------------------
Testing functions single re.sub operation, 14 string replace operations:

Results after 100 loops, with 30 first lines of the Qur'an:
1 - 14 string replace operations: 0.009635100000025432
2 - single re.sub operation: 0.014636200000040844
(14 string replace operations ca. 1.5 times faster than single re.sub operation)

Results after 10000 loops, with 30 first lines of the Qur'an:
1 - single re.sub operation: 1.5175319999999601
2 - 14 string replace operations: 1.7029174000000467
(single re.sub operation ca. 1.1 times faster than 14 string replace operations)

----------------------------------------
Testing functions single re.sub operation, 14 string replace operations:

Results after 10 loops, with large text of 75MB:
1 - 14 string replace operations: 19.107556999999986
2 - single re.sub operation: 43.3557414
(14 string replace operations ca. 2.3 times faster than single re.sub operation)

"""

import re
import timeit


def time_functions(functions, loops, string_descr):
    """Check which function is faster.

    Args:
        functions (list): a list of tuples (function_name (str),
                                            function_descr (str))
        loops (list): a list of integers, representing the numbers
            of times a pair of functions should be timed.
        string_descr (str): a description of the test string.
    NB: the functions to be tested should not have arguments.
    """
    print("--"*20)
    print("Testing functions {}:".format(", ".join([y for x,y in functions])))
    print()
    accuracy = (len(set([eval(f[0]+'()') for f in functions])) == 1)
    print("All functions have the same outcome: ", accuracy)
    for n in loops:
        results = []
        for f, f_descr in functions:
            t = timeit.timeit(f+"()", setup="from __main__ import "+f, number=n)
            results.append([f_descr, t])
        results = sorted(results, key=lambda item: item[1])
        print("Results after {} loops, with {}:".format(n, string_descr))
        for i, x in enumerate(results):
            print("{} - {}: {}".format(i+1, x[0], x[1]))
        for x in results[1:]:
            fmt = "({} ca. {} times faster than {})"
            print(fmt.format(results[0][0], round(x[1]/results[0][1], 1), x[0]))
        print()



def re_sub_deNoise(text):
    noise = re.compile(""" ّ    | # Tashdid
                           َ    | # Fatha
                           ً    | # Tanwin Fath
                           ُ    | # Damma
                           ٌ    | # Tanwin Damm
                           ِ    | # Kasra
                           ٍ    | # Tanwin Kasr
                           ْ    | # Sukun
                           ـ     # Tatwil/Kashida
                         """, re.VERBOSE)
    return re.sub(noise, '', text)


def repl_deNoise(text):
    text = text.replace("ّ", "")  # Tashdid
    text = text.replace("َ", "")  # Fatha
    text = text.replace("ً", "")  # Tanwin Fath
    text = text.replace("ُ", "")  # Damma
    text = text.replace("ٌ", "")  # Tanwin Damm
    text = text.replace("ِ", "")  # Kasra
    text = text.replace("ٍ", "")  # Tanwin Kasr
    text = text.replace("ْ", "")  # Sukun
    text = text.replace("ـ", "") # Tatwil/Kashida
    return text

def re_sub_deNoise_test():
    """A function without arguments, needed for timeit.
    NB: uses global variable text to solve the argument problem"""
    return re_sub_deNoise(text)

def repl_deNoise_test():
    """A function without arguments, needed for timeit.
    NB: uses global variable text to solve the argument problem"""
    return repl_deNoise(text)



def re_sub_normalizeArabic(text):
    text = re.sub("[إأٱآ]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("(ؤ)", "و", text)
    text = re.sub("(ئ)", "ي", text)
    text = re.sub("(ة)", "ه", text)
    return text

def repl_normalizeArabic(text):
    text = text.replace("أ", "ا")
    text = text.replace("ٱ", "ا")
    text = text.replace("آ", "ا")
    text = text.replace("إ", "ا")
    text = text.replace("ى", "ي")
    text = text.replace("ؤ", "و")
    text = text.replace("ئ", "ي")
    text = text.replace("ة", "ه")
    return text


def mix_normalizeArabic(text):
    text = re.sub("[إأٱآ]", "ا", text)
    text = text.replace("ى", "ي")
    text = text.replace("ؤ", "و")
    text = text.replace("ئ", "ي")
    text = text.replace("ة", "ه")
    return text


def re_sub_normalizeArabic_test():
    """A function without arguments, needed for timeit.
    NB: uses global variable text to solve the argument problem"""
    return re_sub_normalizeArabic(text)

def repl_normalizeArabic_test():
    """A function without arguments, needed for timeit.
    NB: uses global variable text to solve the argument problem"""
    return repl_normalizeArabic(text)

def mix_normalizeArabic_test():
    """A function without arguments, needed for timeit.
    NB: uses global variable text to solve the argument problem"""
    return mix_normalizeArabic(text)


def re_sub_denormalize(text):
    """Replace complex characters with a regex covering all variants."""
    alifs = '[إأٱآا]'
    alif_maqsura = '[يى]\b'
    ta_marbutas = '[هة]\b'
    hamzas = '[ؤئء]'
    hamzas_reg = '[ؤئءوي]'
    # Applying deNormalization
    text = re.sub(alifs, alifs, text)
    text = re.sub(alif_maqsura, alif_maqsura, text)
    text = re.sub(ta_marbutas, ta_marbutas, text)
    text = re.sub(hamzas, hamzas_reg, text)
    return text

def repl_denormalize(text):
    """Replace complex characters with a regex covering all variants."""
    text = text.replace("أ", "[إأٱآا]")
    text = text.replace("ٱ", "[إأٱآا]")
    text = text.replace("آ", "[إأٱآا]")
    text = text.replace("إ", "[إأٱآا]")
    text = text.replace("ى", "[يى]")
    text = text.replace("ي", "[يى]")
    text = text.replace("ؤ", "[ؤئءوي]")
    text = text.replace("ئ", "[ؤئءوي]")
    text = text.replace("ء", "[ؤئءوي]")
    text = text.replace("ة", "[هة]")
    return text

def re_sub_denormalize_test():
    """A function without arguments, needed for timeit.
    NB: uses global variable text to solve the argument problem"""
    return re_sub_denormalize(text)

def repl_denormalize_test():
    """A function without arguments, needed for timeit.
    NB: uses global variable text to solve the argument problem"""
    return repl_denormalize(text)


def single_re_sub_empty(text, repl_chars):
    """Remove specific characters from a string using a single regex."""
    repl = re.compile("[{}]".format(repl_chars))
    return repl.sub("", text)

def multiple_str_repl_empty(text, repl_chars):
    """Remove specific characters from a string
    using multiple string replace operations."""
    for c in repl_chars:
        text = text.replace(c, "")
    return text

def single_re_sub_empty_test():
    """A function without arguments, needed for timeit.
    NB: uses global variable text to solve the argument problem"""
    return single_re_sub_empty(text, repl_chars)

def multiple_str_repl_empty_test():
    """A function without arguments, needed for timeit.
    NB: uses global variable text to solve the argument problem"""
    return multiple_str_repl_empty(text, repl_chars)



def single_re_sub(text, repl_chars):
    """Replace specific characters with another character using a single regex."""
    repl = re.compile("[{}]".format(repl_chars))
    return repl.sub("a", text)

def multiple_str_repl(text, repl_chars):
    """Replace specific characters with another character
    using multiple string replace operations."""
    for c in repl_chars:
        text = text.replace(c, "a")
    return text

def single_re_sub_test():
    """A function without arguments, needed for timeit.
    NB: uses global variable text to solve the argument problem"""
    return single_re_sub(text, repl_chars)

def multiple_str_repl_test():
    """A function without arguments, needed for timeit.
    NB: uses global variable text to solve the argument problem"""
    return multiple_str_repl(text, repl_chars)


page = """
بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ
الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ
الرَّحْمَنِ الرَّحِيمِ
مَالِكِ يَوْمِ الدِّينِ
إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ
اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ
صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ
بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ الم
ذَلِكَ الْكِتَابُ لَا رَيْبَ فِيهِ هُدًى لِلْمُتَّقِينَ
الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ وَمِمَّا رَزَقْنَاهُمْ يُنْفِقُونَ
وَالَّذِينَ يُؤْمِنُونَ بِمَا أُنْزِلَ إِلَيْكَ وَمَا أُنْزِلَ مِنْ قَبْلِكَ وَبِالْآخِرَةِ هُمْ يُوقِنُونَ
أُولَئِكَ عَلَى هُدًى مِنْ رَبِّهِمْ وَأُولَئِكَ هُمُ الْمُفْلِحُونَ
إِنَّ الَّذِينَ كَفَرُوا سَوَاءٌ عَلَيْهِمْ أَأَنْذَرْتَهُمْ أَمْ لَمْ تُنْذِرْهُمْ لَا يُؤْمِنُونَ
خَتَمَ اللَّهُ عَلَى قُلُوبِهِمْ وَعَلَى سَمْعِهِمْ وَعَلَى أَبْصَارِهِمْ غِشَاوَةٌ وَلَهُمْ عَذَابٌ عَظِيمٌ
وَمِنَ النَّاسِ مَنْ يَقُولُ آمَنَّا بِاللَّهِ وَبِالْيَوْمِ الْآخِرِ وَمَا هُمْ بِمُؤْمِنِينَ
يُخَادِعُونَ اللَّهَ وَالَّذِينَ آمَنُوا وَمَا يَخْدَعُونَ إِلَّا أَنْفُسَهُمْ وَمَا يَشْعُرُونَ
فِي قُلُوبِهِمْ مَرَضٌ فَزَادَهُمُ اللَّهُ مَرَضًا وَلَهُمْ عَذَابٌ أَلِيمٌ بِمَا كَانُوا يَكْذِبُونَ
وَإِذَا قِيلَ لَهُمْ لَا تُفْسِدُوا فِي الْأَرْضِ قَالُوا إِنَّمَا نَحْنُ مُصْلِحُونَ
أَلَا إِنَّهُمْ هُمُ الْمُفْسِدُونَ وَلَكِنْ لَا يَشْعُرُونَ
وَإِذَا قِيلَ لَهُمْ آمِنُوا كَمَا آمَنَ النَّاسُ قَالُوا أَنُؤْمِنُ كَمَا آمَنَ السُّفَهَاءُ أَلَا إِنَّهُمْ هُمُ السُّفَهَاءُ وَلَكِنْ لَا يَعْلَمُونَ
وَإِذَا لَقُوا الَّذِينَ آمَنُوا قَالُوا آمَنَّا وَإِذَا خَلَوْا إِلَى شَيَاطِينِهِمْ قَالُوا إِنَّا مَعَكُمْ إِنَّمَا نَحْنُ مُسْتَهْزِئُونَ
اللَّهُ يَسْتَهْزِئُ بِهِمْ وَيَمُدُّهُمْ فِي طُغْيَانِهِمْ يَعْمَهُونَ
أُولَئِكَ الَّذِينَ اشْتَرَوُا الضَّلَالَةَ بِالْهُدَى فَمَا رَبِحَتْ تِجَارَتُهُمْ وَمَا كَانُوا مُهْتَدِينَ
مَثَلُهُمْ كَمَثَلِ الَّذِي اسْتَوْقَدَ نَارًا فَلَمَّا أَضَاءَتْ مَا حَوْلَهُ ذَهَبَ اللَّهُ بِنُورِهِمْ وَتَرَكَهُمْ فِي ظُلُمَاتٍ لَا يُبْصِرُونَ
صُمٌّ بُكْمٌ عُمْيٌ فَهُمْ لَا يَرْجِعُونَ
أَوْ كَصَيِّبٍ مِنَ السَّمَاءِ فِيهِ ظُلُمَاتٌ وَرَعْدٌ وَبَرْقٌ يَجْعَلُونَ أَصَابِعَهُمْ فِي آذَانِهِمْ مِنَ الصَّوَاعِقِ حَذَرَ الْمَوْتِ وَاللَّهُ مُحِيطٌ بِالْكَافِرِينَ
يَكَادُ الْبَرْقُ يَخْطَفُ أَبْصَارَهُمْ كُلَّمَا أَضَاءَ لَهُمْ مَشَوْا فِيهِ وَإِذَا أَظْلَمَ عَلَيْهِمْ قَامُوا وَلَوْ شَاءَ اللَّهُ لَذَهَبَ بِسَمْعِهِمْ وَأَبْصَارِهِمْ إِنَّ اللَّهَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ
يَا أَيُّهَا النَّاسُ اعْبُدُوا رَبَّكُمُ الَّذِي خَلَقَكُمْ وَالَّذِينَ مِنْ قَبْلِكُمْ لَعَلَّكُمْ تَتَّقُونَ
الَّذِي جَعَلَ لَكُمُ الْأَرْضَ فِرَاشًا وَالسَّمَاءَ بِنَاءً وَأَنْزَلَ مِنَ السَّمَاءِ مَاءً فَأَخْرَجَ بِهِ مِنَ الثَّمَرَاتِ رِزْقًا لَكُمْ فَلَا تَجْعَلُوا لِلَّهِ أَنْدَادًا وَأَنْتُمْ تَعْلَمُونَ
وَإِنْ كُنْتُمْ فِي رَيْبٍ مِمَّا نَزَّلْنَا عَلَى عَبْدِنَا فَأْتُوا بِسُورَةٍ مِنْ مِثْلِهِ وَادْعُوا شُهَدَاءَكُمْ مِنْ دُونِ اللَّهِ إِنْ كُنْتُمْ صَادِقِينَ
"""

fp = r"D:\London\OpenITI\bok\ShamelaRARs\converted\4_OpenITI_mARkdown_new\Shamela026332.txt"
with open(fp, mode="r", encoding="utf-8") as file:
    large_text = file.read()

##    
##text = page  # set the global text variable
##
##time_functions([("re_sub_deNoise_test", "re.sub deNoise"),
##                ("repl_deNoise_test", "string replace deNoise"),],
##               [100, 10000],
##               "30 first lines of the Qur'an")
##
##text = large_text  # reset the global text variable
##
##time_functions([("re_sub_deNoise_test", "re.sub deNoise"),
##                ("repl_deNoise_test", "string replace deNoise")],
##               [10, 50],
##               "large text of 75MB")
##
##
##text = page  # reset the global text variable
##
##time_functions([("re_sub_normalizeArabic_test", "re.sub normalization"),
##                ("repl_normalizeArabic_test", "string replace normalization"),
##                ("mix_normalizeArabic_test", "mixed normalization")],
##               [100, 10000, 100000],
##               "30 first lines of the Qur'an")
##
##text = large_text  # reset the global text variable
##
##time_functions([("re_sub_normalizeArabic_test", "re.sub normalization"),
##                ("repl_normalizeArabic_test", "string replace normalization"),
##                ("mix_normalizeArabic_test", "mixed normalization")],
##               [10, 50],
##               "large text of 75MB")

##text = page  # reset the global text variable
##
##time_functions([("re_sub_denormalize_test", "re.sub denormalization"),
##                ("repl_denormalize_test", "string replace denormalization")],
##               [100, 10000, 100000],
##               "30 first lines of the Qur'an")
##
##text = large_text  # reset the global text variable
##
##time_functions([("re_sub_denormalize_test", "re.sub denormalization"),
##                ("repl_denormalize_test", "string replace denormalization")],
##               [10, 50],
##               "large text of 75MB")

##chars = "جحخهعغفقثصضكمنتالبيسشزوةىرؤءئ"
##for x in range(15, 25):
##    repl_chars = chars[:x]
##    text = page  # reset the global text variable
##
##    time_functions([("single_re_sub_test", "single re.sub operation"),
##                    ("multiple_str_repl_test",
##                     "{} string replace operations".format(len(repl_chars)))],
##                   [100, 10000],
##                   "30 first lines of the Qur'an")
##
##    text = large_text  # reset the global text variable
##
##    time_functions([("single_re_sub_test", "single re.sub operation"),
##                    ("multiple_str_repl_test",
##                     "{} string replace operations".format(len(repl_chars)))],
##                    [10],
##                   "large text of 75MB")

chars = "جحخهعغفقثصضكمنتالبيسشزوةىرؤءئ"
for x in range(5, 25):
    repl_chars = chars[:x]
    text = page  # reset the global text variable

    time_functions([("single_re_sub_empty_test", "single re.sub remove"),
                    ("multiple_str_repl_empty_test",
                     "{} string replace operations".format(len(repl_chars)))],
                   [100, 10000, 100000],
                   "30 first lines of the Qur'an")

    text = large_text  # reset the global text variable

    time_functions([("single_re_sub_empty_test", "single re.sub remove"),
                    ("multiple_str_repl_empty_test",
                     "{} string replace operations".format(len(repl_chars)))],
                    [10, 50],
                   "large text of 75MB")

