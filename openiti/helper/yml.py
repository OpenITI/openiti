"""Functions to read and write yaml files.

OpenITI metadata is stored in yaml files.
(yaml stands for "yet another markup language")

NB: In correctly formatted OpenITI yml files,
    - keys (lemmata) should always:
        * contain at least one hash (#)
        * end with a colon (:)
        * be free of any other non-letter/numeric characters

    - Values:
        * may contain any character, including colons
          and new line characters
          (only something that looks like a yml key
          (i.e., a combination of letters and hashes ending with a colon)
          should be avoided at the beginning of a line)
        * mutiline values should be indented with 4 spaces

The ymlToDic and dicToYML functions will retain double new lines
and new lines before bullet lists (in which bullets are `*` or `-`)
"""

import os
import re
import textwrap

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    sys.path.append(root_folder)

from openiti.helper.templates import author_yml_template, book_yml_template, \
                                     version_yml_template

all_template_strings = [author_yml_template, book_yml_template, version_yml_template]


# set of yml keys that should not be taken into account when calculating
# completeness of a yml file:
exclude_keys = set(["00#AUTH#URI######:", "00#BOOK#URI######:",
                    "00#VERS#LENGTH###:", "00#VERS#CLENGTH##:", "00#VERS#URI######:"])



def ymlToDic(yml_str, reflow=False, yml_fp=""):
    """Convert a yml string into a dictionary.

    NB: in order to be read correctly, OpenITI yml keys (lemmata) should always:
        * contain at least one hash (#)
        * end with a colon (:)
        * be free of any other non-letter/numeric characters

        Values may contain any character, including colons.

        In multiline values, every new line should be indented with 4 spaces;
        multiline values may use double new lines and
        bullet lists (using `*` or `-` for items) for clarity.

    Args:
        yml_str (str): a yml string.
        reflow (bool): if set to False, the original layout
            (line endings, indentation) of the yml file
            will be preserved (useful for files containing bullet lists etc.);
            in the output string, new line characters will be replaced with ¶.
            if set to True, new line characters will be removed
            (except double line breaks and line breaks in bullet lists)
            and the indentation and line length will be standardized.

    Returns:
        (dict): dictionary representation of the yml key-value pairs

    Examples:
        >>> from yml import ymlToDic
        >>> yml_str = "\
00#BOOK#URI######: 0845Maqrizi.Muqaffa\\n\
90#BOOK#COMMENT##: multiline value; presence\\n\
    of colons: not a problem\\n\\n\\n\
".replace("        ", "") # remove Python indentation for doctest
        >>> yml_dic = {'00#BOOK#URI######:': '0845Maqrizi.Muqaffa',\
                       '90#BOOK#COMMENT##:': 'multiline value; presence of colons: not a problem'}
        >>> ymlToDic(yml_str, reflow=True) == yml_dic
        True
        
    """
    if yml_str.strip() == "":
        #raise Exception(yml_fp, "Empty YML file!")
        return {}
    
    # normalize new line characters:
    data = re.sub("\r\n", "\n", yml_str)
    
    # remove empty lines and spaces at end and beginning of string:
    data = data.strip() 

    # keep empty lines in multiline values:
    data = re.sub("\n([ \t]*)\n+([ \t]+)", r"¶\2¶\2", data)

    # keep linebreaks before bullet list items in multiline values:
    data = re.sub(r"[\n¶]([ \t]+[\*\-])", r"¶\1", data)
    
    if reflow: # remove other line breaks:
        data = re.sub(r"-\n+[ \t]+", "-", data)
        data = re.sub(r"\n+[ \t]+", " ", data)
    else: # keep line breaks:
        data = re.sub(r"\n([ \t]+)", r"¶\1", data)

    # split into key-value pairs and convert to dictionary:

    data = data.split("\n")
    dic = dict()
    for d in data:
        spl = re.split(r"^((?:#+\w+|\w+#+)[\w#]*:+)", d, 1)
        try:
            dic[spl[1]] = spl[2].strip()
        except:
            raise Exception(yml_fp, "no valid yml key in line", d)

    return dic


