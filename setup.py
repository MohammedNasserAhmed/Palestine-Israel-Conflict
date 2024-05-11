from setuptools import find_packages, setup
from typing import List

IGNORE = '-e .'
def extract_requiremnets(filepath:str)->List:
    requirements = []
    with open(filepath) as libs:
        requirements=libs.readlines()
        requirements = [req.replace("\n"," ") for req in requirements]
        if IGNORE in requirements:
            requirements.remove(IGNORE)


setup(
    
    name="palestine-israel-conflict",
    version="0.0.1",
    author="m. n. gaber",
    author_email='abunasserip@gmail.com',
    packages=find_packages(),
    install_requries=extract_requiremnets("requirements.txt")
)