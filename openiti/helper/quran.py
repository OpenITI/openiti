"""
Normalize Qur'an text in a safe way. 

Example:
    >>> from quran import special_letters_regex, normalise_quran
    >>> text_tokens = re.split("\s+", text)
    >>> for tok in text_tokens:
            if re.findall(special_letters_regex, tok):
                n = normalise_quran(tok, post_process=True)
                text = re.sub(tok, n, text)


IMPORTANT: post-correction step will affect non-Quranic text as well!
Use the post-processing of the normalise_quran function only on 
tokens / sections that are positively identified as Qur'an text.

This module contains both a function to normalise Qur'an text
(normalise_quran) and the functions used to create the normalisation procedure.

The way the normalisation procedure was devised was 
to compare the traditional spelling of the text (the so-called "uthmani" spelling)
to a standardized version (the "simple" or "imlāʾī" version of the tanzil.net Qur'ān)
and to build a procedure to convert the traditional spelling to the new one. 

The procedure consists of:
* converting non-standard combinations of characters into standard characters;
* denoising: removing all (remaining) non-standard characters;
* fixing a number of inconsistencies in the traditional spelling / in standard practise (e.g., 
  many words are written with a dagger alif in the traditional spelling and normal alif in standard spelling, 
  but some words like Allāh, lākin and raḥmān are also written with dagger alif in standard spelling)

The procedure was created as follows:
* both texts were tokenized in such a way that each token in the Uthmani version 
  corresponds to a token in the simplified version (e.g., "yĀdam", "yā Ādam")
* a list of characters that is only present in the Uthmani version was made
* For each of those characters, a sample of all its contexts (n characters before/after) was 
  extracted from the Uthmani and simplified tokens
* based on the comparison between both, conversion rules were created
* Finally, a script went through the Uthmani text token by token 
  and checked if applying those rules generated the simplified tokens; 
  if not, the rules were changed or the inconsistency was solved by adding the token to a list of exceptions

NB: The result is near perfect. Only in the case of one token (تَدۡعُواْ), 
which has different spellings in the simplified version (تدعو - تدعوا)
for the same spellling in the Uthmani version (تَدۡعُواْ), 
changing the rules and using the exceptions approach
does not result in a consistent transcription. 
One possibility is adding a post-postprocessing step that corrects 
the reading of the one occurrence of the token where it is written
without alif (using the previous and next word).


Texts used:
* simplified version ("imlāʾī" script: standard Arabic grammar and script rules): tanzil.net/download, quran-simple-clean.txt (also tested with quran-simple.txt)
* Uthmani version: https://github.com/risan/quran-json/blob/main/dist/quran.json

Further checks with the Qur'ān texts from the OpenITI corpus showed that they, too,
have only minimal changes from the Uthmani text when normalised with this script
(in addition to the token mentioned: an extra space in baʿda mā,
and a different choice for an alif maksūra / alif in three tokens)
"""

import re
import unicodedata
import json


if __name__ == '__main__':
    # make sure openiti modules can be loaded:
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    sys.path.append(root_folder)

from openiti.helper import ara


###########################
# NORMALIZATION PROCEDURE #
###########################

# The procedure was created as follows:
# * both texts were tokenized in such a way that each token in the Uthmani version 
#   corresponds to a token in the simplified version (e.g., "yĀdam", "yā Ādam")
# * a list of characters that is only present in the Uthmani version was made
# * For each of those characters, a sample of all its contexts (n characters before/after) was 
#   extracted from the Uthmani and simplified tokens
# * based on the comparison between both, conversion rules were created
# * Finally, a script went through the Uthmani text token by token 
#   and checked if applying those rules generated the simplified tokens; 
#   if not, the rules were changed or the inconsistency was solved by adding the token to a list of exceptions


