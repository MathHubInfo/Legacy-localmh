from lmh.lib import about
from lmh.lib.io import std

def do(args, unknown):
    std("lmh, Version", about.version, "( git", about.git_version(), ")")
    std()
    std(about.license)

    return True
