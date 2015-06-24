from lmh.lib.io import std, err
from lmh.lib.extenv import check_deps
from lmh.lib.config import get_config

import lmh.lib.packs

def do(args, unknown):

    if not args.no_check and not check_deps():
        err("Dependency check failed. ")
        err("Cannot perform specefied action. ")
        err("Use --no-check to skip checking dependencies. ")
        return False

    if len(args.pack) == 0:
        args.pack = ["default"]
        if args.saction == "update":
            # Update self as well when calling lmh setup --update
            args.pack += ["self"]

    if args.saction == "install":
        return lmh.lib.packs.install(*args.pack)
    elif args.saction == "update":
        return lmh.lib.packs.update(*args.pack)
    elif args.saction == "remove":
        return lmh.lib.packs.remove(*args.pack)
    elif args.saction == "reset":
        return lmh.lib.packs.reset(*args.pack)
    else:
        std("No setup action specefied, assuming --install. ")
        std("Please specify some action in the future. ")
        return lmh.lib.packs.install(*args.pack)
