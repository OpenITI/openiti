"""A Converter for al-Maktaba al-Shamela databases to OpenITI mARkdown format.

Al-Maktaba al-Shamela is a digital text collection, but it also 
developed its own reader, which is based on an internal database.

A large number of texts are available on its website (www.shamela.ws), 
and can be downloaded in EPUB or .bok format (the latter is a zipped .mdb file). 
These files must be converted with another script. 
See https://github.com/OpenITI/raw_SHAM19Y/wiki for that conversion process.

However, the program also allows users to add texts from other sources
(incl. their own transcriptions) to the program's database.
The database can be zipped, together with an executable for the reader,
and disseminated. Some users have used this ability
of the program to create their own collections that include many
texts not available in the original program
(for ideological or other reasons), e.g.,

* al-maktaba al-shamela al-dhahabiyya
* al-maktaba al-shamela al-ibadiyya
* al-maktaba al-shamela al-zaydiyya
* etc.

Database structure
==================

The database consists of a large number of folders and files:

* ``./Files/Main.mdb``: contains the metadata for every book in the program,
    in a table called “0bok”
* ``./Files/special.mdb``: contains more metadata + data that could be
    marked up in the text (like Qur’anic passages)
* ``./Books``: contains 10 folders, named "0" to "9", that each contain
    a large number of .mdb files (one .mdb file per text; filename = id number)

NB: in some versions of the database, the books are actually in
in large multi-book .mdb files in another folder (``./Books/Archive``),
which contains large .mdb files, each ca. 600 MB;
each of these contain the bxxxx and txxxx tables for a couple
of thousand books (xxxx being the Shamela id of the book):

- bxxxx contains the text
- txxxx contains the section titles

Module description
==================

This module contains two major components:

* ``extract_metadata``: extracts the metadata from the shamela database
* ``BokJsonConverter`` class: extracts the text and book structure
  from the books' .mdb files into json format,
  fuses this with the book's metadata,
  and converts it into OpenITI mARkdown format

The main component of the module, the BokJsonConverter class,
is a subclass of the GenericConverter from the generic_converter module:

GenericConverter
    \_ GenericEpubConverter
    \_ BokJsonConverter

Methods of both classes:
(methods of GenericConverter are inherited by GenericHtmlConverter;
methods of GenericConverter with the same name
in GenericHtmlConverter are overwritten by the latter)

=================================== =====================================
GenericConverter                    BokJsonConverter
=================================== =====================================
__init__                            __init__ (appended)
convert_files_in_folder             convert_files_in_folder
convert file                        convert file
make_dest_fp                        (inherited - generic!)
get_metadata (dummy)                (metadata collected in get_data step)
get_data                            get_data
pre_process                         pre_process
add_page_numbers (dummy)            (pages added in get_data step)
add_structural_annotations (dummy)  add_structural_annotations
remove_notes (dummy)                remove_notes
reflow                              (inherited)
add_milestones (dummy)              (inherited - dummy!)
post_process                        post_process
compose                             (inherited)
save_file                           (inherited)
                                    mdb2json
                                    format_text
                                    format_metadata
=================================== =====================================

"""


from collections import defaultdict, OrderedDict
from datetime import datetime
import json
import os
import re

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.new_books.convert import generic_converter
from openiti.helper.ara import deNoise
from openiti.new_books.convert.helper import bok

VERBOSE = False



