import re
import math
import random
import urllib.request as url
import os


if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
    sys.path.append(root_folder)
from openiti.helper import ara

splitter = "#META#Header#End#"
ar_ch = "[ذ١٢٣٤٥٦٧٨٩٠ّـضصثقفغعهخحجدًٌَُلإإشسيبلاتنمكطٍِلأأـئءؤرلاىةوزظْلآآ]"
milestone = "Milestone300"
thresh = 1000


def text_cleaner(text):
    text = ara.normalize_ara_extra_light(text)
    text = re.sub("\W|\d|[A-z]", " ", text)
    text = re.sub(" +", " ", text)
    return text


def roundup(x, par):
    new_x = int(math.ceil(int(x) / float(par)) * par)
    return new_x


def generate_ids_through_permutations(char_string_for_ids, id_len_char, limit):
    list_char = list(char_string_for_ids) * id_len_char

    dic = {}
    iterations = 0

    while len(dic) < limit:
        new = "".join(random.sample(list_char, id_len_char))
        dic[new] = 0

        iterations += 1
        if iterations % 100000 == 0:
            print("\tITERATIONS: %d; DICTIONARY: %d" % (iterations, len(dic)))

    ids = "\n".join(list(dic.keys()))

    # where `L` is the length of IDs, `T` is the total number of unique IDs.
    file_name = "IDs_ASCII_L%d_T%d.txt" % (id_len_char, len(dic))
    with open(file_name, 'w', encoding='utf8') as outfile:
        outfile.write(ids)

    print("=" * 80)
    print("Generating TXT file with unique IDs, based on:")
    print("\tPermuations (L=%d) of: %s" % (id_len_char, char_string_for_ids))
    print("\tTotal number of IDs: %s" % '{:,}'.format(len(dic)))
    print("=" * 80)


def ar_ch_len(fp):
    """Count the length of a text in Arabic characters, given its URL"""

    try:
        with url.urlopen(fp) as f:
            book = f.read().decode('utf-8')
    except:
        with open(fp, mode="r", encoding="utf-8") as f:
            book = f.read()

        # splitter/header test
        if splitter in book:
            # split the header and body of the text:
            text = book.split(splitter)[1]

            # remove Editorial sections:
            text = re.sub("### \|EDITOR.+?### ", "### ", text,
                          flags = re.DOTALL)

            # count the number of Arabic letters or numbers:
            toks = re.findall(ar_ch, text)
            ar_ch_cnt = len([c for c in toks if c in ar_ch])
            print("{} Arabic character count: {}".format(fp, ar_ch_cnt))
            return ar_ch_cnt
        else:
            print("{} is missing the splitter!".format(fp))
            return 0


def ar_ch_cnt(text):
    """
    Count the length of a text in Arabic characters

    :param text: text
    :return: number of the Arabic characters in the text
    """

    ar_chars = re.compile("[ذ١٢٣٤٥٦٧٨٩٠ّـضصثقفغعهخحجدًٌَُلإإشسيبلاتنمكطٍِلأأـئءؤرلاىةوزظْلآآ]+")

    toks = re.findall(ar_chars, text)
    return len(''.join(toks))


def ar_toks_cnt(text):
    """
    Count the length of a text in Arabic tokens

    :param text: text
    :return: number of Arabic tokens in the text
    """

    ar_chars = re.compile("[ذ١٢٣٤٥٦٧٨٩٠ّـضصثقفغعهخحجدًٌَُلإإشسيبلاتنمكطٍِلأأـئءؤرلاىةوزظْلآآ]+")
    toks = re.findall(ar_chars, text)

    return len(toks)


def read_header(fp):
    """Read only the OpenITI header of a file without opening the entire file.

    Args:
        fp (str): path to the text file

    Returns:
        header (list): A list of all metadata lines in the header
    """
    with open(fp, mode="r", encoding="utf-8") as file:
        header = []
        line = file.readline()
        i=0
        while i < 100:
        #while "#META#Header#End" not in line and i < 100:
            #if "#META#" in line or "#NewRec#" in line:
            header.append(line)
            if "#META#Header#End" in line:
                return header
            line = file.readline() # move to next line
            i += 1
    return header


def absolute_path(path):
    return os.path.abspath(path)
