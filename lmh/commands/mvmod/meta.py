def about():
    return "Move a multilingual module to a new repository"

def add_parser_args(parser, argparse):
    parser.add_argument('source', nargs=1, help="name of old repository. ")
    parser.add_argument('dest', nargs=1, help="Name of new repository. Assumed to be initalised correctly. ", default=None)
    parser.add_argument('module', nargs="+", help="Relative path(s) of source module(s) in old repository")
    parser.add_argument('--no-depcrawl', action="store_const", default=False, const=True, help="Do not call depcrawl on source and destination. ")
    parser.add_argument('--simulate', action="store_const", default=False, const=True, help="Simulate only. ")

    parser.epilog = """
Example: lmh mvmod smglom/smglom smglom/set set

Which moves the multilingual set module from smglom/smglom into the new
repository smglom/set.

It can be advisable to run an lmh clean before executing this command, as it
speeds it up quite a lot. """
