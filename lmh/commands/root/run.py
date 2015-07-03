from lmh.lib.io import std
from lmh.lib.env import install_dir

def do(args, unknown):
    std(install_dir)
    return True
