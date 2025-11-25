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
from openiti.helper import rgx

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
        > folder = r"D:/OpenITI/25Y_repos"
        > for fp in get_all_text_files_in_folder(folder):
            print(fp)
        > folder = r"D:/OpenITI/25Y_repos/0025AH"
        > AH0025_file_list = [fp for fp in get_all_text_files_in_folder(folder)]
    """
    for root, dirs, files in os.walk(start_folder):
        dirs[:] = [d for d in dirs if d not in exclude_folders]
        files[:] = [f for f in files if f not in exclude_files]
        for fn in files:
            if re.findall(r"-(?:\w\w\w\d)+(?:.inProgress|.completed|.mARkdown)?\Z", fn):
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
        yml_types (list): list of desired yml file types:
            one or more of "author", "book", "version",
            "location", "manuscript" or "transcription"
        excluded_folders (list): list of folder names that should be excluded
            (default: the list of excluded folders defined in this module)
        excluded_files (list): list of file names that should be excluded
            (default: the list of excluded file names defined in this module)

    Examples:
        > folder = r"D:/OpenITI/25Y_repos"
        > for fp in get_all_yml_files_in_folder(folder):
            print(fp)
        > folder = r"D:/OpenITI/25Y_repos/0025AH"
        > AH0025_file_list = [fp for fp in get_all_text_files_in_folder(folder)]
    """
    dots = {"author": 1, "book": 2, "version": 3,
            "location": 1, "manuscript": 2, "transcription": 3,
            }
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
              or re.findall(r"-(?:\w\w\w\d)+$", fn):
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


def count_toks(text, incl_chars=False, return_tok_set=False, clean_tok_set=True,
               tok_splitter=rgx.tok_splitter, do_not_count=rgx.do_not_count):
    """Count non-tag tokens in text.
    If `incl_chars`, the function will return both token and character counts.

    Args:
        text (str): text or path to text
        incl_chars (bool): if True, both tokens and characters will be counted.
           Defaults to False (count only tokens).
        return_tok_set (bool): if True, the function will return a set
           of all tokens in the text.
        clean_tok_set (bool): if True, all non-word characters will
           be removed from the token set.
        tok_splitter (str): regex pattern on which the text should be split
           into tokens and non-tokens
        do_not_count (str): regex pattern to ignore tokens that contain
           letters and numbers but should not be counted as tokens

    Returns: int or (int, int) or (int, int)

    Examples:
        >>> text = 'This contains 4 tokens.'
        >>> count_toks(text)
        4
        >>> count_toks(text, incl_chars=True)
        (4, 19)
        >>> _, toks = count_toks(text, return_tok_set=True)
        >>> sorted(toks)
        ['4', 'This', 'contains', 'tokens']
        >>> _, toks = count_toks(text, return_tok_set=True, clean_tok_set=False)
        >>> sorted(toks)
        ['4', 'This', 'contains', 'tokens.']
        >>> text = 'Tags are not counted: PageV01P234 @P02 @TOP2 YB1234'
        >>> count_toks(text)
        4
        >>> text = 'Neither are markdown links: ![caption](path/to/image.png) [link](https://url.com)'
        >>> count_toks(text)
        4
        >>> text = 'words split with hy-\\nphen are counted as a single token'
        >>> count_toks(text)
        10
        >>> text = '''1. list numbers and footnote references (2) are not counted [3].'''
        >>> count_toks(text)
        8
        >>> text = '|Tables|should not|\\n|be a | problem|'
        >>> count_toks(text)
        6
    """
    if os.path.isfile(text):
        text = read_text(text, remove_header=True)

    all_toks = re.split(tok_splitter, text)

    n_toks = 0
    n_chars = 0
    tok_set = set()
    for tok in all_toks:
        if re.findall(r"\w", tok) and not re.findall(do_not_count, tok):
            # do not count first half of hyphenated token at end of line:
            if not tok.endswith("-"):
                n_toks += 1
            if incl_chars:
                n_chars += len(re.findall(r"\w", tok))
            if return_tok_set:
                tok_set.add(tok)

    if clean_tok_set:
        tok_set = set([re.sub(r"\W+", "", tok) for tok in tok_set])

    if incl_chars:
        if return_tok_set:
            return n_toks, n_chars, tok_set
        else:
            return n_toks, n_chars
    else:
        if return_tok_set:
            return n_toks, tok_set
        else:
            return n_toks

