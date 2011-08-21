#!/usr/bin/env python
from distutils.core import setup
import anidb
setup(name="pyanihttp",
       version=anidb.__version__,
        author="Wieland Hoffmann",
        author_email="themineo@gmail.com",
        packages=["anidb"],
        license="MIT",
        classifiers=["Development Status :: 4 - Beta",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.7"],
        )
