""""""
import copy
import os
import re
import shutil

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
    sys.path.append(root_folder)

from openiti.helper.funcs import read_header
from openiti.helper.ara import ar_cnt_file
from openiti.helper import yml
from openiti.helper.templates import author_yml_template, book_yml_template, \
                                     version_yml_template, readme_template, \
                                     text_questionnaire_template
from openiti.helper.uri import URI

created_folders = []
created_ymls = []

################################################################################
# OpenITI corpus functions dependent on URIs:


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

    Examples:
        # >>> folder = r"D:\OpenITI\barzakh"
        # >>> target_base_pth = r"D:\OpenITI\25Yrepos"
        # >>> initialize_new_texts_in_folder(folder,\
        #                                    target_base_pth, execute=False)
    """
    for fn in os.listdir(folder):
        ext = os.path.splitext(fn)[1]
        if ext not in (".yml", ".md"):
            fp = os.path.join(folder, fn)
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
        # >>> origin_folder = r"D:\OpenITI\barzakh"
        # >>> fn = "0375IkhwanSafa.Rasail.Hindawi95926405Vols-ara1.completed"
        # >>> origin_fp = os.path.join(origin_folder, fn)
        # >>> target_base_pth = r"D:\OpenITI\25Yrepos"
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

    add_character_count(tok_count, tar_uri, execute)

    # Give the option to execute the changes:

    if execute:
        print()
    else:
        print("Execute these changes?")
        resp = input("Type OK + Enter to execute; press Enter to abort: ")
        if resp == "OK":
            initialize_new_text(origin_fp, target_base_pth, execute=True)
        else:
            print("User aborted the execution of the changes.")

def add_readme(target_folder):
    with open(os.path.join(target_folder, "README.md"),
              mode="w", encoding="utf-8") as file:
        file.write(readme_template)

def add_text_questionnaire(target_folder):
    with open(os.path.join(target_folder, "text_questionnaire.md"),
              mode="w", encoding="utf-8") as file:
        file.write(text_questionnaire_template)

def change_uri(old, new, old_base_pth=None, new_base_pth=None, execute=False):
    """Change a uri and put all files in the correct folder.

    If a version URI changes:
        * all text files of that version should be moved
        * the yml file of that version should be updated and moved
    If a book uri changes:
        * the yml file of that book should be updated and moved
        * all annotation text files of all versions of the book should be moved
        * all yml files of versions of that book should be updated and moved
        * the original book folder itself should be (re)moved
    if an author uri changes:
        * the yml file of that author should be updated and moved
        * all book yml files of that should be updated and moved
        * all annotation text files of all versions of all books should be moved
        * all yml files of versions of all books should be updated and moved
        * the original book folders should be (re)moved
        * the original author folder itself should be (re)moved

    Examples:
        change_uri("0255Jahiz", "0256Jahiz")
        change_uri("0255Jahiz", "0255JahizBasri")
        change_uri("0255Jahiz.Hayawan", "0255Jahiz.KitabHayawan")
        change_uri("0255Jahiz.Hayawan.Shamela002526-ara1",
                   "0255Jahiz.Hayawan.Shamela002526-ara2")
        change_uri("0255Jahiz.Hayawan.Shamela002526-ara1.completed",
                   "0255Jahiz.Hayawan.Shamela002526-ara1.mARkdown")

    Args:
        old (str): URI string to be changed
        new (str): URI string to which the new URI should be changed.
        old_base_pth (str): path to the folder containing the
            OpenITI 25-year repos, related to the old uri
        new_base_pth (str): path to the folder containing the
            OpenITI 25-year repos, related to the new uri
        execute (bool): if False, the proposed changes will only be printed
            (the user will still be given the option to execute
            all proposed changes at the end);
            if True, all changes will be executed immediately.
    """
    print("old_base_pth:", old_base_pth)
    old_uri = URI(old)
    old_uri.base_pth = old_base_pth
    new_uri = URI(new)
    new_uri.base_pth = new_base_pth

    if not execute:
        print("old uri:", old)
        print("new uri:", new)
        print("Proposed changes:")
    old_folder = old_uri.build_pth()
    if new_uri.uri_type == "version":
        # only move yml and text file(s) of this specific version:
        for file in os.listdir(old_folder):
            fp = os.path.join(old_folder, file)
            if URI(file).build_uri(ext="") == old_uri.build_uri(ext=""):
                if file.endswith(".yml"):
                    move_yml(fp, new_uri, "version", execute)
                else:
                    old_file_uri = URI(fp)
                    new_uri.extension = old_file_uri.extension
                    move_to_new_uri_pth(fp, new_uri, execute)

        # add readme and text_questionnaire files:

        target_folder = new_uri.build_pth("version")
        if "README.md" not in os.listdir(target_folder):
            add_readme(target_folder)
        if "text_questionnaire.md" not in os.listdir(target_folder):
            add_text_questionnaire(target_folder)

    else: # move all impacted files and directories
        for root, dirs, files in os.walk(old_folder):
            for file in files:
                if file in ["README.md", "text_questionnaire.md"]:
                    # skip README and text_questionnaire files until last
                    # so we can use the uri of the other files to create path
                    pass
                else:
                    print()
                    print("* file:", file)
                    fp = os.path.join(root, file)
                    old_file_uri = URI(fp)
                    print("  (type: {})".format(old_file_uri.uri_type))
                    new_file_uri = copy.deepcopy(old_file_uri)
                    new_file_uri.base_pth = new_uri.base_pth
                    new_file_uri.date = new_uri.date
                    new_file_uri.author = new_uri.author
                    if new_uri.uri_type == "book":
                        new_file_uri.title = new_uri.title
                    if file.endswith(".yml"):
                        new_fp = move_yml(fp, new_file_uri,
                                          old_file_uri.uri_type, execute)
                    else:
                        new_fp = move_to_new_uri_pth(fp, new_file_uri, execute)

            # Deal with non-URI filenames last:

            for fn in ["README.md", "text_questionnaire.md"]:
                fp = os.path.join(root, fn)
                new_folder = os.path.split(new_fp)[0] # defined in previous loop
                new_fp = os.path.join(new_folder, fn)
                if os.path.exists(fp):
                    # if the old folder contained a readme / text questionnaire:
                    if execute:
                        shutil.move(fp, new_fp)
                        print("  Moved", fp, "to", new_fp)
                    else:
                        print("  Move", fp, "to", new_fp)

    # Remove folders:

    if new_uri.uri_type == "author":
        if execute:
            shutil.rmtree(old_folder)
        else:
            for book_dir in os.listdir(old_folder):
                if not book_dir.endswith("yml"):
                    print("REMOVE BOOK FOLDER", os.path.join(old_folder, book_dir))
            print("REMOVE AUTHOR FOLDER", old_folder)
    if new_uri.uri_type == "book":
        if execute:
            shutil.rmtree(old_folder)
        else:
            print("REMOVE BOOK FOLDER", old_folder)

    if not execute:
        resp = input("To carry out these changes: press OK+Enter; \
to abort: press Enter. ")
        if resp == "OK":
            print()
            change_uri(old, new, old_base_pth, new_base_pth, execute=True)
        else:
            print("User aborted carrying out these changes!")


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

        move_to_new_uri_pth(old_fp, new_uri, execute)

        add_character_count(tok_count, new_uri, execute)

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


def add_character_count(tok_count, tar_uri, execute=False):
    """Add the character count to the new version yml file"""

    tar_yfp = tar_uri.build_pth("version_yml")
    if execute:
        with open(tar_yfp, mode="r", encoding="utf-8") as file:
            yml_dic = yml.ymlToDic(file.read().strip())
            yml_dic["00#VERS#LENGTH###:"] = tok_count
        with open(tar_yfp, mode="w", encoding="utf-8") as file:
            file.write(yml.dicToYML(yml_dic))
    else:
        print("  Add the character count to the version yml file")


def new_yml(tar_yfp, yml_type, execute=False):
    """Create a new yml file from template.

    Args:
        tar_yfp (str): filepath to the new yml file
        yml_type (str): type of yml file
            (either "version_yml", "book_yml", or "author_yml")
    """
    template = eval("{}_template".format(yml_type))
    yml_dic = yml.ymlToDic(template)
    uri_key = "00#{}#URI######:".format(yml_type[:4].upper())
    yml_dic[uri_key] = URI(tar_yfp).build_uri()
    if execute:
        with open(tar_yfp, mode="w", encoding="utf-8") as file:
            file.write(yml.dicToYML(yml_dic))
    else:
        if not tar_yfp in created_ymls:
            print("  Create temporary yml file", tar_yfp)
            created_ymls.append(tar_yfp)


def move_yml(yml_fp, new_uri, uri_type, execute=False):
    """Replace the URI in the yml file
    and save the yml file in its new location.

    Args:
        yml_fp (str): path to the original yml file
        new_uri (URI object): the new uri
        uri_type (str): uri type (author, book, version)
        execute (bool): if False, the proposed changes will only be printed
            (the user will still be given the option to execute
            all proposed changes at the end);
            if True, all changes will be executed immediately.
    """
    new_yml_fp = new_uri.build_pth(uri_type=uri_type+"_yml")
    new_yml_folder = os.path.split(new_yml_fp)[0]
    make_folder(new_yml_folder, new_uri, execute)

    if not execute:
        print("  Change URI inside yml file:")
    yml_dict = yml.readYML(yml_fp)
    key = "00#{}#URI######:".format(uri_type[:4].upper())
    yml_dict[key] = new_uri.build_uri(uri_type=uri_type, ext="")
    yml_str = yml.dicToYML(yml_dict)
    if not execute:
        print(yml_str)

    if execute:
        with open(new_yml_fp, mode="w", encoding="utf-8") as yml_file:
            yml_file.write(yml_str)
        os.remove(yml_fp)
        print("Moved", yml_fp, "\n    to", new_yml_fp)
    else:
        print("  Move", yml_fp, "\n    to", new_yml_fp)
    return new_yml_fp


def make_folder(new_folder, new_uri, execute=False):
    """Check if folder exists; if not, make folder (and, if needed, parents)

    Args:
        new_folder (str): path to new folder
        new_uri (OpenITI uri object): uri of the text
        execute (bool): if False, the proposed changes will only be printed
            (the user will still be given the option to execute
            all proposed changes at the end);
            if True, all changes will be executed immediately.
    """
    if not os.path.exists(new_uri.base_pth):
        msg = """PathError: base path ({}) does not exist.
