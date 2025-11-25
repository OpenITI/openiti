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

from openiti.helper.funcs import read_header, count_toks
#from openiti.helper.ara import ar_cnt_file
from openiti.helper.uri import move_to_new_uri_pth, add_character_count, URI, new_yml
from openiti.helper.yml import readYML, check_yml_completeness, dicToYML

created_ymls = []

def initialize_texts_from_CSV(csv_fp, old_base_pth="", new_base_pth="",
                              execute=False, non_25Y_folder=None):
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
        non_25Y_folder (str): name of the parent folder for the new files,
            to be used instead of the 25 years folder (0025AH, 0050AH, ...).
            Defaults to None (that is: use the auto-generated 25 years folder).

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
        #tok_count = ar_cnt_file(old_fp, mode="token")
        #char_count = ar_cnt_file(old_fp, mode="char")
        tok_count, char_count = count_toks(old_fp, incl_chars=True)

        move_to_new_uri_pth(old_fp, new_uri, execute, 
                            non_25Y_folder=non_25Y_folder)

        add_character_count(tok_count, char_count, new_uri, execute, 
                            non_25Y_folder=non_25Y_folder)

    if not execute:
        resp = input("To carry out these changes: press OK+Enter; \
to abort: press Enter. ")
        if resp.upper() == "OK":
            initialize_texts_from_CSV(csv_fp, old_base_pth, new_base_pth,
                                      execute=True, non_25Y_folder=non_25Y_folder)
        else:
            print()
            print("User aborted carrying out these changes!")
            print("*"*60)


