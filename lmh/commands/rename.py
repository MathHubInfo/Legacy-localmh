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
