from lmh.lib.io import err
from lmh.lib.help import repo_wildcard_local

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Manages installed repositories. "
    def add_parser_args(self, parser):

        # What to do.
        whatopts = parser.add_mutually_exclusive_group()
        # Install, upgrade, publish
        whatopts.add_argument('--install', dest="action", action="store_const", const="install", help="Install new repositories. ")
        whatopts.add_argument('--publish', dest="action", action="store_const", const="install", help="Publish local changes to remote repositories. ")
        # List the repositories in places.
        whatopts.add_argument('--list-local', dest="action", action="store_const", const="list_local", help="List locally installed repositories. ")
        whatopts.add_argument('--list-remote', dest="action", action="store_const", const="list_local", help="List repositories available remotely. ")

        # and we can also upgrade.
        parser.add_argument('--upgrade-existing', action="store_true", help="Upgrade already installed repositories. ")

        # Simulations and things.
        simopts = parser.add_mutually_exclusive_group()
        simopts.add_argument('--simulate', "-s", default=False, const=True, action="store_const", help="Simulate only. ")
        simopts.add_argument('--no-confirm', "-y", default=False, const=True, action="store_const", help="Skip all confirmation dialogs. ")

        # Which repositories to operate on.
        parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="Run on all repositories instead of at specific ones. ")
        parser.add_argument('spec', nargs='*', help="Repositories to apply actions to. Supports wildcards. ")

        parser.epilog = repo_wildcard_local
    def do(self, args, unparsed):
        # TODO: Stuff
        return False
