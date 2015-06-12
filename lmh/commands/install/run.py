from lmh.lib.io import std, err, read_raw
from lmh.lib.config import get_config
from lmh.lib.repos.remote import install, ls_remote

def do(args, unknown):
    if len(args.spec) == 0:
        err("Nothing to do here ...")
        return True

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
