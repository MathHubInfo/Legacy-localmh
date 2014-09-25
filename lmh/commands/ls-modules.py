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

import os
from lmh.lib.io import std
from lmh.lib.modules import resolve_pathspec


def create_parser():
    parser = argparse.ArgumentParser(description='Local MathHub List Modules tool.')
    add_parser_args(parser)
    return parser

def add_parser(subparsers, name="ls-modules"):
    parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='lists installed modules')
    add_parser_args(parser_status)


def add_parser_args(parser):
    parser.add_argument('module', nargs='*', default=[os.getcwd()], help="list of module specefiers. ")
    parser.add_argument('-d', '--recursion-depth', type=int, default=-1, help="Recursion depth for paths and repositories. ")

    wheretogen = parser.add_mutually_exclusive_group()
    wheretogen.add_argument('pathspec', metavar="PATH_OR_REPOSITORY", nargs='*', default=[], help="A list of paths or repositories to find modules in. ")
    wheretogen.add_argument('--all', "-a", default=False, const=True, action="store_const", help="Finds modules in all modules. Might take a long time. ")

def do(args):
    modules = set()
    for m in args.module:
        mods = resolve_pathspec(args)
        modules.update([k["file"] for k in mods if "file" in k.keys()])

    for m in sorted(modules):
        std(m)

    return True
