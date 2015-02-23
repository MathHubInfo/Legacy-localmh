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
