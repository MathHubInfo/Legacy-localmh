import os.path

from lmh.lib.repos.local.manager import export, restore

def do(args, unknown):
    if args.dump_action == 0:
        # Export
        if not args.file:
            #Print them to stdout
            return export()
        else:
            #Put them in a file
            return export(os.path.abspath(args.file[0]))
    else:
        if not args.file:
            #Read frm stdin
            return restore()
        else:
            #Read from file
            return restore(os.path.abspath(args.file[0]))
