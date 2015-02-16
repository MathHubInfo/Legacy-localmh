#!/usr/bin/env python
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
from lmh.commands.gen import add_parser_args

def create_parser(submods = {}, commands = [], aliases = {}):
    # Create the main parser
    parser = argparse.ArgumentParser(prog="lmh", description='Local MathHub Tool.', formatter_class=helper.LMHFormatter)

    # Standard arguments.
    parser.add_argument("-q", "--quiet", action="store_true", default=False, help="Disables any output to stdout and stderr. ")
    parser.add_argument("--non-interactive", "-ni",  action="store_true", default=False, help="Disables interactivity (prompts from stdin) and causes lmh to abort in those cases. ")

    # Create the subparsers
    subparsers = parser.add_subparsers(help='valid actions are:', dest="action", metavar='action')

    # Register all the normal commands.
    for cmd in commands:
        module = getattr(getattr(__import__("lmh.commands."+cmd), "commands"), cmd)
        submods[cmd] = module
        module.add_parser(subparsers)

    # for all the aliases.
    for alias in aliases:
        parser_status = subparsers.add_parser(alias, help='Alias for lmh '+aliases[alias], add_help=False)

    # TODO: Reimplement lmh root.
    return parser
