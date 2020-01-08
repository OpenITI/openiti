"""A generic converter for text into OpenITI format.

Subclass the GenericConverter to make a converter for a new
source of scraped books.

TO DO:
    import the deNoise function from the library instead of
        defining it here in the module.
"""

import os
import re
import textwrap


def deNoise(text):
    """Eliminate all diacritics from the text."""
    noise = re.compile(""" َ  | # Fatha
                             ً  | # Tanwin Fath
                             ُ  | # Damma
                             ٌ  | # Tanwin Damm
                             ِ  | # Kasra
                             ٍ  | # Tanwin Kasr
                             ْ  | # Sukun
                             ـ | # Tatwil/Kashida
                             ّ # Tashdid
                             """, re.VERBOSE)
    text = re.sub(noise, "", text)
    text = re.sub("ﭐ", "ا", text) # replace alif-wasla with simple alif
    return text

class GenericConverter(object):

    def __init__(self):
        """Initialize the default values."""
        self.magic_value = "######OpenITI#\n\n\n"
        self.header_splitter = "\n\n#META#Header#End#\n"
        self.endnote_splitter = "\n\n### |EDITOR|\nENDNOTES:\n\n"
        self.dest_folder = "converted"
        self.extension = ".automARkdown"

        # settings for the chunking of the text:

        self.chunk_length = 300
        self.milestone_tag = "Milestone300"

        # regexes describing Arabic characters and tokens:

        self.ara_char = "[؀-ۿࢠ-ࣿﭐ-﷿ﹰ-﻿]"
        ara_tok = "{}+|[^{}+".format(self.ara_char, self.ara_char[1:])
        self.ara_tok = re.compile(ara_tok)

##        self.conversion_procedure(source_fp, dest_dir)


    def convert_files_in_folder(self, source_folder, extensions=[]):
        """Convert all files in a folder to OpenITI format.

        Args:
            source_folder (str): path to the folder that contains
                the files that must be converted.
            extensions (list): list of extensions; if this list is not empty,
                only files with an extension in the list should be converted.

        Returns:
            None
        """
        for source_fn in os.listdir(source_folder):
            if extensions:

                # make sure extensions are preceded by a period:

                extensions = [re.sub("\.+", ".", "."+ext) for ext in extensions]

                # convert a file only if its extension is in the list:

                if os.path.splitext(source_fn)[-1] in extensions:
                    self.convert_file(os.path.join(source_folder, source_fn))
            else:
                self.convert_file(os.path.join(source_folder, source_fn))


    def convert_file(self, source_fp):
        """Convert one file to OpenITI format.

        Args:
            source_fp (str): path to the file that must be converted.

        Returns:
            None
        """
        print("converting", source_fp)
        dest_fp = self.make_dest_fp(source_fp)
        metadata = self.get_metadata(source_fp)

        text = self.get_data(source_fp)
        #print(1, text)
        text = self.pre_process(text)
        #print(2, text)

        text = self.add_page_numbers(text)
        #print(3, text)
        text = self.add_structural_annotations(text)
        #print(4, text)
        text, notes = self.remove_notes(text)
        #print(5, text)
        text = self.reflow(text)
        #print(6, text)
        text = self.add_milestones(text)
        #print(7, text)

        text = self.post_process(text)
        #print(8, text)

        text = self.compose(metadata, text, notes)
        #print(9, text)

        self.save_file(text, dest_fp)
        #print("saved text to", dest_fp)


    def make_dest_fp(self, source_fp):
        """Make a filepath for the converted text file.

        ### Overwrite this method in subclass ###

        Args:
            source_fp (str): path to the file that must be converted.

        Returns:
            dest_fp (str): path to the converted text file.
        """
##        print("""WRITE A make_dest_fp FUNCTION \
##THAT CREATES A FILEPATH FOR THE CONVERTED TEXT FILE.""")
        source_folder, source_fn = os.path.split(source_fp)
        source_fn = os.path.splitext(source_fn)[0]+self.extension
        if self.dest_folder == "converted":
            self.dest_folder = os.path.join(source_folder, "converted")
        self.dest_fp = os.path.join(self.dest_folder, source_fn)
        return self.dest_fp


    def get_metadata(self, source_fp):
        """Gets the metadata from the file at source_fp.

        ### Overwrite this method in subclass ###

        Args:
            source_fp (str): path to the original file

        Returns:
            metadata (str): metadata formatted in OpenITI format
                (including the magic value and the header splitter)
        """
        metadata = ""
##        print("""WRITE A get_metadata FUNCTION \
##THAT COMPOSES THE METADATA HEADER FOR THE TEXT FILE.""")
        metadata = self.magic_value + metadata + self.header_splitter
        return metadata


    def get_data(self, source_fp):
        """Extract the data from the source_fp and format it in OpenITI format.

        ### Overwrite this method in subclass ###

        Args:
            source_fp (str): path to the original file

        Returns:
            text (str): the text in its initial state
        """
##        print("""WRITE A get_data FUNCTION \
##THAT GETS THE TEXT FROM THE source_fp""")
        with open(source_fp, mode="r", encoding="utf-8") as file:
            text = file.read()
        return text


    def pre_process(self, text):
        """Remove unwanted features from the text.

        ### Overwrite this method in subclass ###

        Args:
            text (str): the text in its initial state

        Returns:
            text (str): pre-processed text
        """
        text = deNoise(text)
        return text


    def add_page_numbers(self, text):
        """Add the page numbers in OpenITI format to the text.

        ### Overwrite this method in subclass ###

        Args:
            text (str): the text in its current conversion state

        Returns:
            text_w_pages (str): text with the page numbers added
                (in OpenITI format).
        """
