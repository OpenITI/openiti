# inserting milestones for splitting texts into chunks of the same size

import re, os
#import helper.funcs as hlp
#import zfunc
from openiti.helper import funcs, ara

stopper = 1


def reformatting(path_full, target_folder):
    file_name = path_full.split("/")[-1]
    file_id = "_".join(file_name.split(".")[:2])
    print("Processing:")

    target_path = target_folder + file_id
    print("\t" + target_path)

    # run generation
    if os.path.exists(target_path):
        count = 0
        print("\t\t! The file has been processed")
    else:
        print("Converting:")
        print("\n" + file_name)
        print("\ninto:\t" + file_id)
        with open(path_full, "r", encoding="utf8") as f1:
            data = f1.read()
            #data = data.split(hlp.funcs.splitter)[1]
            data = data.split(funcs.splitter)[1]

            data = data.replace("\n~~", " ")
            # data = data.replace("#", "(@@)")
            data = data.replace("Milestone300", " ")

            data = re.sub(" +", " ", data)

            #data = hlp.ara.normalize_ara_extra_light(data)
            data = ara.normalize_ara_extra_light(data)
            data = re.sub("Page\w+|[#\|\-\%\d]", "", data)

            with open(target_path, "w", encoding="utf8") as ft:
                ft.write(data)

            count = 1

    return count


def load_meta_data():
    # TODO: interactive path to metedata file
    meta_file = "../Annotation/OpenITI_metadata_light.csv"
    meta = {}
    with open(meta_file, "r", encoding="utf8") as f1:
        data = f1.read().split("\n")

        for d in data[1:]:
            da = d.split("\t")
            if da[5] == "pri":
                meta[da[0].strip()] = da

    return meta


# process all texts in OpenITI
def process_all(folder, target_path):
    meta_data = load_meta_data()
    meta_stylo = []

    print()
    print("Generating i.stylo corpus...")
    print()

    count = 1
    not_in_meta_list = []

    for root, dirs, files in os.walk(folder):
        #dirs[:] = [d for d in dirs if d not in zfunc.exclude]
        dirs[:] = [d for d in dirs if d not in funcs.exclude]

        for file in files:
            if re.search("^\d{4}\w+\.\w+\.\w+-\w{4}(\.(mARkdown|inProgress|completed))?$", file):
                if "DhaylTabaqatHanabila" in file:
                    input(file)
                if file in meta_data:
                    path_full = os.path.join(root, file)
                    file_stylo = "_".join(file.split(".")[:2])
                    meta_stylo.append(file_stylo + "\t" + file + "\t%d" % int(file_stylo[:4]))

                    if "DhaylTabaqatHanabila" in file:
                        print(path_full)
                        input(file)

                    if "" in path_full:
                        count += reformatting(path_full)
                        if count % stopper == 0:
                            print()
                            print("=============" * 2)
                            print("Processed: %d" % count)
                            print("=============" * 2)
                            print()

                    if count == stopper:
                        print()

    with open(target_path.replace("_Temp", "") + "meta_stylo", "w", encoding="utf8") as ft:
        ft.write("\n".join(meta_stylo))

    print("Not in META")
    print("\n".join(not_in_meta_list))
