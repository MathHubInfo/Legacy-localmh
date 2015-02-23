import os

from lmh.lib import config
from lmh.lib.io import std, err

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="View or change lmh configuration"
    def add_parser_args(self, parser):
        parser.add_argument('key', nargs='?', help="Name of setting to change. ", default=None)
        parser.add_argument('value', nargs='?', help="New value for setting. If omitted, show some information about the given setting. ", default=None)
        parser.add_argument('--reset', help="Resets a setting. Ignores value. ", default=False, action="store_const", const=True)
        parser.add_argument('--reset-all', help="Resets all settings. ", default=False, action="store_const", const=True)
    def do(self, args, unparsed):
        if args.reset_all:
            try:
                os.remove(config.config_file)
                return True
            except:
                pass
            return False

        if args.reset:
            if args.key == None:
                err("Missing key. ")
                return False
            try:
                return config.reset_config(args.key)
            except:
                pass
            return False

        if args.key == None:
            config.list_config()
            std()
            std("Type 'lmh config KEY' to get more information on KEY. ")
            std("Type 'lmh config KEY VALUE' to change KEY to VALUE. ")
            return True
        elif args.value == None:
            return config.get_config_help(args.key)
        else:
            try:
                return config.set_config(args.key, args.value)
            except:
                pass
            return False
