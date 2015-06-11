def about():
    return "Crawl current repository for dependencies"

def add_parser_args(parser, argparse):
    parser.add_argument('--apply', metavar='apply', const=True, default=False, action="store_const", help="Writes found dependencies to MANIFEST.MF")
