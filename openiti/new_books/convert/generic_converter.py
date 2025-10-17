"""A generic converter for texts into OpenITI format.

This generic converter contains the basic procedure for
converting texts into OpenITI format.

These are the main methods of the GenericConverter class:

* `convert_file(source_fp)`: basic procedure for converting an html file.
* `convert_files_in_folder(source_folder)`: convert all files files in the
    `source_folder` (calls `convert_file`)

The procedure can be used as a template for other converters.
Subclass the GenericConverter to make a converter for a new
source of scraped books::

    class GenericHtmlConverter(GenericConverter):
        def new_function(self, text):
            "This function adds functionality to GenericConverter"

Usually, it suffices to overwrite a small number of methods
of the GenericConverter class in the sub-class, and/or add
a number of methods needed for the conversion of a specific
group of documents: e.g.:: 

    class GenericHtmlConverter(GenericConverter):
        def get_data(self, source_fp):
            # code written here overwrites the GenericConverter's get_data method

        def post_process(self, text):
            # append new actions by appending them to
            # the superclass's post_process method:
            text = super().post_process(text)
            text = re.sub("\\n\\n+", "\\n\\n", text)
            return text

        def new_function(self, text):
            "This function adds functionality to GenericConverter"

The GenericConverter contains a number of dummy (placeholder) functions
that must be overwritten in the subclass because they are dependent on
the data format.

For example, this is the inheritance schema of the EShiaHtmlConverter,
which is a subclass of the GenericHtmlConverter:
(methods of GenericConverter are inherited by GenericHtmlConverter;
and methods of GenericHtmlConverter are inherited by EShiaHtmlConverter.
Methods of the superclass with the same name
in the subclass are overwritten by the latter)

================================== ========================== ==========================
GenericConverter                   GenericHtmlConverter       EShiaHtmlConverter
================================== ========================== ==========================
__init__                           __init__                   (inherited)
convert_files_in_folder            (inherited)                (inherited)
convert file                       (inherited)                (inherited)
make_dest_fp                       (inherited - generic!)     (inherited - generic!)
get_metadata (dummy)               (inherited - dummy!)       get_metadata
get_data                           get_data                   (inherited)
pre_process                        (inherited)                (inherited)
add_page_numbers (dummy)           (inherited - dummy!)       add_page_numbers
add_structural_annotations (dummy) add_structural_annotations add_structural_annotations
remove_notes (dummy)               remove_notes               remove_notes
reflow                             (inherited)                (inherited)
add_milestones (dummy)             (inherited - dummy!)       (inherited - dummy!)
post_process                       (inherited - generic!)     post_process
compose                            (inherited)                (inherited)
save_file                          (inherited)                (inherited)
                                   inspect_tags_in_html       (inherited)
                                   inspect_tags_in_folder     (inherited)
                                   find_example_of_tag        (inherited)
================================== ========================== ==========================

Examples:
    >>> from generic_converter import GenericConverter
    >>> conv = GenericConverter()
    >>> conv.VERBOSE = False
    >>> folder = r"test/"
    >>> conv.convert_file(folder+"86596.html")
    >>> conv.convert_files_in_folder(folder, ["html"])

"""

import os
import re
import textwrap

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.helper.ara import deNoise, normalize, normalize_composites

class GenericConverter(object):

    def __init__(self, dest_folder=None, overwrite=True):
        """Initialize the default values."""
        self.magic_value = "######OpenITI#\n\n\n"
        self.header_splitter = "\n\n#META#Header#End#\n\n"
        self.endnote_splitter = "\n\n### |EDITOR|\nENDNOTES:\n\n"
        #self.dest_folder = "converted"
        #if dest_folder == None:
        #    self.dest_folder = "converted"
        #else:
        if dest_folder:
            self.dest_folder = dest_folder
        else:
            self.dest_folder = None
        self.extension = ".automARkdown"
        
        # settings for line wrapping: max number of characters in a line

        self.max_line_len = 72

        # settings for the chunking of the text:

        self.chunk_length = 300
        self.milestone_tag = "Milestone300"

        # regexes describing Arabic characters and tokens:

        self.ara_char = "[؀-ۿࢠ-ࣿﭐ-﷿ﹰ-﻿]"
        ara_tok = "{}+|[^{}+".format(self.ara_char, self.ara_char[1:])
        self.ara_tok = re.compile(ara_tok)

        self.VERBOSE = False
        self.metadata_file = "inline"
        self.OVERWRITE = overwrite

