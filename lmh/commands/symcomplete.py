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

import os
import argparse

from lmh.lib import helper
from lmh.lib.modules.symbols import check_defs

def add_parser(subparsers, name="symcomplete"):
    parser_status = subparsers.add_parser(name, help='Checks language bindings for completeness. ',formatter_class=helper.LMHFormatter)
    add_parser_args(parser_status)

def add_parser_args(parser):
    parser.add_argument("path", nargs="*", default=[], help="Language Bindings to check for completeness. ")

def do(args, unknown_args):
    if len(args.path) == 0:
        args.path = [os.getcwd()]

    res = True
    for p in args.path:
        res = check_defs(p) and res

    return res
