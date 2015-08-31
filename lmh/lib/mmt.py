import subprocess
import os
import sys

from lmh.lib.extenv import mmt_executable

def run(args, path=None, quiet=False):
    # setup path
    if path == None:
        path = os.getcwd()

    # run the mmt script, wait and return.
    try:
        proc = subprocess.Popen([mmt_executable] + args, stderr=subprocess.PIPE if quiet else sys.stderr, stdout=subprocess.PIPE if quiet else sys.stdout, cwd=path)
        proc.wait()
        return (proc.returncode == 0)
    except KeyboardInterrupt:
        proc.terminate()
        raise KeyboardInterrupt

def run_script(script, path=None, quiet=False):
    return run([script], path, quiet)
