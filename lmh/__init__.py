#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

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
import sys
import time
import subprocess
import traceback

from lmh.lib.env import install_dir
import lmh.lib.io
from lmh.lib.io import write_file, std, err
from lmh.lib.config import get_config
from lmh.lib.init import init

from lmh.commands import create_parser
from lmh.commands import gen

# Contains all the subcommands
submods = {}

def install_excepthook():
    #
    # Exception handler
    #
    cwd = os.getcwd()
    def my_excepthook(exctype, value, tb):
        if exctype == KeyboardInterrupt:
            return
        e = ''.join(traceback.format_exception(exctype, value, tb))
        err(e)
        err("lmh seems to have crashed with %s"%exctype)
        err("a report will be generated in ")
        s = "cwd = {0}\n args = {1}\n".format(cwd, sys.argv)
        s = s + e
        write_file(os.path.join(install_dir, "logs", time.strftime("%Y-%m-%d-%H-%M-%S.log")), s)

    sys.excepthook = my_excepthook

def main(argv = sys.argv[1:]):
    """Calls the main program with given arguments. """
    parser = create_parser(submods)

    try:
        argcomplete.autocomplete(parser)
    except:
        pass
    if len(argv) == 0:
        parser.print_help();
        return

    args = parser.parse_args(argv)

    if args.quiet:
        lmh.lib.io.__supressStd__ = True
        lmh.lib.io.__supressErr__ = True
    if args.non_interactive:
        lmh.lib.io.__supressIn__ = True

    #
    # Default action
    #

    if args.action == None:
        init()
        parser.print_help()
        return

    #
    # Quick Aliases
    # TODO: Port them to actual commands
    #

    if args.action == "root":
        std(install_dir)
        return True

    #
    # Aliases for lmh gen --$action
    #
    if args.action == "sms":
        argv[0] = "gen"
        argv.append("--sms")
        return submods["gen"].do(parser.parse_args(argv))

    if args.action == "omdoc":
        argv[0] = "gen"
        argv.append("--omdoc")
        return submods["gen"].do(parser.parse_args(argv))

    if args.action == "pdf":
        argv[0] = "gen"
        argv.append("--pdf")
        return submods["gen"].do(parser.parse_args(argv))

    #
    # Normal run code
    #

    return submods[args.action].do(args)

def run(argv = sys.argv[1:]):
    install_excepthook()
    if(get_config("::eastereggs") == True and argv == ["what", "is", "the", "answer", "to", "life", "the", "universe", "and", "everything?"]):
        sys.exit(42)
    if main(argv):
        sys.exit(0)
    else:
        sys.exit(1)
