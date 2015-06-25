import os

from lmh.lib.modules.symbols import check_defs

def do(args, unknown):
    if len(args.path) == 0:
        args.path = [os.getcwd()]

    res = True
    for p in args.path:
        res = check_defs(p) and res

    return res
