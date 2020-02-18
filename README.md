# openiti

This is a first attempt to create a Python library that combines all often-used code in the OpenITI project. 

## Change log: 

### v.0.0.5:

* openiti.helper.funcs: added Arabic token count function
* openiti.helper.uri: use Arabic token count instead of Arabic character count for yml file revision. Also, revise token count for every version yml file instead of only for version yml files that do not contain a count.

### v.0.0.4: 

* openiti.helper.uri: removed the restriction on the use of digits in book titles
* openiti.helper.uri: added a check for empty yml files
* openiti.helper.yml: added documentation and doctests
* openiti.helper.yml: added check for empty yml files + changed splitting of yml files so that even unindented multi-line values can be correctly parsed.
