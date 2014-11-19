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

from lmh.lib import helper
import lmh.commands.gen
import lmh.commands.clean

from lmh.lib.help import repo_wildcard_local

def add_parser(subparsers, name="update-build"):
    parser_status = subparsers.add_parser(name, formatter_class=helper.LMHFormatter, help='Updates the build. ')
    add_parser_args(parser_status)

def add_parser_args(parser):
    parser = lmh.commands.gen.add_parser_args(parser)
    parser.add_argument('--git-clean', '-g', action="store_true", default=False, help="Also run git clean over all the repositories. ")
    parser.epilog = repo_wildcard_local

    return parser


def do(args):
    args.repository = args.pathspec
    res = lmh.commands.clean.do(args)
    res = lmh.commands.gen.do(args) or res
    return res
