"""
A library to deal with Shamela's BOK file format.

Bok files are in fact Microsoft Access mdb databases.
The database is accessed using the pypyodbc library
(https://github.com/jiangwen365/pypyodbc).

Problem: the texts are encoded in the Windows-1256 format
instead of UTF-8 in the .bok file.
Pypyodbc has an inbuilt "unicode_results=True" parameter,
but this does not seem to influence the way how the data is read.
Python 3 has difficulties dealing with this,
because it considers any string a unicode string.
Current (convoluted but working) solution for extracting text from bok:
save the text as a temp file, open it with Windows-1256 encoding
(encoding="cp1256") and save it again in utf-8 encoding.
Saving to JSON also seems to do the job.

In order to interact with the database,
use the cursor object cur returned by the connect_to_db function.

Most important functions with the cursor object:

* cur.tables() : get a list of all tables in the database
* cur.execute() : execute an sql string
* cur.description: get the headings of the columns in the current cur object


The bok file contains a number of tables, of which the most important are:

* Main: contains the metadata of the book
* bxxxx (in which xxxx is the Shamela id of the book): contains the text,
  one page per row.
* txxxx (in which xxxx is the Shamela id of the book): contains the headings,
  with reference to the page numbers

List of tables in all bok files in the official Shamela corpus (October 2019):

========== =============== ========================== =======================
table name column name     present in number of files data in number of files
========== =============== ========================== =======================
bxxxx                      7509                       7509
           nass            7509                       7509
           seal            7509                       7509
           id              7509                       7509
           page            7509                       7451
           part            7509                       7449
           hno             1748                       1744
           na              1027                       100
           sora            1027                       100
           aya             1027                       100
           b1              17                         17
           b2              1                          1
           b3              1                          1
           b4              1                          1
           blnk            16                         16
           ppart1          40                         40
           ppage1          40                         40
           ppart2          7                          7
           ppage2          7                          7
           ppart3          7                          7
           ppage3          7                          7
           ppart4          2                          2
           ppage4          2                          2
           done            3                          3
           bhno            1                          1
Main                       7509                       7509
           oauth           7509                       7509
           auth            7509                       7509
           bver            7509                       7509
           oauthver        7509                       7509
           over            7509                       7509
           lng             7509                       7509
           betaka          7509                       7509
           aseal           7509                       7509
           seal            7509                       7509
           bk              7509                       7509
           onum            7509                       7509
           bkid            7509                       7509
           ad              7509                       7509
           cat             7509                       7509
           islamshort      7509                       7508
           authinf         7509                       7265
           higrid          7509                       7265
           pdfcs           7509                       6711
           pdf             7509                       6480
           inf             7509                       5617
           shrtcs          2664                       2124
           tafseernam      7509                       183
           vername         7509                       16
           blnk            7509                       16
txxxx                      7509                       7507
           sub             7509                       7507
           id              7509                       7507
           tit             7509                       7507
           lvl             7509                       7507
abc                        7509                       397
           a               7509                       397
           b               7509                       397
           c               7509                       397
Shorts                     7509                       341
           nass            7509                       341
           ramz            7509                       341
           bk              7509                       341
sPdf                       7509                       236
           part            7509                       236
           sfilename       7509                       236
           onum            7509                       236
men_u                      7509                       148
           id              7509                       148
           name            7509                       148
           bk              7509                       148
avPdf                      7509                       28
           cs              7509                       28
           def             7509                       28
           onum            7509                       28
           vername         7509                       28
           pdfver          7509                       28
men_b                      7509                       17
           id              7509                       17
           manid           7509                       17
           name            7509                       17
           bk              7509                       17
nBound                     7509                       13
           d               7509                       13
           b               7509                       13
           dver            7509                       13
           bver            7509                       13
           bcode           7509                       13
oShr                       7509                       9
           matn            7509                       9
           sharhid         7509                       9
           matnid          7509                       9
           sharh           7509                       9
oShrooh                    7509                       9
           matn            7509                       9
           matnver         7509                       9
           sharhver        7509                       9
           sharh           7509                       9
Shrooh                     7509                       0
           matn            7509                       0
           sharhid         7509                       0
           matnid          7509                       0
           sharh           7509                       0
com                        7509                       0
           id              7509                       0
           com             7509                       0
           bk              7509                       0
men_h                      7509                       0
           id              7509                       0
           name            7509                       0
           upg             7509                       0
10759                      1                          1
           wrd             1                          1
           pos             1                          1
10786                      1                          1
           wrd             1                          1
           pos             1                          1
10772                      1                          1
           wrd             1                          1
           pos             1                          1
10769                      1                          1
           wrd             1                          1
           pos             1                          1
10773                      1                          1
           wrd             1                          1
           pos             1                          1
========== =============== ========================== =======================

"""