# 1. Rules for normalising character combinations:
quran_normalisation_steps = [

    # remove graphical insertions first:

    ["ARABIC TATWEEL", ""],
    ["THIN SPACE", ""],  # only once in Quran: "فَٱدَّٰرَــ ــٰٔتُمۡ" > "فادارأتم"
    ["ARABIC START OF RUB EL HIZB", ""],

    # ARABIC HAMZA ABOVE: 

    ## if preceded by ḍamma:
    ["ARABIC DAMMA_ARABIC HAMZA ABOVE_ARABIC DAMMA", "وء"],
    ["ARABIC DAMMA_ARABIC HAMZA ABOVE_ARABIC SMALL HIGH DOTLESS HEAD OF KHAH", "ؤ"],

    ## if preceded by fatḥa:
    ["ARABIC FATHA_ARABIC HAMZA ABOVE_ARABIC FATHA_ARABIC LETTER ALEF", "آ"],
    ["ARABIC FATHA_ARABIC HAMZA ABOVE_ARABIC FATHA", "آ"],

    ["ARABIC FATHA_ARABIC HAMZA ABOVE_ARABIC FATHATAN_ARABIC LETTER ALEF", "أ"],
    ["ARABIC FATHA_ARABIC HAMZA ABOVE_ARABIC FATHATAN", "أ"],
    ["ARABIC FATHA_ARABIC HAMZA ABOVE_ARABIC INVERTED DAMMA_ARABIC LETTER ALEF", "أ"],
    ["ARABIC FATHA_ARABIC HAMZA ABOVE_ARABIC INVERTED DAMMA", "أ"],
    ["ARABIC FATHA_ARABIC HAMZA ABOVE_ARABIC SMALL HIGH DOTLESS HEAD OF KHAH", "أ"],

    ["ARABIC FATHA_ARABIC HAMZA ABOVE_ARABIC KASRA", "ئ"],
    ["ARABIC FATHA_ARABIC HAMZA ABOVE_ARABIC DAMMA", "ئ"],

    ## if preceded by kasra:
    ["ARABIC KASRA_ARABIC HAMZA ABOVE_ARABIC DAMMA", "ئ"],
    ["ARABIC KASRA_ARABIC HAMZA ABOVE_ARABIC KASRA", "ئ"],
    ["ARABIC SHADDA_ARABIC KASRA_ARABIC HAMZA ABOVE_ARABIC FATHA_ARABIC LETTER ALEF", "ئا"], # as in: سَئَِّاتِكُمۡۗ > سيئاتكم
    ["ARABIC KASRA_ARABIC HAMZA ABOVE_ARABIC FATHA_ARABIC LETTER ALEF", "آ"], # as in: بَِٔايَٰتِنَآ > بآياتنا
    ["ARABIC KASRA_ARABIC HAMZA ABOVE_ARABIC FATHA", "ئ"],

    ## if preceded by dagger alif:
    ["ARABIC LETTER SUPERSCRIPT ALEF_ARABIC HAMZA ABOVE_ARABIC LETTER TEH", "أت"],

    ["ARABIC LETTER SUPERSCRIPT ALEF_ARABIC MADDAH ABOVE_ARABIC HAMZA ABOVE_ARABIC DAMMA", "اء"],

    ## if preceded by madda:
    ["ARABIC MADDAH ABOVE_ARABIC HAMZA ABOVE_ARABIC DAMMA", "ئ"],
    ["ARABIC MADDAH ABOVE_ARABIC HAMZA ABOVE_ARABIC INVERTED DAMMA", "ئ"],
    #["ARABIC LETTER YEH_ARABIC MADDAH ABOVE_ARABIC HAMZA ABOVE_ARABIC FATHA","ئ"],
    ["ARABIC LETTER YEH_ARABIC MADDAH ABOVE_ARABIC HAMZA ABOVE_ARABIC FATHA","يئ"],

    ["ARABIC MADDAH ABOVE_ARABIC HAMZA ABOVE_ARABIC KASRA", "ئ"],

    ["ARABIC FATHA_ARABIC LETTER SUPERSCRIPT ALEF_ARABIC MADDAH ABOVE_ARABIC HAMZA ABOVE_ARABIC FATHA_ARABIC LETTER ALEF", "اآ"],

    # if preceded by sukūn:
    ["ARABIC SMALL HIGH DOTLESS HEAD OF KHAH_ARABIC HAMZA ABOVE_ARABIC FATHA_ARABIC LETTER SUPERSCRIPT ALEF", "آ"],

    ["ARABIC LETTER YEH_ARABIC SMALL HIGH DOTLESS HEAD OF KHAH_ARABIC HAMZA ABOVE_ARABIC FATHA_ARABIC LETTER TEH MARBUTA", "يئة"],  # as in كَهَيَۡٔةِ > كهيئة
    ["ARABIC SMALL HIGH DOTLESS HEAD OF KHAH_ARABIC HAMZA ABOVE_ARABIC FATHA_ARABIC LETTER ALEF", "آ"],  # as in ٱلظَّمَۡٔانُ > الظمآن
    ["ARABIC SMALL HIGH DOTLESS HEAD OF KHAH_ARABIC HAMZA ABOVE_ARABIC FATHA", "أ"],

    ["ARABIC SMALL HIGH DOTLESS HEAD OF KHAH_ARABIC HAMZA ABOVE_ARABIC FATHATAN", "ئ"],
    ["ARABIC SMALL HIGH DOTLESS HEAD OF KHAH_ARABIC HAMZA ABOVE_ARABIC DAMMA", "ئ"],
    ["ARABIC SMALL HIGH DOTLESS HEAD OF KHAH_ARABIC HAMZA ABOVE_ARABIC INVERTED DAMMA", "ئ"],
    ["ARABIC SMALL HIGH DOTLESS HEAD OF KHAH_ARABIC HAMZA ABOVE_ARABIC KASRA", "ئ"],

    # ARABIC HAMZA BELOW: 

    ## preceded by waw:
    ["ARABIC LETTER WAW_ARABIC HAMZA BELOW", "ؤ"],

    ## preceded by yā':
    ["ARABIC LETTER SUPERSCRIPT ALEF_ARABIC MADDAH ABOVE_ARABIC LETTER YEH_ARABIC HAMZA BELOW_ARABIC KASRA", "اء"],

    ["ARABIC LETTER ALEF_ARABIC MADDAH ABOVE_ARABIC LETTER YEH_ARABIC HAMZA BELOW_ARABIC KASRA", "اء"],
    ["ARABIC LETTER YEH_ARABIC HAMZA BELOW_ARABIC KASRA", "ئ"],
    ["ARABIC LETTER YEH_ARABIC HAMZA BELOW_ARABIC SUBSCRIPT ALEF", "ئ"],

    # ARABIC MADDAH ABOVE:

    ## preceded by alif with hamza above:
    ["ARABIC LETTER ALEF WITH HAMZA ABOVE_ARABIC MADDAH ABOVE", "آ"],

    ## preceded by alif:
    ["ARABIC LETTER ALEF_ARABIC MADDAH ABOVE", "ا"], # but in the middle of the word, sometimes alif+madda!

    # preceded by dagger alif:
    ["ARABIC LETTER BEH_ARABIC FATHA_ARABIC LETTER WAW_ARABIC LETTER SUPERSCRIPT ALEF_ARABIC MADDAH ABOVE_ARABIC LETTER ALEF", "با"], 
    ["ARABIC LETTER SUPERSCRIPT ALEF_ARABIC MADDAH ABOVE_ARABIC LETTER ALEF WITH HAMZA ABOVE", "ا أ"],
    ["ARABIC LETTER SUPERSCRIPT ALEF_ARABIC MADDAH ABOVE_ARABIC LETTER ALEF WITH HAMZA BELOW", "ا إ"],
    ["ARABIC LETTER SUPERSCRIPT ALEF_ARABIC MADDAH ABOVE_ARABIC LETTER HAMZA", "ائ"],   # as in إِسۡرَٰٓءِيلَ > إسرائيل
    #["ARABIC LETTER SUPERSCRIPT ALEF_ARABIC MADDAH ABOVE_ARABIC LETTER WAW WITH HAMZA ABOVE", "ؤ"], # hā'ulā'
    #["ARABIC LETTER SUPERSCRIPT ALEF_ARABIC MADDAH ABOVE_ARABIC LETTER YEH WITH HAMZA ABOVE", "ئ"], # ūlā'ika BUT: للملائكة

    ["ARABIC LETTER SUPERSCRIPT ALEF_ARABIC MADDAH ABOVE_ARABIC SMALL HIGH JEEM", ""],  # remove
    ["ARABIC LETTER SUPERSCRIPT ALEF_ARABIC MADDAH ABOVE_ARABIC SMALL HIGH LIGATURE QAF WITH LAM WITH ALEF MAKSURA", ""], # remove
    ["ARABIC LETTER SUPERSCRIPT ALEF_ARABIC MADDAH ABOVE_ARABIC SMALL HIGH LIGATURE SAD WITH LAM WITH ALEF MAKSURA", ""], # remove

    #["ARABIC LETTER WAW_ARABIC LETTER SUPERSCRIPT ALEF_ARABIC MADDAH ABOVE", "ا"],  # as in 'ٱلصَّلَوٰةِۚ' for الصلاة

    ["ARABIC LETTER ALEF MAKSURA_ARABIC LETTER SUPERSCRIPT ALEF_ARABIC MADDAH ABOVE", "ى"],  # as in وَعَلَىٰٓ > وعلى

    ["ARABIC LETTER SUPERSCRIPT ALEF_ARABIC MADDAH ABOVE", "ا"], # replace with alif in all other cases

    ## preceded by waw: 
    ["ARABIC LETTER WAW_ARABIC MADDAH ABOVE_ARABIC LETTER ALEF WITH HAMZA ABOVE_ARABIC FATHA_ARABIC LETTER ALEF MAKSURA", "وأى"],
    ["ARABIC LETTER WAW_ARABIC MADDAH ABOVE_ARABIC LETTER ALEF WITH HAMZA ABOVE", "وء"],
    ["ARABIC LETTER WAW_ARABIC MADDAH ABOVE_ARABIC LETTER HAMZA", "وء"],

    ["ARABIC LETTER WAW_ARABIC DAMMA_ARABIC SMALL WAW_ARABIC MADDAH ABOVE_ARABIC LETTER ALEF", "ووا"],

    ## preceded by yā':
    ["ARABIC LETTER YEH_ARABIC MADDAH ABOVE_ARABIC HAMZA ABOVE", "يئ"],


    # ARABIC SMALL WAW:

    ["ARABIC SMALL WAW_(?!\w)", ""], # remove at end of a word
    ["ARABIC SMALL WAW", "و"], # replace with waw in all other cases

    # ARABIC SMALL YEH:

    ["ARABIC LETTER HEH_ARABIC KASRA_ARABIC SMALL YEH", "ه"], # remove if it follows hā'
    ["ARABIC SMALL YEH", "ي"], # replace with yā' in all other cases

    # ARABIC SMALL HIGH YEH:

    ["ARABIC SMALL HIGH YEH", "ي"], # replace with yā' in all cases

    # ARABIC SMALL HIGH NOON:

    ["ARABIC SMALL HIGH NOON", "ن"], # replace with nūn in the only existing case: "نُــۨــجِي" > "ننجي"

    # ARABIC VOWEL SIGN DOT BELOW:

    ["ARABIC VOWEL SIGN DOT BELOW_ARABIC LETTER ALEF MAKSURA_ARABIC LETTER SUPERSCRIPT ALEF", "ا"],  # only once in the Qur'ān: "مَجۡرــٜــىٰهَا" >  "مجراها"

    # ARABIC LETTER SUPERSCRIPT ALEF

    ## preceded by waw:
    ["ARABIC LETTER WAW_ARABIC LETTER SUPERSCRIPT ALEF", "ا"],  # as in 'ٱلصَّلَوٰةِۚ' for الصلاة

    ## preceded by alif maqṣūra:
    ["ARABIC LETTER ALEF MAKSURA_ARABIC LETTER SUPERSCRIPT ALEF", "ى"], 

    ## preceded by yā' at the beginning of a word:
    ["(\s|^)_ARABIC LETTER YEH_ARABIC FATHA_ARABIC LETTER SUPERSCRIPT ALEF", r"\1يا "],

    # ARABIC LETTER ALEF WASLA:

    ["ARABIC LETTER ALEF WASLA_ARABIC LETTER LAM_ARABIC SHADDA_ARABIC FATHA_ARABIC LETTER THAL_ARABIC KASRA", "الذ"],  # al-laḏī (al-laḏāt with two lams...)
    ["ARABIC LETTER ALEF WASLA_ARABIC LETTER LAM_ARABIC SHADDA_ARABIC FATHA_ARABIC LETTER TEH", "الت"],   # al-latī
    ["ARABIC LETTER ALEF WASLA_ARABIC LETTER LAM_ARABIC SHADDA", "الل"],
    ["ARABIC LETTER ALEF WASLA", "ا"],
    
    # ARABIC FATHA WITH TWO DOTS:
 
    ["ARABIC LETTER WAW WITH HAMZA ABOVE_ARABIC FATHA WITH TWO DOTS_ARABIC LETTER ALEF", "ء"],  # only once: "بَلَٰٓؤــٞــاْ" > "بلاء"
    ["ARABIC FATHA WITH TWO DOTS", ""],  # remove in all other cases

    # ARABIC SMALL HIGH SEEN:

    ["ARABIC LETTER SAD_ARABIC SMALL HIGH SEEN", "س"],
    ["ARABIC SMALL HIGH SEEN", ""],  # remove in all other cases

    # ARABIC SUKUN

    # special case: banū vs banaw vs ibnū:
    ["ARABIC LETTER ALEF WASLA_ARABIC LETTER BEH_ARABIC SMALL HIGH DOTLESS HEAD OF KHAH_ARABIC LETTER NOON_ARABIC DAMMA_ARABIC LETTER WAW_ARABIC MADDAH ABOVE_ARABIC LETTER ALEF_ARABIC SUKUN", "ابنو"], # ibnū
    ["ARABIC LETTER BEH_ARABIC FATHA_ARABIC LETTER NOON_ARABIC DAMMA_ARABIC LETTER WAW_ARABIC MADDAH ABOVE_ARABIC LETTER ALEF_ARABIC SUKUN", "بنو"], # banū
    ["ARABIC LETTER BEH_ARABIC FATHA_ARABIC LETTER NOON_ARABIC FATHA_ARABIC LETTER WAW_ARABIC SMALL HIGH DOTLESS HEAD OF KHAH_ARABIC LETTER ALEF_ARABIC SUKUN", "بنوا"], # banaw

    ## preceded by yā':
    #["ARABIC LETTER ALEF WITH HAMZA BELOW_ARABIC KASRA_ARABIC LETTER YEH_ARABIC SUKUN", "ئ"], # as in وَمَلَإِيْهِۦ > وملئه
    ["ARABIC LETTER YEH_ARABIC SUKUN", ""],  # as in نبإي > نبإ

    ## preceded by waw + maddah above + alef:
    #["ARABIC DAMMA_ARABIC LETTER WAW_ARABIC MADDAH ABOVE_ARABIC LETTER ALEF_ARABIC SUKUN", "و"],  # this works only for third radical weak verbs
    #["ARABIC FATHA_ARABIC LETTER WAW_ARABIC MADDAH ABOVE_ARABIC LETTER ALEF_ARABIC SUKUN", "وا"], # this works only for third radical weak verbs
    ["ARABIC LETTER WAW_ARABIC MADDAH ABOVE_ARABIC LETTER ALEF_ARABIC SUKUN", "وا"], 

    ## preceded by waw + small high dotless head of khah + alef:
    ["ARABIC LETTER WAW_ARABIC SMALL HIGH DOTLESS HEAD OF KHAH_ARABIC LETTER ALEF_ARABIC SUKUN", "وا"],  # as in بَنَوۡاْ > بنوا

    ## preceded by waw + alef:
    #["ARABIC LETTER WAW_ARABIC LETTER ALEF_ARABIC SUKUN", "و"],  # as in مُّلَٰقُواْ > ملاقو  BUT: the alif more commonly stays in place!
    #["ARABIC LETTER ALEF WITH HAMZA ABOVE_ARABIC DAMMA_ARABIC LETTER WAW_ARABIC SUKUN", "أ"], # as in  سَأُوْرِيكُمۡ > سأريكم BUT: ūlā'ika...

    ## preceded by waw with hamza above + alef:
    ["ARABIC LETTER ALEF_ARABIC LETTER WAW WITH HAMZA ABOVE_ARABIC DAMMA_ARABIC LETTER ALEF_ARABIC SUKUN", "اء"], # as in أَبۡنَٰٓؤُاْ > أبناء
    ["ARABIC LETTER WAW WITH HAMZA ABOVE_ARABIC DAMMA_ARABIC LETTER ALEF_ARABIC SUKUN", "أ"], 
    ["ARABIC FATHA_ARABIC LETTER WAW WITH HAMZA ABOVE_ARABIC DAMMATAN_ARABIC LETTER ALEF_ARABIC SUKUN", "أ"],
    ["ARABIC DAMMA_ARABIC LETTER WAW WITH HAMZA ABOVE_ARABIC DAMMATAN_ARABIC LETTER ALEF_ARABIC SUKUN", "ؤ"],

    ## preceded by alef (originally waw + superscript alef) + alef:
    ["ARABIC LETTER WAW_ARABIC LETTER SUPERSCRIPT ALEF_ARABIC LETTER ALEF_ARABIC SUKUN", "ا"],  # waw + superscript alif already changed to alif
    ["ARABIC LETTER ALEF_ARABIC LETTER ALEF_ARABIC SUKUN", "ا"],
    
    ## preceded by fatḥa + alef:
    ["ARABIC FATHA_ARABIC LETTER ALEF_ARABIC SUKUN", ""],  # as in  تَاْيَۡٔسُواْ > تيأسوا

    ## preceded by kasra + alef:
    ["ARABIC KASRA_ARABIC LETTER ALEF_ARABIC SUKUN_ARABIC LETTER YEH", "ي"], # as in  وَجِاْيٓءَ > وجيء

    # ARABIC LETTER HAMZA

    ["ARABIC LETTER HAMZA_ARABIC FATHA_ARABIC LETTER ALEF WITH HAMZA ABOVE_ARABIC FATHA_ARABIC LETTER SUPERSCRIPT ALEF", "أآ"], # as in  ءَأَٰلِهَتُنَا > أآلهتنا
    ["ARABIC LETTER HAMZA_ARABIC FATHA_ARABIC LETTER ALEF WITH HAMZA ABOVE_ARABIC FATHA", "أأ"],  # as in: ءَأَنذَرۡتَهُمۡ > أأنذرتهم
    ["ARABIC LETTER HAMZA_ARABIC FATHA_ARABIC LETTER ALEF_ARABIC ROUNDED HIGH STOP WITH FILLED CENTRE", "أأ"],  # as in:  ءَا۬عۡجَمِيّٞ > أأعجمي
    ["ARABIC LETTER ALEF WITH HAMZA ABOVE_ARABIC FATHA_ARABIC LETTER HAMZA_ARABIC KASRA", "أإ"],  # as in:  أَءِنَّكَ > أإنك
    ["ARABIC LETTER ALEF WITH HAMZA ABOVE_ARABIC FATHA_ARABIC LETTER HAMZA", "أأ"],  # as in:  أَءُنزِلَ > أأنزل
    

    ["ARABIC LETTER HAMZA_ARABIC FATHA_ARABIC LETTER SUPERSCRIPT ALEF", "آ"],  # as in  سَوۡءَٰتِهِمَا > سوآتهما
    ["ARABIC LETTER HAMZA_ARABIC FATHA_ARABIC LETTER ALEF", "آ"],  # as in ءَامَنَّا > آمنا
    ["ARABIC KASRA_ARABIC LETTER HAMZA_ARABIC DAMMA", "ئ"], # as in مُسۡتَهۡزِءُونَ > مستهزئون
    ["ARABIC KASRA_ARABIC LETTER HAMZA_ARABIC SMALL HIGH DOTLESS HEAD OF KHAH", "ئ"], # as in ورءيا > ورئيا
    ["ARABIC LETTER HAMZA_ARABIC KASRA_ARABIC LETTER YEH", "ئي"], 
    #["ARABIC FATHA_ARABIC LETTER HAMZA_ARABIC FATHA_ARABIC LETTER ALIF", "أى"], # as in رَءَا > رأى
    ["ARABIC FATHA_ARABIC LETTER HAMZA_ARABIC FATHA", "أ"], # as in أَرَءَيۡتَكُمۡ > أرأيتكم
    ["ARABIC DAMMA_ARABIC LETTER HAMZA_ARABIC SMALL HIGH DOTLESS HEAD OF KHAH", "ؤ"], # as in  رُءۡيَاكَ > رؤياك


    ["ARABIC LETTER ALEF MAKSURA_(?=\w)", "ا"], #  alif maksura not at the end of a word: replace with alif
    ["اآ", "ا آ"], 


    # ladā vs luddā:
    #["ARABIC LETTER LAM_ARABIC SHADDA_ARABIC DAMMA_ARABIC LETTER DAL_ARABIC SHADDA_ARABIC INVERTED DAMMA_ARABIC LETTER ALEF", "لدا"],  # transcribed correctly by default
    ["\\b_ARABIC LETTER LAM_ARABIC FATHA_ARABIC LETTER DAL_ARABIC FATHA_ARABIC LETTER ALEF_\\b", "لدى"], 


    ## remove in all other cases: 
    ["ARABIC MADDAH ABOVE", ""],

    ## replace in all other cases with normal alif:
    ## (the overcompensation of defective spellings of alif will be fixed in a next step):
    ["ARABIC LETTER SUPERSCRIPT ALEF", "ا"],
]

