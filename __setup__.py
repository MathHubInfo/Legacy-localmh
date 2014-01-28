#!/usr/bin/env python

from distutils.core import setup

# Insert submodules here
submodules = [
	"lmhagg", 
	"lmhcheckpaths", 
	"lmhclean", 
	"lmhcommit", 
	"lmhdepcrawl", 
	"lmhfind", 
	"lmhgen", 
	"lmhgit", 
	"lmhinit", 
	"lmhinstall", 
	"lmhlog", 
	"lmhmmt", 
	"lmhpush", 
	"lmhserver", 
	"lmhsetup", 
	"lmhstatus", 
	"lmhtraverse", 
	"lmhupdate", 
	"lmhutil", 
	"lmhxhtml", 
	"lmhabout"
]

packs = ["lmh"]
packs.extend(map(lambda x: "lmh."+x, submodules))

setup(name='Local MathHub Utility',
      version='0.1',
      description='Local MathHub Utility',
      author='The KWARC Group',
      scripts=['bin/lmh'], 
      license='GPL', 
      packages=packs,
     )