import pypyodbc
import json
import re


def connect_to_db(fp):
    """Connect to the mdb database in the bok file.

    Uses pypyodbc (https://github.com/jiangwen365/pypyodbc)

    Args:
        fp (str): path to the bok file

    Returns:
        conn: a pypyodbc connection object. Needs to be closed (conn.close())\
          at the end of the database session
        cur: a pypyodbc cursor object, needed to execute SQL"""
    # connect to the database:
    conn = pypyodbc.connect(r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
                            + r"Dbq={};unicode_results=True".format(fp))
    #NB: unicode_results doesn't seem to have any influence: setting it to False
    #or leaving it out gives the exact same result

    cur = conn.cursor()

    return conn, cur


def close_db(conn):
    """Close the database connection.

    Args:
        conn: pypyodbc connection object.

    Returns:
        None
    """
    conn.close()


def mdb2dict(cur, VERBOSE=False):
    """
    Save the data tables in the mdb database in a dictionary

    Args:
        cur: a pypyodbc cursor object, needed to execute SQL
        VERBOSE (bool): if True, table names will be printed

    Returns:
        d (dict): a dictionary containing all tables in the database:
            * key: table name
            * value: list of dictionary representations for each row
                               \-> key: column header
                                   value: cell value
                                       (for current row and column)
    """
    if VERBOSE:
        print("Table names:")
    d = dict()
    all_tables = cur.tables()
    for table in list(all_tables):
        # check if the table is a data table:
        if table[3] == "TABLE":
            if VERBOSE:
                print("    ", table)
            table_name = table[2]
            d[table_name] = []
            cur.execute("""SELECT * from {}""".format(table[2]))
            headings = [d[0] for d in cur.description]
            for row in cur.fetchall():
                row_dict = dict()
                for i, heading in enumerate(headings):
                    if row[i]:
                        val = re.sub(r"[\r\n]+", " ¶ ", str(row[i]))
                        val = val.replace("\t", "")
                    else:
                        val = None
                    row_dict[heading] = val
                d[table_name].append(row_dict)
    return d


def save_to_json(d, fp):
    """
    Save the dictionary to a json file

    Args:
        d (dict): a dictionary
        fp (str): the path to the destination json file

    Returns:
        None
    """
    with open(fp, "w", encoding="utf-8") as file:
        json.dump(d, file, sort_keys=True, indent=4, ensure_ascii=False)


def print_table_and_column_names(cur):
    """
    print a list of all tables (and their column headings) in the database

    Args:
        cur: a pypyodbc cursor object, needed to execute SQL

    Returns:
        None
    """
    all_tables = cur.tables()
    print()
    for table in list(all_tables):
        if table[3] == "TABLE":
            cur.execute("""SELECT * from {}""".format(table[2]))
            print("Table", table[2], ": column names:")
            for heading in ["   "+d[0] for d in cur.description]:
                print(heading)



if __name__ == "__main__":
    fp = r"D:\London\OpenITI\bok\ShamelaRARs\converted\2_bok\0008.bok"
    conn, cur = connect_to_db(fp)
    print_table_and_column_names(cur)
    d = mdb2dict(cur, VERBOSE=False)
    save_to_json(d, "test_bok2json.json")
    close_db(conn)

