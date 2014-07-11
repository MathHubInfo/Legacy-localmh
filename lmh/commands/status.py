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

from lmh.lib.repos.local import match_repo_args, status
from lmh.lib.help import repo_wildcard_local


def create_parser():
    parser = argparse.ArgumentParser(description='Local MathHub Status tool.')
    add_parser_args(parser)
    return parser

def add_parser(subparsers, name="status"):
    parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='shows the working tree status of repositories')
    add_parser_args(parser_status)


def add_parser_args(parser):
    parser.add_argument('--show-unchanged', '-u', default=False, const=True, action="store_const", help="Also show status on unchanged repositories. ")

    logtype = parser.add_argument_group("Status Output format ").add_mutually_exclusive_group()
    logtype.add_argument('--long', action="store_const", dest="outputtype", default="--long", const="--long", help="Give the output in the long-format. This is the default.")
    logtype.add_argument('--porcelain', action="store_const", dest="outputtype", const="--porcelain", help="Give the output in an easy-to-parse format for scripts. This is similar to the short output, but will remain stable across Git versions and regardless of user configuration. ")
    logtype.add_argument('--short', action="store_const", dest="outputtype", const="--short", help="Give the output in the short-format.")


    parser.add_argument('repository', nargs='*', help="a list of repositories for which to show the status. ")
    parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs status on all repositories currently in lmh")
    parser.epilog = repo_wildcard_local

def do(args):
    repos = match_repo_args(args.repository, args.all)
    return status(repos, args.show_unchanged, args.outputtype)