def main(meta_folder=None, files_folder=None, books_folder=None,
         conv_folder=None, download_date="", download_source="",
         config_fp=None, extensions=["mdb"], fn_regex=None, verbose=False,
         multiple_books_in_mdb=False, overwrite=True):
    """Collect the variables and carry out the conversion.

    Args:
        meta_folder (str): path to the folder containing metadata extracted
            from the database
        files_folder (str): path to the `Files` folder of the database
            (containing the main metadata database files)
        books_folder (str): path to the `Bookss` folder of the database
            (containing the .mdb files containing the text of the books)
        conv_folder (str): path to the folder where the converted files should
            be stored
        download_date (str): (approximate) date when the database was downloaded
        download_source (str): name and/or dowload url of the database
        config_fp (str): path to a config.py file containing
            the above-mentioned parameters
            NB: to print an empty config file: print_default_config_file()
    """
    # 0- import configuration if configuration file is given:

    if config_fp:
        import shutil
        shutil.copyfile(config_fp, "./temp_config.py")
        from temp_config import files_folder, books_folder, meta_folder,\
            conv_folder, download_date, download_source, fn_regex, extensions
        os.remove("temp_config.py")

    # 1a- collect metadata (extract it if it has not been extracted yet):

    if not meta_folder:
        if files_folder:
            meta_folder = os.path.join(os.path.dirname(files_folder),
                                       "extracted_metadata")
            extract_metadata(files_folder, meta_folder)
        else:
            print("Has the metadata already been extracted?")
            resp = input("Y/N? ")
            if resp.upper() == "Y":
                print("Provide the path to the folder that contains the \
metadata json files:")
                meta_folder = input()
            else:
                print("Provide the path to the `Files` folder of the \
Shamela database:")
                files_folder = input()
                if not re.match("(?:\A|[\\/])Files[\\/]?", folder):
                    msg = "folder path should end with `Files` or `Files/`"
                    raise Exception(msg)
                meta_folder = os.path.join(os.path.dirname(files_folder),
                                           "extracted_metadata")
                extract_metadata(files_folder, meta_folder)
        if not books_folder:
                  books_folder = os.path.join(os.path.dirname(meta_folder),
                                   "Books")

    if not books_folder:
        print("Provide the path to the `Books` folder of the Shamela database:")
        books_folder = input()
    if not conv_folder:
        conv_folder = books_folder+"Converted"

    meta_fp = os.path.join(meta_folder, r"main_metadata_reform.json")
    with open(meta_fp, mode="r", encoding="utf-8") as file:
        all_meta = json.load(file)

    # 1b - Add some additional metadata:

    if not download_date:
        print("Write the (approximate) date when the library was downloaded: ")
        download_date = input()
    if not download_source:
        print("write the name and/or url of the downloaded library: ")
        download_source = input()

    additional_meta = OrderedDict()
    additional_meta["DownloadSource"] = download_source
    additional_meta["DownloadDate"] = download_date
    additional_meta["ConversionDate"] = datetime.today().strftime('%Y-%m-%d')

    # 2- convert files:

    conv = BokJsonConverter(all_meta=all_meta,
                            additional_meta=additional_meta,
                            dest_folder=conv_folder,
                            multiple_books_in_mdb=multiple_books_in_mdb,
                            overwrite=overwrite)
    if verbose:
        conv.VERBOSE = True
    conv.convert_files_in_folder(books_folder,
                                 dest_folder=conv_folder, extensions=extensions,
                                 fn_regex=fn_regex)
    print("Converted files can be found in", conv_folder)
    print("(metadata in {})".format(meta_folder))


################################################################################




