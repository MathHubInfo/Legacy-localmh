from lmh.lib.repos.local import match_repo_args, log
from lmh.lib.help import repo_wildcard_local

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Show recent commits in all repositories"
    def add_parser_args(self, parser):
        parser.add_argument('--ordered', "-o", default=False, const=True, action="store_const", help="Orders log output by time (instead of by repository). ")
        parser.add_argument('repository', nargs='*', help="a list of repositories for which to show the log. ")
        parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs log on all repositories currently in lmh")
        parser.epilog = repo_wildcard_local
    def do(self, args, unknown):
        repos = match_repo_args(args.repository, args.all)
        return log(args.ordered, *repos)
