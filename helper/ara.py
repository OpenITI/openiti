import re


# normalize Arabic light: fixing only Alifs, AlifMaqsuras; replacing hamzas on carriers with standalone hamzas
def normalize_ara_light(text):
    new_text = text
    # patterns to replace
    rep = {"[إأٱآا]": "ا",
           "[يى]ء": "ئ",
           "ى": "ي",
           "(ؤ)": "ء",
           "(ئ)": "ء"
           }

    # do the replacement
    for k, v in rep.items():
        new_text = re.sub(k, rep[k], new_text)
    return new_text


# normalize Arabic extra light: fixing ???
def normalize_ara_extra_light(text):
    new_text = text
    # patterns to replace
    rep = {}

    # do the replacement
    for k, v in rep.items():
        new_text = re.sub(k, rep[k], new_text)
    return new_text


# normalize Arabic heavy: normalizes Arabic by simplifying complex characters
def normalize_ara_heavy(text):
    new_text = text
    # patterns to replace
    rep = {"[إأٱآا]": "ا",
           "[يى]ء": "ئ",
           "ى": "ي",
           "ى": "ي",
           "(ؤ)": "ء",
           "(ئ)": "ء",
           "(ء)": "",
           "(ة)": "ه"
           }

    # do the replacement
    for k, v in rep.items():
        new_text = re.sub(k, rep[k], new_text)
    return new_text
