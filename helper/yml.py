"""Functions to read and write yaml files.

OpenITI metadata is stored in yaml files.
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
    """Convert a yml string into a dictionary"""
    data = re.sub("\n+$", "", yml_str)
    data = re.sub("-\n[ \t]+", "-", data)
    data = re.sub("\n[ \t]+", " ", data)
    data = data.split("\n")
    dic = dict()
    for d in data:
        d = re.split(r"(^[\w#]+:)", d)
        dic[d[1]] = d[2].strip()
    return dic


def readYML(fp):
    """Read a yml file and convert it into a dictionary"""
    with open(fp, "r", encoding="utf8") as file:
        return ymlToDic(file.read())


def dicToYML(dic):
    """Convert a dictionary into a yml string"""
    data = []
    for k,v in dic.items():
        if k.endswith(":"):
            i = k + " " + str(v)
        else:
            i = k + ": " + str(v)
        if "#URI#" in i:
            pass
        else:
            i = "\n    ".join(textwrap.wrap(i, 72))
        data.append(i)

    data = "\n".join(sorted(data))
    return(data)
