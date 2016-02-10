from lmh.lib.io import std
from lmh.lib.dirs import lmh_locate

def do(args, unknown):
    std(lmh_locate())
    return True