def readYML(fp, reflow=False):
    """Read a yml file and convert it into a dictionary.

    Args:
        fp (str): path to the yml file.
        reflow (bool): if set to False, the original layout
            (line endings, indentation) of the yml file
            will be preserved (useful for files containing bullet lists etc.);
            in the output string, new line characters will be replaced with ¶.
            if set to True, new line characters will be removed
            (except double line breaks and line breaks in bullet lists)
            and the indentation and line length will be standardized.
            
    Returns:
        (dict): dictionary representation of the yml key-value pairs

    Examples:
##        >>> fp = "D:/London/OpenITI/25Y_repos/0450AH/data/0429AbuMansurThacalibi/0429AbuMansurThacalibi.AhsanMaSamictu/0429AbuMansurThacalibi.AhsanMaSamictu.Shamela0025011-ara1.yml"
##        >>> readYML(fp)
##        {}
    """
    with open(fp, "r", encoding="utf-8") as file:
        s = file.read()
        try:
           return ymlToDic(s, yml_fp=fp)
        except Exception as e:
           print(fp)
           print(e)


def dicToYML(dic, max_length=80, reflow=True, break_long_words=False):
    """Convert a dictionary into a yml string.

    NB: use the pilcrow (¶) to force a line break within dictionary values.

    Args:
        dic (dict): a dictionary of key-value pairs.
        max_length(int): the maximum number of characters a line should contain.
        reflow (bool): if set to False, the original layout
            (line endings, indentation) of the yml string
            will be preserved (useful for files containing bullet lists etc.);
            if set to True, the indentation and line length
            will be standardized.
        break_long_words (bool): if False, long words will be kept on one line
            
    Returns:
        (str): yml string representation of the dic's key-value pairs

    Examples:
        >>> yml_dic = {'00#BOOK#URI######:': '0845Maqrizi.Muqaffa',\
                       '90#BOOK#COMMENT##:': 'multiline value; presence of colons: not a problem¶¶    * bullet point 1¶    * bullet point 2'}
        >>> yml_str = '\
        00#BOOK#URI######: 0845Maqrizi.Muqaffa\\n\
        90#BOOK#COMMENT##: multiline\\n\
            value; presence of colons: not\\n\
            a problem\\n\
        \\n\
            * bullet point 1\\n\
            * bullet point 2\
        '.replace("        ", "") # remove Python indentation for doctest
        >>> dicToYML(yml_dic, max_length=30, reflow=True) == yml_str
        True
        
        >>> yml_str = '\
        00#BOOK#URI######: 0845Maqrizi.Muqaffa\\n\
        90#BOOK#COMMENT##: multiline value; presence of colons: not a problem\\n\
            \\n\
            * bullet point 1\\n\
            * bullet point 2\
        '.replace("        ", "") # remove Python indentation for doctest
        >>> dicToYML(yml_dic, max_length=30, reflow=False) == yml_str
        True
    """
    data = []
    if dic:
        for k,v in dic.items():
            if k.strip().endswith(":"):
                i = "{} {}".format(k.strip(), str(v).strip())
            else:
                i = "{}: {}".format(k.strip(), str(v).strip())

            # split long values into indented multiline values:

            if "#URI#" not in i:

                lines = re.split("¶", i)

                if len(lines) > 1:
                    lines = [lines[0]] + [line if line.startswith((" ", "\t")) else "    "+line
                                          for line in lines[1:]]
                
                if reflow:
                    lines = ["\n    ".join(textwrap.wrap(line.strip(), max_length,
                                                         break_long_words=break_long_words))
                             for line in lines]

                i = "\n    ".join(lines)
            data.append(i)

    return "\n".join(sorted(data))

def fix_broken_yml(fp, execute=True):
    """Fix a yml file that is broken because
    (1) a line does not start with a valid key or space
    or (2) the colon after the key is absent

    Args:
        fp (str): path to the broken yml file
        execute (bool): if False, user's judgment about the fix
             will be asked before the fix is implemented

    Returns:
        None or yml_d
    """
    with open(fp, mode="r", encoding="utf-8") as file:
        data = file.read()
    key_lines = []
    current = []
    for line in data.splitlines():
        if re.findall("^\d\d#[#\w]{14}:?", line):
            if current:
                key_lines.append(current)
                current = []
        current.append(line.strip())
    if current:
        key_lines.append(current)
    key_lines = ["¶".join(line) for line in key_lines]
    key_regex = "^(\d\d#[#\w]{14}):?"
    yml_d = {re.findall(key_regex, line)[0]+":" : re.sub(key_regex, "", line).strip()
             for line in key_lines}
    print("original yml file:\n")
    print(data)
    print("\nAttempt to solve the issue:\n")
    print(dicToYML(yml_d))
    if execute or input("\nAccept change? Y/N: ").lower() == "y":
        return yml_d
    else:
        print("Aborting change. Please review YML file manually")
        return