Make sure base path is correct.""".format(new_uri.base_pth)
        raise Exception(msg)
    if not os.path.exists(new_folder):
        author_folder = new_uri.build_pth("author")
        if not os.path.exists(author_folder):
            if execute:
                os.makedirs(author_folder)
            else:
                if not author_folder in created_folders:
                    print("  Make author_folder", author_folder)
                    created_folders.append(author_folder)
            new_yml(new_uri.build_pth("author_yml"), "author_yml", execute)
        if new_uri.uri_type == "book" or new_uri.uri_type == "version":
            book_folder = new_uri.build_pth("book")
            if not os.path.exists(book_folder):
                if execute:
                    os.makedirs(book_folder)
                else:
                    if not book_folder in created_folders:
                        print(" Make book_folder", book_folder)
                        created_folders.append(book_folder)
                new_yml(new_uri.build_pth("book_yml"), "book_yml", execute)
            if new_uri.uri_type == "version":
                new_yml(new_uri.build_pth("version_yml"),
                            "version_yml", execute)
                #target_folder = new_uri.build_pth("version")
                if execute:
                    if "README.md" not in os.listdir(book_folder):
                        add_readme(book_folder)
                    if "text_questionnaire.md" not in os.listdir(book_folder):
                        add_text_questionnaire(book_folder)
                else:
                    if os.path.exists(book_folder):
                        if "README.md" not in os.listdir(book_folder):
                            print("Add readme file in {}".format(book_folder))
                        if "text_questionnaire.md" not in os.listdir(book_folder):
                            print("Add text questionnaire in {}".format(book_folder))
                    else:
                        print("Add readme file in {}".format(book_folder))
                        print("Add text questionnaire in {}".format(book_folder))



def move_to_new_uri_pth(old_fp, new_uri, execute=False):
    """Move file to its new location.

    Args:
        old_fp (filepath): path to the old file
        new_uri (URI object): URI of the new file
        execute (bool): if False, the proposed changes will only be printed
            (the user will still be given the option to execute
            all proposed changes at the end);
            if True, all changes will be executed immediately.
    """
    new_folder = new_uri.build_pth(uri_type=new_uri.uri_type)
    new_fp = new_uri.build_pth(uri_type=new_uri.uri_type+"_file")
    make_folder(new_folder, new_uri, execute)
    if execute:
        shutil.move(old_fp, new_fp)
        print("  Move", old_fp, "\n    to", new_fp)
    else:
        print("  Move", old_fp, "\n    to", new_fp)
    return new_fp


def check_token_count(version_uri, ymlD):
    """Check whether the token count in the version yml file agrees with the\
    actual token count of the text file.
    """
    fp = version_uri.build_pth(uri_type="version_file")
    tok_count = ar_cnt_file(fp, mode="token")
    len_key = "00#VERS#LENGTH###:"
    yml_tok_count = ymlD[len_key].strip()
    replace_tok_count = False
    if yml_tok_count == "":
        print("NO TOKEN COUNT", uri)
        replace_tok_count = True
    else:
        try:
            if int(yml_tok_count) != tok_count:
                replace_tok_count = True
                #print("TOKEN COUNT CHANGED", uri)
                #print(yml_tok_count, "!=", tok_count)
        except:
            print("TOKEN COUNT {} IS NOT A NUMBER".format(yml_tok_count), uri)
            replace_tok_count = True
    if replace_tok_count:
        return tok_count

def replace_tok_counts(missing_tok_count):
    """Replace the token counts in the relevant yml files.

    Args:
        missing_tok_count (list): a list of tuples (uri, token_count):
            uri (OpenITI URI object)
            token_count (int): the number of Arabic tokens in the text file
    Returns:
        None
    """
    print("replacing token count in {} files".format(len(missing_tok_count)))
    for uri, tok_count in missing_tok_count:
        yml_fp = uri.build_pth("version_yml")
        ymlD = yml.readYML(yml_fp)
        len_key = "00#VERS#LENGTH###:"
        ymlD[len_key] = str(tok_count)
        ymlS = yml.dicToYML(ymlD)
        with open(yml_fp, mode="w", encoding="utf-8") as outf:
            outf.write(ymlS)


def check_yml_files(start_folder, exclude=[],
                    execute=False, check_token_counts=True):
    """Check whether yml files are missing or have faulty data in them.

    Args:
        start_folder (str): path to the parent folder of the folders
            that need to be checked.
        exclude (list): a list of directory names that should be excluded.
        execute (bool): if execute is set to False, the script will only show
            which changes it would undertake if set to True.
            After it has looped through all files and folders, it will give
            the user the option to execute the proposed changes.
    """
    uri_key = "00#{}#URI######:"
    missing_ymls = []
    missing_tok_count = []
    non_uri_files = []
    erratic_ymls = []
    for root, dirs, files in os.walk(start_folder):
        dirs[:] = [d for d in dirs if d not in exclude]

        for file in files:
            if file not in ["README.md", ".DS_Store",
                            ".gitignore", "text_questionnaire.md"]:
                fp = os.path.join(root, file)

                # Check whether a filename has the uri format:
                try:
                    uri = URI(fp)
                except:
                    non_uri_files.append(file)
                    uri = URI()

                # Check for every text file whether a version, book and author yml file
                # are associated with it:

                if uri.uri_type == "version" and not file.endswith(".yml"):
                    for yml_type in ["version_yml", "book_yml", "author_yml"]:
                        yml_fp = uri.build_pth(uri_type=yml_type)

                        # make new yml file if yml file does not exist:

                        if not os.path.exists(yml_fp):
                            print(yml_fp, "missing")
                            missing_ymls.append(yml_fp)
                            # create a new yml file:
                            if execute:
                                new_yml(yml_fp, yml_type, execute)
                                print("yml file created.")
                            else:
                                print("create yml file {}?".format(yml_fp))

                        # check whether the URI in yml file is the same
                        # as the URI in the filename;
                        # if not: replace URI in yml file with
                        # filename URI:
                        try:
                            ymlD = yml.readYML(yml_fp)
                        except:
                            ymlD = None # mistake in the yml file!
                            msg = "Yml file {} could not be read. "
                            msg += "Check manually!"
                            print(msg.format(uri(yml_type)))
                            erratic_ymls.append(yml_fp)
                        if ymlD == {}:
                            print(yml_fp, "empty")
                            missing_ymls.append(yml_fp)
                            if execute:
                                new_yml(yml_fp, yml_type, execute)
                                print("yml file created.")
                            else:
                                msg = "Replace empty yml file {}?"
                                print(msg.format(uri(yml_type)))
                        elif ymlD == None:
                            continue
                        else:
                            key = uri_key.format(yml_type[:4].upper())
                            if ymlD[key] != uri(yml_type[:-4]):
                                print("URI in yml file wrong!",
                                      ymlD[key], "!=", uri(yml_type[:-4]))
                                if execute:
                                    ymlD[key] = uri(yml_type[:-4])
                                    ymlS = yml.dicToYML(ymlD)
                                    with open(yml_fp, mode="w",
                                              encoding="utf-8") as outf:
                                        outf.write(ymlS)

                            # check whether token count in version yml file
                            # agrees with the current token count of the text

                            if yml_type == "version_yml":
                                if check_token_counts:
                                    tok_count = check_token_count(uri, ymlD)
                                    if tok_count:
                                        missing_tok_count.append((uri, tok_count))
    if  erratic_ymls:
        print()
        print("The following yml files were found to contain errors.")
        print("Check manually:")
        print()
        for file in sorted(erratic_ymls):
            print("    ", file)

    cnt = len(missing_tok_count)
    if not execute and (missing_ymls!=[] or missing_tok_count !=[]):
        print()
        print("Token count must be changed in {} files".format(cnt))
        print("Execute these changes?")
        resp = input("Press OK+Enter to execute; press Enter to abort: ")
        if resp == "OK":
            replace_tok_counts(missing_tok_count)
            check_yml_files(start_folder, exclude=exclude,
                            execute=True, check_token_counts=False)
            print()
            print("Token count changed in {} files".format(cnt))
            print()
        else:
            print("Changes aborted by user")
    else:
        print("No missing yml files.")

    if non_uri_files:
        print()
        print("The following files could have problems with their URI:")
        print()
        for file in sorted(set(non_uri_files)):
            print("    ", file)

    return missing_ymls, missing_tok_count, non_uri_files, erratic_ymls


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    print("passed doctests")

    # tests:

##    print("Checking yml files... This may take a while!")
##    URI.base_pth = r"D:\London\OpenITI\25Y_repos"
##    exclude = (["OpenITI.github.io", "Annotation", "maintenance", "i.mech00",
##                "i.mech01", "i.mech02", "i.mech03", "i.mech04", "i.mech05",
##                "i.mech06", "i.mech07", "i.mech08", "i.mech09", "i.logic",
##                "i.cex", "i.cex_Temp", "i.mech", "i.mech_Temp", ".git"])
##    resp = check_yml_files(r"D:\London\OpenITI\25Y_repos",
##                           exclude=exclude, execute=False,
##                           check_token_counts=False)
##    missing_ymls, missing_tok_count, non_uri_files, erratic_ymls = resp
##    #print(non_uri_files)
##    input("continue?")

    base_pth = r"D:\London\OpenITI\python_library\openiti\openiti\test"

    # test initialize_new_texts_in_folder function:
    print("Testing initialization of new texts in folder:")
    barzakh = r"D:\London\OpenITI\python_library\openiti\openiti\test\barzakh"
    initialize_new_texts_in_folder(barzakh, base_pth, execute=True)

    # test initialize_texts_from_CSV function:
    print("Testing initialization of new texts from csv:")
    csv_fp = r"D:\London\OpenITI\python_library\openiti\openiti\test\initialize.csv"
    initialize_texts_from_CSV(csv_fp, old_base_pth="", new_base_pth=base_pth,
                              execute=True)

##    # test change_uri function for author uri change:
##    old = "0001KitabAllah"
##    new = "0001Allah"
##    change_uri(old, new,
##               old_base_pth=base_pth, new_base_pth=base_pth,
##               execute=False)

##    # test change_uri function for book uri change:
##    old = "0375IkhwanSafa.RisalatJamicaJamica"
##    new = "0375IkhwanSafa.RisalatJamica"
##    change_uri(old, new,
##               old_base_pth=base_pth, new_base_pth=base_pth,
##               execute=False)

##    # test change_uri function for version uri change:
##    old = "0001Allah.KitabMuqaddas.BibleCorpus002-per1"
##    new = "0001Allah.KitabMuqaddas.BibleCorpus2-per1"
##    change_uri(old, new,
##               old_base_pth=base_pth, new_base_pth=base_pth,
##               execute=False)
##
##    input("URI changed??")

    my_uri = "0255Jahiz.Hayawan.Sham19Y0023775-ara1.completed"

    #URI.base_pth = "XXXX"

    t = URI(my_uri)
    print("repr(t):")
    print(repr(t))
    print("print(t):")
    print(t)
    print(t.author)
    print(t.date)
    print("URI type:", t.uri_type)
    print(t.build_uri("author"))
    print(t.build_pth("version"))
    print(t.build_pth("version", ""))
    print("print(t):", t)

    print("*"*30)

    u = URI()
    u.author="IbnCarabi"
    u.date="0681"
    print(u.build_uri("author"))
    print(u)

    print("*"*30)

    my_uri = URI("0255Jahiz.Hayawan.Sham19Y0023775-ara1.completed")
    print(my_uri.split_uri())
#    my_uri.extension=""
    my_uri.language=""
    print(my_uri.split_uri())
    my_uri.extension=""
    print("AN ERROR WARNING SHOULD FOLLOW: ")
    print(my_uri.build_pth(base_pth="./master", uri_type="version_file"))
