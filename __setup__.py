#!/usr/bin/env python

from distutils.core import setup, find_packages

setup(name='Local MathHub Utility',
      version='0.1',
      description='Local MathHub Utility',
      author='The KWARC Group',
      scripts=['bin/lmh'], 
      license='GPL', 
      packages=find_packages(),
     )