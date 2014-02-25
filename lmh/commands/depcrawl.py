#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: depcrawl
   :func: create_parser
   :prog: depcrawl

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

import os
import re
import argparse

from lmh import util

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Path Management tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="depcrawl"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='crawls current repository for dependencies')
  add_parser_args(parser_status)


def add_parser_args(parser):
  parser.add_argument('--apply', metavar='apply', const=True, default=False, action="store_const", help="Option specifying that files should be changed")

def calcDeps(dir="."):
  currentdeps = {};
  for dep in util.get_dependencies(dir):
    currentdeps["/".join(dep)] = True

  paths = {};
  for root, dirs, files in os.walk("."):
      path = root.split('/')
      for file in files:
        fileName, fileExtension = os.path.splitext(file)
        if fileExtension != ".tex":
          continue
        file = open(root+"/"+file, "r")
        for line in file:
          m = re.search("\\MathHub{([\w/]+)}", line)
          if m:
            paths[m.group(1)] = True
          m = re.search("\\importmhmodule\[([\w/]+)\]", line)
          if m:
            paths[m.group(1)] = True
          m = re.search("\\usemhmodule\[([\w/]+)\]", line)
          if m:
            paths[m.group(1)] = True
          m = re.search("\\adoptmhmodule\[([\w/]+)\]", line)
          if m:
            paths[m.group(1)] = True

  repos = {};
  for path in paths:
    comps = path.split("/")
    if len(comps) < 2:
      continue
    repos[comps[0]+"/"+comps[1]] = True

  toAdd = [];
  for rep in repos:
    if rep not in currentdeps:
      toAdd.append(rep)
  

  return " ".join(toAdd);

def do(rest):
  print calcDeps()