class BokJsonConverter(generic_converter.GenericConverter):
    """Extract book data from .mdb files into json, and convert into mARkdown.
    """

    def __init__(self, all_meta=None, additional_meta=None,
                 dest_folder=None, multiple_books_in_mdb=False,
                 overwrite=True):
        """Set up the main variables of the class.

        Args:
            all_meta (dict): dictionary representation of the
                main metadata table (./Files/Main.mdb) of the Shamela
                desktop program.
                Should only be provided for data directly derived
                from the Shamela desktop program.
                Bok-file derived jsons contain the metadata themselves.
            additional_meta (dict): a dictionary containing metadata
                not contained in the Shamela metadata
                that should be added to the metadata
        """
        super().__init__()
        self.all_meta = all_meta
        self.additional_meta = additional_meta
        if dest_folder:
            self.dest_folder = dest_folder  # otherwise: default "converted"
        self.footnote_regex = r"[\r\¶\n ]*¬?_{5,}[\r\n\¶ ]*(.*)"
        self.multiple_books_in_mdb = multiple_books_in_mdb
        self.OVERWRITE = overwrite


    def convert_file(self, source_fp, dest_fp=None):
        """Convert one file to OpenITI format.

        Args:
            source_fp (str): path to the file that must be converted.

        Returns:
            None
        """
        if self.VERBOSE:
            print("converting", source_fp)
        if dest_fp == None:
            dest_fp = self.make_dest_fp(source_fp)
        if not self.OVERWRITE and os.path.exists(dest_fp):
            print("Not overwriting already existing file:", dest_fp)
            print("Set self.overwrite to True if you want to overwrite")
            return
        
        shamid = re.findall("\d+", source_fp)[-1]

        book_data, toc_data, metadata, shamid = self.get_data(source_fp, shamid)
        

        metadata = self.format_metadata(metadata)

        text, notes = self.format_text(book_data, toc_data, shamid)
        text = re.sub(" *LINE_END *", "\n# ", text)
        text = self.reflow(text)
        #text = self.add_milestones(text)
        text = self.post_process(text)
        notes = self.reflow(notes)
        notes = re.sub("(\n+)(?![\n~P])", r"\1# ", notes)
        notes = re.sub("(?:[\r\n]*# )? *LINE_END *", "\n# ", notes)
        text = self.compose(metadata, text, notes)
        #print(9, text)

        self.save_file(text, dest_fp)
        #print("saved text to", dest_fp)

    def convert_files_in_folder(self, source_folder, dest_folder=None,
                                extensions=[], fn_regex=None):
        if "mdb" in " ".join(extensions):
            json_folder = self.mdb2json(source_folder, fn_regex=fn_regex)
            print("conversion from mdb to json completed.")
            extensions = ["json"]
            source_folder = json_folder

        if dest_folder:
            self.dest_folder = dest_folder
        else:
            self.dest_folder = os.path.join(self.dest_folder, "txt")
        print("Converting from json to txt...")
        super().convert_files_in_folder(source_folder, extensions=extensions,
                                        fn_regex=fn_regex)

    def mdb2json(self, source_folder, fn_regex=None):
        """Convert mdb files to json files.

        The .mdb files are usually in the Books folder,
        in subfolders numbered "0" to "9".
        The converted files will be saved in <self.dest_folder>/json/"""
        dest_folder = os.path.join(self.dest_folder, "json")
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        mdb_files = []
        for root, dirs, files in os.walk(source_folder):
            for fn in files:
                if fn_regex:
                    if fn.endswith(".mdb") and re.findall(fn_regex, fn):
                        mdb_files.append(os.path.join(root, fn))
                else:
                    if fn.endswith(".mdb"):
                        mdb_files.append(os.path.join(root, fn))
        print("Converting {} .mdb files to json".format(len(mdb_files)))
        failed = []
        for fp in mdb_files:
            shamid = re.findall("\d+", fp)[-1]
            outfp = os.path.join(dest_folder, shamid+".json")

            print("connecting to db {}...".format(fp))
            conn, cur = bok.connect_to_db(fp)

            print("converting db to dict...")
            d = bok.mdb2dict(cur, VERBOSE=False)
            #print(d.keys())
            #input()

            print("saving to json...")
            if self.multiple_books_in_mdb:
                for k in d:
                    if k.startswith("b"):
                        shamid = k[1:]
                        outfp = os.path.join(dest_folder, shamid+".json")
                        try:
                            t = d["t"+shamid]
                        except:
                            print(k, "TITLE TABLE MISSING!")
                            t = {}
                        try:
                            b = d["b"+shamid]
                        except Exception as e:
                            print(k)
                            print(e)
                            b = {}
                        if b:
                            bok.save_to_json({"b"+shamid: b,
                                              "t"+shamid: t},
                                             outfp)
                        else:
                            print("CONVERSION FAILED")
                            failed.append(shamid)
