from lmh.lib.repos.local import match_repo_args
from lmh.lib.repos.local import do as local_do

def do(args, unknown):
    repos = match_repo_args(args.repository, args.all)
    args.args = (args.args or []) + unknown
    return local_do(args.cmd[0], args.args, *repos)
