Contributor Manual
==================

Creating a new version
----------------------

``openiti`` is in constant development. 

**Before releasing a new version**, make sure: 

* changes have been listed in the changelog in the README.md file
* changes have been adequately tested
* the version number in openiti.__init__ has been changed to the new number
* the current state of the openiti github repository has been tagged with the new version::
    $ git tag -a v0.0.3 -m "openiti version 0.0.3"

Test changes made to the library by installing the new version locally: 
    1. uninstall the old version::
        $ pip uninstall openiti
    2. install the local version::
        $ pip install -e <path\to\parent\folder\of\setup.py>

Generate the version: 

    1. navigate to the location of setup.py
    2. run the following code to build the version files:: 
        $ python setup.py sdist bdist_wheel
    3. run the following command to upload the new version to PyPi ::
        $ python twine upload dist/openiti-<version_number>*
    4. When prompted to enter your username: write ``__token__``
    5. When prompted to enter your password: paste the PyPi token

The new version can now be installed with ``pip install openiti``

You can check the installed version with::
    >>> import openiti
    >>> openiti.__version__
    '0.0.4'

