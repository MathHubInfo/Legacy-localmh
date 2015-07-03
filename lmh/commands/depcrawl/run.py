from lmh.lib.io import err
from lmh.lib.repos.local import calc_deps

def do(args, unknown):
    res = calc_deps(args.apply)
    if res:
        return True
    else:
        err("lmh depcrawl must be run from within a Repository. ")
        return False
