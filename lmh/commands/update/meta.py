from lmh.lib.help import repo_wildcard_local

def about():
    return "Get repository and tool updates"

def add_parser_args(parser, argparse):
    parser.add_argument('repository', nargs='*', help="a list of repositories which should be updated. ")
    parser.add_argument('--verbose', "-v", default=False, const=True, action="store_const", help="be verbose")
    parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="updates all repositories currently in lmh")
    parser.epilog = """
If update::selfupdate is set to True, calling lomh update without any arguments
will also call lmh selfupdate.

Note: LMH will check for tool updates only if run at the root of the LMH
folder. """+repo_wildcard_local
