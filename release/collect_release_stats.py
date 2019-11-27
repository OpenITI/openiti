import re
import os
import sys

# TODO: update the paths using import
sys.path.append("Z:/Documents/GitProjects/PythonFunctions")
sys.path.append("/Users/romanov/Documents/c.GitProjects/PythonFunctions")

sum_r = """
    Min.  1st Qu.   Median     Mean  3rd Qu.     Max. 
     150    32700   105300   306700   266700 10410000 
"""


# loop through all subfolders
# check all files ending with [-ara1]
# count the overall number of files
# count word freqs for all of them (build a table)
# count the overall length in words
# count word frequencies of only longest texts in each text group


def get_len(file_name):
    with open(file_name, "r", encoding="utf8") as f1:
        f1 = f1.read()
        fr = len(re.findall("\w+", f1))
        return fr


def generate_stats(in_dir):
    stats = []
    for root, dirs, filenames in os.walk(in_dir):
        for f in filenames:
            if f.endswith("-ara1"):
                path_to_file = os.path.join(root, f)
                # print(path_to_file)

                fr1 = get_len(path_to_file)
                fr2 = "{:,}".format(fr1)
                stats.append("%010d\t%s\t%s" % (fr1, f, fr2))

                print("%010d\t%s\t%s" % (fr1, f, fr2))

    with open("raw_len_stats.txt", "w", encoding="utf8") as f9:
        f9.write("\n".join(stats))


# generateStats()
def ref(sum_re):
    sum_re = re.sub(" Q", "_Q", sum_re)
    sum_re = re.sub(" +", "\t", sum_re)
    sum_re = re.sub("_", " ", sum_re)
    sum_re = re.sub("\n\n", "", sum_re)
    sum_re = re.sub(r"(^|\n)\t", r"\1", sum_re)

    head = sum_re.split("\n")[1].split("\t")
    vals = sum_re.split("\n")[2].split("\t")

    # TABLE
    doc = "\n\n## Summary statistics on the lengths of texts in the corpus\n\n"

    doc += "| | Words  | Pages (300 w/p) |\n"
    doc += "|:--- | ------:| -----:|\n"

    for i in range(0, 6):
        doc += "| *%s* | %s | %s |\n" % (head[i], "{:,}".format(int(vals[i])), "{:,}".format(int(vals[i]) // 300))
    return doc


def process_stats(len_stats_file, collect_stats_file):
    doc = "## Statistics on the corpus\n\n"
    doc += "| **Category** | **Stats** |\n"
    doc += "|:--- | ------:|\n"

    with open(len_stats_file, "r", encoding="utf8") as f1:
        stats = f1.read().split("\n")

        uri_dic = {}
        uri_lis = []
        for i in stats:
            i = i.split("\t")
            uri_dic[i[1]] = int(i[0])
            uri_lis.append(i[1])

        # count authors and books
        authors = []
        books = []
        for a in uri_lis:
            a = a.split(".")
            authors.append(a[0])
            books.append(a[0] + "." + a[1])

        # count words all and by unique titles
        uni_dic = {}
        words_all = 0
        for k, v in uri_dic.items():
            words_all += v
            new_k = ".".join(k.split(".")[:2])
            if new_k in uni_dic:
                if uni_dic[new_k] < v:
                    uni_dic[new_k] = v
            else:
                uni_dic[new_k] = v

        words_max = 0
        lengths = []
        list_uri_freq = []
        list_freq_uri = []
        for k, v in uni_dic.items():
            words_max += v
            lengths.append(str(v))
            list_uri_freq.append("%s\t%09d" % (k, v))
            list_freq_uri.append("%09d\t%s" % (v, k))

        print("Run in R to get summary stats:\n\nsummary(c(%s))" % ",".join(lengths))

        print("\n\n")

        doc += "| Number of text files | %d |\n" % len(stats)
        doc += "| Number of books      | %d |\n" % len(list(set(books)))
        doc += "| Number of authors    | %d |\n" % len(list(set(authors)))
        doc += "| Length in words (all)| %s |\n" % "{:,}".format(words_all)
        doc += "| Length in pages (300 w/p)| %s |\n" % "{:,}".format(words_all // 300)
        doc += "| Length in words (unique) | %s |\n" % "{:,}".format(words_max)
        doc += "| Length in pages (300 w/p)| %s |\n" % "{:,}".format(words_max // 300)

        doc += ref(sum_r)

        # table of texts by lengths

        doc += "\n\n## Texts by length (duplicates excluded)\n\n"

        doc += "| Num | TextGroup URI | Words  | Pages (300 w/p) |\n"
        doc += "| --: | :--- | ------:| -----:|\n"

        counter = 0

        for i in sorted(list_freq_uri, reverse=True):
            counter += 1
            i = i.split("\t")
            doc += "| %d | %s | %s | %s |\n" % (
                counter, i[1], "{:,}".format(int(i[0])), "{:,}".format(int(i[0]) // 300))

        # table of texts by chronology

        doc += "\n\n## Texts in chronological order (duplicates excluded)\n\n"
        doc += "| TextGroup URI | Words  | Pages (300 w/p) |\n"
        doc += "|:--- | ------:| -----:|\n"

        for i in sorted(list_uri_freq, reverse=False):
            i = i.split("\t")
            doc += "| %s | %s | %s |\n" % (i[0], "{:,}".format(int(i[1])), "{:,}".format(int(i[1]) // 300))

        with open(collect_stats_file, "w", encoding="utf8") as f9:
            f9.write(doc)
