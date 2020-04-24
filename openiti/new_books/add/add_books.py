"""Scripts to add books to the correct OpenITI repositories.

* initialize_texts_from_csv: use a csv file that contains for every file
    that needs to be added to the corpus:
    - the path to its current location
    - the URI it needs to get

* initialize_new_texts_in_folder: initialize all text files in a folder
    (in order for this to work, all files need to have valid URIs)

* download_texts_from_CSV: download texts from the internet and
    directly put them into the correct OpenITI folder


"""

import copy
import os
import re
import requests
import shutil

if __name__ == '__main__':
    from os import sys, path
    root_folder =path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.helper.funcs import read_header
from openiti.helper.ara import ar_cnt_file
from openiti.helper.uri import move_to_new_uri_pth, add_character_count, URI


created_ymls = []

def initialize_texts_from_CSV(csv_fp, old_base_pth="", new_base_pth="",
                              execute=False):
    """
    Use a CSV file (filename, URI) to move a list of texts to the relevant \
    OpenITI folder.

    The CSV file (which should not contain a heading) can contain
    full filepaths to the original files, or only filenames;
    in the latter case, the path to the folder where these files are located
    should be passed to the function as the old_base_pth argument.
    Similarly, the URI column can contain full OpenITI URI filepaths
    or only the URIs; in the latter case, the path to the folder
    containing the OpenITI 25-years folders should be passed to the function
    as the new_base_pth argument.

    Args:
        csv_fp (str): path to a csv file that contains the following columns:
            0. filepath to (or filename of) the text file
            1. full version uri of the text file
            (no headings!)
        old_base_path (str): path to the folder containing
            the files that need to be initialized
        new_base_pth (str): path to the folder containing
            the OpenITI 25-years repos
        execute (bool): if False, the proposed changes will only be printed
            (the user will still be given the option to execute
            all proposed changes at the end);
            if True, all changes will be executed immediately.

    Returns:
        None
    """
    with open(csv_fp, mode="r", encoding="utf-8") as file:
        csv = file.read().splitlines()
        csv = [re.split("[,\t]", row) for row in csv]

    for old_fp, new in csv:
        if old_base_pth:
            old_fp = os.path.join(old_base_pth, old_fp)
        new_uri = URI(new)
        if new_base_pth:
            new_uri.base_pth = new_base_pth
        #char_count = ar_ch_len(old_fp)
        tok_count = ar_cnt_file(old_fp, mode="token")
        char_count = ar_cnt_file(old_fp, mode="char")

        move_to_new_uri_pth(old_fp, new_uri, execute)

        add_character_count(tok_count, char_count, new_uri, execute)

    if not execute:
        resp = input("To carry out these changes: press OK+Enter; \
to abort: press Enter. ")
        if resp == "OK":
            initialize_texts_from_CSV(csv_fp, old_base_pth, new_base_pth,
                              execute=True)
        else:
            print()
            print("User aborted carrying out these changes!")
            print("*"*60)


def initialize_new_texts_in_folder(folder, target_base_pth, execute=False):
    """Move all new texts in folder to their OpenITI repo, creating yml files\
    if necessary (or copying them from the same folder if present).

    Args:
        folder (str): path to the folder that contains new text files
            (with OpenITI uri filenames) and perhaps yml files
        target_base_pth (str): path to the folder containing the 25-years repos
        execute (bool): if False, the proposed changes will only be printed
            (the user will still be given the option to execute
            all proposed changes at the end);
            if True, all changes will be executed immediately.

    Returns:
        None

    Examples::
    
        # >>> folder = r"D:\\OpenITI\\barzakh"
        # >>> target_base_pth = r"D:\\OpenITI\\25Yrepos"
        # >>> initialize_new_texts_in_folder(folder,\
        #                                    target_base_pth, execute=False)
    """
    for fn in os.listdir(folder):
        ext = os.path.splitext(fn)[1]
        if ext not in (".yml", ".md"):
            fp = os.path.join(folder, fn)
            print(fp)
            if os.path.isfile(fp):
                initialize_new_text(fp, target_base_pth, execute)


