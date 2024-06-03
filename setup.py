from setuptools import find_packages, setup
from typing import List

def extract_requirements(filepath:str)->List:
    requirements = []
    with open(filepath) as libs:
        requirements=libs.readlines()
        requirements = [req.replace("\n"," ") for req in requirements]
      
    return requirements


with open("pic\README.md", "r") as f:
    long_description = f.read()


setup(
    name="picviz",
    version="0.0.1",
    description="A collection of visualization charts related to palestine-israel-conflict (pic) project ",
    package_dir={"": "pic"},
    packages=find_packages(where="pic"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MohammedNasserAhmed/Palestine-Israel-Conflict.git",
    author="MohammedNaaserAhmed",
    author_email="abunasserip@gmail.com",
    license="Apache",
    classifiers=[
        "License :: OSI Approved :: Apache License",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    install_requires=
    [
        'bokeh==3.1.1',
        'matplotlib==3.7.5',
        'numpy==1.24.4',
        'pandas==2.0.3',
        'pathlib==1.0.1',
        'plotly==5.22.0',
        'pydantic==2.7.1',
        'seaborn==0.9.0',
        'typing==3.7.4.3'
        ],
    extras_require={
        "dev": ["twine>=5.1.0"],
    },
    python_requires=">=3.8"
)