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

from lmh.lib.io import std
from lmh.lib.repos.local import match_repo_args, status


def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub List tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="ls"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='lists installed repositories')
  add_parser_args(parser_status)


def add_parser_args(parser):
  parser.add_argument('repository', nargs='*', help="list of repository specefiers. ")
  parser.add_argument('--abs', '-A', default=False, action="store_true", help="Print absolute repository paths. ")
  parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="list all repositories")

  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths.
  Example:
    */*       - would match all repositories from all groups.
    mygroup/* - would match all repositories from group mygroup
    .         - matches current repository
Please remember that shell such as bash auto-expand glob arguments. You can use
's to avoid this.
"""

def do(args):
    repos = match_repo_args(args.repository, args.all, abs=args.abs)
    for r in repos:
      std(r)
    return True