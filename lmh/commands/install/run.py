from lmh.lib.io import std, err, read_raw
from lmh.lib.config import get_config
from lmh.lib.env import data_dir
from lmh.lib.repos.remote import install, ls_remote
from lmh.lib.repos.local.dirs import match_repos

def do(args, unknown):
    # If there are no repositories, check everything for dependencies.
    if len(args.spec) == 0:
        std("Nothing to install, re-installing all existing repositories.  ")
        print(match_repos(data_dir))
        return install(args.no_manifest, *match_repos(data_dir))

    if not get_config("install::noglobs"):
        args.spec = ls_remote(args.no_manifest, *args.spec)
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


    return install(args.no_manifest, *args.spec)
