from lmh.lib.io import err
from lmh.lib.repos.local.dirs import match_repo
import lmh.lib.repos.deploy as deploy

def do(args, unknown):
    rep = match_repo(args.repo)

    if rep == None:
        err("Unable to find repository '"+args.repo+"' locally. ")
        return False

    if args.install:
        return deploy.install(rep)

    if args.init:
        return deploy.init(rep)

    if args.pull:
        return deploy.pull(rep)

    if args.push:
        return deploy.push(rep)

    return deploy.print_status(rep)
