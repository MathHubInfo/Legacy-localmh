from lmh.lib.help import repo_wildcard_local

def about():
    return "Run git command on multiple repositories"

allow_unknown_args = True
def add_parser_args(parser, argparse):
    parser.add_argument('cmd', nargs=1, help="a git command to be run.")
    parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs a git command on all repositories currently in lmh")
    parser.add_argument('--args', nargs='+', help="Arguments to add to each of the git commands. ")
    parser.add_argument('repository', nargs='*', help="a list of repositories for which to run the git command.")
    parser.epilog = repo_wildcard_local
