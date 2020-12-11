import os 
from setuptools import setup, find_packages

#Use README file for long description of the project

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def parse_requiremetns(fname):
    with open(fname) as f:
        required = f.read().splitlines()
    return required
    
setup(
    name="FaceAnonymizationToolBox",
    version="0.1.0",
    url=" ",
    license='GNU',
    
    #Author
    author = "Akhil Singh Rana",
    author_email = "akhil.singh-rana@avira.com",
    description = ("A toolbox to provide easy setup for face anonymization"),
    long_description = read("README.md"),
    install_requires = parse_requiremetns("requirements.txt"),    
    packages=find_packages(),
)