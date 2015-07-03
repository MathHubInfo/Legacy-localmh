from lmh.lib.repos.local import match_repo_args, log

def do(args, unknown):
    repos = match_repo_args(args.repository, args.all)
    return log(args.ordered, *repos)
