from openiti.helper.uri import URI, new_yml, ar_ch_len
from openiti.helper import yml
import os



exclude = (["OpenITI.github.io", "Annotation", "maintenance", "i.mech00",
            "i.mech01", "i.mech02", "i.mech03", "i.mech04", "i.mech05",
            "i.mech06", "i.mech07", "i.mech08", "i.mech09", "i.logic",
            "i.cex", "i.cex_Temp", "i.mech", "i.mech_Temp", ".git"])



def check_yml_files(start_folder, exclude=[], execute=False):
    """Check whether yml files are missing or have faulty data in them.

    Args:
        start_folder (str): path to the parent folder of the folders
            that need to be checked.
        exclude (list): a list of directory names that should be excluded.
        execute (bool): if execute is set to False, the script will only show
            which changes it would undertake if set to True.
            After it has looped through all files and folders, it will give
            the user the option to execute the proposed changes."""
    uri_key = "00#{}#URI######:"
    len_key = "00#VERS#LENGTH###:"
    missing_ymls = []
    missing_char_count = []
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
                    uri = None

                # Check for every text file whether a version, book and author yml file
                # are associated with it:
                
                if uri:
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
                                    input("yml file created. Continue?")
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
                                msg = "Yml file {} could not be read. Check manually!"
                                print(msg.format(uri(yml_type)))
                                erratic_ymls.append(yml_fp)
                            if ymlD: 
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

                                # check whether version yml file
                                # has a length:

                                if yml_type == "version_yml":
                                    replace_char_count = False
                                    if ymlD[len_key].strip() == "":
                                        print("NO LEN INFO", uri)
                                        replace_char_count = True
                                    else:
                                        try:
                                            int(ymlD[len_key].strip())
                                        except:
                                            print("LEN INFO NOT A NUMBER", uri)
                                            replace_char_count = True
                                    if replace_char_count:
                                        missing_char_count.append(uri(yml_type))
                                        char_count = ar_ch_len(fp)
                                        if execute:
                                            ymlD[len_key] = str(char_count)
                                            ymlS = yml.dicToYML(ymlD)
                                            with open(yml_fp, mode="w",
                                                      encoding="utf-8") as outf:
                                                outf.write(ymlS)
                                        else:
                                            msg = "Add character count ({}) to {}"
                                            print(msg.format(char_count, uri(yml_type)))
    
    if  erratic_ymls:
        print()
        print("The following yml files were found to contain errors.")
        print("Check manually:")
        print()
        for file in sorted(erratic_ymls):
            print(file)

    if not execute and (missing_ymls!=[] or missing_char_count !=[]):
        print()
        print("Execute these changes?")
        resp = input("Press OK+Enter to execute; press Enter to abort: ")
        if resp == "OK":
            check_yml_files(start_folder, exclude=exclude, execute=True)
        else:
            print("Changes aborted by user")
    else:
        print("No missing yml files; all files contain character count.")

    if non_uri_files:
        print()
        print("The following files could have problems with their URI:")
        print()
        for file in sorted(set(non_uri_files)):
            print(file)

    return missing_ymls, missing_char_count, non_uri_files, erratic_ymls



URI.base_pth = r"D:\London\OpenITI\25Y_repos"
resp = check_yml_files(r"D:\London\OpenITI\25Y_repos",
                       exclude=exclude, execute=False)
missing_ymls, missing_char_count, non_uri_files, erratic_ymls = resp
#print(non_uri_files)


