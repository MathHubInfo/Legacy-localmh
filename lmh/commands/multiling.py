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
import re
import argparse

from lmh.lib.io import std, err
from lmh.lib.modules.translate import create_multi

def create_parser():
    parser = argparse.ArgumentParser(description='Creates a new multilingual module from a monlingual one. ')
    add_parser_args(parser)
    return parser

def add_parser(subparsers, name="multiling"):
    parser_status = subparsers.add_parser(name, help='Creates a new multilingual module from a monlingual one. ')
    add_parser_args(parser_status)

def add_parser_args(parser):
    parser.add_argument('source', nargs=1, help="Name of the existing module. ")
    parser.add_argument('dest', nargs="+", help="Name(s) of the new language(s). ")

    parser.epilog = """
    Example: lmh multiling mono.tex en de

    Which creates a new multilingual module mono.tex with languages
    mono.en.tex and mono.de.tex

    Will require manual completion of the translations.
    """

def do(args):
    ret = True

    args.source = args.source[0]

    if not os.path.isfile(args.source) or not args.source.endswith(".tex"):
        err("Module", args.source, "does not exist or is not a valid module. ")

    # Remove the .tex
    args.source = args.source[:-len(".tex")]

    return create_multi(args.source, *args.dest)
