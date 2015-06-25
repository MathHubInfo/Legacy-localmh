import os
import sys
import json
import time
import shlex
import traceback

from lmh.lib.env import install_dir
import lmh.lib.io
from lmh.lib.io import read_file, write_file, err
from lmh.lib.config import get_config

from lmh.commands import create_parser

# Contains all the subcommands
submods = {}

def install_excepthook():
    """Hook to handle exceptions. """
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

def main(argv=sys.argv[1:]):
    """Calls the main program with given arguments. """

    # Load commands + aliases
    commands = json.loads(read_file(install_dir + "/lmh/data/commands.json"))
    aliases = json.loads(read_file(install_dir + "/lmh/data/aliases.json"))

    parser = create_parser(submods, commands, aliases)

    if len(argv) == 0:
        parser.print_help()
        return

    # parse arguments
    (args, unknown) = parser.parse_known_args(argv)

    # do the quiet stuff.
    if args.quiet:
        lmh.lib.io.__supressStd__ = True
        lmh.lib.io.__supressErr__ = True
    if args.non_interactive:
        lmh.lib.io.__supressIn__ = True

    # No action.
    if args.action == None:
        parser.print_help()
        return

    # an alias, so change the arguments.
    if args.action in aliases:

        # new argvs
        argv = shlex.split(aliases[args.action]) + unknown

        # and re-parse
        (args, unknown) = parser.parse_known_args(argv)

    try:
        if not submods[args.action].allow_unknown and len(unknown) > 0:
            err("Too many arguments. ")
            return False
    except Exception as e:
        err(e)

    # run normally.
    return submods[args.action].do(args, unknown)

def run(argv=sys.argv[1:]):
    install_excepthook()
    if(get_config("::eastereggs") == True and argv == ["what", "is", "the", "answer", "to", "life", "the", "universe", "and", "everything?"]):
        sys.exit(42)
    if main(argv):
        sys.exit(0)
    else:
        sys.exit(1)
