#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility.

.. argparse::
   :module: xhtml
   :func: create_parser
   :prog: xhtml

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

from lmh.lib.io import err
from lmh.lib.repos.local import match_repo_args

import argparse

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub XHTML tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="xhtml"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='generate XHTML ')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('repository', nargs='*', help="a list of repositories for which to generate XHTML")
  parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs status on all repositories currently in lmh")
  pass

def do_xhtml(rep):
  rep_root = util.git_root_dir(rep)
  def msg(m):
    pass
  pass

def do(args):
  err("Warning: lmh xhtml is currently outdated, whatever you are trying to do wont work. ")
  err("If you really need it, you can ask a wizard to enlarge lmh. ")
  return False

  mat_repo_args(arg)

  repos = match_repo_args(args.repository, args.all)

  for rep in repos:
      do_xhtml(rep)
