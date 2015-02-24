from lmh.lib.io import std, term_colors
from lmh.lib.repos.local.package import is_installed
from lmh.lib.repos.remote import ls_remote
from lmh.lib.help import repo_wildcard_remote

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="List remote repositories"
    def add_parser_args(self, parser):
        parser.add_argument('spec', nargs='*', help="list of repository specefiers. ")
        parser.add_argument('-m', '--no-manifest', action="store_true", default=False, help="Do not parse manifest while installing. Equivalent to setting install::nomanifest to True. ")
        parser.epilog = repo_wildcard_remote
    def do(self, args, unknown):
        res = ls_remote(args.no_manifest, *args.spec)
        if res == False:
            return False
        else:
            for r in res:
                if is_installed(r):
                    std(term_colors("green")+r+term_colors("normal"))
                else:
                    std(term_colors("red")+r+term_colors("normal"))
            return True
