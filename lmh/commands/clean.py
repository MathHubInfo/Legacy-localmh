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

from lmh.lib.repos.local import match_repo_args, clean
from lmh.lib.help import repo_wildcard_local

def create_parser():
    parser = argparse.ArgumentParser(description='Local MathHub Clean tool.')
    add_parser_args(parser)
    return parser

def add_parser(subparsers, name="clean"):
    parser_clean = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='clean repositories of generated files')
    add_parser_args(parser_clean)

def add_parser_args(parser):
    ps = parser.add_mutually_exclusive_group()
    ps.add_argument('repository', nargs='*', default=[], help="A list of paths or repositories to generate things in. ")
    ps.add_argument('--all', "-a", default=False, const=True, action="store_const", help="generates files for all repositories")

    parser.add_argument('--git-clean', '-g', action="store_true", default=False, help="Also run git clean over all the repositories. ")

    parser.epilog = repo_wildcard_local

def do(args):
    repos = match_repo_args(args.repository, args.all)
    res = True
    for repo in repos:
        res = clean(repo, git_clean = args.git_clean) and res
    return res
