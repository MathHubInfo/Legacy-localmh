from lmh.lib.io import std
from lmh.lib.repos.local import match_repo_args

def do(args, unknown):
    repos = match_repo_args(args.repository, args.all, abs=args.abs)
    for r in sorted(repos):
        std(r)
    return True