def count_chars(text, tok_splitter=rgx.tok_splitter, do_not_count=rgx.do_not_count):
    """Count characters in non-tag tokens in text.

    Args:
        text (str): text or path to text
        tok_splitter (str): regex pattern on which the text should be split
           into tokens and non-tokens
        do_not_count (str): regex pattern to ignore tokens that contain
           letters and numbers but should not be counted as tokens

    Returns: int

    Examples:
        >>> text = 'This contains 4 tokens'
        >>> count_chars(text)
        19
        >>> text = 'Tags are not counted: PageV01P234 @P02 @TOP2 YB1234'
        >>> count_chars(text)
        17
        >>> text = 'Neither are markdown links: ![caption](path/to/image.png) [link](https://url.com)'
        >>> count_chars(text)
        23
        >>> text = '|Tables|should not|\\n|be a | problem|\\n'
        >>> count_chars(text)
        25
    """
    n_toks, n_chars = count_toks(text, incl_chars=True,
                                 tok_splitter=tok_splitter,
                                 do_not_count=do_not_count)
    return n_chars

def text_cleaner(text):
    """Clean text by normalizing Arabic characters \
    and removing all Latin-language characters and non-word characters

    Args:
        text (str): the string to be cleaned

    Returns:
        (str): the cleaned string
    """
    text = ara.normalize_ara_light(text)
    #text = re.sub(r"\W|\d|[A-z]", " ", text) # until 10/10/2023
    latin_letters = "[" + ara.transcription_chars + "]"
    text = re.sub(r"\W|\d|"+latin_letters, " ", text)
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


def get_page_numbers(text, page_regex=r"(?:Folio|Page)(Beg|End)?V[^P]+P\d+[A-Z]?"):
    """Get all page numbers and their locations (character offsets) in a text

    Args:
        text (str): the text in which the page numbers should be found
        page_regex (str): pattern that describes the page numbers in the text

    Returns:
        tuple of lists (page_numbers, page_ends)
    """
    matches = re.finditer(page_regex, text)
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
    try:
        return page_numbers[i]
    except:
        return "No page number"

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

