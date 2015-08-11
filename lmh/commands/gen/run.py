from lmh.lib.modules.compile.runner import build_targets, run_paralell

def do(args, unknown):
    # Build the targets from the arguments.
    targets = build_targets(args)

    # if we want to pipe worker output
    # we only want one process.
    if args.pipe_worker_output:
        args.silent = False
        args.workers = 1

    # and run them in paralell
    run_paralell(args.pathspec, args.workers, targets, args.silent)

    return True