##                        try:
##                            bok.save_to_json({"b"+shamid: d["b"+shamid],
##                                              "t"+shamid: d["t"+shamid]},
##                                             outfp)
##                        except:
##                            print(k)
##                            print("TITLE TABLE MISSING!")
##                            try:
##                                bok.save_to_json({"b"+shamid: d["b"+shamid],
##                                                  "t"+shamid: {}},
##                                                 outfp)
##                            except:
##                                print("CONVERSION FAILED")
##                                failed.append(shamid)
            else:
                try:
                    bok.save_to_json({"b"+shamid: d["book"],
                                      "t"+shamid: d["title"]},
                                     outfp)
                except:
                    print("TITLE TABLE MISSING!")
                    try:
                        bok.save_to_json({"b"+shamid: d["book"],
                                          "t"+shamid: {}},
                                         outfp)
                    except:
                        print("CONVERSION FAILED")
                        failed.append(fp)
                print("finished")
        if failed:
            print("Conversion of these {} files failed:".format(len(failed)))
            for f in failed:
                print("    ", f)
            input("Press Enter to continue")
        else:
            if VERBOSE:
                msg = "all {} mdb files converted ".format(len(mdb_files))
                print(msg + "successfully to", dest_folder)
        return dest_folder

    def get_data(self, source_fp, shamid):
        """Extract the data from the source_fp and format it in OpenITI format.

        ### Overwrite this method in subclass ###

        Args:
            source_fp (str): path to the original file

        Returns:
            text (str): the text in its initial state
        """
        with open(source_fp, mode="r", encoding="utf-8") as file:
            data = json.load(file)

        try:
            book_data = data["b"+shamid]
        except:
            # sometimes, the ID number on the website is not the id number inside the file:
            shamid = [k[1:] for k in data if re.match("b\d+", k)][0]
            book_data = data["b"+shamid]

        # make sure all keys in the dictionary are lower-case:
        book_data = [{k.lower():v for k,v in d.items()} for d in book_data]

        # load the table of contents:
        toc_data = data["t"+shamid]

        # get the book's metadata.
        # For data converted from bok files,
        # extract it from the "Main" dictionary in the data dict;
        # If extracted from the Shamela program,
        # extract it from the dictionary that
        # contains metadata of all the books:

        if self.all_meta:
            book_meta = self.all_meta[shamid]
        else:
            book_meta = data["Main"]

        return book_data, toc_data, book_meta, shamid

    def format_text(self, book, toc, book_id):
        """Extract text from json, add page numbers and headings.

        Args:
            book (list): a list of  dictionaries
                (keys: id, nass, page, part, [seal])
            toc (list): a list of dictionaries
                (keys: id, tit, lvl, [sub])

        Returns:
            text (str): the formatted text
        """
        def make_numeric(n):
            if str(n).isnumeric():
                return int(n)
            else:
                return 0

        def format_struct_dict(toc):
            """turn the table of contents list into a dictionary.

            Args:
                toc (list): a list of dictionaries
                    (keys: id, tit, lvl, [sub])

            Returns:
                struct_dict (dict): key: id (i.e., the text fragment id;
                    value: list dictionaries that have the same id
                    (keys: id, tit, level, sub)
            """
            struct_dict = defaultdict(list)
            for row in toc:
                struct_dict[row["id"]].append(row)
            return struct_dict
        print(toc)
        self.struct_dict = format_struct_dict(toc)
        #text = ["### |EDITOR|\n", ]
        text = []
        notes = []
        page_no = 0
        vol_page = ""
        try:
            book = sorted(book, key=lambda k: int(k["id"]))
        except Exception as e:
            print("book no.", book_id, ": unable to sort pages by id:", e)
            print("Attempting to sort by volume and page number...")
            try:
                book = sorted(book, key=lambda k: (int(k["part"]), int(k["page"])))
                print("successful")
            except:
                try:
                    book = sorted(book, key=lambda k: (int(k["Part"]), int(k["page"])))
                    print("successful")
                except:
                    print("book no.", book_id, ": unable to sort pages by volume and page:", e)
                    print("Keep book in the current order.")

        for row in book:
            # set variables for current row:

            if VERBOSE:
                print("vol {} page {} id {} : {}".format(row["part"],
                                                         row["page"],
                                                         row["id"],
                                                         row["nass"][:30]))
            passage_text = row["nass"]
            passage_id = row["id"]
            page_no = make_numeric(row["page"])
            vol_no = make_numeric(row["part"])
            vol_page = "\n\nPageV{:02d}P{:03d}\n\n".format(vol_no, page_no)



            # remove the short vowels etc.:

            passage_text = self.pre_process(passage_text)

            # remove the footnotes:

            passage_text, notes = self.remove_notes(passage_text, notes, vol_no, page_no)

            # add the structural formatting:

            if passage_id in self.struct_dict:
                passage_text = self.add_structural_annotations(passage_text,
                                                               passage_id)
            passage_text = re.sub("[\n\r¶]+ *(?![#\|P])", "\n\n# ", passage_text)

            if VERBOSE:
                print("vol {} page {} id {} : {}".format(vol_no,
                                                         page_no,
                                                         passage_id,
                                                         passage_text[:100]))
                input()

            text.append(passage_text)

            # add page numbers:

            if row["page"] != None:
                text.append(vol_page)
            else:
                if row["nass"]:
                    text.append(row["nass"] + "\n\n\n----NO PAGE NO------\n\n\n\n")

        # compile text and endnote strings from lists:
        text = "".join(text)
        if notes:
            notes = "\n\n### |EDITOR|\nENDNOTES\n\n" + "".join(notes)
        else:
            notes = ""

        return text, notes

    def remove_notes(self, passage_text, notes, vol_no, page_no):
        """Remove footnotes from the passage_text and add them to notes list."""
        footnotes = re.findall(self.footnote_regex,
                               passage_text, flags=re.DOTALL)
        if footnotes:
            fmt = "\n\n{}\nPageV{:02d}P{:03d}"
            notes.append(fmt.format(footnotes[0], vol_no, page_no))
            passage_text = re.sub(self.footnote_regex, "",
                                  passage_text, flags=re.DOTALL)
        return passage_text, notes

    def add_structural_annotations(self, passage_text, passage_id):
        """Add structural tags to titles in passage_text."""
        #print("passage_id", passage_id)
        for el in sorted(self.struct_dict[passage_id],
                         key= lambda item: item["lvl"],
                         reverse=True):
            lvl = el["lvl"]
            try:
                tit = deNoise(el["tit"])
            except:
                tit = "[NO TITLE]"
            # create a regex for the title that disregards non-alphanumeric characters:
            tit_regex = re.sub("(\w+)", r"W\1", tit)[1:]
            tit_regex = re.sub("\W+", r"", tit_regex)
            tit_regex = re.sub("W", r"\\W*", tit_regex)
            tit_regex = ".*{}.*".format(tit_regex)
            #print("regex", tit_regex)
            if re.findall(tit_regex, passage_text):
                r = "\n\n### {} AUTO ".format(int(lvl)*"|")+r"\1\n\n"
                passage_text = re.sub("[\n\r¶]*({})".format(tit_regex),
                                      r, passage_text, count=1)
            else:
                if VERBOSE:
                    print("!!!title not inside text", tit)
                t = "\n\n### {} CHECK [{}]\n\n".format(int(lvl)*"|", tit)
                passage_text = t + passage_text
        #print(passage_text[:120])
        return passage_text

    def format_metadata(self, metadata):
        """Convert the metadata in the metadata dict to a string."""
        m = []
        fmt = "#META# {}: {}"
        try:
            for k,v in metadata.items():
                pass
        except: 
            metadata = metadata[0]
        for k,v in metadata.items():
            if v:
                # treat the "betaka" field different from the other fields.
                # It contains a multi-line string with a number of headings.
                # Store each of these headings with their value separately:

                if k == "betaka":
                    m.append(fmt.format("Shamela_short_metadata_record", ""))
                    betaka = re.split("[\n\r]+", v)
                    for b in betaka:
                        b = re.split(": ", b, maxsplit=1)
                        if len(b)>1:
                            m.append(fmt.format(b[0], b[1]))
                        else:
                            m.append(fmt.format("digitization_comments", b[0]))
                else:
                    #print(col_headers[i], field)
                    #print(re.sub(r"\.?\n+", ". ", str(field)))
                    m.append(fmt.format(k, re.sub(r"\.?[\r\n]+", ". ", str(v))))
        try:
            for k,v in self.additional_meta.items():
                m.append(fmt.format(k,v))
        except:
            if VERBOSE:
                print("no additional metadata")
        metadata = "\n\n".join(m)
        metadata = re.sub("(?: *LINE_END *)+", " ¶ ", metadata)
        return self.magic_value + metadata + self.header_splitter

    def pre_process(self, text):
        if not text:
            return ""
        text = re.sub(" ?¶ ?", "\n\n", text)
        text = super().pre_process(text)
        return text

    def post_process(self, text):
        """Carry out post-processing operations on the text.

        ### Overwrite this method in subclass ###

        Args:
            text (str): the text in its current conversion state

        Returns:
            texgt (str): the text after post-processing operations.
        """
        # remove unwanted spaces:
        text = re.sub("  +", " ", text)
        text = re.sub("\n ", "\n", text)
        text = re.sub("\n# ?\n+", "\n", text)

        #print(text[:50000])

        # remove the new lines before page numbers:
        text = re.sub(r" *\n+ *(PageV\d+P\d+)\n+", r" \1\n~~", text)
        # restore new lines when the page number is preceded by a relevant character:
        text = re.sub(r"""([.:!؟|*"]|AUTO|CHECK) +(PageV\d+P\d+)\n~~""",
                      r"\1\n\n\2\n\n", text)
        # restore new lines when the page number is followed by ###:
        text = re.sub(r"""\s+(PageV\d+P\d+)\n~~\s*(\#+)""", r"\n\n\1\n\n\2", text)
        # double the new lines when the page number is preceded by a relevant character
        #text = re.sub("""(?<=[.:!؟|*"])\n+(PageV\d+P\d+)""", r"\n\n\1", text)

        text = re.sub("(PageV\d+P\d+)(\n\n+)(?!#)", r"\1\2# ", text)

        text = re.sub("\n{2,}", "\n", text)
        text = re.sub("[\r\n]+# *(?:[\r\n]+|\Z)", "\n", text)

        text = re.sub(" ### ", "\n### ", text)

        return text


