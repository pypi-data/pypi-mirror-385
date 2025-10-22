#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, Extension
from os.path import join
import sysconfig

macros = []
free_threaded = sysconfig.get_config_var("Py_GIL_DISABLED")

if free_threaded:
    macros.append(("Py_GIL_DISABLED", "1"))

setup(
    ext_modules=[Extension('regex._regex', ['src/_regex.c',
      'src/_regex_unicode.c'])],
      define_macros=macros,
)
