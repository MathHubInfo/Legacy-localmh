#!/usr/bin/env python

"""
Local Math Hub repository installer export/import

.. argparse::
   :module: mine
   :func: create_parser
   :prog: mine

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

import argparse
import os.path

from lmh.lib import config
from lmh.commands import install
from lmh.lib.repos.local import export, restore

# import the root

def create_parser():
  parser = argparse.ArgumentParser(description='Manages all locally installed repositories. ')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="mine"):
  parser_status = subparsers.add_parser(name, help='Manages all locally installed repositories. ')
  add_parser_args(parser_status)

def add_parser_args(parser):

  group = parser.add_mutually_exclusive_group(required=True)

  group.add_argument("--export", action="store_const", const=True, default=False, help="Dump list of installed repositories in file. ")
  group.add_argument("--import", dest="export", action="store_const", const=False, help="Install repositories listed in file. ")

  parser.add_argument("file", help="File to use. ")

def do(args):

  fn = os.path.abspath(args.file)

  if args.export:
    return export(fn)
  else:
    return restore(fn)