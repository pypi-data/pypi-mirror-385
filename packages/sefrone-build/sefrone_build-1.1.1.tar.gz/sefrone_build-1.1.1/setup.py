from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sefrone_build",
    version="1.1.1",
    author="Sefrone",
    author_email="contact@sefrone.com",
    description="A Python package to provide build helpers for sefrone projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/sefrone/sefrone_pypi",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests",
    ],
)