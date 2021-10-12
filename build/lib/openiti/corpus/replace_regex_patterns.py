"""
Replaces regular expression patterns in OpenITI texts.
"""
import os
import re
import sys

if __name__ == '__main__':
    main_folder = input("Enter the path to the folder containing OpenITI texts: ")
    overwrite = input("Do you want to overwrite the files (y/n)? ")
    # pat_type = input("Remove only OpenITI mARkdown (y) or a specific regular expression patterns (n)? ")
    pats = {}
    # if pat_type.lower() == "y":
    #     rm_pats.append(" *### \|+ ")
    # elif pat_type.lower() == "n":
    conti = "y"
    while conti.lower() == 'y':
        pat = input("Enter the custom pattern to find: ")  #" *### \|+ "
        replace = input("Enter the custom pattern to replace: ")
        pats[pat] = replace
        conti = input("more patterns to remove (y/n)? ").lower()
    # page_nr_pat = "PageV\d+P\d+"

    if len(sys.argv) > 0:
        if not os.path.exists(main_folder):
            print("invalid path: ", main_folder)
        else:
            # process all texts
            for root, dirs, files in os.walk(main_folder):
                for file in files:
                    if re.search("^\d{4}\w+\.\w+\.\w+-[a-z]{3}\d{1}(\.(mARkdown|inProgress|completed))?$", file):
                        path_full = os.path.join(root, file)
                        with open(path_full, "r", encoding="utf8") as f1:
                            text = f1.read()
                            # remove the specified patterns in the texts
                            for pat in pats:
                                text = re.sub(pat, pats[pat], text)
                        if overwrite.lower() == "y":
                            write_path = path_full
                        else:
                            write_path = path_full + "_replaced"
                        with open(write_path, "w", encoding="utf8") as f9:
                            f9.write(text)