def report_missing_numbers(fp, no_regex=r"### \$ \((\d+)",
                           report_repeated_numbers=True):
    r"""Use a regular expression to check whether numbers\
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
                         for t in re.split(r'(\d+)', s)]
    return sorted(obj, key=natsort)
    

def get_semantic_tag_elements(tag_name, text, include_tag=False,
        include_prefix=False, include_offsets=False,
        include_pages=False, page_numbers=None, page_ends=None,
        page_regex=r"PageV[^P]+P\d+[A-Z]?",
        max_tokens=99, normalize_spaces=True):
    r"""Extract semantic tags (the likes of @TOP\d\d+) from OpenITI texts

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
        include_pages (bool): if True, page numbers of the pages
            in which the match was found  will be included in the output
        page_numbers (list): a list of all page numbers in the text;
            generated by the `get_page_numbers` function
        page_ends (list): a list of the positions of each page number;
            generated by the `get_page_numbers` function
        page_regex (str): regular expressions pattern describing
            the page number format used in the text
        max_tokens (int): the maximum number of tokens inside a tag.
            Default: 99.
        normalize_spaces (bool): if True, new lines, page numbers etc. 
            will be removed from the returned tokens.

    Returns:
        list of strings: if 
    """
    if include_pages and (page_numbers is None or page_ends is None):
        page_numbers, page_ends = get_page_numbers(text, page_regex=page_regex)

    token_pattern = "[" + "".join(ara.ar_chars)+"]+"
    not_token = "[^"+token_pattern[1:]
    not_token_not_tag = "[^@"+token_pattern[1:]
    
    # first extract a large number of tokens after the tag
    n_tokens = "{1,"+str(max_tokens)+"}"
    pattern = rf"{tag_name}\d\d+(?:{not_token_not_tag}{token_pattern}){n_tokens}"
    tmp_results = re.finditer(pattern, text)

    # select the amount of tokens as defined in the tag:
    final_results = []
    for result in tmp_results:
        # extract the tag from the result:
        res_tag = re.findall(tag_name+r"\d\d+", result.group())[0]
        # get the number of prefix characters and tokens:
        n_prefix, n_toks = re.findall(r"(\d)(\d+)", res_tag)[-1]

        # split the string into tokens and not-tokens: 
        tokens = re.split("("+not_token+")", result.group()[len(res_tag):])
        # remove empty string matches:
        tokens = [tok for tok in tokens if tok != ""]

        # select the specified number of tokens (and not-tokens):
        selected_toks = tokens[1:(2*int(n_toks))]
        space_after_tag = tokens[0]
        if not include_tag:
            cleaned_res = "".join(selected_toks)
            # move start offset to first character of the content of the tag:
            start_offset = result.start() + len(res_tag+space_after_tag)
            if not include_prefix:
                # remove the prefix from the match:
                cleaned_res = cleaned_res[int(n_prefix):]
                # move the start offset to the first character after the prefix:
                start_offset += int(n_prefix)
            # calculate the offset of the last character:
            end_offset =  start_offset + len(cleaned_res)
            # remove new lines, page numbers, etc. from the tokens:
            if normalize_spaces:
                cleaned_res = re.sub(not_token, " ", cleaned_res)
        else:
            start_offset = result.start()
            end_offset = start_offset+len(res_tag+space_after_tag+("".join(selected_toks)))
            
            if normalize_spaces:
                space_after_tag = " "
                selected_toks = [re.sub(not_token, " ", tok) for tok in selected_toks]
            cleaned_res = "".join(selected_toks)
            if not include_prefix:
                # remove the prefix from the match:
                cleaned_res = cleaned_res[int(n_prefix):]
            cleaned_res = res_tag+space_after_tag+cleaned_res

        # prepare the output:
        d = dict()
        d["match"] = cleaned_res
        if include_offsets:
            d["start"] = start_offset
            d["end"] = end_offset
        if include_pages:
            page = get_page_number(start_offset, page_numbers, page_ends)
            d["page"] = page
        if len(d) > 1:
            final_results.append(d)
        else:
            final_results.append(cleaned_res)

    return final_results


def get_section_title(loc, section_titles, section_starts):
    """Find the section title(s) for a specified character offset in the text

    NB: you can generate the section_titles and section_starts lists
        using the `get_sections` function

    Args:
        loc (int): character offset for which the section title is wanted
        section_titles (list): a list of all section titles in the document
        section_starts (list): a list of character offsets of the
            starts of all sections in the text

    Examples:
        >>> section_titles = ["Section 1", "Section 2", "Section 3"]
        >>> section_starts = [0, 150, 200]
        >>> get_section_title(10, section_titles, section_starts)
        'Section 1'
        >>> get_section_title(180, section_titles, section_starts)
        'Section 2'
        >>> get_section_title(210, section_titles, section_starts)
        'Section 3'
    """
    i = bisect.bisect_left(section_starts, loc) -1
    if i < 0:
        return None
    try:
        return section_titles[i]
    except:
        return "[no title]"

##def get_sections(text, section_header_regex="### .+",
##                 include_hierarchy=False, include_pages=True,
##                 page_numbers=None, page_ends=None, page_regex=r"PageV[^P]+P\d+[A-Z]?"):
##    """Get the section titles and start offsets for all sections in the text
##
##    Args:
##        text (str): the text containing the sections
##        section_header_regex (str): regular expression pattern for section headers
##        include_hierarchy (bool): if False, only the title of the section
##            will be returned; if True, a list of titles of all parent sections
##            will be returned
##        include_pages (bool): if True, page numbers of the pages
##            in which the match was found  will be included in the output
##        page_numbers (list): a list of all page numbers in the text;
##            generated by the `get_page_numbers` function
##        page_ends (list): a list of the positions of each page number;
##            generated by the `get_page_numbers` function
##        page_regex (str): regular expressions pattern describing
##            the page number format used in the text
##
##    Returns:
##        tuple (section_titles, start_offsets[, start_pages])
##
##    Examples:
##        >>> text = '''### | فارس
##        ... ### || قصبة فارس
##        ... شيراز قصبة فارس.
##        ... PageV01P001'''
##        >>> section_titles, section_starts, page_numbers = get_sections(text)
##        >>> for title, page in zip(section_titles, page_numbers):
##        ...     print(page, title)
##        PageV01P001 ### | فارس
##        PageV01P001 ### || قصبة فارس
##        >>> section_titles, section_starts = get_sections(text, include_pages=False)
##        >>> for title, start in zip(section_titles, section_starts):
##        ...     print(start, title)
##        0 ### | فارس
##        11 ### || قصبة فارس
##        >>> section_titles, section_starts = get_sections(text, include_pages=False, include_hierarchy=True)
##        >>> for title, start in zip(section_titles, section_starts):
##        ...     print(start, title)
##        0 ['### | فارس']
##        11 ['### | فارس', '### || قصبة فارس']
##    """
##    if include_pages and (page_numbers is None or page_ends is None):
##        page_numbers, page_ends = get_page_numbers(text, page_regex=page_regex)
##    
##    section_titles = [] 
##    start_offsets = [] 
##    open_sections = []
##    start_pages = []
##    for m in re.finditer(section_header_regex, text):
##        title = m.group()
##        level = title.count("|") - 1
##        if not include_hierarchy:
##            open_sections = title
##        elif level == 0:
##            open_sections = [title,] 
##        else:
##            open_sections = open_sections[:level]
##            open_sections.append(title)
##         
##        section_titles.append(open_sections) 
##        start_offsets.append(m.start())
##
##        if include_pages:
##            page = get_page_number(m.start(), page_numbers, page_ends)
##            start_pages.append(page)
##
##    if not include_pages:
##        return section_titles, start_offsets
##    else:
##        return section_titles, start_offsets, start_pages

