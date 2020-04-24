"""Convert a YML file to json.

The yml2json function can be used to convert a yml metadata file to

* a list of dictionaries: useful for
    - conserving the order
    - conserving comments between the records
* a dictionary of dictionaries (key: record id, val: metadata dictionary),
  useful for easy lookup by record id
"""

import json
import re


def prettyprint(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=4, sort_keys=True))


def yml2json(yml_fp, container=[], rec_start="##RECORD",
             id_key="01#BookID###", key_val_splitter=":::: "):
    """Convert a YML file to json.

    Args:
        yml_fp (str): the filepath to the YML file.
        container (obj): an empty list or dict into which the 
            metadata dictionaries will be stored.
            If the container is a list, the order of the records will be stored
            as well as comment lines between the records.
        rec_start (str): the starting characters of a record;
        id_key (str): the yml key that indicates the id of a record
        key_val_splitter (str): the separator used to separate keys and values.

    Returns:
        container (obj): the container filled with the metadata dictionaries.
    """
    spl = key_val_splitter

    with open(yml_fp, mode="r", encoding="utf-8") as file:
        yml_str = file.read()
    blocks = re.split("\n{2,}", yml_str)
    #print("The file contains {} blocks".format(len(blocks)))    
    for b in blocks:

        # if the block is a record: build a record dictionary
        
        if b.startswith(rec_start):
            record_lines = b.strip().splitlines()
            r_dic = {line.split(spl)[0]:line.split(spl)[1]
                     for line in record_lines[1:]}
            try:
                container.append(r_dic)
            except:
                container[r_dic[id_key]] = r_dic

        # if the block is a comment in between records,
        # save the comment only if the container is a list:
        
        else:
            try:
                container.append(b)
            except:
                pass
    return container

if __name__ == "__main__":
    meta_fp = r"test/hindawi_metadata_man.yml"
    meta = yml2json(meta_fp, container=[])
    print("A LIST OF DICTIONARIES:")
##    for dic in meta[:2]:
##        try:
##            for k,v in sorted(dic.items()):
##                print(k, v)
##        except:
##            print(dic)
##        print()
    prettyprint(meta[:2])
    print()
    uri_fp = r"test/hindawi_metadata_man.yml"
    uri_data = yml2json(uri_fp, container={})
    print("A DICTIONARY OF DICTIONARIES:")
    for key, dic in sorted(list(uri_data.items()))[:2]:
        for k,v in sorted(dic.items()):
            print(k, v)
        print()
