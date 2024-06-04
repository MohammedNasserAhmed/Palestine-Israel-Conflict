from setuptools import find_packages, setup
from typing import List

def extract_requirements(filepath:str)->List:
    requirements = []
    with open(filepath) as libs:
        requirements=libs.readlines()
        requirements = [req.replace("\n"," ") for req in requirements]
      
    return requirements


with open("app\README.md", "r") as f:
    long_description = f.read()


setup(
    name="picviz",
    version="0.0.6",
    description="A collection of visualization charts related to palestine-israel-conflict (pic) project ",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MohammedNasserAhmed/Palestine-Israel-Conflict.git",
    author="MohammedNaaserAhmed",
    author_email="abunasserip@gmail.com",
    license="Apache License 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    install_requires=
    [
        'bokeh',
        'matplotlib',
        'numpy',
        'pandas',
        'pathlib',
        'plotly',
        'pydantic',
        'seaborn',
        'typing'
        ],
    extras_require={
        "dev": ["twine>=5.1.0"],
    },
    python_requires=">=3.8"
)