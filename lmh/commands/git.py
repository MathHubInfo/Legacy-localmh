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

from lmh.lib.repos import parseRepo
from lmh.lib.repos.local import match_repositories
from lmh.lib.repos.local import do as local_do

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Git Wrapper.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="git"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='run git command on multiple repositories')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('cmd', nargs=1, help="a git command to be run.")
  parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs a git command on all repositories currently in lmh")
  parser.add_argument('--args', nargs='+', help="Arguments to add to each of the git commands. ")
  parser.add_argument('repository', type=parseRepo, nargs='*', help="a list of repositories for which to run the git command.")
  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would be equivalent to "git status ."
""";

def do(args):
  repos = match_repositories(args)
  return local_do(args.cmd[0], args.args, *repos)