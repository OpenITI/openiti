# Shamela converter configuration file:

# path to the Files folder of the shamela database
# (this folder contains the main metadata database files):
files_folder = None

# path to the Books folder of the shamela database:
# (this folder contains subfolders with the separate book .mdb files)
books_folder = r"test\shamela"

# path to the folder that contains the converted metadata files
# (if the metadata has been extracted before):
meta_folder = r"test\shamela"

# path to the folder in which the converted text files should be saved:
conv_folder = r"test\shamela"

# date when the database was downloaded:
download_date = "2020-03-20"

# name and/or url of the downloaded database:
download_source = "al-Maktaba al-Zaydiyya"

# regular expression pattern for file names to be converted:
fn_regex = "32"

# extensions of the files that should be converted:
extensions = ["mdb"]
