import os

from lmh.lib import config
from lmh.lib.io import std, err

def do(args, unknown):
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