# 2. Deal with exceptions: replace specific tokens output by the script
#    with corrected tokens:

post_process_steps = [
    # defective_alifs:
    # NB: in the quran_normalisation_steps, the dagger alif is converted to alif
    # in cases where it is not written in standard Arabic practice.
    # Remove these overcorrections:
    ["لاكن", "لكن"],
    ["اللاه", "الله"], 
    ["إلاه", "إله"], 
    ["هاذا", "هذا"],
    ["هاذه", "هذه"],
    ["هاذان", "هذان"],
    ["هاذين", "هذين"],
    ["هاؤلاء", "هؤلاء"],
    ["هاكذا", "هكذا"],
    ["ذالك", "ذلك"],
    ["أولائك", "أولئك"],
    ["لرحمان", "لرحمن"],

    # sukūn above alif 
    # (NB: there does not seem to be a rule that can be derived from the Uthmani script alone
    # to decide whether the simplified version has waw + alif or only waw for waw + sukūn above alif;
    # in most cases, it does have the alif, so we decided to use that as the standard
    # and fix the exceptions:)
    ["يربوا", "يربو"], 
    ["ترجوا", "ترجو"], 
    ["يرجوا", "يرجو"], 
    ["يمحوا", "يمحو"], 
    ["ناكسوا", "ناكسو"], 
    ["باسطوا", "باسطو"],  
    ["أدعوا", "أدعو"], 
    #["تدعوا", "تدعو"], # problem: in line 5391 the simplified form is without alif, in 2138, 2868, 4579 and 5464 with alif (exact same spelling in original)
    ["ندعوا", "ندعو"], 
    ["يدعوا", "يدعو"], 
    ["كاشفوا", "كاشفو"], 
    [r"\bيعفوا", "يعفو"],  # \b: make sure وليعفوا does not get replaced!
    ["ويعفوا", "ويعفو"], 
    ["لذائقوا", "لذائقو"], 
    ["ملاقوا", "ملاقو"], 
    ["لتاركوا", "لتاركو"], 
    ["مهلكوا", "مهلكو"], 
    ["أشكوا", "أشكو"], 
    ["صالوا", "صالو"], 
    [r"\bتتلوا", "تتلو"], 
    ["تبلوا", "تبلو"],  
    ["سأتلوا", "سأتلو"], 
    ["نتلوا", "نتلو"], 
    ["يتلوا", "يتلو"],  
    ["مرسلوا", "مرسلو"], 
    ["أولوا", "أولو"],   
    
    # examples of cases where the alif is present in the simplified text, 
    # even though it carries the sukūn in the Uthmani text:
    # ["كفرو", "كفروا"], # sukūn above alif but alif stays!
    # ["آمنو", "آمنوا"], # sukūn above alif but alif stays!
    # ["كانو", "كانوا"], # sukūn above alif but alif stays!
    # ["تفسدو", "تفسدوا"], # sukūn above alif but alif stays!
    # ["قالو", "قالوا"], # sukūn above alif but alif stays!
    # ["لقو", "لقوا"], # sukūn above alif but alif stays!
    # ["قامو", "قاموا"], # sukūn + high jeem above alif but alif stays!
    # ["اعبدو", "اعبدوا"], # sukūn above alif but alif stays!
    # ["تجعلو", "تجعلوا"], # sukūn above alif but alif stays!
    # ["فأتو", "فأتوا"], # sukūn above alif but alif stays!
    # ["وادعو", "وادعوا"], # sukūn above alif but alif stays!
    # ["تفعلو", "تفعلوا"], # sukūn above alif but alif stays! (many more examples could be given)

    # Fix missing final alifs:
    ["وباءو", "وباءوا"],
    ["فباءو", "فباءوا"],
    [r"\bوعتو\b", "وعتوا"], 
    ["تبوءو", "تبوءوا"],
    ["فاءو", "فاءوا"],
    [r"جاءو\b", "جاءوا"], 
    [r"\bسعو\b", "سعوا"],     

    # sa'ala
    ["وسألوا", "واسألوا"],   
    ["وسألهم", "واسألهم"], 
    ["فسأل", "فاسأل"], 
    ["وسأل", "واسأل"],

    # sukūn above yā' but yā' stays:
    ["وملإه", "وملئه"],

    # sukūn above waw
    ["سأوريكم", "سأريكم"],

    # final yā' + kasra: ḥayā exception
    ["([تنيأ])"+r"حي(\s|$)", r"\1حيي\2"],  
    [r"\bلمحي\b", "لمحيي"], 

    # vocative yā':
    ["ياقوم", "يا قوم"], 
    ["ياسماء", "يا سماء"],
    ["يبنؤم", "يا ابن أم"], 

    # spaces after an, mā and law:
    [r"\bلوما\b", "لو ما"], 
    [r"\bمالي\b", "ما لي"], 
    [r"\bومالي\b", "وما لي"], 
    [r"\bومامنا\b", "وما منا"], 
    [r"\bمامنا\b", "ما منا"],
    [r"\bوألو\b", "وأن لو"],

    # defectively written, without indication of the alif in Uthmani script:
    ["لتخذت", "لاتخذت"],  
    [r"\bلأيكة", "الأيكة"], 
 
    # final alif maqṣūra
    ["أقصا", "أقصى"],
    [r"ونآ\b", "ونأى"],
    [r"\bطغا\b", "طغى"],
    [r"رآ\b", "رأى"],  # ra'ā
    ["ترائا", "تراءى"], 
    [r"تترا\b", "تترى"], 

    ["المسيطرون", "المصيطرون"], # overriding the normal rule. Not sure why this specific word form is not following the rule?

]


