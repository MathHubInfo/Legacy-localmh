from lmh.lib.io import std

def do(arguments, unparsed):
    res = calc_deps(args.apply)
    if res:
        return True
    else:
        err("lmh depcrawl must be run from within a Repository. ")
        return False
