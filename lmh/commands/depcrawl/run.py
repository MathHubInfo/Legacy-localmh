from lmh.lib.io import err
from lmh.lib.repos.local import calc_deps,  match_repo_args

def do(args, unknown):
    repos = match_repo_args(args.repository, args.all)

    res = calc_deps(repos, apply=args.apply)
    
    if res:
        return True
    else:
        err("lmh depcrawl must be run from within a Repository. ")
        return False