# 3. List of all the (names of) characters that can be removed
# from the Qur'ān text without impact:
quran_noise = [
    "ARABIC SMALL HIGH LIGATURE QAF WITH LAM WITH ALEF MAKSURA",
    "ARABIC SMALL HIGH LIGATURE SAD WITH LAM WITH ALEF MAKSURA",
    "ARABIC SUBSCRIPT ALEF",
    "ARABIC INVERTED DAMMA",
    "ARABIC SMALL HIGH MEEM INITIAL FORM",
    "ARABIC SMALL HIGH JEEM",
    "ARABIC SMALL HIGH THREE DOTS",
    "ARABIC SMALL HIGH UPRIGHT RECTANGULAR ZERO",
    "ARABIC SMALL HIGH DOTLESS HEAD OF KHAH",
    "ARABIC SMALL HIGH MEEM ISOLATED FORM",
    "ARABIC SMALL HIGH MADDA",
    "ARABIC ROUNDED HIGH STOP WITH FILLED CENTRE",
    "ARABIC SMALL LOW MEEM",
    "ARABIC START OF RUB EL HIZB",
    "ARABIC PLACE OF SAJDAH",
    ]
quran_noise = [unicodedata.lookup(c) for c in quran_noise]
quran_noise = "[" + "".join(quran_noise) + "]+"

