from lmh.lib.repos.local import match_repo_args
from lmh.lib.repos.git.push import push

def do(args, unknown):
    repos = match_repo_args(args.repository, args.all)
    return push(args.verbose, *repos)
