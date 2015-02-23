from lmh.lib.repos.local import match_repo_args
from lmh.lib.repos.find_and_replace import find
from lmh.lib.help import repo_wildcard_local

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Find tool"
    def add_parser_args(self, parser):
        parser.add_argument('matcher', metavar='matcher', help="RegEx matcher on the path of the module")
        parser.add_argument('--replace', nargs=1, help="Replace string")
        parser.add_argument('--apply', metavar='apply', const=True, default=False, action="store_const", help="Option specifying that files should be changed")
        parser.add_argument('repository', nargs='*', help="a list of repositories for which to show the status. ")
        parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs a git command on all repositories currently in lmh")
        parser.epilog = repo_wildcard_local
    def do(self, args, unknown):
        ret = True
        repos = match_repo_args(args.repository, args.all)
        for rep in repos:
            ret = find(rep, args) and ret

        return ret
