from lmh.lib.config import get_config

def about():
    return "Update generated content"

def add_parser_args(parser, argparse):
    f = parser.add_argument_group("Generic Options")

    f1 = f.add_mutually_exclusive_group()
    f1.add_argument('-w', '--workers',  metavar='number', default=get_config("gen::default_workers"), type=int, help='Number of worker processes to use. Default determined by gen::default_workers. ')
    f1.add_argument('-s', '--single',  action="store_const", dest="workers", const=1, help='Use only a single process. Shortcut for -w 1')

    f2 = f.add_mutually_exclusive_group()
    f2.add_argument('-n', '--nice', type=int, default=1, help="Assign the worker processes the given niceness. ")
    f2.add_argument('-H', '--high', const=0, dest="nice", action="store_const", help="Generate files using the same priority as the main process. ")

    f3 = f.add_mutually_exclusive_group()
    f3.add_argument('-v', '--verbose', '--simulate', const=True, default=False, action="store_const", help="Dump commands for generation to STDOUT instead of running them. Implies --quiet. ")
    f3.add_argument('-q', '--quiet', const=True, default=False, action="store_const", help="Do not write log messages to STDOUT while generating files. ")

    f4 = parser.add_argument_group("Which files to generate").add_mutually_exclusive_group()
    f4.add_argument('-u', '--update', const="update", default="update", action="store_const", help="Only generate files which have been changed, based on original files. Default. ")
    f4.add_argument('-ul', '--update-log', const="update_log", dest="update", action="store_const", help="Only generate files which have been changed, based on log files. Treated as --force by some generators. ")
    f4.add_argument('-gl', '--grep-log', metavar="PATTERN", dest="grep_log", default=None, help="grep for PATTERN in log files and generate based on those. Treated as --force by some generators. ")
    f4.add_argument('-f', '--force', const="force", dest="update", action="store_const", help="Force to regenerate all files. ")

    whattogen = parser.add_argument_group("What to generate")


    whattogen.add_argument('--sms', action="store_const", const=True, default=False, help="generate sms files")
    whattogen.add_argument('--omdoc', action="store_const", const=True, default=False, help="generate omdoc files")
    whattogen.add_argument('--pdf', action="store_const", const=True, default=False, help="generate pdf files, implies --sms, --alltex, --localpaths")
    whattogen.add_argument('--xhtml', action="store_const", const=True, default=False, help="generate xhtml files, implies --sms, --alltex, --localpaths, --omdoc")
    whattogen.add_argument('--alltex', action="store_const", const=True, default=False, help="Generate all.tex files")
    whattogen.add_argument('--localpaths', action="store_const", const=True, default=False, help="Generate localpaths.tex files")
    whattogen.add_argument('--list', action="store_const", const=True, default=False, help="Lists all modules which exist in the given paths. Blocks all other generation. ")


    parser.add_argument('--pdf-add-begin-document', action="store_const", const=True, default=False, help="add \\begin{document} to LaTeX sources when generating pdfs. Backward compatibility for issue #82")
    parser.add_argument('--pdf-pipe-log', action="store_const", const=True, default=False, help="Displays only the pdf log as output. Implies --quiet, --single")

    whattogen.add_argument('--skip-implies', action="store_const", const=True, default=False, help="Ignore all implications from --omdoc, --pdf and --xhtml. Might cause generation to fail. ")

    wheretogen = parser.add_argument_group("Where to generate")
    wheretogen.add_argument('-d', '--recursion-depth', type=int, default=-1, help="Recursion depth for paths and repositories. ")

    wheretogen = wheretogen.add_mutually_exclusive_group()
    wheretogen.add_argument('pathspec', metavar="PATH_OR_REPOSITORY", nargs='*', default=[], help="A list of paths or repositories to generate things in. ")
    wheretogen.add_argument('--all', "-a", default=False, const=True, action="store_const", help="Generates all files in all repositories. Might take a long time. ")

    return parser