##        self.conversion_procedure(source_fp, dest_dir)


    def filter_files_in_folder(self, source_folder, extensions=[],
                               exclude_extensions=[], fn_regex=None):
        """Make a list of all the files that have (or don't have) \
        specific extensions, and/or match a specific regex pattern.

        Args:
            source_folder (str): path to the folder.
            extensions (list): if defined, only files with one of the \
                extensions in the list will be used.
                Defaults to an empty list
                (=> all files in the `source_folder` will be used)
            exclude_extensions (list): if defined
                (and no `extensions` list is defined),
                only files without one of the extensions in this list
                will be usedwill.
                Defaults to an empty list
                (=> all files in the `source_folder` will be used)
            fn_regex (str): regular expression defining the filename pattern
                e.g., "-(ara|per)\d". If `fn_regex` is defined,
                only files whose filename matches the pattern will be converted.
                Defaults to None
                (=> all files in the `source_folder` will be used)

        Returns:
            fp_list (list): a list of file paths that comply with the user's parameters
        """
        # make sure all extensions (except "") start with a period:
        extensions = [re.sub("^\.?(\w+)", r".\1", ext) for ext in extensions]
        exclude_extensions = [re.sub("^\.?(\w+)", r".\1", ext) \
                              for ext in exclude_extensions]
        
        fp_list = []
        for fn in os.listdir(source_folder):
            fp = os.path.join(source_folder, fn)
            if os.path.isfile(fp):
                incl = True
                ext = os.path.splitext(fn)[-1]
                if fn_regex:
                    if not re.findall(fn_regex, fn):
                        incl = False
                if extensions:
                    if ext not in extensions:
                        incl = False
                if exclude_extensions:
                    if ext in exclude_extensions:
                        incl = False
                if incl:
                    fp_list.append(fp)
        return fp_list


    def convert_files_in_folder(self, source_folder, dest_folder=None,
                                extensions=[], exclude_extensions=[],
                                fn_regex=None):
        """Convert all files in a folder to OpenITI format.\
        Use the `extensions` and `exclude_extensions` lists to filter\
        the files to be converted.

        Args:
            source_folder (str): path to the folder that contains
                the files that must be converted.
            extensions (list): list of extensions; if this list is not empty,
                only files with an extension in the list should be converted.
            exclude_extensions (list): list of extensions;
                if this list is not empty,
                only files whose extension is not in the list will be converted.
            fn_regex (str): regular expression defining the filename pattern
                e.g., "-(ara|per)\d". If `fn_regex` is defined,
                only files whose filename matches the pattern will be converted.

        Returns:
            None
        """
        if dest_folder:
            self.dest_folder = dest_folder
        fp_list = self.filter_files_in_folder(source_folder, extensions,
                                              exclude_extensions, fn_regex)
        for fp in fp_list:
            self.convert_file(fp)


    def convert_file(self, source_fp, dest_fp=None):
        """Convert one file to OpenITI format.

        Args:
            source_fp (str): path to the file that must be converted.

        Returns:
            None
        """
        if self.VERBOSE:
            print("converting", source_fp)

        # make the file path for the converted file
        # (based on the source_fp and the self.dest_folder value;
        # if no specific self.dest_folder is given, a `converted` folder
        # will be created in the folder of the source file)
        if not dest_fp:
            dest_fp = self.make_dest_fp(source_fp)
        self.source_fp = source_fp

        if not self.OVERWRITE and os.path.exists(dest_fp):
            print("Not overwriting already existing file:", dest_fp)
            print("Set self.overwrite to True if you want to overwrite")
            return

