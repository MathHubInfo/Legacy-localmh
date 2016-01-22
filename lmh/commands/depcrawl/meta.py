from lmh.lib.help import repo_wildcard_local

def about():
    return "Crawl current repository for dependencies"

def add_parser_args(parser, argparse):
    parser.add_argument('repository', nargs='*', help="a list of repositories for which to show the status. ")
    parser.add_argument('--apply', metavar='apply', const=True, default=False, action="store_const", help="Writes found dependencies to MANIFEST.MF")
    parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs commit on all repositories currently in lmh")
    parser.epilog = repo_wildcard_local
