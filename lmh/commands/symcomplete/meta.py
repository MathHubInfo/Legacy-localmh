def about():
    return "Checks language bindings for completeness"

def add_parser_args(parser, argparse):
    parser.add_argument("path", nargs="*", default=[], help="Language Bindings to check for completeness. ")
