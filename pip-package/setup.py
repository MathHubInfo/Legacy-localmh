#!/usr/bin/env python

from setuptools import setup

setup(name='lmh',
      version='1.6',
      description='Local MathHub Utility (setup package)',
      author='The KWARC Group', 
      author_email = "postmaster@kwarc.info",
      scripts=['lmh'], 
      license='GPL', 
      packages=['lmh_core'],
)
