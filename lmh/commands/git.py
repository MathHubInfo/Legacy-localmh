from lmh.lib.repos.local import match_repo_args
from lmh.lib.repos.local import do as local_do
from lmh.lib.help import repo_wildcard_local

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Run git command on multiple repositories"
    def add_parser_args(self, parser):
        parser.add_argument('cmd', nargs=1, help="a git command to be run.")
        parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs a git command on all repositories currently in lmh")
        parser.add_argument('--args', nargs='+', help="Arguments to add to each of the git commands. ")
        parser.add_argument('repository', nargs='*', help="a list of repositories for which to run the git command.")
        parser.epilog = repo_wildcard_local

    def do(self, args, unknown):
        repos = match_repo_args(args.repository, args.all)
        args.args += unknown
        return local_do(args.cmd[0], args.args, *repos)
