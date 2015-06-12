from lmh.lib.modules.rename import rename

def do(args, unknown):
    return rename(args.directory, args.renamings, simulate=args.simulate)
