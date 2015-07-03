def about():
    return "Launch a shell with everything set to run build commands"

allow_unknown_args = True
def add_parser_args(parser, argparse):
    parser.add_argument('shell', nargs="?", help="shell to use")
    parser.add_argument('--args', nargs="*", default=[], help="Arguments to append to the shell. ")
