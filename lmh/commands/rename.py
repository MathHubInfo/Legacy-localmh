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

from lmh.lib.modules.rename import rename

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Rename symbol names in glossary components"
    def add_parser_args(self, parser):
        parser.add_argument('--directory', '-d', default=os.getcwd(), help="Directory to replace symbols in. Defaults to current directory. ")
        parser.add_argument('--simulate', '-s', default=False, action="store_const", const=True, help="Simulate only. ")
        parser.add_argument('renamings', nargs="+", help="Renamings to be provided in pairs. ", default=None)

        parser.epilog = """
Examples:

lmh rename foo bar
lmh rename foo bar foo2 bar2
lmh rename foo bar-baz """
    def do(self, args, unknown_args):
        return rename(args.directory, args.renamings, simulate=args.simulate)
