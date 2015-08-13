from lmh.lib.modules.compile.runner import build_targets, run_paralell
from lmh.lib.modules import get_build_groups
from lmh.lib.io import std

def do(args, unknown):
    # Build the targets from the arguments.
    targets = build_targets(args)

    # if we want to list files, do **only** that
    if targets["list"]:
        for (r, f) in get_build_groups(args.pathspec):
            std("Repository", r+":")
            for ff in f:
                std("    ", ff)
        return True

    # if we want to pipe worker output
    # we only want one process.
    if args.pipe_worker_output:
        args.silent = False
        args.workers = 1

    # and run them in paralell
    return run_paralell(args.pathspec, args.workers, targets, args.silent)
