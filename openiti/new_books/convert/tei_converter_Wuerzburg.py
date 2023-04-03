
import os
import re
from bs4 import BeautifulSoup


from openiti.new_books.convert.tei_converter_generic import TeiConverter
from openiti.new_books.convert.helper import html2md_Wuerzburg
from openiti.helper.ara import deNoise


def convert_file(fp, dest_fp=None):
    """Convert one file to OpenITI format.

    Args:
        source_fp (str): path to the file that must be converted.
        dest_fp (str): path to the converted file. Defaults to None
            (in which case, the converted folder will be put in a folder
            named "converted" in the same folder as the source_fp)

    Returns:
        None
    """
    conv = WuerzburgTeiConverter() 
    conv.convert_file(fp, dest_fp=dest_fp)

def convert_files_in_folder(src_folder, dest_folder=None,
                            extensions=[], exclude_extensions=["yml"],
                            fn_regex=None):
    """Convert all files in a folder to OpenITI format.\
    Use the `extensions` and `exclude_extensions` lists to filter\
    the files to be converted.

    Args:
        src_folder (str): path to the folder that contains
            the files that must be converted.
        dest_folder (str): path to the folder where converted files
            will be stored.
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
    conv = WuerzburgTeiConverter()
    conv.convert_files_in_folder(src_folder, dest_folder=dest_folder,
                                 extensions=extensions,
                                 exclude_extensions=exclude_extensions,
                                 fn_regex=fn_regex)


################################################################################

class WuerzburgTeiConverter(TeiConverter):
    def extract_by_attribute(self, soup, tag, attrs):
        tags = soup.find_all(tag, attrs=attrs)
        if tags:
            return " :: ".join([tag.get_text().strip() for tag in tags])
        else:
            return ""

    def get_metadata(self, text):
        """Extracts the metadata from the text.


        Args:
            text (str): text of the file that contains data + metadata

        Returns:
            metadata (str): metadata formatted in OpenITI format
                (including the magic value and the header splitter)
        """
        soup = BeautifulSoup(text, "xml")
        metadata = ""
        
        header = soup.find("teiHeader")
        short_title = self.extract_by_attribute(header, "title", {"type": "short"})
        latin_title = self.extract_by_attribute(header, "title", {"xml:lang": "la"})
        transcr_title = self.extract_by_attribute(header, "title", {"xml:lang": "ar-Latn"})
        latin_author = self.extract_by_attribute(header.author, "name", {"xml:lang": "la"})
        transcr_author = self.extract_by_attribute(header.author, "name",
                                              {"xml:lang": "ar-Latn"})
        resp = header.respStmt.get_text(" ", strip=True)
        version = header.editionStmt.get_text(" ", strip=True)
        ed = header.bibl.get_text(" ", strip=True)
        text_id = re.sub("\s+", "_", short_title) + "_ar.xml"
        
        
        metadata += "#META# text_id: {}\n".format(text_id)
        url = "https://www.arabic-latin-corpus.philosophie.uni-wuerzburg.de/text/"
        metadata += "#META# url: {}{}\n".format(url, text_id)
        metadata += "#META# title_short: {}\n".format(short_title)
        metadata += "#META# title_latin: {}\n".format(latin_title)
        metadata += "#META# title_transcription: {}\n".format(transcr_title)
        metadata += "#META# author_latin: {}\n".format(latin_author)
        metadata += "#META# author_transcription: {}\n".format(transcr_author)
        metadata += "#META# responsibility: {}\n".format(resp)
        metadata += "#META# version: {}\n".format(version)
        metadata += "#META# ed_info: {}\n".format(ed)
        # remove unwanted line breaks:
        metadata = re.sub(r"\n([^#])", r" \1", metadata)
        
        metadata = self.magic_value + metadata + self.header_splitter
        print(metadata)
        return metadata

    def pre_process(self, text):            
        text = super().pre_process(text)

        # remove zero-width joiner:
        text = re.sub(r"‌", "", text)
        
        text = re.sub("([\n ])[|*] ", r"\1", text)
        text = re.sub('>', "> ", text)
        text = re.sub(" +", " ", text)
        # reformat page numbers
        text = re.sub('(<p>|<head>)([\r\n\t ]*)(PageV[^P]+P\d+)', r"\3\2\1", text)

        return text


    def get_html_metadata(self, soup):
        return ""

    def get_html_data(self, soup):
        text_soup = soup.find("body")
        c = html2md_Wuerzburg.WuerzburgHtmlConverter()
        text = c.convert(text_soup)
        return text

##    def convert_files_in_folder(self, folder):
##        for fn in os.listdir(folder):
##            fp = os.path.join(folder, fn)
##            if os.path.isfile(fp) and fn.endswith("ara1"):
##                self.convert_file(fp)

    def add_structural_annotations(self, text, **options):
        soup = BeautifulSoup(text, "xml")
        text_soup = soup.find("text")
        text = html2md_Wuerzburg.markdownify(str(text_soup), **options)
        return text

    def convert_file(self, source_fp, dest_fp=None):
        """Convert one file to OpenITI format.

        Args:
            source_fp (str): path to the file that must be converted.
            dest_fp (str): path to the converted file. Defaults to None
                (in which case, the converted folder will be put in a folder
                named "converted" in the same folder as the source_fp)

        Returns:
            None
        """
        if self.VERBOSE:
            print("converting", source_fp)
        if dest_fp == None:
            dest_fp = self.make_dest_fp(source_fp)
        with open(source_fp, mode="r", encoding="utf-8") as file:
            text = file.read()
        text = self.pre_process(text)
        soup = BeautifulSoup(text, "xml")
        self.metadata = self.get_metadata(text)
        text = self.add_structural_annotations(text, strip=["note"])

        # remove notes:
        notes = ""
        #text, notes = self.remove_notes(text)
        
        if not soup.find_all("lb") and not soup.find_all(title="linebreak"):
            text = self.reflow(text)
        text = self.post_process(text)
        text = self.compose(self.metadata, text, notes)

        self.save_file(text, dest_fp)

    def post_process(self, text, verbose=False):
        text = super().post_process(text)
        vols = re.findall("vol. (\d+) pp", self.metadata)
        #print(vols)
        if len(vols) == 1:
            text = re.sub("PageV00", "PageV{:02d}".format(int(vols[0])), text)
        elif len(vols) == 0:
            text = re.sub("PageV00", "PageV01", text)
        elif len(vols) > 1:
            print("More than one volume! adjust volume numbers manually")
        text = re.sub("# Page(V\d+P\d+)", r"Page\1\n\n#", text)
        if verbose:
            print(text)
            input()
        text = re.sub("\n~~ *(PageV\d+P\d+)\n", r"\n\n\1\n", text)
        text = re.sub("\n~~ ", r"\n~~", text)
        text = re.sub("(### \|+[^#]+)\n~~", r"\1 ", text)
        text = re.sub("(### \|+ \[[^\]]+\]) *\n+### \|{3}", r"\1", text)
        text = re.sub("([^.؟])\n{2}# (PageV\d+P\d+) ?", r"\1 \2\n~~", text)
        # if a page number does not follow a dot/question mark
        text = re.sub("([^.؟])\n{2}(PageV\d+P\d+)\n+# ", r"\1 \2\n~~", text)
        text = re.sub("([^.؟])\n{2}(PageV\d+P\d+) *(?!\n)", r"\1 \2\n~~", text)
        text = re.sub("#[\r\n]+~~", "# ", text)
        text = re.sub("[\r\n]+#? ?~~(?=[\r\n])", "", text)
        text = re.sub("(PageV\d+P\d+)[\r\n]+~~(\d+)", r"\1\2", text)
        #text = re.sub("@QUOTE@", "", text)
        # fix tildes at start and end of text:
        text = re.sub(r"\A~~ *", "# ", text.strip())
        text = re.sub(r"[\r\n]+~~\Z", "", text)

        text = deNoise(text)
        return text



if __name__ == "__main__":
    convert_files_in_folder("xml")
    