def initialize_new_texts_in_folder(folder, target_base_pth, execute=False, 
                                   non_25Y_folder=None):
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
        non_25Y_folder (str): name of the parent folder for the new files,
            to be used instead of the 25 years folder (0025AH, 0050AH, ...).
            Defaults to None (that is: use the auto-generated 25 years folder).

    Returns:
        None

    Examples::
    
        # >>> folder = r"D:\\OpenITI\\barzakh"
        # >>> target_base_pth = r"D:\\OpenITI\\25Yrepos"
        # >>> initialize_new_texts_in_folder(folder, target_base_pth,
        #                                    execute=False)
    """
    for fn in os.listdir(folder):
        ext = os.path.splitext(fn)[1]
        if ext not in (".yml", ".md"):
            fp = os.path.join(folder, fn)
            print(fp)
            if os.path.isfile(fp):
                initialize_new_text(fp, target_base_pth, execute, non_25Y_folder=non_25Y_folder)


def replace_yml_values(yfp, tar_yfp, execute=False):
    non_default_keys = check_yml_completeness(yfp)[0]
    non_default_keys_tar = check_yml_completeness(tar_yfp)[0]
    yml_d = readYML(yfp, reflow=False)
    tar_d = readYML(tar_yfp, reflow=False)
    changed = 0
    for k in non_default_keys:
        if k not in non_default_keys_tar:
            tar_d[k] = yml_d[k]
            changed += 1
            if not execute:
                print("Adding value to yml key", k)
                print(yml_d[k])
        elif tar_d[k] != yml_d[k]:
            print("-----------")
            print("Non-default value in both yml files:")
            print("1. original:", k, tar_d[k])
            print("2. new:", k, yml_d[k])
            print("If you want to combine both, choose 3")
            print("Alternatively, write a combined value yourself")
            r = input("Your choice (default: keep original): ")
            if r.strip() == "2":
                tar_d[k] = yml_d[k]
                changed += 1
            elif r.strip() == "3":
                tar_d[k] += ";" + yml_d[k]
                changed += 1
            elif r.strip() == "" or r.strip() == "1":
                if not execute:
                    print("  -> Keep original value")
            else:
                tar_d[k] = r.strip().replace("\\n", "\n")
                changed += 1
                
    if changed:
        if execute:
            with open(tar_yfp, mode="w", encoding="utf-8") as file:
                file.write(dicToYML(tar_d, reflow=False))
        else:
            print(changed, "yml values changed")
            print(dicToYML(tar_d, reflow=False))
    if execute:
        os.remove(yfp)

def initialize_new_text(origin_fp, target_base_pth, execute=False, non_25Y_folder=None):
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
        non_25Y_folder (str): name of the parent folder for the new files,
            to be used instead of the 25 years folder (0025AH, 0050AH, ...).
            Defaults to None (that is: use the auto-generated 25 years folder).

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
    if "version" in tar_uri.uri_type:
        target_fp = tar_uri.build_pth("version_file")
        yml_types = ("version_yml", "book_yml", "author_yml")
    elif "transcription" in tar_uri.uri_type:
        target_fp = tar_uri.build_pth("transcription_file")
        yml_types = ("transcription_yml", "manuscript_yml", "location_yml")
    else:
        print("ABORTING: unsuitable uri type:", tar_uri.uri_type)
        return
    
    if non_25Y_folder:
        target_fp = re.sub(r"\d{4}AH", non_25Y_folder, target_fp)
        print("target_fp:", target_fp)

    # Check whether the text file has OpenITI format:

    #header = "\n".join(read_header(origin_fp))
    header = read_header(origin_fp)
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
    #tok_count = ar_cnt_file(origin_fp, mode="token")
    #char_count = ar_cnt_file(origin_fp, mode="char")
    tok_count, char_count = count_toks(origin_fp, incl_chars=True)

    # Move the text file:    
    move_to_new_uri_pth(origin_fp, tar_uri, execute, non_25Y_folder=non_25Y_folder)

    # Move or create the YML files:
    
    for yf in yml_types:
        yfp = os.path.join(ori_uri.base_pth, ori_uri.build_uri(yf))
        tar_yfp = tar_uri.build_pth(yf)
        if non_25Y_folder:
            tar_yfp = re.sub(r"\d{4}AH", non_25Y_folder, tar_yfp)
        if os.path.exists(yfp):
            if execute:
                if not os.path.exists(tar_yfp):
                    shutil.move(yfp, tar_yfp)
                else:
                    replace_yml_values(yfp, tar_yfp, execute=execute)
            else:
                if not os.path.exists(tar_yfp):
                    print("  move", yfp, "to", tar_yfp)
                else:
                    print("yml file already exists: ", tar_yfp)
                    replace_yml_values(yfp, tar_yfp, execute=execute)
        else:
            if not os.path.exists(tar_yfp):
                new_yml(tar_yfp, yf, execute)
            else:
                if tar_yfp not in created_ymls:
                    if not execute:
                        print("  {} already exist; no yml file created".format(tar_yfp))


    # Add the character count to the new yml file:

    add_character_count(tok_count, char_count, tar_uri, execute, 
                        non_25Y_folder=non_25Y_folder)

    # Give the option to execute the changes:

    if not execute:
        print("Execute these changes?")
        resp = input("Type OK + Enter to execute; press Enter to abort: ")
        if resp.upper() == "OK":
            initialize_new_text(origin_fp, target_base_pth, execute=True, 
                                non_25Y_folder=non_25Y_folder)
        else:
            print("User aborted the execution of the changes.")

    return target_fp


def download_texts_from_CSV(csv_fp, base_url="", new_base_pth="", 
                            non_25Y_folder=None):
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
        non_25Y_folder (str): name of the parent folder for the new files,
            to be used instead of the 25 years folder (0025AH, 0050AH, ...).
            Defaults to None (that is: use the auto-generated 25 years folder).
    
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
            

            move_to_new_uri_pth(temp_fp, new_uri, execute=True, 
                                non_25Y_folder=non_25Y_folder)

            if not temp_fp.endswith("pdf") and not temp_fp.endswith("zip"):
                #tok_count = ar_cnt_file(temp_fp, mode="token")
                #char_count = ar_cnt_file(temp_fp, mode="char")
                tok_count, char_count = count_toks(temp_fp, incl_chars=True)
                add_character_count(tok_count, char_count, new_uri, execute=True, 
                                    non_25Y_folder=non_25Y_folder)

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

##    # test download_texts_from_CSV function:
##    csv_fp = os.path.join(base_pth, "download_csv_to_uri.csv")
##    download_texts_from_CSV(csv_fp, new_base_pth=base_pth)
##    print("Texts in csv file downloaded and in the right folder. Check!")

    folder = r"D:\London\OpenITI\barzakh\barzakh"
    target_base_pth = r"D:\London\OpenITI\25Y_repos"
    ignore = (".yml", ".md", ".py", ".git", ".gitignore")
    for fn in os.listdir(folder):
        if not fn.endswith(ignore) and "oorlib" not in fn:
            fp = os.path.join(folder, fn)
            print(fp)
            if os.path.isfile(fp):
                initialize_new_text(fp, target_base_pth, execute=False)