##        # get the metadata from the source_fp and format it
##        # WARNING: this is a dummy method, returning
##        #          a string with magic_value and header_splitter only.
##        #          Overwrite this method in subclass!
##        self.metadata = self.get_metadata(source_fp)

        # Get the raw data from the source_fp
        # WARNING: this method only reads the file at source_fp
        #          and returns it as a string.
        #          Overwrite this method in subclass if necessary!
        text = self.get_data(source_fp)

        # get the metadata from the text or from a separate file,
        # and format it.
        # WARNING: this is a dummy method, returning
        #          a string with magic_value and header_splitter only.
        #          Overwrite this method in subclass!
        if self.metadata_file == "inline":
            self.metadata = self.get_metadata(text)
        else:
            self.metadata = self.get_metadata(self.metadata_file)

        # Remove unwanted features from the text:
        # NB: this method executes a standard cleaning of the text.
        #     If the text needs more pre-processing,
        #     append additional operations to the method in the sub-class.
        text = self.pre_process(text)

        # add page numbers to the text, or convert them to OpenITI format:
        # WARNING: this is a dummy function, and returns the text without
        #          making any changes. Overwrite this method in the sub-class
        #          if page numbers need to be added to the text.
        text = self.add_page_numbers(text, source_fp)

##        # add structural tags in OpenITI format to the text:
##        # WARNING: this is a dummy function, and returns the text without
##        #          making any changes. Overwrite this method in the sub-class
##        #          if structural annotations need to be added to the text.
##        text = self.add_structural_annotations(text)

        # remove the footnotes from the text, and convert them into endnotes
        # WARNING: this is a dummy function, and returns the text without
        #          making any changes, and an empty string for the endnotes.
        #          Overwrite this method in the sub-class if notes need to be
        #          extracted from the text.
        text, notes = self.remove_notes(text)

        # add structural tags in OpenITI format to the text:
        # WARNING: this is a dummy function, and returns the text without
        #          making any changes. Overwrite this method in the sub-class
        #          if structural annotations need to be added to the text.
        text = self.add_structural_annotations(text)

        # wrap long lines (i.e., break long lines down)
        # and mark the start of paragraphs with "# ":
        # NB: this function should not be overwritten in the sub-class.
        text = self.reflow(text)

        # Add milestones to the text.
        # NB: the add_milestones method is old and needs to be replaced
        #     with the most recent function written by Masoumeh!
        #     It has been disabled and now returns the text without changes.
        text = self.add_milestones(text)

        # Make last changes to the text;
        # NB: this default method only takes care of paragraph marks.
        #     Write a post_processing method for your sub_class if needed.
        text = self.post_process(text)

        # Join the formatted metadata, text and notes strings:
        text = self.compose(self.metadata, text, notes)

        # Save the file to the dest_fp:
        self.save_file(text, dest_fp)

        return dest_fp


    def make_dest_fp(self, source_fp):
        """Make a filepath for the converted text file, \
        based on the `source_fp` and the class's `self.dest_folder`.\
        If no specific self.dest_folder is given,
        a `converted` folder is created in the source folder.

        Args:
            source_fp (str): path to the file that must be converted.

        Returns:
            dest_fp (str): path to the converted text file.
        """
        source_folder, source_fn = os.path.split(source_fp)
        fn, old_ext = os.path.splitext(source_fn)
        if len(old_ext) > 10: # not an extension but part of the file name
            source_fn += self.extension
        else:
            source_fn = fn + self.extension
        #if self.dest_folder == "converted":
        if self.dest_folder is None:
            self.dest_folder = os.path.join(source_folder, "converted")
        if not os.path.exists(self.dest_folder):
            os.makedirs(self.dest_folder)
        self.dest_fp = os.path.join(self.dest_folder, source_fn)
        return self.dest_fp


    def get_metadata(self, source_fp):
        """Gets the metadata from the file at source_fp.
        (### DUMMY: returns string with magic_value and header_splitter only.
        Overwrite this method in subclass ###)

        Args:
            source_fp (str): path to the original file

        Returns:
            metadata (str): metadata formatted in OpenITI format
                (including the magic value and the header splitter)
        """
        metadata = ""
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
        with open(source_fp, mode="r", encoding="utf-8") as file:
            text = file.read()
        return text


    def pre_process(self, text):
        """Remove unwanted features from the text.

        This method removes Arabic vowels and other non-basic characters
        from the text, and normalizes composite letters.

        ### DO NOT overwrite this method in subclass unless it is necessary;
        First, try extending it by using `text = super().pre_process`
        in the subclass's `pre_process` method

        Args:
            text (str): the text in its initial state

        Returns:
            text (str): pre-processed text
        """
        text = deNoise(text)
        text = normalize_composites(text)
        
        repl = [("۱", "١"),   # EXTENDED ARABIC-INDIC DIGIT
                ("۲", "٢"),   # EXTENDED ARABIC-INDIC DIGIT
                ("۳", "٣"),   # EXTENDED ARABIC-INDIC DIGIT
                ("۴", "٤"),   # EXTENDED ARABIC-INDIC DIGIT
                ("۵", "٥"),   # EXTENDED ARABIC-INDIC DIGIT
                ("ک", "ك"),   # Farsi kaf
                ("ی", "ي"),   # Farsi ya
                ("ے", "ي"),   # Farsi yeh barri
                ("‌", ""),     # ZERO WIDTH NON-JOINER
                ("‍", ""),     # ZERO WIDTH JOINER
                ("ۀ", "ة"),   # Farsi ta marbuta in ezafe construction
                ("ۂ", "ة"),   # Farsi ta marbuta in ezafe construction (bis)
                ]
        text = normalize(text, repl)
        
        # attach separated wa- and a- prefixes to the following word: 
        text = re.sub(r"\b([وأ])[\s~]+", r"\1", text)
        return text


    def add_page_numbers(self, text, source_fp):
        """Add the page numbers in OpenITI format to the text.

        ### DUMMY METHOD. Overwrite this method in subclass ###

        Args:
            text (str): the text in its current conversion state
            source_fp (str): the path of the source file
               (sometimes contains information on the volumen number)

        Returns:
            text_w_pages (str): text with the page numbers added
                (in OpenITI format).
        """
        text_w_pages = text
        return text_w_pages


    def add_structural_annotations(self, text):
        """Add strucural annotations in OpenITI format to the text.

        ### DUMMY METHOD. Overwrite this method in subclass ###

        Args:
            text (str): the text in its current conversion state

        Returns:
            text_w_pages (str): text with the structural markup
                (in OpenITI format) added.
        """
        ann_text = text
        return ann_text


    def remove_notes(self, text):
        """Remove the footnotes from the text and convert them into endnotes.

        ### DUMMY METHOD. Overwrite this method in subclass ###

        Args:
            text (str)

        Returns:
            text_without_notes (str): text from which the notes were removed.
            notes (str): the footnotes converted to endnotes
                (if there are endnotes: add the endnote_splitter before them)
        """
        text_without_notes = text
        notes = ""
        if notes:
            notes = self.endnote_splitter + notes
        return text_without_notes, notes


    def reflow(self, text, max_len=None):
        """wrap long lines, i.e. break long lines down \
        by inserting a new line character (and two tildes) \
        so that no line is longer than max_len characters. \
        
        See https://docs.python.org/3.1/library/textwrap.html
        Mark the start of paragraphs with "# ".

        Args:
            text (str): text string to be wrapped
            max_len (int): "width" = max number of characters in a line.
                Default: None (in this case, the default value will be used
                (self.max_line_len)

        Returns:
            newtext (str): wrapped string

        Examples:
            >>> import generic_converter
            >>> g = generic_converter.GenericConverter()
            >>> text = "# This is a short paragraph\\n\\n\
# This is a longer paragraph (longer than max_len)"
            >>> g.reflow(text, max_len=40)
            '# This is a short paragraph\\n\\n\
# This is a longer paragraph (longer\\n\
~~than max_len)'
            
        """
        if max_len:
            self.max_line_len = max_len
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
                        s_wrap = textwrap.wrap(s, self.max_line_len)
                        new_line.append("\n~~".join(s_wrap))
                    line = "\n".join(new_line)
            newtext.append(line)

        # re-assemble the text:
        
        newtext = "".join(newtext)

        # unwrap lines that are less than 6 characters long:
        
        newtext = re.sub(r"[\r\n]+~~(.{1,6}?[\r\n]+)", r" \1", newtext)
        return newtext


    def add_milestones(self, text):
        """Add a milestone tag after a pre-defined number of words.

        NB: THIS METHOD IS OLD AND MUST BE REPLACED WITH MASOUMEH'S!
        """
