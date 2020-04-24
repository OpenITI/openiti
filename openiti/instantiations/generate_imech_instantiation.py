import re, os


#import zfunc
#import helper as hlp
from openiti.helper import funcs


def mechanical_chunking(path_full, target_folder):
    file_name = path_full.split("/")[-1]
    print("\n" + file_name)
    file_id = re.sub("\d{4}\w+\.\w+\.", "", file_name)
    print("\n" + file_id)

    target_path = target_folder + file_id

    # run generation
    cex = []

    if os.path.exists(target_path + "-%05d" % thresh):
        count = 0
    else:
        with open(path_full, "r", encoding="utf8") as f1:
            data = f1.read()
            #data = data.split(hlp.funcs.splitter)[1]
            data = data.split(funcs.splitter)[1]

            data = data.replace("\n~~", " ")
            data = data.replace("#", "(@@)")
            data = data.replace("\n", "(@)")
            data = re.sub(" +", " ", data)

            #data = data.split(hlp.funcs.milestone)
            data = data.split(funcs.milestone)

            print("\t%d items will be created..." % len(data))

            rec = '{"id":"%s", "series":"%s", "text": "%s"}'

            counter = 0
            for d in data:
                print("d: ", d)
                counter += 1
                id = file_id + ".ms%d" % counter
                #text = hlp.text_cleaner(d)
                text = funcs.text_cleaner(d)

                rec_t = rec % (id, file_id, text)

                cex.append(rec_t)

                #if counter % hlp.funcs.thresh == 0:
                if counter % funcs.thresh == 0:
                    with open(target_path + "-%05d" % counter, "w", encoding="utf8") as ft:
                        ft.write("\n".join(cex))
                    cex = []

            #counter_final = hlp.roundup(counter, hlp.funcs.thresh)
            counter_final = funcs.roundup(counter, funcs.thresh)
            with open(target_path + "-%05d" % counter_final, "w", encoding="utf8") as ft:
                ft.write("\n".join(cex))

            count = 1

    return count


# process all texts in OpenITI
def process_all(folder, target_path):

    print()
    print("Generating mechanical passim_new corpus...")
    print()

    count = 1

    for root, dirs, files in os.walk(folder):
        #dirs[:] = [d for d in dirs if d not in zfunc.exclude]
        dirs[:] = [d for d in dirs if d not in funcs.exclude_folders]

        for file in files:
            if re.search("^\d{4}\w+\.\w+\.\w+-\w{4}(\.(mARkdown|inProgress|completed))?$", file):
                path_full = os.path.join(root, file)
                # input(file)

                if "" in path_full:

                    # print(d)
                    count += mechanical_chunking(path_full, target_path)
                    return
                    if count % 100 == 0:
                        print()
                        print("=============" * 2)
                        print("Processed: %d" % count)
                        print("=============" * 2)
                        print()
                if count == 100:
                    break
                else:
                    continue
