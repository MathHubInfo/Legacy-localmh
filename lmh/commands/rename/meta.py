import os

def about():
    return "Rename symbol names in glossary components"

def add_parser_args(parser, argparse):
    parser.add_argument('--directory', '-d', default=os.getcwd(), help="Directory to replace symbols in. Defaults to current directory. ")
    parser.add_argument('--simulate', '-s', default=False, action="store_const", const=True, help="Simulate only. ")
    parser.add_argument('renamings', nargs="+", help="Renamings to be provided in pairs. ", default=None)

    parser.epilog = """
Examples:

lmh rename foo bar
lmh rename foo bar foo2 bar2
lmh rename foo bar-baz """
