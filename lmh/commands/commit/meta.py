from lmh.lib.help import repo_wildcard_local

def about():
    return "Commit all changed files"

def add_parser_args(parser, argparse):
    parser.add_argument('repository', nargs='*', help="a list of repositories for which to show the status. ")
    parser.add_argument('--message', "-m", default=["automatic commit by lmh"], nargs=1, help="message to be used for commits")
    parser.add_argument('--verbose', "-v", default=False, const=True, action="store_const", help="be verbose")
    parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs commit on all repositories currently in lmh")
    parser.epilog = repo_wildcard_local
