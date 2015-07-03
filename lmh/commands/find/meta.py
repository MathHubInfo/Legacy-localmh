from lmh.lib.help import repo_wildcard_local

def about():
    return "Find tool"

def add_parser_args(parser, argparse):
    parser.add_argument('matcher', metavar='matcher', help="RegEx matcher on the path of the module")
    parser.add_argument('--replace', nargs=1, help="Replace string")
    parser.add_argument('--apply', metavar='apply', const=True, default=False, action="store_const", help="Option specifying that files should be changed")
    parser.add_argument('repository', nargs='*', help="a list of repositories for which to show the status. ")
    parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs a git command on all repositories currently in lmh")
    parser.epilog = repo_wildcard_local