def get_sections(text, section_header_regex="### .+",
                 include_hierarchy=False, include_offsets=False, include_pages=False,
                 page_numbers=None, page_ends=None, page_regex=r"PageV[^P]+P\d+[A-Z]?"):
    """Get the section titles and start offsets for all sections in the text

    Args:
        text (str): the text containing the sections
        section_header_regex (str): regular expression pattern for section headers
        include_hierarchy (bool): if True, a list of titles of all parent sections
            will be included in the output
        include_offsets (bool): if True, the start and end character offsets of the
            sections and section titles will be included in the output
        include_pages (bool): if True, the start and end page numbers of
            sections will be included in the output
        page_numbers (list): a list of all page numbers in the text;
            generated by the `get_page_numbers` function
        page_ends (list): a list of the positions of each page number;
            generated by the `get_page_numbers` function
        page_regex (str): regular expressions pattern describing
            the page number format used in the text

    Returns:
        list of strings: with default parameters, a list of strings is returned
        list of dictionaries: if any of the include_... parameters is set to True,
            a list of dictionaries will be returned
            (possible keys: "title", "level", "parent_sections", "start_offset",
            "title_end", "end_offset", "start_page", "end_page")

    Examples:
        >>> text = '''### | فارس
        ... ### || قصبة فارس
        ... شيراز قصبة فارس.
        ... PageV01P001'''
        >>> sections = get_sections(text)
        >>> for title in sections:
        ...     print(title)
        ### | فارس
        ### || قصبة فارس
        >>> sections = get_sections(text, include_pages=True)
        >>> for section in sections:
        ...     print(section["start_page"], section["end_page"], section["title"])
        PageV01P001 PageV01P001 ### | فارس
        PageV01P001 PageV01P001 ### || قصبة فارس
    """
    if include_pages and (page_numbers is None or page_ends is None):
        page_numbers, page_ends = get_page_numbers(text, page_regex=page_regex)
    
    sections = []
    open_sections = []
    open_levels = dict()
    i = 0
    for m in re.finditer(section_header_regex, text):
        title = m.group()
        level = title.count("|") - 1
        if level == 0:
            open_sections = [title,] 
        else:
            open_sections = open_sections[:level]
            open_sections.append(title)

        d = dict()
        d["title"] = title
        d["level"] = level
        if include_hierarchy:
            if len(open_sections) > 1:
                d["parent_sections"] = open_sections[:-1]
            else:
                d["parent_sections"] = []
        if include_offsets:
            d["start_offset"] = m.start()
            d["title_end"] = m.end()
        if include_pages:
            page = get_page_number(m.start(), page_numbers, page_ends)
            d["start_page"] = page
            
        if len(d) > 2:
            sections.append(d)
            # add the end offset and/or page for all sections closed off by this section header:
            to_be_closed = [lvl for lvl in open_levels if lvl >= level]
            for lvl in to_be_closed:
                lvl_idx = open_levels[lvl]
                if include_pages:
                    sections[lvl_idx]["end_page"] = page
                if include_offsets:
                    sections[lvl_idx]["end_offset"] = m.end()
                del open_levels[lvl]
            open_levels[level] = i

        else:
            sections.append(title)
        i += 1

    # add the end offset and/or page for all sections that are still open at the end of the text:
    to_be_closed = [lvl for lvl in open_levels]
    for lvl in to_be_closed:
        lvl_idx = open_levels[lvl]
        if include_pages:
            sections[lvl_idx]["end_page"] = page
        if include_offsets:
            sections[lvl_idx]["end_offset"] = m.end()
        del open_levels[lvl]

    return sections

