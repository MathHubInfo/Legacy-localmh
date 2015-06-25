import os

from lmh.lib.io import err
from lmh.lib.modules.translate import create_multi

def do(args, unknown):
    args.source = args.source[0]

    if not os.path.isfile(args.source) or not args.source.endswith(".tex"):
        err("Module", args.source, "does not exist or is not a valid module. ")

    # Remove the .tex
    args.source = args.source[:-len(".tex")]

    return create_multi(args.source, args.terms, *args.dest)
