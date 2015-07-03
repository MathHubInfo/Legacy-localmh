from lmh.lib.io import std
from lmh.lib.modules import resolve_pathspec

def do(args, unknown):
    modules = set()
    for m in args.module:
        mods = resolve_pathspec(args, find_alltex=False)
        modules.update([k["file"] for k in mods if "file" in k.keys()])

    for m in sorted(modules):
        std(m)

    return True
