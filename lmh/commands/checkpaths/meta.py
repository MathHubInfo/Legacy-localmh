from lmh.lib.help import repo_wildcard_local

def about():
    return "Check paths for validity"

def add_parser_args(parser, argparse):
    parser.add_argument('repository', nargs='*', help="a list of repositories for which to show the status. ")
    parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="generates files for all repositories")
    parser.add_argument('--interactive', metavar='interactive', const=True, default=False, action="store_const", help="Should check paths be interactive")
    parser.epilog = repo_wildcard_local
