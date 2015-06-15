from lmh.lib.io import std, err, read_raw
from lmh.lib.config import get_config
from lmh.lib.env import data_dir
from lmh.lib.repos.git.install import install
from lmh.lib.repos.indexer import ls_remote
from lmh.lib.repos.local.dirs import match_repos

def do(args, unknown):
    # If there are no repositories, check everything for dependencies.
    if len(args.spec) == 0:
        std("Nothing to install, re-installing all existing repositories.  ")
        return install(*match_repos(data_dir))

    if not get_config("install::noglobs"):
        args.spec = ls_remote(*args.spec)
        if len(args.spec) == 0:
            err("Nothing to install...")
            return True
        if args.no_confirm_install:
            std("Picked", len(args.spec),"repositories. ")
        else:
            std("Picked", len(args.spec),"repositories: ")
            std(*args.spec)
            if read_raw("Continue (y/N)?").lower() != "y":
                err("Installation aborted. ")
                return False


    return install(*args.spec)
