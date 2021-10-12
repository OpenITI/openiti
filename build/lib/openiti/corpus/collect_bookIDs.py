import os
from collections import Counter
import re


def collect_book_ids(source_dir):
    """
    Collects book ids of the OpenITI corpus and return a dictionary of source identifiers
    and the, frequencies. Source identifier is the first part of a book id that specifies
    the source form which the book comes, e.g., Shamela, JK, etc.

    Output sample:
    {'Shamela': 3691, 'JK': 2309}

    Args:
        source_dir: path to the folder containing OpenITI texts or XXXXAH repos

    Returns:
        Dictionary: source ids to frequency

    """

    id_set = set()
    for root, dirs, files in os.walk(source_dir):
        for f in files:
            txt_f = re.search("^\d{4}\w+\.\w+\.\w+-\w{4}(\.(mARkdown|inProgress|completed))?$", f)
            if txt_f:
                b_id = re.sub("-\w{4}", "", txt_f.group(0).split(".")[2])
                id_set.add(b_id)

    lib_ids = [re.sub("\d+(Vols)?([A-Z]{1})?(BK\d{1})?$", "", x) for x in id_set]
    return Counter(lib_ids)


if __name__ == '__main__':

    source = input("Enter the source directory of all AH repositories: ")

    if not os.path.exists(source):
        print("No such directory %s " % source)
    else:
        collect_book_ids(source)
