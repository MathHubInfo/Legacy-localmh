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
