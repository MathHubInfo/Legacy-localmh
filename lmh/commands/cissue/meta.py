def about():
    return "Opens a url to display issues in the browser"

def add_parser_args(parser, argparse):
    parser.add_argument('repo', nargs='?', help='Repository to work with. ', default='.')
