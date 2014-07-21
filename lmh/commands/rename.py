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
import argparse

from lmh.lib.modules.rename import rename

def create_parser():
  parser = argparse.ArgumentParser(description='Renames symbol names in glossary components. ')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="rename"):
  parser_status = subparsers.add_parser(name, help='Renames symbol names in glossary components. ')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('--directory', '-d', default=os.getcwd(), help="Directory to replace symbols in. Defaults to current directory. ")
  parser.add_argument('--simulate', '-s', default=False, action="store_const", const=True, help="Simulate only. ")
  parser.add_argument('renamings', nargs="+", help="Renamings to be provided in pairs. ", default=None)


  parser.epilog = """
    Examples:

    lmh rename foo bar
    lmh rename foo bar foo2 bar2
    lmh rename foo bar-baz
  """
def do(args):
    return rename(args.directory, args.renamings, simulate=args.simulate)
