#!/usr/bin/env python
import argparse

from lmh.lib import helper
from lmh.lib.io import err

class CommandClass():
    def __init__(self):
        self.help = "<No help available for this command>"
    def add_parser_args(self, parser):
        pass
    def do(self, arguments, unparsed):
        pass

def load_command(cmd, subparsers):

    # Load the module
    module = getattr(getattr(__import__("lmh.commands."+cmd), "commands"), cmd)

    # if we have a class attribute, use the class
    # else, use just the module
    try:
        command = module.Command()

        # Create the sub parser
        new_parser = subparsers.add_parser(cmd, help=command.help, description=command.help, formatter_class=helper.LMHFormatter)

        # and add some arguments.
        command.add_parser_args(new_parser)
    except Exception as e:
        err(e)
        err("Command", cmd, "failed to load. ")
        command = None

    # return the new command instance.
    return command


def create_parser(submods = {}, commands = [], aliases = {}):
    # Create the main parser
    parser = argparse.ArgumentParser(prog="lmh", description='Local MathHub Tool.', formatter_class=helper.LMHFormatter)

    # Standard arguments.
    parser.add_argument("-q", "--quiet", action="store_true", default=False, help="Disables any output to stdout and stderr. ")
    parser.add_argument("--non-interactive", "-ni",  action="store_true", default=False, help="Disables interactivity (prompts from stdin) and causes lmh to abort in those cases. ")

    # Create the subparsers
    subparsers = parser.add_subparsers(help='valid actions are:', dest="action", metavar='action')

    # Load all the commands.
    for cmd in commands:
        submods[cmd] = load_command(cmd, subparsers)

    # for all the aliases.
    for alias in aliases:
        subparsers.add_parser(alias, help='Alias for lmh '+aliases[alias], add_help=False)

    return parser
