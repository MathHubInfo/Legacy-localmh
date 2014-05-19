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

from lmh.lib.repos.local import create

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Init tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="init"):
  parser_status = subparsers.add_parser(name, help='initialize repository with MathHub repository structure')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('--use-git-root', '-g', action="store_const", default=False, const=True, help="initialise repository in the current git repository root. ")

def do(args): 
  return create("./", args.use_git_root)