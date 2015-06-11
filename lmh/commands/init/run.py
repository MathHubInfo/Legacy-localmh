from lmh.lib.repos.create import create, find_types

def do(args, unknown):
    return create(args.name, type=args.type, remote=not args.remote_readonly)
