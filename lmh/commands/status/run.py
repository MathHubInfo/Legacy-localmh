from lmh.lib.repos.local import match_repo_args, status

def do(args, unknown):
    repos = match_repo_args(args.repository, args.all)
    return status(repos, args.show_unchanged, args.remote, args.outputtype)
