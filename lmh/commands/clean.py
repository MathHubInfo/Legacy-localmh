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

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Clean tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="clean"):
  parser_clean = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='clean repositories of generated files')
  add_parser_args(parser_clean)

def add_parser_args(parser):
  parser.add_argument('repository', type=util.parseRepo, nargs='*', help="a list of repositories for which to show the clean. ").completer = util.autocomplete_mathhub_repository
  parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs status on all repositories currently in lmh")

  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would be equivalent to "git clean ."
""";

def do_clean(rep):
  remove = [];
  rep_root = util.git_root_dir(rep);
  ignoreFile = rep_root+"/.gitignore";
  if not os.path.exists(ignoreFile):
    print "No .gitignore file found in %s"%rep_root
    return
  for line in open(ignoreFile):
    pattern = line.strip()
    if len(pattern) > 0:
      remove.append(pattern);

  for root, dirs, files in os.walk(rep):
    for rem in remove:
      for file in glob.glob(root+"/"+rem):
        os.remove(file)

def do(args):
  if len(args.repository) == 0:
    args.repository = [util.tryRepo(".", util.lmh_root()+"/MathHub/*/*")]
  if args.all:
    args.repository = [util.tryRepo(util.lmh_root()+"/MathHub", util.lmh_root()+"/MathHub")]  
  for repo in args.repository:
    for rep in glob.glob(repo):
      do_clean(rep);