def search_in_text(search_term, text, use_regex=False, verbose=True,
        include_locations=False,
        include_section_titles=False, include_pages=True,
        section_titles=None, section_starts=None, include_hierarchy=True,
        page_numbers=None, page_ends=None, page_regex=r"PageV[^P]+P\d+[A-Z]?"):
    """Search a word or expression in the text

    NB: by default, search terms are considered not to be regular expressions;
    special characters will be escaped. If you want to search using regular
    expressions, set the `use_regex` parameter to `True`,
    or use the `search_regex_in_text` function instead.

    By default, this function prints and returns a list of matches for the
    search term.

    You can include the page number and/or section title(s) for each match
    by setting the `include_section_titles` and/or `include_pages` to `True`

    You can provide lists of section titles, page numbers, and their
    character offsets in the text; if you don't, the function will
    generate these lists itself if needed.

    Args:
        search_term (str): the regular expression pattern to be searched
        text (str): the text to be searched in
        use_regex (bool): if True, regular expression patterns will be used
        verbose (bool): if True, the matches will be printed
        include_locations (bool): if True, the character index where each
            match starts in the text will be included in the output
        include_section_titles (bool): if True, the titles of the sections
            in which the match was found will be included in the output
        include_pages (bool): if True, page numbers of the pages
            in which the match was found  will be included in the output
        section_titles (list): a list of all section titles in the text;
            can be extracted from the `get_sections` function
        section_starts (list): a list of the start position
            of each section title; can be extracted from the `get_sections` function
        include_hierarchy (bool): if True, the titles of the parent section
            will be included
        page_numbers (list): a list of all page numbers in the text;
            generated by the `get_page_numbers` function
        page_ends (list): a list of the positions of each page number;
            generated by the `get_page_numbers` function
        page_regex (str): regular expressions pattern describing
            the page number format used in the text

    Returns:
        list or list of lists ( [search_results[, locations][, sections][, pages]])

    Examples:
        >>> search_term = "شيراز"
        >>> text = '''### | فارس
        ... ### || قصبة فارس
        ... شيراز قصبة فارس.
        ... PageV01P001'''
        >>> matches = search_in_text(search_term, text)
        PageV01P001 شيراز
        >>> matches = search_in_text(search_term, text, verbose=False)
        >>> for match in matches:
        ...    print(match["match"])
        ...    print(match["page"])
        شيراز
        PageV01P001
        >>> results = search_in_text(search_term, text, verbose=False, \
                                           include_pages=True, \
                                           include_section_titles=True)
        >>> for result in results:
        ...     for title in result["parent_sections"]:
        ...         print(title)
        ...     print(result["section_title"])
        ...     print(result["match"])
        ...     print(result["page"])
        ### | فارس
        ### || قصبة فارس
        شيراز
        PageV01P001
    """
    # escape special characters if regex search is not used:
    if not use_regex:
        search_term = re.escape(search_term)
    
    return search_regex_in_text(
              search_term,
              text,
              verbose=verbose,
              include_locations=include_locations,
              include_section_titles=include_section_titles,
              include_pages=include_pages,
              section_titles=section_titles,
              section_starts=section_starts,
              include_hierarchy=include_hierarchy,
              page_numbers=page_numbers,
              page_ends=page_ends,
              page_regex=page_regex
              )

