import os

def about():
    return "List local modules"

def add_parser_args(parser, argparse):
    parser.add_argument('module', nargs='*', default=[os.getcwd()], help="list of module specefiers. ")
    parser.add_argument('-d', '--recursion-depth', type=int, default=-1, help="Recursion depth for paths and repositories. ")

    wheretogen = parser.add_mutually_exclusive_group()
    wheretogen.add_argument('pathspec', metavar="PATH_OR_REPOSITORY", nargs='*', default=[], help="A list of paths or repositories to find modules in. ")
    wheretogen.add_argument('--all', "-a", default=False, const=True, action="store_const", help="Finds modules in all modules. Might take a long time. ")