#################
# MAIN FUNCTION #
#################

def normalise_quran(s, post_process=False, custom_post_process_steps=None):
    """Normalize the "Uthmani" spelling of the Qurʾān to the "imlāʾī" spelling.

    NB: the post-processing step carries out a number of replacements
    that may affect non-Quranic text. 
    Make sure not to use the post-processing step on strings 
    that are not positively identified as Quran text!

    Args:
        s (str): input string
        post_process (bool): if True, the post-processing steps 
            will be carried out.
        custom_post_process_steps (list of tuples): if a list of tuples is provided,
            the first element of each tuple will be replaced with the second
            element. If no list is provided and post_process is True, 
            the default post-processing steps will be carried out
            

    Returns:
        str
    """
    # first, replace combinations of characters:
    for pattern, repl in quran_normalisation_steps:
        s = re.sub(ara.decode_unicode_name(pattern), repl, s)
    
    # then, remove vowels and other "noisy" characters:

    s = re.sub(quran_noise, "", s)
    s = ara.deNoise(s)

    # fix the overcompensation of defective spellings of alif etc.:
    
    if post_process:
        if custom_post_process_steps is None:
            for pattern, repl in post_process_steps:
                s = re.sub(pattern, repl, s)
        elif custom_post_process_steps:
            for pattern, repl in custom_post_process_steps:
                s = re.sub(pattern, repl, s)

    return s


####################
# HELPER FUNCTIONS #
####################

# def decode_unicode_name(s):
#     """Convert unicode names into the characters they refer to.

#     Args:
#         s (str): input string
    
#     Returns:
#         str

#     Examples:
#         >>> decode_unicode_names("ARABIC LETTER ALIF_ARABIC LETTER YEH")
#         اي
#         >>> decode_unicode_names("ARABIC LETTER ALIF_*")
#         ا*
#     """
#     new_s = ""
#     for x in s.split("_"):
#         try:
#             new_s += unicodedata.lookup(x)
#         except:
#             new_s += x
#     return new_s


def deNoise(s):
    s = re.sub(quran_noise, "", s)
    s = ara.deNoise(s)

    return s


def tokenize_both_lines(s_line, u_line):
    """Tokenize a line of simple Quran text and a line of Uthmani Quran text
    in such a way that they have the same number of tokens
    (deal with issues like 'yĀdam' > 'yā Ādam').
    
    Args:
        s_line (str): a line of simple Quran text
        u_line (str): a line of Uthmani Quran text
    
    Returns:
        tuple (tokenized simple line, tokenized Uthmani line)
    """
    # deal with inconsistencies of basmala presence at beginning of sura:
    if re.findall(basmala_regex, u_line) and not re.findall(basmala_regex, s_line):
        s_line = basmala + " " + s_line

    if re.findall(basmala_regex, s_line) and not re.findall(basmala_regex, u_line):
        u_line = basmala2 + " " + u_line
    
    # tokenize both using space as separator:
    u_toks = re.split(" +", u_line.strip())
    s_toks = re.split(" +", s_line.strip())

    # if both have the same number of tokens, we're finished:
    if len(u_toks) == len(s_toks):
        return (s_toks, u_toks)

    # if both have a different number of tokens, we need to use a different approach:
    
    # use stable letters that are not affected by simplification as anchors:
    stable_letters = "بتثجحخدذرزسشصضطظعغفقكلمنهوي"
    

    # create a list of all tokens in the uthmani string,
    # leaving out all unstable letters:
    u_toks_base = [[c for c in tok if c in stable_letters] for tok in u_toks]

    # move through the simple string and the stable letters of the uthmani tokens
    # and check for each character if it belongs to the current Uthmani token;
    # if we reach a space, check if it appears in the middle of an Uthmani token or at the end

    s_toks = []  # will contain the tokens of the simple string
    s_tok = ""   # contains the current token in the simple string
    s_i = 0     # current character index in the s_line string
    u_i = 0     # current token index in the u_toks_base list
    u_c_i = 0   # current character index in the current u_tok
    
    
    while True:
        # load the current token character in the uthmani token list:
        # (and return the tokenized strings if we reached the end of the uthmani token list)
        u_tok = u_toks_base[u_i]  # current token in the uthmani line
        try:
            uc = u_tok[u_c_i]     # current character inside the u_tok
        except: # end of token reached; consume next token:
            u_i += 1
            try:
                u_tok = u_toks_base[u_i]
                u_c_i = 0
                uc = u_tok[u_c_i]
            except: # end of line reached: we're done with this line
                s_tok += s_line[s_i:].strip()
                s_toks.append(s_tok)
                print(s_toks)
                print(u_toks)
                if len(u_toks) != len(s_toks):
                    print ("DIFFERENT LENGTH:", len(u_toks), len(s_toks))
                return (s_toks, u_toks)
        
        # check if the currenct Uthmani character is the last character of the current token:
        # (we'll use this to check what to do with spaces in the simple string)
        #uc_is_last_u_tok_char = (u_c_i == len(u_tok)-1)  # True or False

        # load the current character in the simple string:
        sc = s_line[s_i]

        # check if we reached the end of a token in the simple string
        # (that is, a space when the current uthmani character is the last character of a token):
        #if uc_is_last_u_tok_char and sc == " ":
        if u_c_i == 0 and sc == " ":
            # add the current simple token to the list and initialize a new token:
            s_toks.append(s_tok)
            s_tok = ""
            # move to the next token in the uthmani token list:
            # NB: not necessary here, is already done in the try/except section above
            #u_i += 1  
            #u_c_i = 0
        # if not, compare the current simple character to the current Uthmani character:
        elif sc == uc:
            # add the character to the current simple token:
            s_tok += sc
            # move to the next character in the the Uthmani token:
            u_c_i += 1
        # in all other cases, add the current simple character it to the current simple token:
        else:
            if sc == uc:
                # add the character to the current simple token:
                s_tok += sc
                # move to the next character in the the Uthmani token:
                u_c_i += 1
            if sc not in stable_letters:
                # add the character to the current simple token 
                # but do not move to the next character in the Uthmani token:
                s_tok += sc
            else:
                print("UNCEXPECTED STABLE CHARACTER IN SIMPLE STRING:")
                print(sc, unicodedata.name(sc))
                print(uc, unicodedata.name(uc))
                print(u_toks)
                print(s_toks, s_tok)
                for c in u_toks[u_i]:
                    print(c, unicodedata.name(c))
                print("----")

                # replace special letters:
                print("Replacing special character (combinations) and retrying...")
                for k,v in special_letters:
                    u_line = re.sub(k, v, u_line)
                return tokenize_both_lines(s_line, u_line)
        
        # go to the next iteration to consume the next simple string character
        s_i += 1



def tokenize_both_texts(simple, uthmani):
    """Tokenize both texts in a way that they both have the same number of tokens 
    and each token in one text corresponds to the token in the other
    (deal with issues like 'yĀdam' > 'yā Ādam')
    """
    # split the sura and aya numbers off:
    simple = [s.split("|")[-1] for s in simple]
    print(simple[0])
    print(uthmani[0])


    s_tok_lines = []
    u_tok_lines = []
    
    for i in range(len(uthmani)):
        s_line = simple[i]
        u_line = uthmani[i]
        print(i, s_line)
        s_toks, u_toks = tokenize_both_lines(s_line, u_line)
        s_tok_lines.append(s_toks)
        u_tok_lines.append(u_toks)

    return s_tok_lines, u_tok_lines


def compare_tokens(s_toks, u_toks):
    """Compare each token in the simplified and Uthmani Quran text.
    
    If the normalised version of the Uthmani Quran text differs 
    from the simplified Quran text, show both original versions
    and the normalised one.
    """
    for i in range(len(u_toks)):
        s = s_toks[i]
        u = u_toks[i]
        norm_u = normalise_quran(u)
        if deNoise(s) != norm_u:
            print(s_toks)
            print(u_toks)
            print(s)
            print(u)
            print(norm_u)
            for c in norm_u:
                print(c, unicodedata.name(c))
            print("----")
            for c in u:
                print(c, unicodedata.name(c))
            
            input()



