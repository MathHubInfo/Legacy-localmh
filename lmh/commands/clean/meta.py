from lmh.lib.help import repo_wildcard_local

def about():
    return "Clean repositories of generated files"

def add_parser_args(parser, argparse):
    ps = parser.add_mutually_exclusive_group()
    ps.add_argument('repository', nargs='*', default=[], help="A list of paths or repositories to generate things in. ")
    ps.add_argument('--all', "-a", default=False, const=True, action="store_const", help="generates files for all repositories")
    parser.add_argument('--git-clean', '-g', action="store_true", default=False, help="Also run git clean over all the repositories. ")
    parser.epilog = repo_wildcard_local
