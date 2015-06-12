def about():
    return "Fetch a MathHub repository and its dependencies"

def add_parser_args(parser, argparse):
    parser.add_argument('spec', nargs='*', help="A list of repository specs to install. ")
    parser.add_argument('-y', '--no-confirm-install', action="store_true", default=False, help="Do not prompt before installing. ")
    parser.add_argument('-m', '--no-manifest', action="store_true", default=False, help="Do not parse manifest while installing. Equivalent to setting install::nomanifest to True. ")
    parser.epilog = """
Use install::sources to configure the sources of repositories.

Use install::nomanifest to configure what happens to repositories without a
manifest.

Use install::noglobs to disable globbing for lmh install. """
