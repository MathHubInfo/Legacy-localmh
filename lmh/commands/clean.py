#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: clean
   :func: create_parser
   :prog: clean

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
import glob
import argparse
import subprocess

from lmh import util
from lmh.commands.gen import resolve_pathspec

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Clean tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="clean"):
  parser_clean = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='clean repositories of generated files')
  add_parser_args(parser_clean)

def add_parser_args(parser):
  ps = parser.add_mutually_exclusive_group()
  ps.add_argument('pathspec', metavar="PATH_OR_REPOSITORY", nargs='*', default=[], help="A list of paths or repositories to generate things in. ")
  ps.add_argument('--all', "-a", default=False, const=True, action="store_const", help="generates files for all repositories")  

  parser.add_argument('-d', '--recursion-depth', type=int, default=-1, help="Recursion depth for paths and repositories. ")


  parser.add_argument('--verbose', "-v", default=False, const=True, action="store_const", help="prints lots of debug output to the console ")  

  types = parser.add_argument_group()
  types.add_argument('--keep-omdoc', default=False, const=True, action="store_const", help="keep omdoc files")  
  types.add_argument('--keep-omdoc-log', default=False, const=True, action="store_const", help="keep omdoc log files")  
  types.add_argument('--keep-pdf', default=False, const=True, action="store_const", help="keep pdf files")  
  types.add_argument('--keep-pdf-log', default=False, const=True, action="store_const", help="keep pdf log files")  
  types.add_argument('--keep-sms', default=False, const=True, action="store_const", help="keep sms files") 
  types.add_argument('--keep-alltex', default=False, const=True, action="store_const", help="keep all.tex files") 
  types.add_argument('--keep-localpaths', default=False, const=True, action="store_const", help="keep localpaths.tex files") 

def do(args):
  try:
    if args.verbose:
      print "Looking for modules ..."
    modules = resolve_pathspec(args)
    if args.verbose:
      print "Found", len(modules), "paths to work on. "
  except KeyboardInterrupt:
    print "<<KeyboardInterrupt>>"
    sys.exit(1) 

  if args.verbose:
    def rm(file):
      print "Removing", file
      os.remove(file)
  else:
    def rm(file):
      os.remove(file)

  # remove all the modules
  for mod in modules:
    if mod["type"] == "file":
      if os.path.isfile(mod["omdoc_path"]) and not args.keep_omdoc:
        rm(mod["omdoc_path"])
      if os.path.isfile(mod["omdoc_log"]) and not args.keep_omdoc_log:
        rm(mod["omdoc_log"])
      if os.path.isfile(mod["pdf_path"]) and not args.keep_pdf:
        rm(mod["pdf_path"])
      if os.path.isfile(mod["pdf_log"]) and not args.keep_pdf_log:
        rm(mod["pdf_log"])
      if os.path.isfile(mod["sms"]) and not args.keep_sms:
        rm(mod["sms"])
    else:
      if os.path.isfile(mod["alltex_path"]) and not args.keep_alltex:
        rm(mod["alltex_path"])
      if os.path.isfile(mod["localpaths_path"]) and not args.keep_localpaths:
        rm(mod["localpaths_path"])


