"""
Test relative speed of compiled regexes vs. normal regex

Result: no significant speed difference

Printout:

----------------------------------------
Testing functions re.sub(uncompiled_noise, '', text),
                  compiled_noise.sub('', text),
                  re.sub(compiled_noise, '', text),
                  re.sub(uncompiled_noise, '', text) second run:

All functions have the same outcome:  True
Results after 100 loops, with 30 first lines of the Qur'an:
1 - compiled_noise.sub('', text): 0.025620200000000003
2 - re.sub(compiled_noise, '', text): 0.027312799999999998
3 - re.sub(uncompiled_noise, '', text): 0.0312185
4 - re.sub(uncompiled_noise, '', text) second run: 0.0332567
(compiled_noise.sub('', text) ca. 1.1 times faster than re.sub(compiled_noise, '', text))
(compiled_noise.sub('', text) ca. 1.2 times faster than re.sub(uncompiled_noise, '', text))
(compiled_noise.sub('', text) ca. 1.3 times faster than re.sub(uncompiled_noise, '', text) second run)

Results after 10000 loops, with 30 first lines of the Qur'an:
1 - compiled_noise.sub('', text): 2.5880406999999996
2 - re.sub(compiled_noise, '', text): 2.5930370000000007
3 - re.sub(uncompiled_noise, '', text): 2.6693532
4 - re.sub(uncompiled_noise, '', text) second run: 2.7063191
(compiled_noise.sub('', text) ca. 1.0 times faster than re.sub(compiled_noise, '', text))
(compiled_noise.sub('', text) ca. 1.0 times faster than re.sub(uncompiled_noise, '', text))
(compiled_noise.sub('', text) ca. 1.0 times faster than re.sub(uncompiled_noise, '', text) second run)


Results after 100000 loops, with 30 first lines of the Qur'an:
1 - compiled_noise.sub('', text): 26.794016499999998
2 - re.sub(uncompiled_noise, '', text) second run: 26.809392700000004
3 - re.sub(uncompiled_noise, '', text): 27.1023572
4 - re.sub(compiled_noise, '', text): 27.329767200000006
(compiled_noise.sub('', text) ca. 1.0 times faster than re.sub(uncompiled_noise, '', text) second run)
(compiled_noise.sub('', text) ca. 1.0 times faster than re.sub(uncompiled_noise, '', text))
(compiled_noise.sub('', text) ca. 1.0 times faster than re.sub(compiled_noise, '', text))

----------------------------------------
Testing functions compiled_noise.sub('', text), re.sub(compiled_noise, '', text), re.sub(uncompiled_noise, '', text):

All functions have the same outcome:  True
Results after 10 loops, with large text of 75MB:
1 - re.sub(uncompiled_noise, '', text): 3.2946443999999957
2 - compiled_noise.sub('', text): 3.3465494000000007
3 - re.sub(compiled_noise, '', text): 3.352638099999993
(re.sub(uncompiled_noise, '', text) ca. 1.0 times faster than compiled_noise.sub('', text))
(re.sub(uncompiled_noise, '', text) ca. 1.0 times faster than re.sub(compiled_noise, '', text))


Results after 50 loops, with large text of 75MB:
1 - re.sub(compiled_noise, '', text): 16.902413100000018
2 - re.sub(uncompiled_noise, '', text): 16.9217314
3 - compiled_noise.sub('', text): 17.0021323
(re.sub(compiled_noise, '', text) ca. 1.0 times faster than re.sub(uncompiled_noise, '', text))
(re.sub(compiled_noise, '', text) ca. 1.0 times faster than compiled_noise.sub('', text))
"""

import re
import timeit

noiseC = re.compile(""" ّ    | # Tashdīd / Shadda
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
noise = '[ًࣰٌࣱٍࣲَُِّْٰۡـ]'



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


def re_sub_deNoise_test1():
    return noiseC.sub('', text)

def re_sub_deNoise_test2():
    return re.sub(noiseC, '', text)

def re_sub_deNoise_test3():
    return re.sub(noise, '', text)

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

fp = r"D:\London\OpenITI\new_books\bok\ShamelaRARs\converted\4_OpenITI_mARkdown_new\Shamela026332.txt"
with open(fp, mode="r", encoding="utf-8") as file:
    large_text = file.read()

text = page  # reset the global text variable

time_functions([("re_sub_deNoise_test3", "re.sub(uncompiled_noise, '', text)"),
                ("re_sub_deNoise_test1", "compiled_noise.sub('', text)"),
                ("re_sub_deNoise_test2", "re.sub(compiled_noise, '', text)"),
                ("re_sub_deNoise_test3", "re.sub(uncompiled_noise, '', text) second run")],
               [100, 10000, 100000],
               "30 first lines of the Qur'an")

text = large_text  # reset the global text variable

time_functions([("re_sub_deNoise_test1", "compiled_noise.sub('', text)"),
                ("re_sub_deNoise_test2", "re.sub(compiled_noise, '', text)"),
                ("re_sub_deNoise_test3", "re.sub(uncompiled_noise, '', text)")],
                [10, 50],
               "large text of 75MB")

