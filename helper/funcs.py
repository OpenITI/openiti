import helper.ara as ara
import re
import math
import random
import urllib.request as url
import os

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


# Count the length of a text in Arabic characters
def ar_ch_len(file):
    print(file)

    with url.urlopen(file) as f1:
        book = f1.read().decode('utf-8')

        # splitter/header test
        if splitter in book:
            # split the header and body of the text.
            text = book.split(splitter)[1]

            # count the number of Arabic letters or numbers
            toks = re.findall(ar_ch, text)
            ar_ch_cnt = len([c for c in toks if c in ar_ch])
            print(ar_ch_cnt)
            return ar_ch_cnt
        else:
            print("The file is missing the splitter!")
            print(file)
            return 0


def absolute_path(path):
    return os.path.abspath(path)
