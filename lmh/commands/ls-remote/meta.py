from lmh.lib.help import repo_wildcard_remote

def about():
    return "List remote repositories"

def add_parser_args(parser, argparse):
    parser.add_argument('spec', nargs='*', help="list of repository specefiers. ")
    parser.add_argument('-m', '--no-manifest', action="store_true", default=False, help="Do not parse manifest while installing. Equivalent to setting install::nomanifest to True. ")
    parser.epilog = repo_wildcard_remote