##
##        The number of words is defined in the self.chunk_length variable.
##
##        Example:
##            >>> import generic_converter
##            >>> g = generic_converter.GenericConverter()
##            >>> g.chunk_length = 5
##            >>> g.milestone_tag = "###"
##            >>> text = '\
##بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ\
## * الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ\
## * الرَّحْمَنِ الرَّحِيمِ\
## * مَالِكِ يَوْمِ الدِّينِ\
## * إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ\
## * اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ\
## * صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ'
##            >>> g.add_milestones(text)
##            '\
##بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ\
## * الْحَمْدُ ### لِلَّهِ رَبِّ الْعَالَمِينَ\
## * الرَّحْمَنِ الرَّحِيمِ\
## * ### مَالِكِ يَوْمِ الدِّينِ\
## * إِيَّاكَ نَعْبُدُ ### وَإِيَّاكَ نَسْتَعِينُ\
## * اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ\
## * ### صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ ### الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ'
##        """
##        # start counting only after the first ### | tag
##        try:
##            editorial, text = text.split("### | ", maxsplit=1)
##            text = "### | " + text
##        except:
##            editorial = ""
##        ms_text = ""  # the text with the milestones added
##        token_count = 0
##        milestones = 0
##        for token in self.ara_tok.finditer(text):
##            #print(token_count, [token.group()])
##            if re.findall(self.ara_char, token.group()[0]):
##                if token_count == self.chunk_length:
##                    token_count = 1
##                    milestones += 1
##                    ms_text += self.milestone_tag
##                else:
##                    token_count += 1
##            else:
##                pass  # do not increment the token count for non-Arabic tokens
##            ms_text += token.group()
##
##        # add spaces before and after the milestone_tag:
##        ms_text = re.sub(" *({}) *".format(self.milestone_tag),
##                         r" \1 ", ms_text)
##
##        return editorial + ms_text
        return text


    def post_process(self, text):
        """Carry out post-processing operations on the text.

        ### Overwrite this method in subclass ###

        Args:
            text (str): the text in its current conversion state

        Returns:
            processed (str): the text after post-processing operations.
        """
        processed = re.sub("[\n\r]{2,}(?![#\|P])", "\n\n# ", text)
        processed = re.sub("[\n\r]+#* *[\n\r]+", "\n\n", processed)
        return processed

    def compose(self, metadata, text, notes):
        """Compose the final text from its parts.

        ### Overwrite this method in subclass if necessary ###

        Args:
            metadata (str): the metadata string in OpenITI format
                (including the magic_value and header_splitter)
            text (str): the main text (incl. page numbers and milestones)
            notes (str): the footnotes, converted to endnotes.

        Returns:
            composite_text (str)
        """
        composite_text = metadata + text + notes
        return composite_text


    def save_file(self, text, dest_fp):
        if not os.path.exists(os.path.split(dest_fp)[0]):
            os.makedirs(os.path.split(dest_fp)[0])
        with open(dest_fp, mode="w", encoding="utf-8") as file:
            file.write(text)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    print("all test passed")

    input("Press Enter to start converting")

    conv = GenericConverter()
    conv.convert_file("test/test.txt")




