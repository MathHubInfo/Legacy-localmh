from lmh.lib.repos.local import match_repo_args, clean

def do(args, unknown):
    repos = match_repo_args(args.repository, args.all)
    res = True
    for repo in repos:
        res = clean(repo, git_clean = args.git_clean) and res
    return res