def initialize_new_text(origin_fp, target_base_pth, execute=False):
    """Move a new text file to its OpenITI repo, creating yml files\
    if necessary (or copying them from the same folder if present).

    The function also checks whether the new text adheres to OpenITI text format.

    Args:
        origin_fp (str): filepath of the text file (filename must be
                         in OpenITI uri format)
        target_base_pth (str): path to the folder
                               that contains the 25-years-repos
        execute (bool): if False, the proposed changes will only be printed
            (the user will still be given the option to execute
            all proposed changes at the end);
            if True, all changes will be executed immediately.

    Returns:
        None

    Example:
        # >>> origin_folder = r"D:\\OpenITI\\barzakh"
        # >>> fn = "0375IkhwanSafa.Rasail.Hindawi95926405Vols-ara1.completed"
        # >>> origin_fp = os.path.join(origin_folder, fn)
        # >>> target_base_pth = r"D:\\OpenITI\\25Yrepos"
        # >>> initialize_new_text(origin_fp, target_base_pth, execute=False)
    """
    ori_uri = URI(origin_fp)
    tar_uri = copy.deepcopy(ori_uri)
    tar_uri.base_pth = target_base_pth
    target_fp = tar_uri.build_pth("version_file")

    # Check whether the text file has OpenITI format:

    header = "\n".join(read_header(origin_fp))
    if "#META#Header#End" not in header:
        print("Initialization aborted: ")
        print("{} does not contain OpenITI metadata header splitter!".format(origin_fp))
        return
    if "######OpenITI#" not in header:
        print("Initialization aborted: ")
        print("{} does not contain OpenITI magic value!".format(origin_fp))
        return

    # Count the Arabic characters in the text file:

    #tok_count = ar_ch_len(origin_fp)
    tok_count = ar_cnt_file(origin_fp, mode="token")
    char_count = ar_cnt_file(origin_fp, mode="char")

    # Move the text file:

    target_folder = tar_uri.build_pth("version")
    move_to_new_uri_pth(origin_fp, tar_uri, execute)

    # Move or create the YML files:

    for yf in ("version_yml", "book_yml", "author_yml"):
        yfp = os.path.join(ori_uri.base_pth, ori_uri.build_uri(yf))
        tar_yfp = tar_uri.build_pth(yf)
        if os.path.exists(yfp):
            if execute:
                shutil.move(yfp, tar_yfp)
            else:
                print("  move", yfp, "to", tar_yfp)
        else:
            if not os.path.exists(tar_yfp):
                new_yml(tar_yfp, yf, execute)
            else:
                if tar_yfp not in created_ymls:
                    if not execute:
                        print("  {} already exist; no yml file created".format(tar_yfp))


    # Add the character count to the new yml file:

    add_character_count(tok_count, char_count, tar_uri, execute)

    # Give the option to execute the changes:

    if not execute:
        print("Execute these changes?")
        resp = input("Type OK + Enter to execute; press Enter to abort: ")
        if resp == "OK":
            initialize_new_text(origin_fp, target_base_pth, execute=True)
        else:
            print("User aborted the execution of the changes.")


def download_texts_from_CSV(csv_fp, base_url="", new_base_pth=""):
    """
    Use a CSV file (filename, URI) to download a list of texts to the relevant \
    OpenITI folder.

    The CSV file (which should not contain a heading) can contain
    full urls for the original files, or only filenames;
    in the latter case, the url of the website where these files are located
    should be passed to the function as the base_url argument.
    Similarly, the URI column can contain full OpenITI URI filepaths
    or only the URIs; in the latter case, the path to the folder
    containing the OpenITI 25-years folders should be passed to the function
    as the new_base_pth argument.

    Args:
        csv_fp (str): path to a csv file that contains the following columns:
            0. filepath to (or filename of) the text file
            1. full version uri of the text file
            (no headings!)
        old_base_path (str): path to the folder containing
            the files that need to be initialized. Defaults to "".
        new_base_pth (str): path to the folder containing
            the OpenITI 25-years repos. Defaults to "".
    
    Returns:
        None
    """
    with open(csv_fp, mode="r", encoding="utf-8") as file:
        csv = file.read().splitlines()
        csv = [re.split("[,\t]", row) for row in csv]

    temp_folder = "temp"
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    for old_fp, new in csv:
        print(old_fp)
        if not os.path.exists(new):
            if base_url:
                old_fp = os.path.join(base_url, old_fp)
            new_uri = URI(new)
            if new_base_pth:
                new_uri.base_pth = new_base_pth
            #char_count = ar_ch_len(old_fp)

            fn = os.path.split(old_fp)[1]
            temp_fp = os.path.join(temp_folder, fn)

            with requests.get(old_fp, stream=True) as r:
                r.raise_for_status()
                print("download starting")
                with open(temp_fp, mode="wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print("download finished")
            

            move_to_new_uri_pth(temp_fp, new_uri, execute=True)

            if not temp_fp.endswith("pdf") and not temp_fp.endswith("zip"):
                tok_count = ar_cnt_file(temp_fp, mode="token")
                char_count = ar_cnt_file(temp_fp, mode="char")
                add_character_count(tok_count, char_count, new_uri, execute=True)

    shutil.rmtree(temp_folder)



if __name__ == "__main__":
    base_pth = r"D:\London\OpenITI\python_library\openiti\openiti\test"

##    # test initialize_new_texts_in_folder function:
##    barzakh = os.path.join(base_pth, "barzakh")
##    initialize_new_texts_in_folder(barzakh, base_pth, execute=True)
##    print("Texts in test/barzakh initialized; check if initialization was successful!")
##    input("Press Enter to continue")

##    # test initialize_texts_from_CSV function:
##    csv_fp = os.path.join(base_pth, "initialize.csv")
##    initialize_texts_from_CSV(csv_fp, old_base_pth="", new_base_pth=base_pth,
##                              execute=False)
##    print("Texts in csv file initialized; check if initialization was successful!")
##    input("Press Enter to continue")

    # test download_texts_from_CSV function:
    csv_fp = os.path.join(base_pth, "download_csv_to_uri.csv")
    download_texts_from_CSV(csv_fp, new_base_pth=base_pth)
    print("Texts in csv file downloaded and in the right folder. Check!")
