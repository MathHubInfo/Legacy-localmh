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

from lmh.commands.gen import locate_modules, needsPreamble

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

def do_file(fname):
  content = util.get_file(fname)
  
  def_pattern = "\\\\def(i{1,3}){(.+)}"

  print fname
  print re.match(def_pattern, content)
  

def do(args):
  # Find all the modules that we have to worry about
  mods = filter(lambda x:x["type"] == "file", locate_modules(os.getcwd()))
  mods = filter(lambda x:needsPreamble(x["file"]), mods)

  for mod in mods:

    do_file(mod["file"])