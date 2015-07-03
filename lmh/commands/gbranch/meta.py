def about():
    return "Manages generated files branches. "

def add_parser_args(parser, argparse):
    parser.add_argument('branch', nargs='?', help='Name of generated files branch. Mandatory for everything but --list and --status. ', default=None)
    parser.add_argument('repo', nargs='?', help='Repository to work with. ', default='.')

    mode = parser.add_argument_group('Mode').add_mutually_exclusive_group(required=True)
    mode.add_argument('--init', help='Create a new deploy branch, install it locally and push it to the remote. ', action='store_true')
    mode.add_argument('--install', help='Install deploy branch mentioned in META-INF/MANIFEST.MF from remote. ', action='store_true')
    mode.add_argument('--pull', help='Pull updates on the deploy branch. ', action='store_true')
    mode.add_argument('--push', help='Push updates on the deploy branch. ', action='store_true')
    mode.add_argument('--status', help='Show deploy branch status. ', action='store_true')
    mode.add_argument('--list', help='List all deploy branches available. ', action='store_true')