def search_regex_in_text(search_term, text, verbose=True, include_locations=False,
           include_section_titles=False, include_pages=True,
           section_titles=None, section_starts=None, include_hierarchy=True,
           page_numbers=None, page_ends=None, page_regex=r"PageV[^P]+P\d+[A-Z]?"):
    """Search a regular expression in the text

    By default, this function prints and returns a list of matches for the
    search term.

    You can include the page number and/or section title(s) for each match
    by setting the `include_section_titles` and/or `include_pages` to `True`

    You can provide lists of section titles, page numbers, and their
    character offsets in the text; if you don't, the function will
    generate these lists itself if needed.

    Args:
        search_term (str): the regular expression pattern to be searched
        text (str): the text to be searched in
        verbose (bool): if True, the matches will be printed
        include_locations (bool): if True, the character index where each
            match starts in the text will be included in the output
        include_section_titles (bool): if True, the titles of the sections
            in which the match was found will be included in the output
        include_pages (bool): if True, page numbers of the pages
            in which the match was found  will be included in the output
        section_titles (list): a list of all section titles in the text;
            generated by the `get_sections` function
        section_starts (list): a list of the start position
            of each section title; generated by the `get_sections` function
        include_hierarchy (bool): if True, the titles of the parent section
            will be included
        page_numbers (list): a list of all page numbers in the text;
            generated by the `get_page_numbers` function
        page_ends (list): a list of the positions of each page number;
            generated by the `get_page_numbers` function
        page_regex (str): regular expressions pattern describing
            the page number format used in the text

    Returns:
        list or tuple of lists ( (search_results[, locations][, sections][, pages]))

    Examples:
        >>> search_term = "شيراز"
        >>> text = '''### | فارس
        ... ### || قصبة فارس
        ... شيراز قصبة فارس.
        ... PageV01P001'''
        >>> matches = search_regex_in_text(search_term, text)
        PageV01P001 شيراز
        >>> matches = search_regex_in_text(search_term, text, verbose=False)
        >>> for match in matches:
        ...    print(match["match"])
        ...    print(match["page"])
        شيراز
        PageV01P001
        >>> results = search_regex_in_text(search_term, text, verbose=False, \
                                           include_pages=True, \
                                           include_section_titles=True)
        >>> for result in results:
        ...     for title in result["parent_sections"]:
        ...         print(title)
        ...     print(result["section_title"])
        ...     print(result["match"])
        ...     print(result["page"])
        ### | فارس
        ### || قصبة فارس
        شيراز
        PageV01P001
    """

    # get the required information on section titles and pages if not provided:
    if include_section_titles and section_starts is None:
        #section_titles, section_starts = get_sections(text, include_pages=False, include_hierarchy=include_hierarchy)
        sections = get_sections(text, include_offsets=True, include_hierarchy=include_hierarchy)
        section_titles = [d["title"] for d in sections]
        section_starts = [d["start_offset"] for d in sections]
        if include_hierarchy:
            section_parents = [d["parent_sections"] for d in sections]
    if include_pages and (page_numbers is None or page_ends is None):
        page_numbers, page_ends = get_page_numbers(text, page_regex=page_regex)

    # search for a word and get the section titles and page it was found in:
    #text_matches = []
    #pages = []
    #sections = []
    #locations = []
    results = []
    matches = re.finditer(search_term, text)
    for m in matches:
        d = dict()
        d["match"] = m.group()
        #d["match_object"] = m  # problem: if we include it, it's not json serializable
        loc = m.start()
        if include_locations:
            d["start_offset"] = m.start()
            d["end_offset"] = m.end()
            #locations.append(loc)
        if include_section_titles:
            section = get_section_title(loc, section_titles, section_starts)
            d["section_title"] = section
            if include_hierarchy:
                parent_sections = get_section_title(loc, section_parents, section_starts)
                #section = parent_sections + [section]
                d["parent_sections"] = parent_sections
            #sections.append(section)

        #text_matches.append(m.group())
        if include_pages:
            page = get_page_number(loc, page_numbers, page_ends)
            d["page"] = page
            #pages.append(page)

        results.append(d)

        if verbose:
            print_search_result(d, include_section_titles, include_hierarchy, include_pages)
    return results

