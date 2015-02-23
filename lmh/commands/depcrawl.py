from lmh.lib.io import err
from lmh.lib.repos.local import calc_deps

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Crawl current repository for dependencies"
    def add_parser_args(self, parser):
        parser.add_argument('--apply', metavar='apply', const=True, default=False, action="store_const", help="Writes found dependencies to MANIFEST.MF")
    def do(self, args, unknown):
        res = calc_deps(args.apply)
        if res:
            return True
        else:
            err("lmh depcrawl must be run from within a Repository. ")
            return False
