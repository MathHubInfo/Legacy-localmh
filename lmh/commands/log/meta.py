from lmh.lib.help import repo_wildcard_local

def about():
    return "Show recent commits in all repositories"

def add_parser_args(parser, argparse):
    parser.add_argument('--ordered', "-o", default=False, const=True, action="store_const", help="Orders log output by time (instead of by repository). ")
    parser.add_argument('repository', nargs='*', help="a list of repositories for which to show the log. ")
    parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs log on all repositories currently in lmh")
    parser.epilog = repo_wildcard_local
