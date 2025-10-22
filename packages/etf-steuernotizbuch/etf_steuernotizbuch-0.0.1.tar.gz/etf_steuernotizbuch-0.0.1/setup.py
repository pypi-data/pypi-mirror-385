import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "etf_steuernotizbuch",
    version = "0.0.1",
    author = "just1436",
    author_email = "ju.sto@mailbox.org",
    long_description_content_type = "text/markdown",
    description = ("Notizbuch für Ausland-ETF-Depots für Steuertracking"),
    packages = find_packages(),
    license = "BSD",
    keywords = "example documentation tutorial",
    #url = "http://packages.python.org/an_example_pypi_project",
    #packages=['an_example_pypi_project', 'tests'],
    long_description=read('README.md'),
    
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities"
    ],
)
