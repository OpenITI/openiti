"""Functions to read and write yaml files.

OpenITI metadata is stored in yaml files.
(yaml stands for "yet another markup language"
or "YAML ain't markup language")

NB: In correctly formatted OpenITI yml files,
    - keys (lemmata) should always:
        * start with a 2-digit number (for sorting the keys);
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

This module contains functions to convert YAML to Python dictionary format
and vice versa, fix broken YAML strings and check the completeness of YML files.

The ymlToDic and dicToYML functions will retain
new lines before bullet lists (in which bullets are `*` or `-`),
even when the argument `reflow` is set to True.
"""

import os
import re
import textwrap

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    sys.path.append(root_folder)

from openiti.helper.templates import author_yml_template, book_yml_template, \
                                     version_yml_template, location_yml_template, \
                                     manuscript_yml_template, transcription_yml_template

all_template_strings = [
    author_yml_template,
    book_yml_template,
    version_yml_template,
    location_yml_template,
    manuscript_yml_template,
    transcription_yml_template
]

# set of yml keys that should not be taken into account when calculating
# completeness of a yml file:
exclude_keys = set(["00#AUTH#URI######:",
                    "00#BOOK#URI######:",
                    "00#VERS#LENGTH###:", "00#VERS#CLENGTH##:", "00#VERS#URI######:",
                    "00#LOC#URI#######:",
                    "00#MS#URI########:",
                    "00#TRNS#LENGTH###:", "00#TRNS#CLENGTH##:", "00#TRNS#URI######:",])

def ymlToDic(yml_str, fix_yml_errors_silently=False, yml_fp="", reflow=False):
    """Convert a yml string into a dictionary.

    NB: in order to be read correctly, OpenITI yml keys (lemmata) should always:
        * start with a 2-digit number (for sorting the keys);
        * contain at least one hash (#)
        * end with a colon (:)
        * be free of any other non-letter/numeric characters

        Values may contain any character, including colons.

        In multiline values, every new line should be indented with 4 spaces;
        multiline values may use double new lines and
        bullet lists (using `*` or `-` for items) for clarity.

    Args:
        yml_str (str): a yml string.
        fix_yml_errors_silently (bool): if True, faulty yml files will
            be fixed and saved to `yml_fp`. If False, an attempt will be made to
            read the yml string but it will not be saved.
        yml_fp (str): path to the yaml file (optional); if defined,
            faulty yml files will be fixed and saved to `yml_fp`
            if `fix_yml_errors_silently` is set to True.
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
        return {}
    
    # normalize whitespace:
    data = re.sub(r"\r\n", "\n", yml_str)
    data = re.sub(r"\t", "    ", yml_str)
    
    # remove empty lines and spaces at end and beginning of string:
    data = data.strip() 

    # keep empty lines in multiline values:
    data = re.sub(r"\n( *)\n+( +)", r"¶\2¶\2", data)

    # keep line breaks before bullet list items in multiline values:
    data = re.sub(r"[\n¶]( +[*-])", r"¶\1", data)
    
    if reflow: # remove other line breaks:
        data = re.sub(r"-\n+ +", "-", data)
        data = re.sub(r"\n+ +", " ", data)
    else:      # keep line breaks:
        data = re.sub(r"\n( +)", r"¶\1", data)

    # split into key-value pairs and convert to dictionary:
    data = data.split("\n")
    dic = dict()
    for d in data:
        spl = re.split(r"^((?:#+\w+|\w+#+)[\w#]*:+)", d, 1)
        try:
            dic[spl[1]] = spl[2].strip()
        except:
            return fix_broken_yml(yml_fp, yml_str=yml_str,
                                 execute=fix_yml_errors_silently,
                                 silent=fix_yml_errors_silently,
                                 reflow=reflow)
    return dic


def readYML(fp, reflow=False, fix_yml_errors_silently=False):
    """Read a yml file and convert it into a dictionary.

    Args:
        fp (str): path to the yml file.
        reflow (bool): if set to False, the original layout
            (line endings, indentation) of the yml file will be preserved;
            in the output dictionary values, new line characters will be replaced with ¶.
            if set to True, new line characters will be removed
            (except double line breaks and line breaks in bullet lists)
            and the indentation and line length will be standardized.
        fix_yml_errors_silently (bool): if True, faulty yml files will
            be fixed and saved. If False, an attempt will be made to
            read the yml file but it will not be saved.
            
    Returns:
        (dict): dictionary representation of the yml key-value pairs

    Examples:
