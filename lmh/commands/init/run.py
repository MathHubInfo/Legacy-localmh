from lmh.lib.repos.create import create

def do(args, unknown):
    return create(args.name, type=args.type, remote=not args.remote_readonly)