def print_search_result(d, include_section_titles, include_hierarchy, include_pages):
    if include_section_titles:
        if include_hierarchy:
            for s in d["parent_sections"]:
                print(s)
        print(d["section_title"])
    if include_pages:
        print(d["page"], end=" ")
    print(d["match"])
    if include_section_titles:
        print("------")

def search_in_folder(search_term, folder,
        exclude_folders=exclude_folders,
        exclude_files=exclude_files, use_regex=False, verbose=True, include_locations=False,
        include_section_titles=False, include_pages=True,
        section_titles=None, section_starts=None, include_hierarchy=True,
        page_numbers=None, page_ends=None, page_regex=r"PageV[^P]+P\d+[A-Z]?"):
    """Search a word or expression in all text files in a folder

    NB: by default, search terms are considered not to be regular expressions;
    special characters will be escaped. If you want to search using regular
    expressions, set the `use_regex` parameter to `True`,
    or use the `search_regex_in_text` function instead.

    By default, this function prints and returns a list of matches for the
    search term.

    You can include the page number and/or section title(s) for each match
    by setting the `include_section_titles` and/or `include_pages` to `True`

    You can provide lists of section titles, page numbers, and their
    character offsets in the text; if you don't, the function will
    generate these lists itself if needed.

    Args:
        search_term (str): the regular expression pattern to be searched
        folder (str): path to the folder containing the texts to be searched in
        exclude_folders (list): list of folder names that should be excluded
            (default: the list of excluded folders defined in this module)
        exclude_files (list): list of file names that should be excluded
            (default: the list of excluded file names defined in this module)
        use_regex (bool): if True, regular expression patterns will be used
        verbose (bool): if True, the matches will be printed
        include_locations (bool): if True, the character index where each
            match starts in the text will be included in the output
        include_section_titles (bool): if True, the titles of the sections
            in which the match was found will be included in the output
        include_pages (bool): if True, page numbers of the pages
            in which the match was found  will be included in the output
        section_titles (list): a list of all section titles in the text;
            generated by the `get_sections` function
        section_starts (list): a list of the start position
            of each section title; generated by the `get_sections` function
        include_hierarchy (bool): if True, the titles of the parent section
            will be included
        page_numbers (list): a list of all page numbers in the text;
            generated by the `get_page_numbers` function
        page_ends (list): a list of the positions of each page number;
            generated by the `get_page_numbers` function
        page_regex (str): regular expressions pattern describing
            the page number format used in the text

    Returns:
        dictionary (
            keys: file path,
            values: list or tuple of lists ( (search_results[, locations][, sections][, pages]))

    Examples:
        > folder = r"D:/OpenITI/25Y_repos"
        > search_term = "شيراز"
        > results = search_in_folder(search_term, folder)
        > for fp, matches in results.items():
        ...    print(fn)
        ...    for match in matches:
        ...        print(match)
        > results = search_in_folder(search_term, folder, include_pages=True)
        > for fp, (matches, pages) in results.items():
        ...    print(fn)
        ...    for match, page in zip(matches, pages):
        ...        print(match)
        ...        print(page)
    """
    # escape special characters if regex search is not used:
    if not use_regex:
        search_term = re.escape(search_term)
    
    return search_regex_in_folder(
              search_term,
              folder,
              verbose=verbose,
              include_locations=include_locations,
              include_section_titles=include_section_titles,
              include_pages=include_pages,
              section_titles=section_titles,
              section_starts=section_starts,
              include_hierarchy=include_hierarchy,
              page_numbers=page_numbers,
              page_ends=page_ends,
              page_regex=page_regex
              )



