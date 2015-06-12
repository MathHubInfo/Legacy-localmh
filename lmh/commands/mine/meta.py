def about():
    return "Manage all locally installed repositories"

def add_parser_args(parser, argparse):
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--export", dest="dump_action", action="store_const", const=0, default=0, help="Dump list of installed repositories in file. ")
    group.add_argument("--import", dest="dump_action", action="store_const", const=1, help="Install repositories listed in file. ")
    parser.add_argument("file", nargs="?", help="File to use. If not given, assume STDIN or STDOUT respectivelsy. ")
