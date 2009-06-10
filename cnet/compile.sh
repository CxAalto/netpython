#!/bin/bash
swig -python -c++ sn.i
python setup.py build_ext --inplace
