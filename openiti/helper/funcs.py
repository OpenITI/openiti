import math
import os
import random
import re
import unicodedata
import urllib.request as url
import requests
import bisect

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

#def get_all_yml_files_in_folder(start_folder, yml_type,
def get_all_yml_files_in_folder(start_folder, yml_types,
                                excluded_folders=exclude_folders,
                                exclude_files=exclude_files):
    """A generator that yields the file path for all yml files \
    of a specific type in a folder and its subfolders.

    OpenITI yml files exist for authors, books and versions.
    
    The script creates a generator over which you can iterate.
    It yields the full path to each of the yml files.

    Args:
        start_folder (str): path to the folder containing the text files
        yml_type (list): list of desired yml file types:
            one or more of "author", "book", or "version"
        excluded_folders (list): list of folder names that should be excluded
            (default: the list of excluded folders defined in this module)
        excluded_files (list): list of file names that should be excluded
            (default: the list of excluded file names defined in this module)

    Examples:
        > folder = r"D:\London\OpenITI\25Y_repos"
        > for fp in get_all_yml_files_in_folder(folder):
            print(fp)
        > folder = r"D:\London\OpenITI\25Y_repos\0025AH"
        > AH0025_file_list = [fp for fp in get_all_text_files_in_folder(folder)]
    """
    dots = {"author": 1, "book": 2, "version": 3}
    if isinstance(yml_types, str):
        yml_types = [yml_types,]
    for root, dirs, files in os.walk(start_folder):
        dirs[:] = [d for d in dirs if d not in exclude_folders]
        files[:] = [f for f in files if f not in exclude_files]
        for fn in files:
            for yml_type in yml_types:
                if re.findall(r"^(?:[^.]+\.){%s}yml$" % dots[yml_type], fn):
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
    and removing all Latin-language characters and non-word characters

    Args:
        text (str): the string to be cleaned

    Returns:
        (str): the cleaned string
    """
    text = ara.normalize_ara_light(text)
    #text = re.sub("\W|\d|[A-z]", " ", text) # until 10/10/2023
    latin_letters = "[" + ara.transcription_chars + "]"
    text = re.sub("\W|\d|"+latin_letters, " ", text)
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



def read_header(pth, lines=300, header_splitter="#META#Header#End#", 
                encoding="utf-8-sig"):
    """Read only the OpenITI header of a file without opening the entire file.

    Args:
        pth (str): path to local text file / URL of remote text file 
        lines (int): number of lines at the top of the file to be read
        header_splitter (str): string that separates the header from the body text
        encoding (str): text encoding to use. Default: "utf-8-sig" 
            (Unicode utf-8, strips BOM at start of file)

    Returns:
        (str): the metadata header of the text file
    """
    header = ""
    i=0
    try:   # local text file:
        with open(pth, mode="r", encoding=encoding) as file:
            while i <= lines:
                # read next line in file:
                line = file.readline()
                # add the line to the header:
                header += line
                # stop and return the header when we reach the header splitter:
                if header_splitter in line:
                    return header
                # start a new iteration
                i += 1
    except:  # URL of online text:
        with requests.get(pth, stream=True) as r:
            for line in r.iter_lines():
                # decode the new line and add it to the header:
                line = line.decode(encoding)
                header += line+"\n"   # r.iter_lines() strips off the newline character!
                # stop and return the header when we reach the header splitter:
                if header_splitter in line:
                    return header
                # start a new iteration iteration unless we run out of lines to read:
                i+=1
                if i >= lines:
                    break

    print("{}: header splitter not reached after {} lines".format(fp, lines))
    
    return ""




def read_text(pth, max_header_lines=300, split_header=False, remove_header=False,
              encoding="utf-8-sig", header_splitter="#META#Header#End#"):
    """Read a text from a file or from a URL.
    
    The parameters allow you to choose to  
    * full text file content: metadata header + text in a single string
    * only the text, without the header, in a single string (remove_header=True)
    * header and text, separated, in a tuple of strings (split_header=True)

    Args:
        pth (str): path to local text file / URL of remote text file 
        max_header_lines (int): number of lines at the top of the file to be read to find the header
        split_header (bool): if True, the header and main body of the text 
            will be returned as separate strings
        remove_header (bool): if True, only the main body of the text will be returned
        encoding (str): text encoding to use. Defaults to "utf-8-sig" 
            (Unicode utf-8, strips BOM at start of file)
        header_splitter (str): string that separates the header from the body text.
            Defaults to "#META#Header#End#" (end of the standard OpenITI metadata header)

    Returns: 
        str or tuple
    """
    # full text+header:
    if not split_header and not remove_header:
        try:
            with open(pth, mode="r", encoding=encoding) as file:
                return file.read()
        except:
            r = requests.get(pth)
            return r.text
    # split the main text from the header:
    else:
        # get the header:
        header = read_header(pth, lines=max_header_lines)
        
        # get the main body of the text:
        try:   # path to local text file:
            with open(pth, mode="r", encoding="utf-8") as file:
                # read the full text file:
                text = file.read()
                # strip the header:
                text = text[len(header):]
                
        except:  # URL to online text:
            with requests.get(pth) as r:
                # download and read the full text file:
                text = r.text
                # strip the header:
                text = text[len(header):]
        
        if remove_header:  # return only the main body of the text
            return text
        # else: return both header and text
        return (header, text) 


def absolute_path(path):
    return os.path.abspath(path)


def get_page_numbers(text, page_regex=r"PageV[^P]+P\d+[A-Z]?"):
    """Get all page numbers and their locations (character offsets) in a text

    Args:
        text (str): the text in which the page numbers should be found
        page_regex (str): pattern that describes the page numbers in the text

    Returns:
        tuple of lists (page_numbers, page_ends)
    """
    matches = regex.finditer(page_regex, text)
    page_numbers = []
    page_ends = []
    for m in matches:
        page_numbers.append(m.group())
        page_ends.append(m.end())
    return (page_numbers, page_ends)

def get_page_number(loc, page_numbers, page_ends):
    """Find the page number of a specified character position in the text

    NB: the page_numbers and page_ends lists can be generated
        by the `get_page_numbers` function

    Args:
        loc (int): a character position in the text
        page_numbers (list): a list of all page numbers in the text
        page_ends (list): a list of the character position
            of each page number in the text

    Returns:
        str
    """
    i = bisect.bisect_right(page_ends, loc)
    return page_numbers[i]

##def get_page_number(page_numbers, pos):
##    """Get the page number of a token at index position `pos` in a string \
##    based on a dictionary `page_numbers` that contains the index positions \
##    of the page numbers in that string.
##
##    Args:
##        page_numbers (dict):
##            key: index of the last character of the page number in the string
##            value: page number
##        pos (int): the index position of the start of a token in the string
##    """
##    for k in sorted(page_numbers.keys()):
##        if pos < k:
##            return page_numbers[k]

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
    #page_numbers = {m.end(): m.group(0) \
    #                for m in re.finditer("PageV\d+P\d+", text)}
    page_numbers, page_ends = get_page_numbers(text)
    for match in re.finditer(no_regex, text):
        no = int(match.group(1))
        if no == 1:
            current_num = 1
            page = get_page_number(match.start(), page_numbers, page_ends)
            print("start recounting from 1 at", page)
        elif no == current_num:
            page = get_page_number(match.start(), page_numbers, page_ends)
            if report_repeated_numbers:
                print(page, no, "follows", current_num)
        elif no != current_num + 1:
            page = get_page_number(match.start(), page_numbers, page_ends)
            print(page, no, "follows", current_num)
            current_num = no
        else:
            current_num = no

