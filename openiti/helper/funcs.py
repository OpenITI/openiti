import math
import os
import random
import re
import unicodedata
import urllib.request as url

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
    sys.path.append(root_folder)
from openiti.helper import ara

splitter = "#META#Header#End#"
milestone = "Milestone300"
thresh = 1000

exclude_folders = ["OpenITI.github.io", "Annotation", "maintenance",
                   "i.mech00", "i.mech01", "i.mech02", "i.mech03",
                   "i.mech04", "i.mech05", "i.mech06", "i.mech07",
                   "i.mech", "i.mech_Temp", "i.mech08", "i.mech09",
                   "i.logic", "i.cex", "i.cex_Temp", ".git"]

exclude_files = ["README.md", ".DS_Store",
                 ".gitignore", "text_questionnaire.md"]

def get_all_text_files_in_folder(start_folder, excluded_folders=exclude_folders,
                                 exclude_files=exclude_files):
    """A generator that yields the file path for all OpenITI text files \
    in a folder and its subfolders.

    OpenITI text files are defined here as files that have a language
    identifier (-ara1, -ara2, -per1, etc.) and have either no extension
    or .mARkdown, .completed, or .inProgress.
    
    The script creates a generator over which you can iterate.
    It yields the full path to each of the text files.

    Args:
        start_folder (str): path to the folder containing the text files
        excluded_folders (list): list of folder names that should be excluded
            (default: the list of excluded folders defined in this module)
        excluded_files (list): list of file names that should be excluded
            (default: the list of excluded file names defined in this module)

    Examples:
        > folder = r"D:\London\OpenITI\25Y_repos"
        > for fp in get_all_text_files_in_folder(folder):
            print(fp)
        > folder = r"D:\London\OpenITI\25Y_repos\0025AH"
        > AH0025_file_list = [fp for fp in get_all_text_files_in_folder(folder)]
    """
    for root, dirs, files in os.walk(start_folder):
        dirs[:] = [d for d in dirs if d not in exclude_folders]
        files[:] = [f for f in files if f not in exclude_files]
        for fn in files:
            if re.findall(r"-\w\w\w\d(?:.inProgress|.completed|.mARkdown)?\Z", fn):
                fp = os.path.join(root, fn)
                yield(fp)

def get_all_characters_in_text(fp):
    """Get a set of all characters used in a text.

    Args:
        fp (str): path to a text file.

    Returns:
        (set): a set of all characters used in the text.
    """
    with open(fp, mode="r", encoding="utf-8") as file:
        text = file.read()
        return set(text)
    

def get_all_characters_in_folder(start_folder, verbose=False,
                                 exclude_folders=[], exclude_files=[]):
    """Get a set of all characters used in all OpenITI text files \
    in a folder and its subfolders.

    Args:
        start_folder (str): path to the root directory. All files and folders
            in it, except if they are in the exclude lists, will be processed.
        verbose (bool): if True, filenames and current number of characters
            in the set will be printed.
        exclude_folders (list): list of folder names to be excluded
            from the process.
        exclude_folders (list): list of file names to be excluded.

    Returns:
        (set): a set of all characters used in the folder.
    """
    all_characters = set()
    for root, dirs, files in os.walk(start_folder):
        dirs[:] = [d for d in dirs if d not in exclude_folders]
        files[:] = [f for f in files if f not in exclude_files]
        for fn in files:
            fp = os.path.join(root, fn)
            extensions = [".completed", ".mARkdown", ".inProgress"]
            if os.path.splitext(fn)[1] in extensions \
              or re.findall(r"(ara|per)\d$", fn):
                if verbose:
                    print(len(all_characters), fn)
                text_chars = get_all_characters_in_text(fp)
                all_characters = all_characters.union(text_chars)
    return all_characters


def get_character_names(characters, verbose=False):
    """Print the unicode name of a list/set/string of characters.

    Args:
        characters (list/set/string): a list, string or set of characters.
        verbose (bool): if set to True, the output will be printed

    Returns:
        (dict): a dictionary of characters and their names.

    Examples:
        >>> char_dict = {"١": "ARABIC-INDIC DIGIT ONE",\
                         "٢": "ARABIC-INDIC DIGIT TWO"}
        >>> char_dict == get_character_names("١٢")
        True
        >>> char_dict == get_character_names(["١", "٢"])
        True
        >>> char_dict == get_character_names({"١", "٢"})
        True
    """
    char_dict = dict() 
    for c in sorted(list(characters)):
        try:
            name = unicodedata.name(c)            
        except:
            name = None
        char_dict[c] = name
        if verbose:
            print("{}\t{}".format(c, name))
    
    return char_dict

def text_cleaner(text):
    """Clean text by normalizing Arabic characters \
    and removing all non-Arabic characters

    Args:
        text (str): the string to be cleaned

    Returns:
        (str): the cleaned string
    """
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



def read_header(fp):
    """Read only the OpenITI header of a file without opening the entire file.

    Args:
        fp (str): path to the text file

    Returns:
        (list): A list of all metadata lines in the header
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

def get_page_number(page_numbers, pos):
    """Get the page number of a token at index position `pos` in a string \
    based on a dictionary `page_numbers` that contains the index positions \
    of the page numbers in that string.

    Args:
        page_numbers (dict):
            key: index of the last character of the page number in the string
            value: page number
        pos (int): the index position of the start of a token in the string
    """
    for k in sorted(page_numbers.keys()):
        if pos < k:
            return page_numbers[k]

def report_missing_numbers(fp, no_regex="### \$ \((\d+)",
                           report_repeated_numbers=True):
    """Use a regular expression to check whether numbers\
    (of books, pages, etc.) are in sequence and no numbers are missing.

    Arguments:
        fp (str): path to the text file
        no_regex (str): regular expression pattern describing the number
            for which the sequence should be checked.
            NB: the numbers should be in the first/only capture group

    Use cases:
        - Page numbers: use regex `PageV\d+P(\d+)`
        - numbered sections: e.g.,
          `### \$ \(?(\d+)` for dictionary items,
          `### \|{2} (\d+)` for second-level sections, ...
    """
    with open(fp, mode="r", encoding="utf-8") as file:
        text = file.read()
    current_num = 0
    page_numbers = {m.end(): m.group(0) \
                    for m in re.finditer("PageV\d+P\d+", text)}
    for match in re.finditer(no_regex, text):
        no = int(match.group(1))
        if no == 1:
            current_num = 1
            page = get_page_number(page_numbers, match.start())
            print("start recounting from 1 at", page)
        elif no == current_num:
            page = get_page_number(page_numbers, match.start())
            if report_repeated_numbers:
                print(page, no, "follows", current_num)
        elif no != current_num + 1:
            page = get_page_number(page_numbers, match.start())
            print(page, no, "follows", current_num)
            current_num = no
        else:
            current_num = no


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    start_folder = r"D:\London\OpenITI\25Y_repos"
    chars = get_all_characters_in_folder(start_folder, verbose=False,
                                         exclude_folders=exclude_folders,
                                         exclude_files=exclude_files)
    #get_character_names(chars, verbose=True)
