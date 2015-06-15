from lmh.lib.io import std
from lmh.lib.git import get_remote_status
from lmh.lib.packs import update
from lmh.lib.repos.local import match_repo_args
from lmh.lib.config import get_config

def do(args, unknown):
    def needs_push(r):
        state = get_remote_status(r)
        return state == "push" or state == "failed" or state == "divergence"
    def needs_pull(r):
        state = get_remote_status(r)
        return state == "push" or state == "failed" or state == "divergence"

    repos = match_repo_args(args.repository, args.all)

    if args.mode == "human":
        for r in repos:
            state = get_remote_status(r)
            if state == "ok":
                std(r, "Synced")
            elif state == "push":
                std(r, "Local version newer, to sync run git push")
            elif state == "pull":
                std(r, "Remote version newer, to sync run git pull")
            elif state == "divergence":
                std(r, "Diverged from remote")
    elif args.mode == "synced":
        [std(r) for r in repos if get_remote_status(r) == "ok"]
    elif args.mode == "push":
        [std(r) for r in repos if needs_push(r)]
    elif args.mode == "pull":
        [std(r) for r in repos if needs_pull(r)]

    return True
