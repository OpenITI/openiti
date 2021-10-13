# openiti

This is a first attempt to create a Python library that combines all often-used code in the OpenITI project. 
Full documentation and deescription can be found here: <https://openiti.readthedocs.io/>

# Installation

```{python}
pip install OpenITI
```

Alternatively, you might need to use `pip3 install OpenITI` or `python -m pip install OpenITI`.

## Change log: 

### v.0.1.5.4: bug fix
* `helper.yml`: fix remaining bugs with long lines.
* `helper.uri`: fix bugs in `check_yml_file` function.

### v.0.1.5.3: bug fix
* `helper.yml`: make sure that yml keys always contain a hashtag.

### v.0.1.5.2: bug fix
* `helper.uri`: Remove test that blocked the script.

### v.0.1.5.1: bug fix
* `helper.yml`: fix bug related to long lines in the `dicToYML` function.

### v.0.1.5: 
* `helper.yml`: add `fix_broken_yml` function to fix yml files
that are unreadable due to indentation problems 
(or keys that don't end with a colon)
* `helper.uri`: rewrite the `check_yml_files` function to fix
a bug in the character count and add additional checks.
* `helper.funcs`: allow more than one `yml_type` in the function
`get_all_yml_files_in_folder`.
* `helper.ara`: 
  - Add missing EXTENDED ARABIC-INDIC DIGITS characters 67890
  - Add tokenize function
  - Fix typos in `normalize_per` doctest
* `new_books.convert`: add converter for Masāḥa Ḥurra epub files
(`epub_converter_masaha.py`, with helper file `html2md_masaha.py`)
* `new_books.convert.epub_converter_generic.py`: implement overwrite 
option for (dis)allowing overwriting existing converted files.

### v.0.1.4:
* `helper.templates`: replace the multiple book relations fields in the 
book yml file with a single field, `#40#BOOK#RELATED##:`.
* `helper.yml`: make not rearranging lines ("reflowing") in yml files the default,
and change the default line length to 80.
* `helper.funcs`: add a `get_all_yml_files_in_folder`, analogous to the existing
`get_all_text_files_in_folder` function

### v.0.1.3:

* `new_books.convert`: add converters for ALCorpus and Ptolemaeus texts
* `new_books.convert.helper.html2md`: tweaks to import of options + small tweaks
* `helper.ara`: Stop ar_cnt_file from raising exception if book misses splitter; instead, print warning
* `helper.funcs`: 
  - fix bug in `get_all_text_files_in_folder` function: missing periods in regex.
  - improve missing splitter message
  - use `ara.normalize_ara_light` function instead of `ara.normalize_ara_extra_light` in `text_cleaner` function
* `helper.uri`: 
  - make it possible to pass a specific `version_fp` to the `check_token_count` function; before, that function generated that path from the URI, but this created problems when files were not stored in the standard OpenITI folders. 
  - add `find_latest` parameter in `check_token_count` function; if ``False`, the function will count the tokens in the specific `version_fp` provided; if `True, the script will count tokens in the file with the most advanced extension (.mARkdown > .completed > .inProgress > [no extension])
* `helper.yml`: 
  - make it possible to pass a specific `yml_fp` to the `ymlToDic` function, so that the script can print the path (if provided) for signalling empty yml files.
  - Include possibility that yml key ends with more than one colon
  - `readYML`: add exception message when yml file could not be read.


### v.0.1.2:

* `openiti.helper.funcs`: Fixed bug in report_missing_numbers function.
* `openiti.new_books.convert`: added ShamAY converter and small updates to
    other shamela converters.

### v.0.1.1:

* `openiti.helper.funcs`: Added get_all_text_files_in_folder() generator
* `openiti.helper.uri`: Fix bug in `new_yml` function (URI used to have ".yml" in it)
* `openiti.new_books.convert.shamela_converter.py`: Improved formatting of the text and notes and added support for shamela collections in which the .mdb files contain more than one book.
* `openiti.new_books.convert.tei_converter_Thielen`, `new_books/convert/helper/html2md_Thielen`: added new converter for TEI files provided by Jan Thielen.
* `new_books/convert/tei_converter_generic.py`, `new_books/convert/helper/html2md.py`: Add the possibility to pass options to the `markdownify` function


### v.0.1.0:

* `openiti.helper.yml`: add support for empty lines and bullet lists in multiline values
* `openiti.new_books.convert.shamela_converter`: fix bugs in shamela converter

### v.0.0.9.post1 (patch): 

* `openiti.helper.ara`: fix bug in regex compilation

### v.0.0.9:

* `openiti.new_books.convert` : check and update all converters
* `openiti.helper.ara` : make counting characters in editorial sections optional (default: include Arabic characters in editorial sections)
* `openiti.helper.yml` : add custom error messages for broken and empty yml files
* `openiti.git.git_util` : add git utilities class, with `commit` method

### v.0.0.8: 

* `openiti.new_books.add.add_books`: fix import bug
* `openiti.new_books.convert`: add converter for Noorlib html files

### v.0.0.7: 

* `openiti.git.get_issues`: change authentication from username/password to GitHub token
* `openiti.helper.ara`: add function to normalize composite Arabic characters
* `openiti.helper.uri`: move functions for adding texts to the corpus to a new module, `openiti.new_books.add.add_books` 
* `openiti.helper.uri`: fix bug in the character count function (did not work if execute==True)
* `openiti.new_books.convert`: restructured folder and moved helper functions into a new subfolder called `helper`
* `openiti.new_books.convert.generic_converter`: 
    - reordered the main `convert_file` function and added inline documentation
    - made `convert_files_in_folder` function more flexible
* `openiti.new_books.convert`: added generic converters for shamela libraries, html and tei xml files, and custom converters for eShia and GRAR libraries
    - `openiti.new_books.convert.shamela_converter`
    - `openiti.new_books.convert.html_converter_generic`
    - `openiti.new_books.convert.html_converter_eShia`
    - `openiti.new_books.convert.tei_converter_generic`
    - `openiti.new_books.convert.tei_converter_GRAR`
* `openiti.new_books.convert.helper`: added helper functions for the new converters:
    - `openiti.new_books.convert.helper.html2md_eShia`
    - `openiti.new_books.convert.helper.html2md_GRAR`
    - `openiti.new_books.convert.helper.tei2md`
    - `openiti.new_books.convert.helper.bok`
 
### v.0.0.6: 

* `openiti.helper.uri`: use both Arabic character and token count in yml files
* `openiti.helper.uri`: add support for paths to files that are not in 25-years repos (e.g., for release)
* `openiti.helper.uri`: fix bugs
* added Sphinx documentation

### v.0.0.5:

* `openiti.helper.funcs`: added Arabic token count function
* `openiti.helper.uri`: use Arabic token count instead of Arabic character count for yml file revision. Also, revise token count for every version yml file instead of only for version yml files that do not contain a count.

### v.0.0.4: 

* `openiti.helper.uri`: removed the restriction on the use of digits in book titles
* `openiti.helper.uri`: added a check for empty yml files
* `openiti.helper.yml`: added documentation and doctests
* `openiti.helper.yml`: added check for empty yml files + changed splitting of yml files so that even unindented multi-line values can be correctly parsed.
