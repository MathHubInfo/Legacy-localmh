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

import sys

from lmh.lib.extenv import run_shell

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Launch a shell with everything set to run build commands"
    def add_parser_args(self, parser):
        parser.add_argument('shell', nargs="?", help="shell to use")
        parser.add_argument('--args', default="", help="Arguments to append to the shell. ")
    def do(self, args, unknown_args):
        code = run_shell(args.shell, args.args)
        sys.exit(code)
