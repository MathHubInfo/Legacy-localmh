from lmh.lib.modules.move import movemod

def do(args, unknown):
    args.source = args.source[0]
    args.dest = args.dest[0]

    return movemod(args.source, args.dest, args.module, args.no_depcrawl, simulate=args.simulate)
