def about():
    return "Generate smybols needed by language bindings"

def add_parser_args(parser, argparse):
    parser.add_argument("path", nargs="*", default=[], help="Path to modules where to generate symbols. ")
    parser.epilog = """
Example:
    lmh symbols .
will generate symbols in all files in the current directory. Can be used on
single files, however it needs to know which language bindings to add new
symbols from.
Use
    lmh symbols foo.*.tex
to add missing symbols from language bindings to foo.tex.
Use
    lmh symbols foo.tex
to display warnings about double symdef and symi warnings.
"""