def natural_sort(obj):
    """Sort a list containing letters and numbers in its natural order
    (1,2,3,4,5,6,7,8,9,10, ... instead of 1,10,2,3,4,5,6,7,8,9,10)

    based on https://stackoverflow.com/a/16090640/4045481
    """
    natsort = lambda s: [int(t) if t.isdigit() else t.lower()
                         for t in re.split('(\d+)', s)]
    return sorted(obj, key=natsort)
    

def get_semantic_tag_elements(tag_name, text, include_tag=False,
                                  include_prefix=False, include_offsets=False,
                                  max_tokens=99, normalize_spaces=False):
    """Extract semantic tags (the likes of @TOP\d\d+) from OpenITI texts

    Args:
        tag_name (str): the tag you want to extract (e.g., @TOP, @PER, ...)
        text (str): the string from which the tags are to be extracted
        include_tag (bool): if False, only the content of the tag
            will be returned. If True, both tag+content (default: False)
        include_prefix (bool): if False, the prefix (that is, the number
            of characters defined by the first digit after the tag)
            will be stripped off from the result. Only if include_tag is
            set to False. Default: False.
        include_offsets (bool): if True, the start and end offsets of
            each element will be included (as a dictionary:
            with keys "match", "start", "end")
        max_tokens (int): the maximum number of tokens inside a tag.
            Default: 99.
        normalize_spaces (bool): if True, new lines, page numbers etc. 
            will be removed from the returned tokens.

    Returns:
        list
    """
    # first extract a large number of tokens after the tag
    ar_tok = "[" + "".join(ara.ar_chars)+"]+"
    not_token_not_tag = "[^@"+ar_tok[1:]
    n_tokens = "{1,"+str(max_tokens)+"}"
    #pattern = tag_name+"\d\d+(?:[^@\w]+\w+){1,"+str(max_tokens)+"}"
    pattern = f"{tag_name}\d\d+(?:{not_token_not_tag}{ar_tok}){n_tokens}"
    tmp_results = re.finditer(pattern, text)

    # select the amount of tokens as defined in the tag:
    final_results = []
    for result in tmp_results:
        # extract the tag from the result:
        res_tag = re.findall(tag_name+"\d\d+", result.group())[0]
        not_token = "[^"+ar_tok[1:]
        tokens = re.split("("+not_token+")", result.group()[len(res_tag):])
        # remove empty string matches:
        tokens = [tok for tok in tokens if tok != ""]
        n_prefix, n_toks = re.findall("(\d)(\d+)", res_tag)[-1]
        if not include_tag:
            selected_toks = tokens[1:(2*int(n_toks))]
            cleaned_res = "".join(selected_toks)
            # move start offset to first character of the content of the tag:
            start_offset = result.start() + len(res_tag+tokens[0])
            if not include_prefix:
                # remove the prefix from the match:
                cleaned_res = cleaned_res[int(n_prefix):]
                # move the start offset to the first character after the prefix:
                start_offset += int(n_prefix)
            end_offset =  start_offset + len(cleaned_res)
            # remove new lines, page numbers, etc. from the tokens:
            if normalize_spaces:
                selected_toks = [re.sub(not_token, " ", tok) for tok in selected_toks]
                cleaned_res = "".join(selected_toks)
                if not include_prefix:
                    # remove the prefix from the match:
                    cleaned_res = cleaned_res[int(n_prefix):]
            if include_offsets:
                final_results.append({"match":cleaned_res,
                                      "start":start_offset,
                                      "end":end_offset})
            else:
                final_results.append(cleaned_res)
        else:
            selected_toks = tokens[0:(2*int(n_toks))]
            cleaned_res = res_tag+("".join(selected_toks))
            start = result.start()
            end = start+len(cleaned_res)
            if normalize_spaces:
                selected_toks = [re.sub(not_token, " ", tok) for tok in selected_toks]
                cleaned_res = res_tag+("".join(selected_toks))
            if include_offsets:
                final_results.append({"match":cleaned_res,
                                      "start":start,
                                      "end":end})
            else:
                final_results.append(cleaned_res)

    return final_results