def search_regex_in_folder(search_term, folder,
        exclude_folders=exclude_folders,
        exclude_files=exclude_files,
        verbose=True, include_locations=False,
        include_section_titles=False, include_pages=True,
        section_titles=None, section_starts=None, include_hierarchy=True,
        page_numbers=None, page_ends=None, page_regex=r"PageV[^P]+P\d+[A-Z]?"):
    """Search a regular expression in the text

    By default, this function prints and returns a list of matches for the
    search term.

    You can include the page number and/or section title(s) for each match
    by setting the `include_section_title` and/or `include_pages` to `True`

    You can provide lists of section titles, page numbers, and their
    character offsets in the text; if you don't, the function will
    generate these lists itself if needed.

    Args:
        search_term (str): the regular expression pattern to be searched
        folder (str): path to the folder containing the texts to be searched in
        exclude_folders (list): list of folder names that should be excluded
            (default: the list of excluded folders defined in this module)
        exclude_files (list): list of file names that should be excluded
            (default: the list of excluded file names defined in this module)
        verbose (bool): if True, the matches will be printed
        include_locations (bool): if True, the character index where each
            match starts in the text will be included in the output
        include_section_titless (bool): if True, the titles of the sections
            in which the match was found will be included in the output
        include_pages (bool): if True, page numbers of the pages
            in which the match was found  will be included in the output
        section_titles (list): a list of all section titles in the text;
            generated by the `get_sections` function
        section_starts (list): a list of the start position
            of each section title; generated by the `get_sections` function
        include_hierarchy (bool): if True, the titles of the parent section
            will be included
        page_numbers (list): a list of all page numbers in the text;
            generated by the `get_page_numbers` function
        page_ends (list): a list of the positions of each page number;
            generated by the `get_page_numbers` function
        page_regex (str): regular expressions pattern describing
            the page number format used in the text

    Returns:
        dictionary (
            keys: file path,
            values: list or tuple of lists ( (search_results[, locations][, sections][, pages]))

    Examples:
        > folder = r"D:/OpenITI/25Y_repos"
        > search_term = "*.شيراز.*"
        > results = search_regex_in_folder(search_term, folder)
        D:/OpenITI/25Y_repos/0075AH/data/0068CabdAllahIbnCabbas/0068CabdAllahIbnCabbas.GharibQuran/0068CabdAllahIbnCabbas.GharibQuran.Zaydiyya0000300-ara1
        PageV01P096 ~~التنوخي، عن القاسم بن عساكر، أنبأنا أبو نصر محمد بن عبد الله الشيرازي،
        D:/OpenITI/25Y_repos/0125AH/data/0110IbnSirin/0110IbnSirin.MuntakhabKalamFiTafsirAhlam/0110IbnSirin.MuntakhabKalamFiTafsirAhlam.JK006856-ara2
        PageV01P437 ~~المعروف ممن لا خير فيه ، والشيراز استماع كلام من نسوة والإنفحة مال مع
        ...
        > results = search_regex_in_folder(search_term, folder, verbose=False, include_section_titles=True)
        > for fp, file_results in results.items():
        ...     print(fp)
        ...     for r in file_results:
        ...         print(r["section_title"])
        ...         print(r["page"], r["match"])
        D:/OpenITI/25Y_repos/0075AH/data/0068CabdAllahIbnCabbas/0068CabdAllahIbnCabbas.GharibQuran/0068CabdAllahIbnCabbas.GharibQuran.Zaydiyya0000300-ara1
        PageV01P096 ~~التنوخي، عن القاسم بن عساكر، أنبأنا أبو نصر محمد بن عبد الله الشيرازي،
        D:/OpenITI/25Y_repos/0125AH/data/0110IbnSirin/0110IbnSirin.MuntakhabKalamFiTafsirAhlam/0110IbnSirin.MuntakhabKalamFiTafsirAhlam.JK006856-ara2
        PageV01P437 ~~المعروف ممن لا خير فيه ، والشيراز استماع كلام من نسوة والإنفحة مال مع
        ...
    """
    files = get_all_text_files_in_folder(folder, excluded_folders=exclude_folders,
                                         exclude_files=exclude_files)
    d = dict()
    for fp in files:
        with open(fp, mode="r", encoding="utf-8") as file:
            text = file.read()
        r = search_regex_in_text(
              search_term,
              text,
              verbose=False,
              include_locations=include_locations,
              include_section_titles=include_section_titles,
              include_pages=include_pages,
              section_titles=section_titles,
              section_starts=section_starts,
              include_hierarchy=include_hierarchy,
              page_numbers=page_numbers,
              page_ends=page_ends,
              page_regex=page_regex
              )
        if r:
            d[fp] = r
            if verbose:
                print(fp)
                for match_d in r:
                    print_search_result(match_d, include_section_titles, include_hierarchy, include_pages)
    return d

if __name__ == "__main__":
    search_term = "شيراز"
    text = '''### | فارس
    ### || قصبة فارس
    شيراز قصبة فارس.
    PageV01P001'''
    
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
