# -*- coding: utf-8 -*-
import setuptools
import LyricLib

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read().replace(
        "./docs/", "https://github.com/TriM-Organization/Lyric/blob/master/README.md"
    )

setuptools.setup(
    name="LyricLib",
    version=LyricLib.__version__,
    author="Eilles Wan, bgArray",
    author_email="TriM-Organization@hotmail.com",
    description="歌词的处理库\n"
    "A library for processing lyrics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TriM-Organization/Lyric",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: Chinese (Simplified)",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
