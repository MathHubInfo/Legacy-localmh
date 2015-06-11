from lmh.lib.modules import checkpaths
from lmh.lib.repos.local import match_repo_args

def do(args, unknown):
    checkpaths.init()

    ret = True
    repos = match_repo_args(args.repository, args.all)
    for rep in repos:
        ret = checkpaths.checkpaths(rep, args) and ret

    return ret
