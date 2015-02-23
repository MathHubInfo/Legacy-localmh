from lmh.lib.io import std
from lmh.lib.git import get_remote_status
from lmh.lib.packs import update
from lmh.lib.repos.local import match_repo_args
from lmh.lib.config import get_config
from lmh.lib.help import repo_wildcard_local

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Show if repositories are in sync with the remote"
    def add_parser_args(self, parser):
        parser.add_argument('repository', nargs='*', help="a list of repositories whcih should be checked. ")
        parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="updates all repositories currently in lmh")

        modes = parser.add_mutually_exclusive_group()

        modes.add_argument("--human", dest="mode", default="human", action="store_const", const="human", help="Show information in human-redable form. Default. ")
        modes.add_argument("--push", dest="mode", action="store_const", const="push", help="Print list of repositories where the remote is older than then local version. ")
        modes.add_argument("--pull", dest="mode", action="store_const", const="pull", help="Print list of repositories where the remote is newer than then local version. ")
        modes.add_argument("--synced", dest="mode", action="store_const", const="synced", help="Print list of repositories where the remote and local version are the same. ")

        parser.epilog = repo_wildcard_local
    def do(self, args, unknown_args):

        def needs_push(r):
            state = get_remote_status(r)
            return state == "push" or state == "failed" or state == "divergence"
        def needs_pull(r):
            state = get_remote_status(r)
            return state == "push" or state == "failed" or state == "divergence"

        if False and len(args.repository) == 0:
            if get_config("update::selfupdate"):
                std("Selfupdate: ")
                if not update("self"):
                    return False

        repos = match_repo_args(args.repository, args.all)

        if args.mode == "human":
            for r in repos:
                state = get_remote_status(r)
                if state == "ok":
                    std(r, "Synced")
                elif state == "push":
                    std(r, "Local version newer, to sync run git push")
                elif state == "pull":
                    std(r, "Remote version newer, to sync run git pull")
                elif state == "divergence":
                    std(r, "Diverged from remote")
        elif args.mode == "synced":
            [std(r) for r in repos if get_remote_status(r) == "ok"]
        elif args.mode == "push":
            [std(r) for r in repos if needs_push(r)]
        elif args.mode == "pull":
            [std(r) for r in repos if needs_pull(r)]

        return True
