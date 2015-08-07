import subprocess
import os
import sys

from lmh.lib.extenv import mmt_executable

def run(args, path=None):
    # setup path
    if path == None:
        path = os.getcwd()

    # run the mmt script, wait and return.
    proc = subprocess.Popen([mmt_executable] + args, stderr=sys.stderr, stdout=sys.stdout, cwd=path)
    proc.wait()
    return (proc.returncode == 0)
