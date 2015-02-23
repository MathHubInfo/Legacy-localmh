import os
from lmh.lib.io import std
from lmh.lib.modules import resolve_pathspec

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="List installed modules"
    def add_parser_args(self, parser):
        parser.add_argument('module', nargs='*', default=[os.getcwd()], help="list of module specefiers. ")
        parser.add_argument('-d', '--recursion-depth', type=int, default=-1, help="Recursion depth for paths and repositories. ")

        wheretogen = parser.add_mutually_exclusive_group()
        wheretogen.add_argument('pathspec', metavar="PATH_OR_REPOSITORY", nargs='*', default=[], help="A list of paths or repositories to find modules in. ")
        wheretogen.add_argument('--all', "-a", default=False, const=True, action="store_const", help="Finds modules in all modules. Might take a long time. ")

    def do(self, args, unknown):
        modules = set()
        for m in args.module:
            mods = resolve_pathspec(args, find_alltex=False)
            modules.update([k["file"] for k in mods if "file" in k.keys()])

        for m in sorted(modules):
            std(m)

        return True
