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

from lmh.lib.repos.local import match_repo_args
from lmh.lib.repos.find_and_replace import find
from lmh.lib.help import repo_wildcard_local


def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Find tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="find"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='find tool')
  add_parser_args(parser_status)


def add_parser_args(parser):
  parser.add_argument('matcher', metavar='matcher', help="RegEx matcher on the path of the module")
  parser.add_argument('--replace', nargs=1, help="Replace string")
  parser.add_argument('--apply', metavar='apply', const=True, default=False, action="store_const", help="Option specifying that files should be changed")
  parser.add_argument('repository', nargs='*', help="a list of repositories for which to show the status. ")
  parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs a git command on all repositories currently in lmh")
  parser.epilog = repo_wildcard_local

def do(args):
  ret = True
  repos = match_repo_args(args.repository, args.all)
  for rep in repos:
      ret = find(rep, args) and ret

  return ret
