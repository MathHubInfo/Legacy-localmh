#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: status
   :func: create_parser
   :prog: status

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
import glob
import subprocess
import argparse

from lmh import util

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Status tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="status"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='shows the working tree status of repositories')
  add_parser_args(parser_status)


def add_parser_args(parser):
  parser.add_argument('repository', type=util.parseRepo, nargs='*', help="a list of repositories for which to show the status. ").completer = util.autocomplete_mathhub_repository
  parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs status on all repositories currently in lmh")

  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would be equivalent to "git status ."
""";

def do_status(rep):
  cmd = [util.which("git"), "status", "-u", "-s"];
  result = subprocess.Popen(cmd, 
                                stdout=subprocess.PIPE,
                                cwd=rep
                               ).communicate()[0]
  if len(result) == 0:
    return

  print rep
  print result

def do(args):
  if len(args.repository) == 0:
    args.repository = [util.tryRepo(".", util.lmh_root()+"/MathHub/*/*")]
  if args.all:
    args.repository = [util.tryRepo(util.lmh_root()+"/MathHub", util.lmh_root()+"/MathHub")]
  for repo in args.repository:
    for rep in glob.glob(repo):
      do_status(rep);