def inspect_character_contexts(d, s_toks, u_toks, n_samples=5, include_naive=False):
    """Show contexts in the Qur'ān for one or more characters
    
    Args:
        d (dict): dictionary of empty dictionaries. 
            The keys of the main dictionary are unicode character names;
            the keys of the nested dictionaries will be sequences of character names,
            values are examples of these sequences from the Qur'an
        s_toks (list): each element is a list of tokens from a line in the simplified Quran
        u_toks (list): each element is a list of tokens from a line in the Uthmani Quran
        n_samples (int): number of samples for each context to be added to the dictionary
        include_naive (bool): if True, a naively simplified version of the token will be included
    """
    
    for i in range(len(s_toks)):
        # go through both versions of the text line by line:
        s_line = s_toks[i]
        u_line  = u_toks[i]

        # go through each token of the line in the uthmani version
        for j, u_tok in enumerate(u_line):
            # for each character we're interested in, check whether it is present in the token:
            for char_name in d:
                # generate the character from its name and assign it to a variable
                char = unicodedata.lookup(char_name)
                
                if char in u_tok :
                    # find the corresponding token in the simplified version of the Qur'an:
                    s_tok = s_line[j]

                    # create a key consisting of the names of the characters around the character of interest:
                    key = "_".join([unicodedata.name(c) for c in re.findall(".{,1}"+char+".{,1}", u_tok)[0]])
                    
                    # initialize a new entry (a list of samples) for this key if it does not yet exist:
                    if key not in d[char_name]:
                        d[char_name][key] = [0] # the first element in the list is a counter: it will store the number of tokens that contain this context
                    
                    # increment the counter:
                    d[char_name][key][0] += 1
                    
                    # if the desired number of samples for this context has not been reached yet:
                    # add the sample to the list:
                    if len(d[char_name][key]) < n_samples: 
                        # emphasize the location of the character of interest by surrounding it with kashīdas:
                        emph_u_tok = re.sub("("+char+")", r"ــ\1ــ", u_tok)
                        if include_naive:
                            naively_simplified = re.sub(special_chars, "", u_tok)
                            # add the tokens from both text versions to the list of samples:
                            d[char_name][key].append([emph_u_tok, s_tok, naively_simplified])
                        else:
                            d[char_name][key].append([emph_u_tok, s_tok])

    return d


##################################################################################




# list of special letters to be (temporarily) replaced during the tokenization process:

special_letters = [
    ["ARABIC SMALL HIGH YEH_ARABIC LETTER NOON", "ARABIC LETTER YEH_ARABIC LETTER NOON"],
    ["ARABIC SMALL HIGH YEH_ARABIC LETTER MEEM", "ARABIC LETTER YEH_ARABIC LETTER MEEM"],
    ["ARABIC SMALL HIGH YEH", ""],
    ["ARABIC LETTER YEH_ARABIC KASRA_ARABIC SMALL YEH", "ARABIC LETTER YEH_ARABIC LETTER YEH"],
    ["ARABIC SMALL YEH", ""],
    ["ARABIC LETTER WAW_ARABIC LETTER SUPERSCRIPT ALEF", "ARABIC LETTER ALEF"],
    ["ARABIC SMALL HIGH LIGATURE QAF WITH LAM WITH ALEF MAKSURA", ""],
    ["ARABIC SMALL WAW_ARABIC MADDAH ABOVE_ARABIC LETTER ALEF", "ARABIC LETTER WAW_ARABIC LETTER ALEF"],
    ["ARABIC LETTER WAW_ARABIC DAMMA_ARABIC SMALL WAW", "ARABIC LETTER WAW_ARABIC DAMMA_ARABIC LETTER WAW"],
    ["ARABIC LETTER ALEF WASLA_ARABIC LETTER LAM_ARABIC SHADDA_ARABIC FATHA_ARABIC LETTER YEH", "ARABIC LETTER ALEF WASLA_ARABIC LETTER LAM_ARABIC LETTER LAM_ARABIC LETTER YEH"],  # as in ٱلَّيۡلِ > الليل (but notice that al-laḏī should be kept in the Qur'ān's defective writing!)
    ["ARABIC LETTER ALEF WASLA_ARABIC LETTER LAM_ARABIC SHADDA_ARABIC FATHA_ARABIC LETTER SUPERSCRIPT ALEF", "ARABIC LETTER ALEF WASLA_ARABIC LETTER LAM_ARABIC LETTER LAM_ARABIC LETTER ALEF"],  # as in ٱلَّٰتِيٓ > اللاتي
    ["ARABIC LETTER YEH_ARABIC HAMZA BELOW", "ARABIC LETTER YEH WITH HAMZA ABOVE"],
    ["ARABIC LETTER ALEF WITH HAMZA ABOVE_ARABIC FATHA_ARABIC LETTER LAM_ARABIC SHADDA_ARABIC FATHA_ARABIC LETTER WAW", "ARABIC LETTER ALEF WITH HAMZA ABOVE_ARABIC FATHA_ARABIC LETTER NOON_SPACE_ARABIC LETTER LAM_ARABIC LETTER WAW"],  # wa-al-law > wa-an-law

]



special_letters = [[ara.decode_unicode_name(k), ara.decode_unicode_name(v)] for k,v in special_letters]
special_letters_regex = "[" + "".join([tup[0] for tup in special_letters]) + "]"



# since the simple Quran text does not always have a basmalla at the start of a sura
# in the same way as the Uthmani version has it, a basmala will be inserted
# whenever one version has it and another hasn't in the tokenization process
# (to balance the number of tokens per line)
basmala = "بسم الله الرحمن الرحيم"
basmala2 = "بِسۡمِ ٱللَّهِ ٱلرَّحۡمَٰنِ ٱلرَّحِيمِ"
basmala_regex = "\W*".join(basmala) + " *|" + "\W*".join(basmala2)
#print(basmala_regex)




##############################################################################################


