from lmh.lib.repos.local import match_repo_args, commit

def do(args, unknown):
    repos = match_repo_args(args.repository, args.all)
    return commit(args.message[0], args.verbose, *repos)
