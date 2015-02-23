import os.path

from lmh.lib.repos.local import export, restore

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Manage all locally installed repositories"
    def add_parser_args(self, parser):
        group = parser.add_mutually_exclusive_group()

        group.add_argument("--export", dest="dump_action", action="store_const", const=0, default=0, help="Dump list of installed repositories in file. ")
        group.add_argument("--import", dest="dump_action", action="store_const", const=1, help="Install repositories listed in file. ")

        parser.add_argument("file", nargs="?", help="File to use. If not given, assume STDIN or STDOUT respectivelsy. ")
    def do(self, args, unknown):
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
