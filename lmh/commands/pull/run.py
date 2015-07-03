from lmh.lib.io import std
from lmh.lib.packs import update
from lmh.lib.repos.local import match_repo_args
from lmh.lib.repos.git.pull import pull
from lmh.lib.config import get_config

def do(args, unknown):
    repos = match_repo_args(args.repository, args.all)
    return pull(args.verbose, *repos)
