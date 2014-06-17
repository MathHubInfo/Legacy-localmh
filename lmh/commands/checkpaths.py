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

from lmh.lib.modules import checkpaths
from lmh.lib.repos.local import match_repo_args
from lmh.lib.help import repo_wildcard_local

def create_parser():
	parser = argparse.ArgumentParser(description='Local MathHub Path Checking tool.')
	add_parser_args(parser)
	return parser

def add_parser(subparsers, name="checkpaths"):
	parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='check paths for validity')
	add_parser_args(parser_status)


def add_parser_args(parser):
	parser.add_argument('repository', nargs='*', help="a list of repositories for which to show the status. ")
	parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="generates files for all repositories")

	parser.add_argument('--interactive', metavar='interactive', const=True, default=False, action="store_const", help="Should check paths be interactive")
	parser.epilog = repo_wildcard_local

def do(args):

	checkpaths.init()

	ret = True
	repos = match_repo_args(args.repository, args.all)
	for rep in repos:
			ret = checkpaths.checkpaths(rep, args) and ret

	return ret
