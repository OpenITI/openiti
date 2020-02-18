# Copies all data from the XXXXAH directories to a single directory in order to publish a version of OpenITI.

import os
import shutil
import sys
import re


def copy_ah_data(source_dir, dest_dir):
    # All XXXXAH direcortories
    ah_dirs = os.listdir(source_dir)
    for ad in ah_dirs:
        # Get the path to the "data" folder (in each XXXXAH dir)
        data_path = os.path.join(source_dir, ad, "data")
        # If the data directory exists (for cases the "data" dir is not available, like 1475AH)
        if os.path.exists(data_path):
            # Get the list of directories in "data" directory
            cur_dirs = os.listdir(data_path)
            # Copy the dirs in "/data"
            for cpy_d in cur_dirs:
                # Source is the path to the current folder in data folder (cpy_d) that will be copied,
                # Target is a join of the target path (given as input) and the current folder (cpy_d)
                shutil.copytree(os.path.join(data_path, cpy_d), os.path.join(dest_dir, cpy_d))
                for root, dirs, files in os.walk(os.path.join(dest_dir, cpy_d)):
                # texts = [f for f in files if
                #          os.path.isfile(os.path.join(dest_dir, cpy_d, f)) and
                #          re.search("^\d{4}\w+\.\w+\.\w+-\w{4}(\.(mARkdown|inProgress|completed))?$", f)]
                # texts_noExt = set([re.split("\.(mARkdown|inProgress|completed)", t)[0] for t in texts])
                    for f in files:
                        no_ext_file = re.split("\.(mARkdown|inProgress|completed)", f)[0]
                        no_ext_path = os.path.join(root, no_ext_file)
                        if f.endswith(".mARkdown"):
                            if os.path.exists(no_ext_path + ".completed"):
                            #     try:
                                os.remove(no_ext_path + ".completed")
                                # except OSError:
                                #     pass
                            if os.path.exists(no_ext_path + ".inProgress"):
                                #     try:
                                os.remove(no_ext_path + ".inProgress")
                                    # except OSError:
                                    #     pass
                        elif f.endswith(".completed"):
                            #     try:
                            if os.path.exists(no_ext_path + ".inProgress"):
                                os.remove(no_ext_path + ".inProgress")
                                # except OSError:
                                #     pass

                        elif f.endswith(".inProgress"):
                            # try:
                            os.remove(os.path.join(root, f))
                            # except OSError:
                            #     pass

        else:
            print("%s repository doesn't have any 'data' directory!" % ad)


if __name__ == '__main__':

    source = input("Enter the source directory: ")
    target = input("Enter the target directory: ")

    if len(sys.argv) > 0:
        if not os.path.exists(source):
            print("source directory doesn't exists. Re-run the script and give the source!")
        else:
            copy_ah_data(source, target)
    else:
        print("Give the path to the script...!")