################################################################################


def extract_metadata(files_folder, outfolder):
    """Extract the book metadata from the Files folder of the Shamela program.

    The metadata is located in two separate mdb files:
    
    * Files/main.mdb
    * Files/special.mdb

    The metadata is extracted into json files in the outfolder:
    
    * [outfolder]/main_metadata.json: full metadata from Files/main.mdb
      in json format (dictionary). Under key "0bok" it contains a
      list of metadata dictionaries, one for each book in the collection
    * [outfolder]/special_metadata.json: full metadata from Files/special.mdb
      in json format
    * [outfolder]/genres.json: a dictionary of genres and their ids
      extracted from main.mdb
    * [outfolder]/Authors_metadata.json: a dictionary of authors and their ids
      extracted from special.mdb
    * [outfolder]/main_metadata_reform.json: a reformatted version of
      main_metadata.json (dictionary of dictionaries, one for each book:
      key = bookID, value = book metadata in dictionary format)

    Only main_metadata_reform.json is necessary for the conversion
    of Shamela mdb files to txt.
    """
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    # extract metadata from special.mdb (most importantly, the author metadata):
    fp = os.path.join(files_folder, "special.mdb")
    conn, cur = bok.connect_to_db(fp)
    d = bok.mdb2dict(cur, VERBOSE=False)
    print("Saving special.mdb to json...")
    bok.save_to_json(d, os.path.join(outfolder, "special_metadata.json"))
    print("Saving authors_dict...")
    authors_dict = {row["authid"]: row for row in d["Auth"]}
    bok.save_to_json(authors_dict,
                     os.path.join(outfolder, "Authors_metadata.json"))
    conn.close()

    # extract metadata from main.mdb:
    fp = os.path.join(files_folder, "main.mdb")
    conn, cur = bok.connect_to_db(fp)
    d = bok.mdb2dict(cur, VERBOSE=False)
    bok.save_to_json(d["0cat"], os.path.join(outfolder, "genres.json"))
    reformatted_list = reformat_metadata(d, authors_dict)
    d = {"0bok" : reformatted_list}
    bok.save_to_json(d, os.path.join(outfolder, "main_metadata.json"))
    conn.close()

    # save metadata also in dictionary format (key = bookID, value = data):
    new = dict()
    books = d["0bok"]
    for book_data in sorted(books, key=lambda x: int(x["bkid"])):
        #print(book_data["bkid"])
        if int(book_data["bkid"])%1000 == 0:
            print(book_data["bkid"])
        if book_data["bkid"] in new:
            print(book_data["bkid"], "double!")
        new[book_data["bkid"]] = book_data

    outfp = os.path.join(outfolder, "main_metadata_reform.json")
    with open(outfp, mode="w", encoding="utf-8") as file:
        json.dump(new, file, ensure_ascii=False, indent=4, sort_keys=True)




