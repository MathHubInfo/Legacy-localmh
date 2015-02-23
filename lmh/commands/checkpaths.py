from . import CommandClass

from lmh.lib.modules import checkpaths
from lmh.lib.repos.local import match_repo_args
from lmh.lib.help import repo_wildcard_local

class Command(CommandClass):
    def __init__(self):
        self.help="Check paths for validity"
    def add_parser_args(self, parser):
        parser.add_argument('repository', nargs='*', help="a list of repositories for which to show the status. ")
        parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="generates files for all repositories")
        parser.add_argument('--interactive', metavar='interactive', const=True, default=False, action="store_const", help="Should check paths be interactive")
        parser.epilog = repo_wildcard_local

    def do(self, args, unparsed):
        checkpaths.init()

        ret = True
        repos = match_repo_args(args.repository, args.all)
        for rep in repos:
            ret = checkpaths.checkpaths(rep, args) and ret

        return ret
