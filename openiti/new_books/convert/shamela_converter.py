from collections import defaultdict, OrderedDict
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

class BokJsonConverter(generic_converter.GenericConverter):
    def __init__(self, all_meta=None, additional_meta=None, dest_folder=None):
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


    def convert_file(self, source_fp):
        """Convert one file to OpenITI format.

        Args:
            source_fp (str): path to the file that must be converted.

        Returns:
            None
        """
        if self.VERBOSE:
            print("converting", source_fp)
        dest_fp = self.make_dest_fp(source_fp)
        shamid = re.findall("\d+", source_fp)[-1]

        book_data, toc_data, metadata = self.get_data(source_fp, shamid)

        metadata = self.format_metadata(metadata)

        text, notes = self.format_text(book_data, toc_data, shamid)
        text = self.reflow(text)
        #text = self.add_milestones(text)
        text = self.post_process(text)
        text = self.compose(metadata, text, notes)
        #print(9, text)

        self.save_file(text, dest_fp)
        #print("saved text to", dest_fp)

    def convert_files_in_folder(self, source_folder,
                                extensions=[]):
        if extensions == ["mdb"] or extensions == [".mdb"]:
            self.mdb2json(source_folder)
            print("conversion from mdb to json completed.")
            extensions = ["json"]
            source_folder = os.path.join(source_folder, "json")
            print("Converting from json to txt...")
        super().convert_files_in_folder(source_folder, extensions=extensions)

    def mdb2json(self, source_folder):
        dest_folder = os.path.join(source_folder, "json")
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        mdb_files = []
        for root, dirs, files in os.walk(source_folder):
            for fn in files:
                if fn.endswith(".mdb"):
                    mdb_files.append(os.path.join(root, fn))
        print("Converting {} .mdb files to json".format(len(mdb_files)))
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
            print("finished")        

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
        
        book_data = data["b"+shamid]

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

        return book_data, toc_data, book_meta

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

        self.struct_dict = format_struct_dict(toc)
        text = ["### |EDITOR|\n", ]
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
            
            passage_text, notes = self.remove_notes(passage_text, notes)

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
                text.append(row["nass"] + "\n\n\n----NO PAGE NO------\n\n\n\n")                    
        
        # compile text and endnote strings from lists:
        text = "".join(text)
        notes = "".join(notes)

        return text, notes
                    
        

    def remove_notes(self, passage_text, notes):
        """Remove footnotes from the passage_text and add them to notes list."""
        footnotes = re.findall(self.footnote_regex,
                               passage_text, flags=re.DOTALL)
        if footnotes:
            fmt = "PageV{:02d}P{:03d}:\n\n{}\n\n"
            notes.append(fmt.format(vol_no, page_no, footnotes[0]))       
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
            tit = deNoise(el["tit"])
            #print("title", tit)
            tit_regex = re.sub("(\w+)", r"W\1", tit)[1:]
            tit_regex = re.sub("\W+", r"", tit_regex)
            tit_regex = re.sub("W", r"\W*", tit_regex)
            tit_regex = ".*{}.*".format(tit_regex)
            #print("regex", tit_regex)
            if re.findall(tit_regex, passage_text):
                r = "\n\n### {} AUTO ".format(int(lvl)*"|")+r"\1\n\n"
                passage_text = re.sub("[\n\r¶]*({})".format(tit_regex),
                                      r, passage_text)
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
        for k,v in additional_meta.items():
            m.append(fmt.format(k,v))
        metadata = "\n\n".join(m)
        return self.magic_value + metadata + self.header_splitter

    def pre_process(self, text):
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
        text = re.sub(r" *\n+ *(PageV\d+P\d+)\n+", r" \1 ", text)
        # restore new lines when the page number is preceded by a relevant character:
        text = re.sub(r"""([.:!؟|*"]|AUTO|CHECK) +(PageV\d+P\d+) """,
                      r"\1\n\n\2\n\n", text)
        # restore new lines when the page number is followed by ###:
        text = re.sub(r"""\s+(PageV\d+P\d+)\s+(\#+)""", r"\n\n\1\n\n\2", text)
        # double the new lines when the page number is preceded by a relevant character
        #text = re.sub("""(?<=[.:!؟|*"])\n+(PageV\d+P\d+)""", r"\n\n\1", text)

        text = re.sub("(PageV\d+P\d+)(\n\n)(?!#)", r"\1\2# ", text)

        text = re.sub("\n{2,}", "\n\n", text)

        return text



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
                metadata of each book in the Shamela metadata table 'Main'
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



if __name__ == "__main__":

##    meta_fp = r"Zaydiyya_metadata_reform.json"    
##    with open(meta_fp, mode="r", encoding="utf-8") as file:
##        all_meta = json.load(file)

    #extract_metadata(r"Zaydiyya\Files", r"metadata")
    meta_fp = r"metadata\main_metadata_reform.json"
    with open(meta_fp, mode="r", encoding="utf-8") as file:
        all_meta = json.load(file)
    
    additional_meta = OrderedDict()
    additional_meta["ScrapeDate"] = "21-02-2020"
    additional_meta["ScrapedFrom"] = "al-Maktaba al-Shamela al-Zaydiyya"

    src_folder = r"test"
    dest_folder = r"test"
    VERBOSE=False

    conv = BokJsonConverter(all_meta=all_meta,
                            additional_meta=additional_meta,
                            dest_folder=dest_folder)
    conv.convert_files_in_folder(src_folder, extensions=[".mdb"])
