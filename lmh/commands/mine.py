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

import os.path
import argparse

from lmh.lib import config
from lmh.lib.io import std, err
from lmh.lib.repos.local import find_all_locals, export, restore

# import the root

def create_parser():
  parser = argparse.ArgumentParser(description='Manages all locally installed repositories. ')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="mine"):
  parser_status = subparsers.add_parser(name, help='Manages all locally installed repositories. ')
  add_parser_args(parser_status)

def add_parser_args(parser):

  group = parser.add_mutually_exclusive_group()

  group.add_argument("--show", dest="dump_action", action="store_const", const=0, default=0, help="Show installed repositories. ")
  group.add_argument("--export", dest="dump_action", action="store_const", const=1, help="Dump list of installed repositories in file. ")
  group.add_argument("--import", dest="dump_action", action="store_const", const=2, help="Install repositories listed in file. ")

  parser.add_argument("file", nargs="?")

def do(args):
  if args.dump_action == 0:
    for m in find_all_locals():
      std(m)
    return True
  elif not args.file[0]:
    err("Missing filename! ")
    return False
  elif args.dump_action == 1:
    fn = os.path.abspath(args.file[0])
    return export(fn)
  elif args.dump_action == 2:
    return restore(fn)