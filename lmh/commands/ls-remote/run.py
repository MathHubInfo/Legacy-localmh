from lmh.lib.io import std, term_colors
from lmh.lib.repos.local.package import is_installed
from lmh.lib.repos.remote import ls_remote

def do(args, unknown):
    res = ls_remote(*args.spec)
    if res == False:
        return False
    else:
        for r in res:
            if is_installed(r):
                std(term_colors("green")+r+term_colors("normal"))
            else:
                std(term_colors("red")+r+term_colors("normal"))
        return True
