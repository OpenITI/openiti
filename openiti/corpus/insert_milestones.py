# inserting milestones of a fixed len () into the texts
import re
import os
import math
import sys
from itertools import groupby
import openiti.helper.ara as ara


def milestones(file, length, last_ms_cnt):
    # ara_regex = re.compile("^[ذ١٢٣٤٥٦٧٨٩٠ّـضصثقفغعهخحجدًٌَُلإإشسيبلاتنمكطٍِلأأـئءؤرلاىةوزظْلآآ]+$")
    # new char list without ZERO WIDTH NON-JOINER and ZERO WIDTH JOINER
    # ara_regex = re.compile("[ءآأؤإئابةتثجحخدذرزسشصضطظعغـفقكلمنهوىيًٌٍَُِّْ٠١٢٣٤٥٦٧٨٩ٮٰٹپچژکگیے۱۲۳۴۵]+")
    splitter = "#META#Header#End#"
    file_name = re.split("-[a-z]{3}\d{1}(\.(mARkdown|inProgress|completed))?$", file.split("/")[-1])[0]
    print(file_name)
    if re.search("[A-Z]{1}$", file_name):
        continuous = True
    else:
        continuous = False

    with open(file, "r", encoding="utf8") as f:
        data = f.read()

        # splitter test
        if splitter in data:
            data_parts = re.split("\n*#META#Header#End#\n*", data)
            head = data_parts[0]
            # remove the final new line and spaces to avoid having the milestone tag in a new empty line
            text = data_parts[1].rstrip()
            # remove old milestone ids. Fixed strings, until we make them as user input, if required!
            text = re.sub(" Milestone300", "", text)
            text = re.sub(" ms[A-Z]?\d+", "", text)

            # insert Milestones
            ara_toks_count = ara.ar_tok_cnt(text)
            # ara_toks_count = len(ara_regex.findall(text))

            ms_tag_str_len = len(str(math.floor(ara_toks_count / length)))
            # find all tokens to check the Arabic tokens in their positions
            all_toks = re.findall(r"\w+|\W+", text)

            token_count = 0
            ms_count = last_ms_cnt

            new_data = []
            for i in range(0, len(all_toks)):
                # check each token at its position
                # if ara.ar_tok.search(all_toks[i]):
                # if ara_regex.search(all_toks[i]):
                if re.search(ara.ar_tok, all_toks[i]):
                    token_count += 1
                    new_data.append(all_toks[i])
                else:
                    new_data.append(all_toks[i])

                if token_count == length or i == len(all_toks) - 1:
                    ms_count += 1
                    if continuous:
                        milestone = " ms" + file_name[-1] + str(ms_count).zfill(ms_tag_str_len)
                    else:
                        milestone = " ms" + str(ms_count).zfill(ms_tag_str_len)
                    new_data.append(milestone)
                    token_count = 0

            ms_text = "".join(new_data)

            test = re.sub(" ms[A-Z]?\d+", "", ms_text)
            if test == text:
                # print("\t\tThe file has not been damaged!")
                # Milestones TEST
                ms = re.findall("ms[A-Z]?\d+", ms_text)
                print("\t\t%d milestones (%d words)" % (len(ms), length))
                ms_text = head.rstrip() + "\n\n" + splitter + "\n\n" + ms_text
                with open(file, "w", encoding="utf8") as f9:
                    f9.write(ms_text)
                return ms_count
            else:
                print("\t\tSomething got messed up...")
                return -1

        else:
            print("The file is missing the splitter!")
            print(file)
            return -1


def groupby_books(name):
    b_id = re.split("-[a-z]{3}\d{1}", name)[0]
    if re.search("[A-Z]{1}$", b_id):
        return b_id[:-1]
    else:
        return b_id


def process_files(main_folder, ms_len):
# main_folder = sys.argv[1]
#     ms_len = 300

    # The pattern is to remove the old ms ids. For now, we have it fixed, so no need to pass it as an argument to
    # milestone func. For any changes in the future, this can be a user input to decide what to remove from and
    # insert into
    # the text.
    # ms_pattern = " ms[A-Z]?\d+"

    if not os.path.exists(main_folder):
            print("invalid path: ", main_folder)
            sys.exit(1)
    else:
        # process all texts in OpenITI
        for root, dirs, files in os.walk(main_folder):
            book_files = [f for f in files if
                          re.search("^\d{4}\w+\.\w+\.\w+-[a-z]{3}\d{1}(\.(mARkdown|inProgress|completed))?$", f)]
            # books = map(lambda x: re.split("-[a-z]{3}\d{1}", x)[0], book_files)
            grouped_books = [list(items) for gr, items in groupby(sorted(book_files), key=lambda name: groupby_books(name))]

            for group in grouped_books:
                if not all(re.search("[A-Z]$", re.split("-[a-z]{3}\d{1}", x)[0]) for x in sorted(group)):
                    for g in group:
                        milestones(os.path.join(root, g), ms_len, 0)

                elif any(re.search("[A-Z]$", re.split("-[a-z]{3}\d{1}", x)[0]) for x in sorted(group)):
                    # prev_ms_cnt = 0
                    group.sort(key=lambda f: f.split("-")[1])
                    grouped_extensions = [list(items) for gr, items in groupby(group,
                                                                               key=lambda name: name.split("-")[1])]
                    for sub_g in grouped_extensions:
                        prev_ms_cnt = 0
                        for f in sorted(sub_g):
                            prev_ms_cnt = milestones(os.path.join(root, f), ms_len, prev_ms_cnt)
    # return main_folder


if __name__ == '__main__':
    folder = input("Enter the path to the OpenITI folder: ")
    ms_length = input("Enter the length of milestones: ")
    # TODO:
    #  skip for the time being as we are not sure whether some Arabic content is being changed since last run
    # re_insert = input("Do you want to re-insert milestone ids to a file with milestone ids? (Y or N)")
    process_files(folder, int(ms_length))
    print("Done!")