##        >>> fp = "D:/OpenITI/25Y_repos/0450AH/data/0429AbuMansurThacalibi/0429AbuMansurThacalibi.AhsanMaSamictu/0429AbuMansurThacalibi.AhsanMaSamictu.Shamela0025011-ara1.yml"
##        >>> readYML(fp)
##        {}
    """
    with open(fp, "r", encoding="utf-8") as file:
        yml_s = file.read()
    return ymlToDic(yml_s, yml_fp=fp, reflow=reflow,
                    fix_yml_errors_silently=fix_yml_errors_silently)           
           
def dicToYML(dic, max_length=80, reflow=True, break_long_words=False):
    """Convert a dictionary into a yml string.

    NB: use the pilcrow (¶) to force a line break within dictionary values.

    Args:
        dic (dict): a dictionary of key-value pairs.
        max_length(int): the maximum number of characters a line should contain.
        reflow (bool): if False, the original layout (line endings, indentation)
            of the yml string will be preserved. if set to True,
            the indentation and line length will be standardized.
        break_long_words (bool): if False, long words will be kept on one line
            (if set to True, this might break URLs!)
            
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
            * bullet point 1\\n\
            * bullet point 2\
        '.replace("        ", "") # remove Python indentation for doctest
        >>> dicToYML(yml_dic, max_length=35, reflow=True) == yml_str
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
                item = "{} {}".format(k.strip(), str(v).strip())
            else:
                item = "{}: {}".format(k.strip(), str(v).strip())

            if reflow:
                # split the item on bullet points into lines:
                lines = re.split(r"\s*¶(?=\s*[*-])", item)

                # reflow each line separately:
                reflowed_lines = []
                for i, line in enumerate(lines):
                    indent = "    "
                    # remove existing line breaks:
                    line = re.sub(r"\s*¶\s*", " ", line)
                    # add indentation if the line does not have it
                    # (except for the first line)
                    if i != 0 and not line.startswith(" "):
                        line = indent + line
                    # define the indentation level:
                    indent = "\n" + re.findall("^ *", line)[0]
                    if len(indent) == 1:
                        indent += "    "
                    # if the line starts with a bullet point,
                    # indent the following sublines by two extra spaces:
                    if line.strip().startswith(("-", "*")):
                        indent += "  "
                    # Never break a URI:
                    if "#URI#" in line:
                        reflowed_lines.append(line)
                    # subdivide the value into sublines:
                    else:
                        sublines = textwrap.wrap(line.rstrip(), max_length-len(indent),
                                                 break_long_words=break_long_words,
                                                 break_on_hyphens=False)
                        reflowed_line = indent.join(sublines)
                        # fix broken URLs (unnecessary when break_long_words is set to False):
                        #reflowed_line = re.sub(r"(http[^\n\s]+-)\n( +)([^\n\s]+) ",
                        #                       r"\n\2\1\3\n\2", reflowed_line)
                        reflowed_lines.append(reflowed_line.rstrip())
                lines = reflowed_lines
            else:
                lines = re.split(r"\s*¶", item)

            # merge the lines, making sure that they are indented:
            indented_lines = [lines[0]]
            for line in lines[1:]:
                if not line.startswith(" "):
                    line = "    " + line
                indented_lines.append(line)
            item = "\n".join(indented_lines)
            data.append(item)

    return "\n".join(sorted(data))

def fix_broken_yml(fp, yml_str="", execute=True, silent=False, reflow=False):
    """Fix a yml file that is broken because
    (1) a line does not start with a valid key or space (s)
    or (2) the colon after the key is absent

    Args:
        fp (str): path to the broken yml file
        yml_str (str): broken yml string.
        execute (bool): if True, the fixed yml string will be
            saved to `fp`.
        silent (bool): if True, user's judgment about the fix
            will be asked before it is saved
        reflow (bool): if set to False, the original layout
            (line endings, indentation) of the yml string will be preserved;
            if set to True, the indentation and line length
            will be standardized.

    Examples:
        >>> yml_str = "10#AUTH#ISM####AR missing colon"
        >>> fix_broken_yml(None, yml_str=yml_str, silent=True)
        {'10#AUTH#ISM####AR:': 'missing colon'}
        >>> yml_str = "10#AUTH#ISM####AR: no indent no indent\\nno indent"
        >>> fix_broken_yml(None, yml_str=yml_str, silent=True)
        {'10#AUTH#ISM####AR:': 'no indent no indent¶no indent'}
        >>> yml_str = "no valid key at all"
        >>> fix_broken_yml(None, yml_str=yml_str, silent=True)
        {}
        >>> empty_yml_str = ""
        >>> fix_broken_yml(None, yml_str=empty_yml_str, silent=True)
        {}

    Returns:
        dict
    """
    if yml_str:
        data = yml_str
    else:
        try:
            with open(fp, mode="r", encoding="utf-8") as file:
                data = file.read()
        except:
            return {}

    # create a list of key-value strings
    key_values = []
    current = []
    key_regex = r"^(\d\d#[#\w]+):*"  # colon will be removed from key!
    for line in data.splitlines():
        line = line.rstrip()
        if re.findall(key_regex, line):
            # finalize the current key-value line and initialize a new one:
            if current:
                key_values.append("¶".join(current))
            current = []
        #elif not line.startswith(" "):
        #    print("NO INDENTATION!", line)
        current.append(line.rstrip())
    if current:
        key_values.append("¶".join(current))

    # build the dictionary by breaking the strings into keys and values:
    #yml_d = {re.findall(key_regex, line)[0]+":" : re.sub(key_regex, "", line).strip()
    #         for line in key_values}
    yml_d = dict()
    for line in key_values:
        try:
            key = re.findall(key_regex, line)[0]
            val = re.sub(key+":*", "", line).strip()
            if re.findall(key_regex, val):
                if not silent:
                    print("WARNING: is there a YML key in this value?")
                    print(val)
            yml_d[key+":"] = val
        except:
            if not silent:
                print("No valid key in", line)

    if not silent:
        print("\noriginal yml file with errors:\n")
        print(data)
        print("\nAttempt to solve the issue:\n")
        print(dicToYML(yml_d, reflow=reflow))
    
    if not fp:
        return yml_d

    if execute and (silent or input("\nAccept change? Y/N: ").lower() == "y"):
        with open(fp, mode="w", encoding="utf-8") as file:
            file.write(dicToYML(yml_d, reflow=reflow))
    else:
        print("\n-> Not writing the proposed change to the yml file. Please review YML file manually")
    return yml_d


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
    import doctest
    doctest.testmod()
