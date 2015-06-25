from lmh.lib.help import repo_wildcard_remote

def about():
    return "List remote repositories"

def add_parser_args(parser, argparse):
    parser.add_argument('spec', nargs='*', help="list of repository specefiers. ")
    parser.epilog = repo_wildcard_remote
