def about():
    return "View or change lmh configuration"

def add_parser_args(parser, argparse):
    parser.add_argument('key', nargs='?', help="Name of setting to change. ", default=None)
    parser.add_argument('value', nargs='?', help="New value for setting. If omitted, show some information about the given setting. ", default=None)
    parser.add_argument('--reset', help="Resets a setting. Ignores value. ", default=False, action="store_const", const=True)
    parser.add_argument('--reset-all', help="Resets all settings. ", default=False, action="store_const", const=True)