def reformat_metadata(d, authors_dict):
    """Reformats the Shamela Betaka

    The Shamela metadata table contains a field called 'betaka',
    i.e., a kind of human-readable index card of the main metadata
    of the book (author, title, etc.).
    The betaka field is a string, with key: value pairs split by
    new lines. This function splits the metadata in the
    betaka string and adds it to the meta dictionary.

    Args:
        d (dict): a dictionary containing two items:
            d["0bok"]: a list of dictionary representations of the
            metadata of each book in the Shamela metadata table 'Main'.
            d["0cat"]: a list of dictionary representations of the
            genre metadata in the Shamela metadata table
            (keys: id, name, catord, lvl)
    Returns:
        meta (list): the same list of dictionaries, but with the metadata
            in the betaka field split out into keys and values
    """
    genres = {row["id"] : row for row in d["0cat"]}
    meta = d["0bok"]

    for i, row in enumerate(meta):

        # reformat the betaka:

        if row["betaka"]:
            meta = reformat_betaka(meta, i, row)

        # replace the genre id with the genre name:

        if row["cat"]:
            id_ = row["cat"]
            meta[i]["cat"] = genres[id_]["name"]

        if row["authno"]:
            id_ = row["authno"]
            for k,v in {"auth":"auth",
                        "higrid":"higrid",
                        "ad":"ad",
                        "Lng":"lng",
                        "authinf":"inf"}.items():
                if authors_dict[id_][v]:
                    if k in meta[i]:
                        if meta[i][k]:
                            if authors_dict[id_][v] not in meta[i][k]:
                                meta[i][k] += " :: " + authors_dict[id_][v]
                        else:
                            meta[i][k] = authors_dict[id_][v]
                    else:
                        meta[i][k] = authors_dict[id_][v]
    return meta


