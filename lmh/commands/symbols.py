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
from lmh.lib.modules.symbols import check_symbols


def add_parser(subparsers, name="symbols"):
    parser_status = subparsers.add_parser(name, help='Generates smybols needed by language bindings. ',formatter_class=helper.LMHFormatter)
    add_parser_args(parser_status)

def add_parser_args(parser):
    parser.add_argument("path", nargs="*", default=[], help="Path to modules where to generate symbols. ")
    parser.epilog = """
Example:
    lmh symbols .
will generate symbols in all files in the current directory. Can be used on
single files, however it needs to know which language bindings to add new
symbols from.
Use
    lmh symbols foo.*.tex
to add missing symbols from language bindings to foo.tex.
Use
    lmh symbols foo.tex
to display warnings about double symdef and symi warnings.
"""

def do(args):
    if len(args.path) == 0:
        args.path = [os.getcwd()]

    res = True
    for p in args.path:
        res = check_symbols(p) and res

    return res
