from lmh.lib.io import std
from lmh.lib.packs import update
from lmh.lib.repos.local import match_repo_args, pull
from lmh.lib.config import get_config
from lmh.lib.help import repo_wildcard_local

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Get repository and tool updates"
    def add_parser_args(self, parser):
        parser.add_argument('repository', nargs='*', help="a list of repositories which should be updated. ")
        parser.add_argument('--verbose', "-v", default=False, const=True, action="store_const", help="be verbose")
        parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="updates all repositories currently in lmh")
        parser.epilog = """
    If update::selfupdate is set to True, calling lomh update without any arguments
    will also call lmh selfupdate.

    Note: LMH will check for tool updates only if run at the root of the LMH
    folder. """+repo_wildcard_local

    def do(self, args, unknown_args):

        if False and len(args.repository) == 0:
            if get_config("update::selfupdate"):
                std("Selfupdate: ")
                if not update("self"):
                    return False

        repos = match_repo_args(args.repository, args.all)
        return pull(args.verbose, *repos)
