from lmh.lib.repos.local import match_repo_args, push
from lmh.lib.help import repo_wildcard_local

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Send changes to MathHub"
    def add_parser_args(self, parser):
        parser.add_argument('repository', nargs='*', help="a list of repositories for which to show the status. ")
        parser.add_argument('--verbose', "-v", default=False, const=True, action="store_const", help="be verbose")
        parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs status on all repositories currently in lmh")
        parser.epilog = repo_wildcard_local
    def do(self, args, unknown):
        repos = match_repo_args(args.repository, args.all)
        return push(args.verbose, *repos)
