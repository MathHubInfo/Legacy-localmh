import sys
from lmh.lib.env import run_shell

def do(args, unknown):
    code = run_shell(args.shell, args.args+list(unknown))
    sys.exit(code)
