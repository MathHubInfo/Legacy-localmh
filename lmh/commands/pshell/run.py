import sys
from lmh.lib.env import run_pshell

def do(args, unknown):
    code = run_pshell()
    sys.exit(code)
