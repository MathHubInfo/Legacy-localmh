import os

from lmh.lib.io import std, err
from lmh.lib.modules.compile import run_build

def do(args, unknown):
    run_build(args.pathspec, {
        "sms": None
    })
    return False
