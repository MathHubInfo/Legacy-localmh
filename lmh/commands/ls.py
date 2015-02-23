from lmh.lib.io import std
from lmh.lib.repos.local import match_repo_args
from lmh.lib.help import repo_wildcard_local

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="List installed repositories"
    def add_parser_args(self, parser):
        parser.add_argument('repository', nargs='*', help="list of repository specefiers. ")
        parser.add_argument('--abs', '-A', default=False, action="store_true", help="Print absolute repository paths. ")
        parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="list all repositories")
        parser.epilog = repo_wildcard_local
    def do(self, args, unknown_args):
        repos = match_repo_args(args.repository, args.all, abs=args.abs)
        for r in repos:
            std(r)
        return True
