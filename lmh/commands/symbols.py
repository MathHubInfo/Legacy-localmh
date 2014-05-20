#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: config
   :func: create_parser
   :prog: config

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
import sys
import shutil

from lmh import util
from lmh import config
from lmh import main

from lmh.lib.modules import locate_modules, needsPreamble

def create_parser():
  parser = argparse.ArgumentParser(description='Views or changes lmh configuration. ')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="symbols"):
  parser_status = subparsers.add_parser(name, help='Moves a multilingual module to a new repository')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('--simulate', action="store_const", default=False, const=True, help="Simulate only. ")


  parser.epilog = """
      TBD
  """

def pat_to_match(pat):
  # turn it into a match
  if pat[1] == "i":
    return [pat[0], 1, pat[3], [pat[5]]]
  elif pat[1] == "ii":
    return [pat[0], 2, pat[3], [pat[5], pat[7]]]
  elif pat[1] == "iii":
    return [pat[0], 3, pat[3], [pat[5], pat[7], pat[9]]]


def find_all_defis(text):
  # find all a?defs and turn them into nice matches
  pattern = r"\\(def|adef)(i{1,3})(\[(.*?)\])?({([^{}]+)?})({([^{}]+)?})?({([^{}]+)?})?"
  return [pat_to_match(x) for x in re.findall(pattern, text)]

def find_all_symis(text):
  # find all the symis
  pattern = r"\\begin{modsig}((.|\n)*)\\end{modsig}"
  pattern2 = r"\\(sym)(i{1,3})(\[(.*?)\])?({([^{}]+)?})({([^{}]+)?})?({([^{}]+)?})?"
  matches = re.findall(pattern, text)
  if len(matches) == 0:
    return []
  text = matches[0][0]
  return [pat_to_match(x) for x in re.findall(pattern2, text)]


def do_file(fname):
  with open(fname, 'r') as content_file:
    content = content_file.read()

  defs = find_all_defis(content)
  syms = find_all_symis(content)

  if defs == None:
    defs = []
  if syms == None:
    syms = []

  def has_syms(d):
    req = ["sym", d[1], d[2], d[3]]

    return not (req in syms)

  required = filter(has_syms, defs)
  print "We will have to add: "
  print required
  print "for", fname



def do(args):
  # Find all the modules that we have to worry about
  mods = filter(lambda x:x["type"] == "file", locate_modules(os.getcwd()))
  mods = filter(lambda x:needsPreamble(x["file"]), mods)

  for mod in mods:
    do_file(mod["file"])