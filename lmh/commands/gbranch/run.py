from lmh.lib.io import std, err
from lmh.lib.repos.local.dirs import match_repo
from lmh.lib.repos.gbranch import Generated

def do(args, unknown):
    rep = match_repo(args.repo)

    if rep == None:
        err("Unable to find repository '"+args.repo+"' locally. ")
        return False

    # Create a generated instance.
    gen = Generated(rep)

    if args.branch == None and not args.list and not args.status:
        err("Branch argument is required unless --list or --status is given. ")
        return False

    if args.install:
        return gen.install_branch(args.branch)

    if args.init:
        return gen.init_branch(args.branch)

    if args.pull:
        return gen.pull_branch(args.branch)

    if args.push:
        return gen.push_branch(args.branch)

    if args.list:
        for b in gen.get_all_branches(tuple=False):
            std(b)
        return True

    return gen.print_status()