def reformat_betaka(meta, i, row):
    """Reformats the Shamela Betaka

    The Shamela metadata table contains a field called 'betaka',
    i.e., a kind of human-readable index card of the main metadata
    of the book (author, title, etc.).
    The betaka field is a string, with key: value pairs split by
    new lines. This function splits the metadata in the
    betaka string and adds it to the meta dictionary.
    """

    betaka = re.split("[\n\r¶]+", row["betaka"])
    for b in betaka:
        b = re.split(": ", b, maxsplit=1)
        if len(b)>1:
            meta[i][b[0].strip()] = b[1].strip()
        else:
            meta[i]["digitization_comments"] = b[0].strip()
    return meta


def print_default_config_file():
    config="""\
# Shamela converter configuration file:

# path to the Files folder of the shamela database
# (this folder contains the main metadata database files):
files_folder = None

# path to the Books folder of the shamela database:
# (this folder contains subfolders with the separate book .mdb files)
books_folder = None

# path to the folder that contains the converted metadata files
# (if the metadata has been extracted before):
meta_folder = None

# path to the folder in which the converted text files should be saved:
conv_folder = None

# date when the database was downloaded:
download_date = ""

# name and/or url of the downloaded database:
download_source = ""

# regular expression pattern for file names to be converted:
fn_regex = None

# extensions of the files that should be converted:
extensions = ["mdb"]

"""
    print(config)



if __name__ == "__main__":
    #print_default_config_file()
    # path to the Files folder of the shamela database
    # (this folder contains the main metadata database files):
    files_folder = r"G:\London\OpenITI\new\Zaydiyya\Zaydiyya\Files"

    # path to the Books folder of the shamela database:
    # (this folder contains subfolders with the separate book .mdb files)
    books_folder = r"G:\London\OpenITI\new\Zaydiyya\Zaydiyya\Books"

    # path to the folder that contains the converted metadata files
    # (if the metadata has been extracted before):
    meta_folder = r"G:\London\OpenITI\new\Zaydiyya\Zaydiyya\extracted_metadata"

    # path to the folder in which the converted text files should be saved:
    conv_folder = r"G:\London\OpenITI\new\Zaydiyya\Zaydiyya\BooksConverted2"

    # date when the database was downloaded:
    download_date = "2020-04-16"

    # name and/or url of the downloaded database:
    download_source = "al-Maktaba al-Shamela al-Zaydiyya"

    # regular expression pattern for file names to be converted:
    fn_regex = "337"

    # extensions of the files that should be converted:
    extensions = ["mdb"]

    main(files_folder=files_folder,
         books_folder=books_folder,
         meta_folder=meta_folder,
         conv_folder=conv_folder,
         download_date=download_date,
         download_source=download_source,
         fn_regex=fn_regex,
         extensions=extensions)
