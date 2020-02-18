# Moves all ara1 () file from all directories into a single directory

import os
import re
import shutil
import sys


def move_ara_files(source_dir, dest_dir):
    for root, dirs, files in os.walk(source_dir):
        # print("root: ",root)
        dirs[:] = [d for d in dirs]
        for file in files:
            if re.search("^\d{4}\w+\.\w+\.\w+-\w{4}(\.(mARkdown|inProgress|completed))+$", file):
            # if re.search("^\d{4}\w+\.\w+\.\w+-ara\d$", file):
                # to rename the files and keep only the text ID
                old_name = os.path.join(root, file)
                new_name = os.path.join(dest_dir, file.rsplit(".")[-1])
                shutil.copy(old_name, new_name)
                # copy th file with the original name
                # shutil.copy(os.path.join(root, file), dest_dir)


if __name__ == '__main__':

    source = input("Enter the source directory: ")
    target = input("Enter the target directory: ")

    if len(sys.argv) > 0:
        if not os.path.exists(source):
            print("source directory doesn't exists!")
        elif not os.path.exists(target):
            if target:
                os.makedirs(target)
                move_ara_files(source, target)
            else:
                print("please enter a target path")
        else:
            move_ara_files(source, target)
    else:
        print("give the path to the script...!")

