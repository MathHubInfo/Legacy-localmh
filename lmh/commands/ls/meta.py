from lmh.lib.help import repo_wildcard_local

def about():
    return "List installed repositories"

def add_parser_args(parser, argparse):
    parser.add_argument('repository', nargs='*', help="list of repository specefiers. ")
    parser.add_argument('--abs', '-A', default=False, action="store_true", help="Print absolute repository paths. ")
    parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="list all repositories")
    parser.epilog = repo_wildcard_local
