def about():
    return "Meta-command for all update workflows"

def add_parser_args(parser, argparse):
    opts = parser.add_mutually_exclusive_group()
    opts.add_argument("--all", action="store_const", const="all", default="all", dest="mode", help="all of the things below, default. ")
    opts.add_argument("--self", action="store_const", const="self", dest="mode", help="alias for lmh selfupdate")
    opts.add_argument("--build", action="store_const", const="build", dest="mode", help="alias for lmh update-build")
    opts.add_argument("--external", action="store_const", const="external", dest="mode", help="alias for lmh setup --update")
