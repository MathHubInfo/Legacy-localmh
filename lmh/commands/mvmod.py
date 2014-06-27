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

from lmh.lib.modules.move import movemod

def create_parser():
  parser = argparse.ArgumentParser(description='Moves a multilingual module to a new repository')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="mvmod"):
  parser_status = subparsers.add_parser(name, help='Moves a multilingual module to a new repository')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('source', nargs=1, help="name of old repository. ")
  parser.add_argument('dest', nargs=1, help="Name of new repository. Assumed to be initalised correctly. ", default=None)
  parser.add_argument('module', nargs="+", help="Relative path(s) of source module(s) in old repository")
  parser.add_argument('--no-depcrawl', action="store_const", default=False, const=True, help="Do not call depcrawl on source and destination. ")
  parser.add_argument('--simulate', action="store_const", default=False, const=True, help="Simulate only. ")


  parser.epilog = """
    Example: lmh mvmod smglom/smglom smglom/set set

    Which moves the multilingual set module from smglom/smglom into the new repository smglom/set.

    It can be advisable to run an lmh clean before executing this command, as it speeds it up quite a lot.
  """
def do(args):
  args.source = args.source[0]
  args.dest = args.dest[0]

  return movemod(args.source, args.dest, args.module, args.no_depcrawl, simulate=args.simulate)
