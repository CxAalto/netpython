#!/usr/bin/env python

"""
setup.py file for Python wrapping of a C++ network data structure
"""

from distutils.core import setup, Extension


example_module = Extension('_cnet',
                           sources=['sn_wrap.cxx', 'sn.cpp','dn.cpp','netext.cpp','transforms.cpp'],
                           )

setup (name = 'sn',
       version = '0.1',
       author      = "Mikko Kivela",
       description = """Python wrapping of a C++ network data structure""",
       ext_modules = [example_module],
       py_modules = ["sn"],
       )
