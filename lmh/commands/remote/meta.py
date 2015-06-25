from lmh.lib.help import repo_wildcard_local

def about():
    return "Show if repositories are in sync with the remote"

def add_parser_args(parser, argparse):
    parser.add_argument('repository', nargs='*', help="a list of repositories which should be checked. ")
    parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="updates all repositories currently in lmh")

    modes = parser.add_mutually_exclusive_group()

    modes.add_argument("--human", dest="mode", default="human", action="store_const", const="human", help="Show information in human-redable form. Default. ")
    modes.add_argument("--push", dest="mode", action="store_const", const="push", help="Print list of repositories where the remote is older than then local version. ")
    modes.add_argument("--pull", dest="mode", action="store_const", const="pull", help="Print list of repositories where the remote is newer than then local version. ")
    modes.add_argument("--synced", dest="mode", action="store_const", const="synced", help="Print list of repositories where the remote and local version are the same. ")

    parser.epilog = repo_wildcard_local