##        print("""WRITE AN add_page_numbers FUNCTION \
##THAT ADDS THE PAGE NUMBERS TO THE TEXT""")
        text_w_pages = text
        return text_w_pages


    def add_structural_annotations(self, text):
        """Add strucural annotations in OpenITI format to the text.

        ### Overwrite this method in subclass ###

        Args:
            text (str): the text in its current conversion state

        Returns:
            text_w_pages (str): text with the structural markup
                (in OpenITI format) added.
        """
##        print("""WRITE AN add_structural_annotations FUNCTION \
##THAT ADDS THE PAGE NUMBERS TO THE TEXT""")
        ann_text = text
        return ann_text


    def remove_notes(self, text):
        """Remove the footnotes from the text.

        ### Overwrite this method in subclass ###

        Args:
            text (str)

        Returns:
            text_without_notes (str): text from which the notes were removed.
            notes (str): the footnotes converted to endnotes
                (if there are endnotes: add the endnote_splitter before them)
        """
##        print("""WRITE A remove_notes FUNCTION \
##THAT SPLITS THE NOTES FROM THE TEXT""")
        text_without_notes = text
        notes = ""
        if notes:
            notes = self.endnote_splitter + notes
        return text_without_notes, notes


    def reflow(self, text, max_len=72):
        """wrap long lines, i.e. break long lines down
        by inserting a new line character (and two tildes)
        so that no line is longer than max_len characters.
        See https://docs.python.org/3.1/library/textwrap.html
        Mark the start of paragraphs with "# ".

        Args:
            text (str): text string to be wrapped
            max_len (int): "width" = max number of characters in a line

        Returns:
            newtext (str): wrapped string
        """
        newtext = []

        # split the text, keeping the number of newline characters:

        text = re.sub("\r", "\n", text)
        text = re.split("(\n\n+)", text)

        # wrap each line:

        ignoreTuple = ("#000000#", "#NewRec#", "#####", "### ",
                       "#META#", "Page")
        for line in text:
            if not line.startswith(ignoreTuple):
                if line != "" and "\n\n" not in line:

                    # make sure the new lines that signal the end of a tag
                    # are treated differently from textwrap newlines:
                    
                    sublines = line.split("\n")
                    new_line = []
                    for s in sublines:
                        new_line.append("\n~~".join(textwrap.wrap(s, max_len)))
                    line = "\n".join(new_line)
##                if line != "" and "\n" not in line:
##                    if not line.startswith("# "):
##                        line = "# " + line
##                    line = "\n~~".join(textwrap.wrap(line, max_len))
            newtext.append(line)

        # re-assemble the text:
        
        newtext = "".join(newtext)

        # unwrap lines that are less than 10 characters long
        
        newtext = re.sub(r"[\r\n]+~~(.{1,6}?[\r\n]+)", r" \1", newtext)
        return newtext


    def add_milestones(self, text):
        """Add a milestone tag after a pre-defined number of words.

        The number of words is defined in the self.chunk_length variable.

        Example:
            >>> import generic_converter
            >>> g = generic_converter.GenericConverter()
            >>> g.chunk_length = 5
            >>> g.milestone_tag = "###"
            >>> text = '\
بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ\
 * الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ\
 * الرَّحْمَنِ الرَّحِيمِ\
 * مَالِكِ يَوْمِ الدِّينِ\
 * إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ\
 * اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ\
 * صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ'
            >>> g.add_milestones(text)
            '\
بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ\
 * الْحَمْدُ ### لِلَّهِ رَبِّ الْعَالَمِينَ\
 * الرَّحْمَنِ الرَّحِيمِ\
 * ### مَالِكِ يَوْمِ الدِّينِ\
 * إِيَّاكَ نَعْبُدُ ### وَإِيَّاكَ نَسْتَعِينُ\
 * اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ\
 * ### صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ ### الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ'
        """
        # start counting only after the first ### | tag
        editorial, text = text.split("### | ", maxsplit=1)
        ms_text = "### | "  # the text with the milestones added
        token_count = 0
        milestones = 0
        for token in self.ara_tok.finditer(text):
            #print(token_count, [token.group()])
            if re.findall(self.ara_char, token.group()[0]):
                if token_count == self.chunk_length:
                    token_count = 1
                    milestones += 1
                    ms_text += self.milestone_tag
                else:
                    token_count += 1
            else:
                pass  # do not increment the token count for non-Arabic tokens
            ms_text += token.group()

        # add spaces before and after the milestone_tag:
        ms_text = re.sub(" *({}) *".format(self.milestone_tag), r" \1 ", ms_text)

        return editorial + ms_text


    def post_process(self, text):
        """Carry out post-processing operations on the text.

        ### Overwrite this method in subclass ###

        Args:
            text (str): the text in its current conversion state

        Returns:
            processed (str): the text after post-processing operations.
        """
##        print("""WRITE A post_process FUNCTION \
##THAT CARRIES OUT THE LAST POST-PROCESSING OPERATIONS ON THE TEXT""")
        processed = text
        return processed

    def compose(self, metadata, text, notes):
        """Compose the final text from its parts.

        ### Overwrite this method in subclass ###

        Args:
            metadata (str): the metadata string in OpenITI format
                (including the magic_value and header_splitter)
            text (str): the main text (incl. page numbers and milestones)
            notes (str): the footnotes, converted to endnotes.

        Returns:
            composite_text (str)
        """
        composite_text = metadata+text+notes
        return composite_text


    def save_file(self, text, dest_fp):
        if not os.path.exists(os.path.split(dest_fp)[0]):
            os.makedirs(os.path.split(dest_fp)[0])
        with open(dest_fp, mode="w", encoding="utf-8") as file:
            file.write(text)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    input("Press Enter to start converting")

    conv = GenericConverter()
    conv.convert_file("test/test.txt")




