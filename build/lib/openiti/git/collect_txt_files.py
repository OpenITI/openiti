"""Moves all text files from all subdirectories into a single directory.

Todo:
    if more than one version of the text file is in the folder,
        the script will not automatically copy the best version! 

Examples:
    Command line usage::
    
        $ collect_txt_files D:\\OpenITI\\25Y_folders D:\\OpenITI\\release\\texts

    If the source and target directories were not given,
    the user will be prompted for them::

        $ collect_txt_files
        Enter the source directory:
        Enter the target directory:
"""

import os
import re
import shutil
import sys

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
    sys.path.append(root_folder)

from openiti.helper.uri import URI

def move_ara_files(source_dir, dest_dir):
    """ old name of the collect_text_files function;
    renamed because the name does not reflect what function does;
    old name kept for backward compatibility
    """
    return collect_text_files(source_dir, dest_dir)


def collect_text_files(source_dir, dest_dir,
                       exclude_folders=[],
                       extensions=["mARkdown", "inProgress", "completed", ""],
                       version_id_only=True):
    """Copy all text files in `source_dir` (+ its subfolders) to `dest_dir`.

    Args:
        source_dir (str): path to the directory that contains
            (subfolders containing) the text files
        dest_dir (str): path to a directory to which text files will be copied.
        exclude_folders (list): directories to be excluded
            from the collection process
        extensions (list): list of extensions; only text files with these
            extensions will be copied.
            Defaults to ["mARkdown", "inProgress", "completed", ""]
        version_id_only (bool): if True, the filename will be shortened
            to the last part of the URI, i.e., the version id + language id
            (e.g., Shamela001185-ara1). Defaults to True.
        
    Returns:
        (int): number of files copied
    """
    cnt = 0
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in exclude_folders]
        for file in files:
            #if re.search("^\d{4}\w+\.\w+\.\w+-\w{4}(\.(mARkdown|inProgress|completed))+$", file):
            # if re.search("^\d{4}\w+\.\w+\.\w+-ara\d$", file):
            try:
                uri = URI(os.path.join(root, file))
            except:
                uri = URI()
            if uri.uri_type == "version" and uri.extension in extensions:
                # to rename the files and keep only the text ID
                old_fp = os.path.join(root, file)
                if version_id_only:
                    new_fp = os.path.join(dest_dir, uri(ext="").rsplit(".")[-1])
                else:
                    new_fp = os.path.join(dest_dir, file)
                shutil.copy(old_fp, new_fp)
                #print(old_fp)
                #print(">", new_fp)
                cnt += 1
    return cnt


if __name__ == '__main__':

    if len(sys.argv) == 3:
        source = sys.argv[1]
        target = sys.argv[2]
    else:
        source = input("Enter the source directory: ")
        while not source:
            source = input("Enter the source directory: ")

        target = input("Enter the target directory: ")
        while not target:
            target = input("Enter the target directory: ")

    if not os.path.exists(source):
        print("Aborting. Source directory doesn't exist!")
        sys.exit()    
    cnt = move_ara_files(source, target)
    print("done; {} files copied".format(cnt))

    source = r"D:\London\OpenITI\25Y_repos"
    target = r"D:\London\OpenITI\python_library\openiti\openiti\test\0025AH"
    cnt = move_ara_files(source, target)
    print("done; {} files copied".format(cnt))
    sys.exit()
