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
from lmh.lib.io import err
from lmh.lib.packs import update

def add_parser(subparsers, name="selfupdate"):
    subparsers.add_parser(name, help='Updates lmh itself. ',formatter_class=helper.LMHFormatter)

def add_parser_args(parser):
    pass

def do(args, unknown_args):
    # Update the 'self' package
    return update("self")
