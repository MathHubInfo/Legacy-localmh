#!/usr/bin/env python

"""
Local Math Hub repository installer

.. argparse::
   :module: install
   :func: create_parser
   :prog: install

"""

"""
This file is part of LMH.

LMH is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

LMH is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LMH.  If not, see <http://www.gnu.org/licenses/>.
"""


import re
import os
import sys
import argparse
from subprocess import call

from lmh import util

repoRegEx = util.repoRegEx;

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Install tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="install"):
  parser_status = subparsers.add_parser(name, help='fetches a MathHub repository and its dependencies')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('repository', default=["."], type=util.parseSimpleRepo, nargs='*', help="a list of remote repositories to fetch locally. Should have form mygroup/myproject. No wildcards allowed. ")

def do(args):
  for rep in args.repository:
    installrepo(rep)

def getURL(repoName):
  # TODO: Add different urls here
  root_urls = ["git@gl.mathhub.info:"]

  for url in root_urls:
    if util.git_exists(url+repoName):
      return url+repoName

  raise Exception("Can not find repository "+repoName)


def cloneRepository(repoName):
  try:
    gitpath = util.which("git")
    if os.path.exists(repoName):
      return
    repoURL = getURL(repoName)
    print "cloning " + repoURL    
    call([gitpath, "clone", repoURL, repoName])
  except Exception, e:
    print e
    pass

def installNoCycles(repoName, tried):
  if (repoName) in tried:
    return True

  tried[repoName] = True
  cloneRepository(repoName)

  print "Checking dependencies for project "+repoName
  try:
    deps = util.get_dependencies(repoName)
  except:
    print "Failed to install "+repoName+", please check if it exists. "
    return False
  if deps == None:
    print("Error: META-INF/MANIFEST.MF file missing or invalid.\n You should consider running lmh init.")
    return False

  for dep in deps:
    if not installNoCycles(dep, tried):
      return False

  return True


def installrepo(repoName):
  root = util.lmh_root()+"/MathHub"
  os.chdir(root)
  if not installNoCycles(repoName, {}):
    sys.exit(1)
  else:
    sys.exit(0)

