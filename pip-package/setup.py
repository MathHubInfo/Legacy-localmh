#!/usr/bin/env python

from setuptools import setup

setup(name='lmh',
      version='1.7.0',
      description='Local MathHub Utility (setup package)',
      author='The KWARC Group',
      author_email = "postmaster@kwarc.info",
      scripts=['lmh'],
      license='GPL',
      packages=['lmh_core'],
      install_requires=['beautifulsoup4', 'psutil', 'pyapi-gitlab']
)
