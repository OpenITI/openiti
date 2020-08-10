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
"""

import re
import textwrap

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    sys.path.append(root_folder)

from openiti.helper.templates import author_yml_template, book_yml_template, \
                                     version_yml_template



def ymlToDic(yml_str):
    """Convert a yml string into a dictionary.

    NB: in order to be read correctly, OpenITI yml keys (lemmata) should always:
        * contain at least one hash (#)
        * end with a colon (:)
        * be free of any other non-letter/numeric characters

        Values may contain any character, including colons
        and new line characters
        (only something that looks like a yml key
        (i.e., a combination of letters and hashes ending with a colon)
        should be avoided at the beginning of a line)

        In principle, mutiline values should be indented with 4 spaces,
        but unindented multiline values will be parsed without a problem.

    Args:
        yml_str (str): a yml string.

    Returns:
        (dict): dictionary representation of the yml key-value pairs

    Examples:
        >>> from yml import ymlToDic
        >>> yml_str = "\
00#BOOK#URI######: 0845Maqrizi.Muqaffa\\n\
90#BOOK#COMMENT##: multiline value; missing-\\n\
indentation: (and presence\\n\
of colons): not a problem\\n\\n\\n\
".replace("        ", "") # remove Python indentation for doctest
        >>> yml_dic = {'00#BOOK#URI######:': '0845Maqrizi.Muqaffa',\
                       '90#BOOK#COMMENT##:': 'multiline value; missing-indentation: (and presence of colons): not a problem'}
        >>> ymlToDic(yml_str) == yml_dic
        True
    """
    if yml_str.strip() == "":
        raise Exception("Empty YML file!")
        return {}
    
    # remove new lines (and indentation) except before yaml keys:

    data = re.sub("\n+$", "", yml_str)
    data = re.sub("-\n[ \t]+", "-", data)
    data = re.sub("\n[ \t]+", " ", data)
    #data = re.sub("-\n+(?!\w*#+[\w#]+:)[ \t]*", "-", yml_str)
    #data = re.sub("\n+(?!\w*#+[\w#]+:)[ \t]*", " ", data).strip()

    # split into key-value pairs and convert to dictionary:

    data = data.split("\n")
    dic = dict()
    for d in data:
        spl = re.split(r"(^[\w#]+:)", d, 1)
        try:
            dic[spl[1]] = spl[2].strip()
        except:
            raise Exception("no valid yml key in line", d)

    return dic


def readYML(fp):
    """Read a yml file and convert it into a dictionary.

    Args:
        fp (str): path to the yml file.

    Returns:
        (dict): dictionary representation of the yml key-value pairs

    Examples:
        >>> fp = "D:/London/OpenITI/25Y_repos/0450AH/data/0429AbuMansurThacalibi/0429AbuMansurThacalibi.AhsanMaSamictu/0429AbuMansurThacalibi.AhsanMaSamictu.Shamela0025011-ara1.yml"
        >>> readYML(fp)
        {}
    """
    with open(fp, "r", encoding="utf8") as file:
        return ymlToDic(file.read())


def dicToYML(dic, max_length=72):
    """Convert a dictionary into a yml string.

    Args:
        dic (dict): a dictionary of key-value pairs.
        max_length(int): the maximum number of characters a line should contain.

    Returns:
        (str): yml strin representation of the dic's key-value pairs

    Examples:
        >>> yml_dic = {'00#BOOK#URI######:': '0845Maqrizi.Muqaffa',\
                       '90#BOOK#COMMENT##:': 'multiline value; missing-indentation: (and presence of colons): not a problem'}
        >>> yml_str = '\
        00#BOOK#URI######: 0845Maqrizi.Muqaffa\\n\
        90#BOOK#COMMENT##: multiline\\n\
            value; missing-indentation:\\n\
            (and presence of colons): not\\n\
            a problem\
        '.replace("        ", "") # remove Python indentation for doctest
        >>> dicToYML(yml_dic, max_length=30) == yml_str
        True
    """
    data = []
    for k,v in dic.items():
        if k.strip().endswith(":"):
            i = "{} {}".format(k.strip(), str(v).strip())
        else:
            i = "{}: {}".format(k.strip(), str(v).strip())

        # split long values into indented multiline values:

        if "#URI#" not in i:
            i = "\n    ".join(textwrap.wrap(i, max_length))
        data.append(i)

    return "\n".join(sorted(data))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
