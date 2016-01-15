def about():
    return "Fetch a MathHub repository and its dependencies"

def add_parser_args(parser, argparse):
    parser.add_argument('spec', nargs='*', help="A list of repository specs to install. If no repositories are given, check if all depependencies are installed. ")
    parser.add_argument('-y', '--no-confirm-install', action="store_true", default=False, help="Do not prompt before installing. ")
    parser.epilog = """

Use install::noglobs to disable globbing for lmh install. """
