from lmh.lib.config import get_config

def about():
    return "Generate MathHub Content. "

def add_parser_args(parser, argparse):
    f = parser.add_argument_group("Generic Options")

    f1 = f.add_mutually_exclusive_group()
    f1.add_argument('-w', '--workers',  metavar='number', default=get_config("gen::default_workers"), type=int, help='Number of worker processes to use. Default determined by gen::default_workers. ')
    f1.add_argument('-s', '--single',  action="store_const", dest="workers", const=1, help='Use only a single process. Shortcut for -w 1')

    f2 = f.add_mutually_exclusive_group()
    f2.add_argument('-n', '--nice', type=int, default=1, help="Assign the worker processes the given niceness. ")
    f2.add_argument('-H', '--high', const=0, dest="nice", action="store_const", help="Generate files using the same priority as the main process. ")

    whattogen = parser.add_argument_group("What to generate")

    whattogen.add_argument('--sms', action="store_const", const=True, default=False, help="generate sms files")
    whattogen.add_argument('--omdoc', action="store_const", const=True, default=False, help="generate omdoc files")
    whattogen.add_argument('--pdf', action="store_const", const=True, default=False, help="generate pdf files")
    whattogen.add_argument('--xhtml', action="store_const", const=True, default=False, help="generate xhtml files")

    wheretogen = parser.add_argument_group("Where to generate")

    wheretogen = wheretogen.add_mutually_exclusive_group()
    wheretogen.add_argument('pathspec', metavar="PATH_OR_REPOSITORY", nargs='*', default=[], help="A list of paths or repositories to generate things in. ")

    return parser