def get_section_title(loc, section_titles, section_starts):
    """Find the section title(s) for a specified character offset in the text

    Args:
        loc (int): character offset for which the section title is wanted
        section_titles (list): a list of all section titles in the document
        section_starts (list): a list of character offsets of the
            starts of all sections in the text
    """
    i = bisect.bisect_left(section_starts, loc)
    return section_titles[i]

def get_sections(text, section_header_regex="### .+", include_hierarchy=True):
    """Get the section titles and start offsets for all sections in the text

    Args:
        text (str): the text containing the sections
        section_header_regex (str): regular expression pattern for section headers
        include_hierarchy (bool): if False, only the title of the section
            will be returned; if True, a list of titles of all parent sections
            will be returned

    Returns:
        list (section_titles, section_starts)
    """
    section_titles = [] 
    section_starts = [] 
    open_sections = [] 
    for m in re.finditer(section_header_regex, text):
        title = m.group()
        level = title.count("|") - 1
        if not include_hierarchy:
            open_sections = title
        elif level == 0:
            open_sections = [title,] 
        else:
            open_sections = open_sections[:level]
            open_sections.append(title)
         
        section_titles.append(open_sections) 
        section_starts.append(m.start())

    return section_titles, section_starts


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    start_folder = r"D:\London\OpenITI\25Y_repos"
    chars = get_all_characters_in_folder(start_folder, verbose=False,
                                         exclude_folders=exclude_folders,
                                         exclude_files=exclude_files)
    #get_character_names(chars, verbose=True)
    test_str = """هذه محاولة ثانية: @TOP01 بغداد مدينة
يعرف أيضا @TOP12 بمدينة ms001 PageV01P001 السلام.
واسم المؤسس: @PER01 أحمد!"""


    res = get_semantic_tag_elements("@T(?:OP)?", test_str, include_tag=False, include_prefix=False, include_offsets=True)
    print(res)
