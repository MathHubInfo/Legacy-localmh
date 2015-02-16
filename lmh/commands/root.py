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
from lmh.lib.io import std
from lmh.lib.env import install_dir

def add_parser(subparsers, name="root"):
    about_parser = subparsers.add_parser(name, help='shows the root directory of the lmh installation. ', formatter_class=helper.LMHFormatter)
    add_parser_args(about_parser)

def add_parser_args(parser):
    pass

def do(args, unknown_args):
    std(install_dir)
    return True