def check_yml_completeness(fp, exclude_keys=exclude_keys, templates=all_template_strings):
    """Check how much of a yml file's fields have been filled in.

    Returns a list of all keys in the yml file that do not contain
    default values or are empty, and a list of all relevant keys.

    NB: some fields are filled automatically (e.g., the URI field,
    token count, etc.), so you can choose to exclude such fields
    from the check.

    Use this function if you are interested in which fields exactly
    are not filled in; if you are only interested in the percentage,
    use the `check_yml_completeness_pct` function instead.
    
    Args:
        fp (str): path to the yml file
        exclude_keys (set): do not take these keys into account when 
        templates (list): list of templates from which the default values are taken

    Returns:
        tuple (list of keys that contain non-default values,
               list of relevant keys)
    """
    # convert the yml file to a dictionary:
    yml_d = readYML(fp)
    
    # create a dictionary containing the default values for all yml keys:
    defaults = dict()
    for t in templates:
        #defaults.update(ymlToDic(t))
        for k, v in ymlToDic(t).items():
            if not k in defaults:
                defaults[k] = set([""])
            defaults[k].add(v)
        
    # check for all relevant yml keys whether they contain default values:
    relevant_keys = [k for k in yml_d if k not in exclude_keys]
    non_default_vals = []
    for k in relevant_keys:
        try:
            if yml_d[k] not in defaults[k]:
                non_default_vals.append(k)
        except:
            print("non-default key in", os.path.basename(fp), ":", k)
            non_default_vals.append(k)
                
    return (non_default_vals, relevant_keys)
        
def check_yml_completeness_pct(fp, exclude_keys=exclude_keys,
                               templates=all_template_strings):
    """Check which proportion of the relevant fields in a yml file have been filled.

    NB: some fields are filled automatically (e.g., the URI field,
    token count, etc.), so you can choose to exclude such fields
    from the check.

    Use this function if you are only interested in the percentage
    of fields filled in; if you are interested in which fields exactly
    are not filled in, use the `check_yml_completeness` function instead.
    
    Args:
        fp (str): path to the yml file
        exclude_keys (set): do not take these keys into account when 
        templates (list): list of templates from which the default values are taken

    Returns:
        float (percentage of the fields filled in)
    """
    non_default_vals, relevant_keys = check_yml_completeness(fp, exclude_keys=exclude_keys)
    return len(non_default_vals) / len(relevant_keys) 


if __name__ == "__main__":
    yml_fp = "../../../../../OpenITI/Github_clone/0875AH/data/0852IbnHajarCasqalani/0852IbnHajarCasqalani.InbaGhumr/0852IbnHajarCasqalani.InbaGhumr.Shamela0026317-ara1.yml" 
#    with open(yml_fp, mode="r", encoding="utf-8") as file:
#        t = file.read()
#    print(t)
#    input("continue?")
#    t = t.replace("\xa0", " ")
#    print(t)
#    input("continue?")
#    with open(yml_fp, mode="w", encoding="utf-8") as file:
#        file.write(t)
#    yml_dic = readYML(yml_fp)
#    print(yml_dic)
#    yml_str = dicToYML(yml_dic)
#    print(yml_str)
#    input("continue?")
    yml_str = """\
key1: short description
key2: longer description with : :: colons
key3: longer multiline description longer multiline description longer multiline description
    longer multiline description

    longer multiline description after double line break
    longer multiline description

    * bullet item 1
    * bullet item 2
"""
    print("do not reflow:")
    print(ymlToDic(yml_str, reflow=False))
    print(dicToYML(ymlToDic(yml_str, reflow=False), reflow=False, max_length=25))
    print("*******************")
    print("reflow:")
    print(ymlToDic(yml_str, reflow=True))
    print(dicToYML(ymlToDic(yml_str, reflow=True), reflow=True, max_length=25))
    d = {'key2:': 'longer description with : :: colons',
         'key1:': 'short description',
         'key3:': 'longer multiline description longer multiline description longer multiline description longer multiline description¶¶longer multiline description after double line break longer multiline description¶    ¶    * bullet item 1¶    * bullet item 2'}
    print("*******************")
    print(dicToYML(d, reflow=True, max_length=25))
    print("*******************")
    print(dicToYML(d, reflow=False, max_length=25))
    import doctest
    input()

#    doctest.testmod()
