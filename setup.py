import setuptools
import openiti

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

##################################################################

#    MAKE SURE YOU CHANGED THE VERSION IN OPENITI.__INIT__.PY !

##################################################################

#print("Make sure you have changed the version number in openiti.__init__.py")
#input("Press Enter to continue. ")

setuptools.setup(
    name="openiti",
    version=openiti.__version__,
    author="Sohail Merchant, Maxim Romanov, Masoumeh Seydi, Peter Verkinderen",
    author_email="peter.verkinderen@gmail.com",
    description="A package for dealing with the openITI corpus",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OpenITI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "beautifulsoup4",
        "requests",
        "six",
        "sphinx_rtd_theme",
        # added the following three to solve Read The Docs import problem:
        "pypyodbc",
        "bs4",
        "pygithub",
    ],
    python_requires='>=3.6',
)

