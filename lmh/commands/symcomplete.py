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

from lmh.lib.modules.symbols import check_defs

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Checks language bindings for completeness"
    def add_parser_args(self, parser):
        parser.add_argument("path", nargs="*", default=[], help="Language Bindings to check for completeness. ")
    def do(self, args, unknown):
        if len(args.path) == 0:
            args.path = [os.getcwd()]

        res = True
        for p in args.path:
            res = check_defs(p) and res

        return res
