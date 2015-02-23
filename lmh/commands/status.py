from lmh.lib.config import get_config
from lmh.lib.repos.local import match_repo_args, status
from lmh.lib.help import repo_wildcard_local

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Show the working tree status of repositories"
    def add_parser_args(self, parser):
        parser.add_argument('--show-unchanged', '-u', default=False, const=True, action="store_const", help="Also show status on unchanged repositories. ")

        remotes = parser.add_mutually_exclusive_group()
        remotes.add_argument('--remote', '-r', action="store_const", const=True, default=get_config("gl::status_remote_enabled"), dest="remote", help="Enable checking remote for status. Default can be changed by gl::status_remote_enabled. ")
        remotes.add_argument('--no-remote', '-n', action="store_const", const=False, dest="remote", help="Disable checking remote for status. See --remote")

        logtype = parser.add_argument_group("Status Output format ").add_mutually_exclusive_group()
        logtype.add_argument('--long', action="store_const", dest="outputtype", default="--long", const="--long", help="Give the output in the long-format. This is the default.")
        logtype.add_argument('--porcelain', action="store_const", dest="outputtype", const="--porcelain", help="Give the output in an easy-to-parse format for scripts. This is similar to the short output, but will remain stable across Git versions and regardless of user configuration. ")
        logtype.add_argument('--short', action="store_const", dest="outputtype", const="--short", help="Give the output in the short-format.")

        parser.add_argument('repository', nargs='*', help="a list of repositories for which to show the status. ")
        parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs status on all repositories currently in lmh")
        parser.epilog = repo_wildcard_local
    def do(self, args, unknown):
        repos = match_repo_args(args.repository, args.all)
        return status(repos, args.show_unchanged, args.remote, args.outputtype)
