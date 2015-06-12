from lmh.lib.repos.local import match_repo_args, push

def do(args, unknown):
    repos = match_repo_args(args.repository, args.all)
    return push(args.verbose, *repos)