if __name__ == "__main__":
    #####################
    # LOADING THE TEXTS #
    #####################

    # load the simplified Quran transcription from the tanzil file:
    simple_fp = r"C:\Users\peter\Downloads\quran-simple-clean.txt"
    #simple_fp = r"C:\Users\peter\Downloads\quran-simple.txt"

    with open(simple_fp, mode="r", encoding="utf-8") as file:
        simple = file.read().splitlines()
        

    # # load the uthmani transcription from the tanzil file:
    # # NB: this file is corrupt on the tanzil website!
    # uthmani_fp = r"C:\Users\peter\Downloads\quran-uthmani.txt"
    # with open(uthmani_fp, mode="r", encoding="utf-8") as file:
    #     uthmani = file.read().replace("ـ", "")  # remove tatweel
    #     uthmani = uthmani.splitlines()

    # load the uthmani transcription from the GitHub json file: 
    # https://github.com/risan/quran-json/blob/main/dist/quran.json
    uthmani_fp = r"C:\Users\peter\Downloads\quran.json"
    with open(uthmani_fp, mode="r", encoding="utf-8") as file:
        data = json.load(file)
        uthmani = []
        for sura in data:
            for verse in sura["verses"]:
                uthmani.append(verse["text"].replace("ـ", ""))  # remove the kashida/tatweel character

    # check if both texts have the same number of lines:
    print(len(simple), len(uthmani)) # both 6266
    #print(simple[0])
    #print(uthmani[0])

    #################################################
    # FIND CHARACTERS UNIQUE TO THE UTHMANI VERSION #
    #################################################

    # for each version, create a set containing all unique characters
    simple_chars = set("".join(simple))
    uthmani_chars = set("".join(uthmani))

    # create a set of characters unique to the Uthmani version:
    only_in_uthmani = uthmani_chars - simple_chars

    # create a regular expression that matches any of these characters:
    special_chars = "|".join(only_in_uthmani)


    """
    # print the set of all characters in the Uthmani version, with their names:
    for i, c in enumerate(sorted(uthmani_chars)):
        print(i, c, unicodedata.name(c))

    0   SPACE
    1 ء ARABIC LETTER HAMZA
    2 أ ARABIC LETTER ALEF WITH HAMZA ABOVE
    3 ؤ ARABIC LETTER WAW WITH HAMZA ABOVE
    4 إ ARABIC LETTER ALEF WITH HAMZA BELOW
    5 ئ ARABIC LETTER YEH WITH HAMZA ABOVE
    6 ا ARABIC LETTER ALEF
    7 ب ARABIC LETTER BEH
    8 ة ARABIC LETTER TEH MARBUTA
    9 ت ARABIC LETTER TEH
    10 ث ARABIC LETTER THEH
    11 ج ARABIC LETTER JEEM
    12 ح ARABIC LETTER HAH
    13 خ ARABIC LETTER KHAH
    14 د ARABIC LETTER DAL
    15 ذ ARABIC LETTER THAL
    16 ر ARABIC LETTER REH
    17 ز ARABIC LETTER ZAIN
    18 س ARABIC LETTER SEEN
    19 ش ARABIC LETTER SHEEN
    20 ص ARABIC LETTER SAD
    21 ض ARABIC LETTER DAD
    22 ط ARABIC LETTER TAH
    23 ظ ARABIC LETTER ZAH
    24 ع ARABIC LETTER AIN
    25 غ ARABIC LETTER GHAIN
    26 ف ARABIC LETTER FEH
    27 ق ARABIC LETTER QAF
    28 ك ARABIC LETTER KAF
    29 ل ARABIC LETTER LAM
    30 م ARABIC LETTER MEEM
    31 ن ARABIC LETTER NOON
    32 ه ARABIC LETTER HEH
    33 و ARABIC LETTER WAW
    34 ى ARABIC LETTER ALEF MAKSURA
    35 ي ARABIC LETTER YEH
    36 ً ARABIC FATHATAN
    37 ٌ ARABIC DAMMATAN
    38 ٍ ARABIC KASRATAN
    39 َ ARABIC FATHA
    40 ُ ARABIC DAMMA
    41 ِ ARABIC KASRA
    42 ّ ARABIC SHADDA
    43 ْ ARABIC SUKUN
    44 ٓ ARABIC MADDAH ABOVE
    45 ٔ ARABIC HAMZA ABOVE
    46 ٕ ARABIC HAMZA BELOW
    47 ٖ ARABIC SUBSCRIPT ALEF
    48 ٗ ARABIC INVERTED DAMMA
    49 ٜ ARABIC VOWEL SIGN DOT BELOW
    50 ٞ ARABIC FATHA WITH TWO DOTS
    51 ٰ ARABIC LETTER SUPERSCRIPT ALEF
    52 ٱ ARABIC LETTER ALEF WASLA
    53 ۖ ARABIC SMALL HIGH LIGATURE SAD WITH LAM WITH ALEF MAKSURA
    54 ۗ ARABIC SMALL HIGH LIGATURE QAF WITH LAM WITH ALEF MAKSURA
    55 ۘ ARABIC SMALL HIGH MEEM INITIAL FORM
    56 ۚ ARABIC SMALL HIGH JEEM
    57 ۛ ARABIC SMALL HIGH THREE DOTS
    58 ۜ ARABIC SMALL HIGH SEEN
    59 ۞ ARABIC START OF RUB EL HIZB
    60 ۠ ARABIC SMALL HIGH UPRIGHT RECTANGULAR ZERO
    61 ۡ ARABIC SMALL HIGH DOTLESS HEAD OF KHAH
    62 ۢ ARABIC SMALL HIGH MEEM ISOLATED FORM
    63 ۤ ARABIC SMALL HIGH MADDA
    64 ۥ ARABIC SMALL WAW
    65 ۦ ARABIC SMALL YEH
    66 ۧ ARABIC SMALL HIGH YEH
    67 ۨ ARABIC SMALL HIGH NOON
    68 ۩ ARABIC PLACE OF SAJDAH
    69 ۬ ARABIC ROUNDED HIGH STOP WITH FILLED CENTRE
    70 ۭ ARABIC SMALL LOW MEEM
    71   THIN SPACE
    """

    """
    # print the set of only those characters in the Uthmani version that are not in the simple version:

    for i, c in enumerate(sorted(only_in_uthmani)):
        print(i, c, unicodedata.name(c))

    0 ً ARABIC FATHATAN
    1 ٌ ARABIC DAMMATAN
    2 ٍ ARABIC KASRATAN
    3 َ ARABIC FATHA
    4 ُ ARABIC DAMMA
    5 ِ ARABIC KASRA
    6 ّ ARABIC SHADDA
    7 ْ ARABIC SUKUN
    8 ٓ ARABIC MADDAH ABOVE
    9 ٔ ARABIC HAMZA ABOVE
    10 ٕ ARABIC HAMZA BELOW
    11 ٖ ARABIC SUBSCRIPT ALEF
    12 ٗ ARABIC INVERTED DAMMA
    13 ٜ ARABIC VOWEL SIGN DOT BELOW
    14 ٞ ARABIC FATHA WITH TWO DOTS
    15 ٰ ARABIC LETTER SUPERSCRIPT ALEF
    16 ٱ ARABIC LETTER ALEF WASLA
    17 ۖ ARABIC SMALL HIGH LIGATURE SAD WITH LAM WITH ALEF MAKSURA
    18 ۗ ARABIC SMALL HIGH LIGATURE QAF WITH LAM WITH ALEF MAKSURA
    19 ۘ ARABIC SMALL HIGH MEEM INITIAL FORM
    20 ۚ ARABIC SMALL HIGH JEEM
    21 ۛ ARABIC SMALL HIGH THREE DOTS
    22 ۜ ARABIC SMALL HIGH SEEN
    23 ۞ ARABIC START OF RUB EL HIZB
    24 ۠ ARABIC SMALL HIGH UPRIGHT RECTANGULAR ZERO
    25 ۡ ARABIC SMALL HIGH DOTLESS HEAD OF KHAH
    26 ۢ ARABIC SMALL HIGH MEEM ISOLATED FORM
    27 ۤ ARABIC SMALL HIGH MADDA
    28 ۥ ARABIC SMALL WAW
    29 ۦ ARABIC SMALL YEH
    30 ۧ ARABIC SMALL HIGH YEH
    31 ۨ ARABIC SMALL HIGH NOON
    32 ۩ ARABIC PLACE OF SAJDAH
    33 ۬ ARABIC ROUNDED HIGH STOP WITH FILLED CENTRE
    34 ۭ ARABIC SMALL LOW MEEM
    35   THIN SPACE
    """

    """
    # print the set of all characters in the simple version, with their names:

    for i, c in enumerate(sorted(simple_chars)):
        print(i, c, unicodedata.name(c))

    0   SPACE
    1 0 DIGIT ZERO
    2 1 DIGIT ONE
    3 2 DIGIT TWO
    4 3 DIGIT THREE
    5 4 DIGIT FOUR
    6 5 DIGIT FIVE
    7 6 DIGIT SIX
    8 7 DIGIT SEVEN
    9 8 DIGIT EIGHT
    10 9 DIGIT NINE
    11 | VERTICAL LINE
    12 ء ARABIC LETTER HAMZA
    13 آ ARABIC LETTER ALEF WITH MADDA ABOVE
    14 أ ARABIC LETTER ALEF WITH HAMZA ABOVE
    15 ؤ ARABIC LETTER WAW WITH HAMZA ABOVE
    16 إ ARABIC LETTER ALEF WITH HAMZA BELOW
    17 ئ ARABIC LETTER YEH WITH HAMZA ABOVE
    18 ا ARABIC LETTER ALEF
    19 ب ARABIC LETTER BEH
    20 ة ARABIC LETTER TEH MARBUTA
    21 ت ARABIC LETTER TEH
    22 ث ARABIC LETTER THEH
    23 ج ARABIC LETTER JEEM
    24 ح ARABIC LETTER HAH
    25 خ ARABIC LETTER KHAH
    26 د ARABIC LETTER DAL
    27 ذ ARABIC LETTER THAL
    28 ر ARABIC LETTER REH
    29 ز ARABIC LETTER ZAIN
    30 س ARABIC LETTER SEEN
    31 ش ARABIC LETTER SHEEN
    32 ص ARABIC LETTER SAD
    33 ض ARABIC LETTER DAD
    34 ط ARABIC LETTER TAH
    35 ظ ARABIC LETTER ZAH
    36 ع ARABIC LETTER AIN
    37 غ ARABIC LETTER GHAIN
    38 ف ARABIC LETTER FEH
    39 ق ARABIC LETTER QAF
    40 ك ARABIC LETTER KAF
    41 ل ARABIC LETTER LAM
    42 م ARABIC LETTER MEEM
    43 ن ARABIC LETTER NOON
    44 ه ARABIC LETTER HEH
    45 و ARABIC LETTER WAW
    46 ى ARABIC LETTER ALEF MAKSURA
    47 ي ARABIC LETTER YEH
    """









    ###############################################################################


    
    ############
    # TOKENIZE #
    ############

    # tokenize both texts in such a way that 
    # each token from the simple text corresponds to a token from the Uthmani text
    # and vice versa:

    s_toks, u_toks = tokenize_both_texts(simple, uthmani)


    ##########################################
    # INSPECT CONTEXTS OF SPECIAL CHARACTERS #
    ##########################################


    # Create a dictionary of all the characters that are only in the Uthmani text:
    # (it is used to collect examples of sequences in which each of these characters
    # are present; only the features not commented out)
    d = {
        # "ARABIC MADDAH ABOVE": dict(), 
        # "ARABIC SMALL HIGH MADDA": dict(),
        "ARABIC HAMZA ABOVE": dict(),
        # "ARABIC HAMZA BELOW": dict(),
        # "ARABIC LETTER SUPERSCRIPT ALEF": dict(),
        # "ARABIC MADDAH ABOVE": dict(),
        # "ARABIC HAMZA ABOVE": dict(),
        # "ARABIC SUBSCRIPT ALEF": dict(),
        # "ARABIC INVERTED DAMMA": dict(),
        # "ARABIC VOWEL SIGN DOT BELOW": dict(),
        # "ARABIC FATHA WITH TWO DOTS": dict(),
        # "ARABIC LETTER SUPERSCRIPT ALEF": dict(),
        # "ARABIC LETTER ALEF WASLA": dict(),
        # "ARABIC SMALL HIGH LIGATURE SAD WITH LAM WITH ALEF MAKSURA": dict(),
        # "ARABIC SMALL HIGH LIGATURE QAF WITH LAM WITH ALEF MAKSURA": dict(),
        # "ARABIC SMALL HIGH MEEM INITIAL FORM": dict(),
        # "ARABIC SMALL HIGH JEEM": dict(),
        # "ARABIC SMALL HIGH THREE DOTS": dict(),
        # "ARABIC SMALL HIGH SEEN": dict(),
        # "ARABIC START OF RUB EL HIZB": dict(),
        # "ARABIC SMALL HIGH UPRIGHT RECTANGULAR ZERO": dict(),
        # "ARABIC SMALL HIGH DOTLESS HEAD OF KHAH": dict(),
        # "ARABIC SMALL HIGH MEEM ISOLATED FORM": dict(),
        # "ARABIC SMALL WAW": dict(),
        # "ARABIC SMALL YEH": dict(),
        # "ARABIC SMALL HIGH YEH": dict(),
        # "ARABIC SMALL HIGH NOON": dict(),
        # "ARABIC PLACE OF SAJDAH": dict(),
        # "ARABIC ROUNDED HIGH STOP WITH FILLED CENTRE": dict(),
        # "ARABIC SMALL LOW MEEM": dict(),
        # "THIN SPACE": dict(), 
    }

    # inspect the characters' contexts and collect samples:
    d = inspect_character_contexts(d, s_toks, u_toks, n_samples=5, include_naive=False)

    print("------------------")
    print("Samples of contexts for the selected special characters:")
    print(json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True))

    ##########################################
    # CHECK THE NORMALIZATION TOKEN BY TOKEN #
    ##########################################

    # for i, (s_line, u_line) in enumerate(zip(s_toks, u_toks)):
    #     print(i)
    #     compare_tokens(s_line, u_line)

    ###########################################################
    # CHECK NORMALIZATION LINE BY LINE (WITHOUT TOKENIZATION) #
    ###########################################################

    def compare_lines(uthmani, simple, additional_changes=[]):
        """Compare the normalised Uthmani spelling with the simplified text for each line (without tokenization)
        
        Args:
            uthmani (list): a list of lines of the Qur'an text, in Uthmani spelling
            simple (list): a list of lines of the Qur'an text, in imlai spelling
            additional_changes (list): optional post-processing replacements,
            in addition to the replacements already part of the normalise_quran function
            """
        for i, u_line in enumerate(uthmani):
            s_line = re.split("[|()]", simple[i])[-1].strip()

            if re.findall(basmala_regex, s_line) and not re.findall(basmala_regex, u_line):
                u_line = basmala2 + " " + u_line
            simplified = normalise_quran(u_line)
            if s_line != simplified:
                if additional_changes:
                    for pattern, repl in additional_changes:
                        simplified = re.sub(pattern, repl, simplified)
                if s_line != simplified:
                    print(i)
                    print(u_line)
                    print(s_line)
                    print(simplified)
                    input()
        print("done!")

    print("---------------")
    print("Check if after normalisation, the Uthmani text agrees with the Tanzil simple clean:")
    additional_changes = [["تدعوا من أدبر", "تدعو من أدبر"]]
    #compare_lines(uthmani, simple, additional_changes)

    print("---------------")
    print("Check if after normalisation, the Uthmani text agrees with QuranAnalysis001:")
    fp = r"D:\AKU\OpenITI\25Y_repos\0025AH\data\0001Quran\0001Quran.Mushaf\0001Quran.Mushaf.QuranAnalysis001-ara1.mARkdown"
    with open(fp, mode="r", encoding="utf-8") as file:
        text = file.read()
        text = re.split("#META#Header#End#", text, maxsplit=1)[-1].strip()
        text = re.sub("[\r\n]*###.+", "", text)
        text = re.sub(" *ms\d+ *| *PageV[^P]+P\d+ *|[\r\n]+~~", " ", text)
        text = re.sub(" +", " ", text)

    quran_analysis_differences = [
        # [simplified, quran_analysis]
        ["بعد ما", "بعدما"], # 187, 1165, 1743
        ["ويلتى", "ويلتا"],  # 699
        ["الزنى", "الزنا"],  # 2060
        ["حسرتى", "حسرتا"],  # 4113
        ["تدعوا من أدبر", "تدعو من أدبر"] # 5391
    ]
    simple = re.split("[\r\n]*# ", text.strip())[1:]
    #compare_lines(uthmani, simple, quran_analysis_differences)

    print("---------------")
    print("Check if after normalisation, the Uthmani text agrees with Shia000001:")
    fp = r"D:\AKU\OpenITI\25Y_repos\0025AH\data\0001Quran\0001Quran.Mushaf\0001Quran.Mushaf.Shia000001-ara1.mARkdown"

    with open(fp, mode="r", encoding="utf-8") as file:
        text = file.read()
        text = re.split("#META#Header#End#", text, maxsplit=1)[-1].strip()
        text = re.sub("[\r\n]*###.+", "", text)
        text = re.sub(" *ms\d+ *| *PageV[^P]+P\d+ *|[\r\n]+~~", " ", text)
        text = re.sub(" *\(\d+\) *", " ", text)
        text = re.sub(" +", " ", text)
        

    shia_differences = [
        # [simplified, shia]
        ["بعد ما", "بعدما"], # 187, 1165, 1743
        ["ويلتى", "ويلتا"],  # 699
        ["الزنى", "الزنا"],  # 2060
        ["حسرتى", "حسرتا"],  # 4113
        ["تدعوا من أدبر", "تدعو من أدبر"], # 5391
        #["", "\?"],  # 1159, 1721, 1950, 2137, 2307, 2612, 2671, 2914, 3184, 3517, 3993, 4225, 4845, 5904, 6124, (for sajda mark!)
        ]
    simple = re.split("[\r\n]*# ", text.strip())[1:]
    #compare_lines(uthmani, simple, shia_differences)


