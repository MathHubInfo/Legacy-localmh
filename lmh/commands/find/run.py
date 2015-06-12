from lmh.lib.repos.local import match_repo_args
from lmh.lib.repos.find_and_replace import find

def do(args, unknown):
    ret = True
    repos = match_repo_args(args.repository, args.all)
    for rep in repos:
        ret = find(rep, args) and ret

    return ret
