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

import argparse

from lmh import util

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Configuration Tool. ')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="config"):
  about_parser = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='configures this lmh installation. ')
  add_parser_args(about_parser)

def add_parser_args(parser):
  parser.add_argument('-a', '--all', action="store_const", const=True, default=False, help="Shows all available settings. ")
  parser.add_argument('--reset', action="store_const", const=True, default=False, help="Resets the given setting or all settings. ")
  parser.add_argument('setting', nargs='?', default=None, metavar="setting", help="Setting to show or edit. ")
  parser.add_argument('value', nargs='?', default=None, help="New value for setting. ")
def do(args):
  if args.all == True:
    print "List all"
    pass
  elif args.value == None:
    if args.setting == None:
      print "Nothing to do ..."
    else:
      print util.get_setting(args.setting)
  else:
    print ""
