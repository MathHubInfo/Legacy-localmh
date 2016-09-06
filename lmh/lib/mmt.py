"""
    Functionality to interface with MMT. 
"""
import subprocess
import os
import os.path
import sys

from lmh.lib.io import err
from lmh.lib.env import java_executable, mmt_executable

def run(args, path=None, quiet=False):
    """
    Runs MMT with the given arguments in a given path
    """
    # setup path
    if path == None:
        path = os.getcwd()
    

    # run the mmt script, wait and return.
    try:
        if not os.path.isfile(mmt_executable):
            raise FileNotFoundError
        proc = subprocess.Popen([java_executable, "-jar", mmt_executable] + args, stderr=subprocess.PIPE if quiet else sys.stderr, stdout=subprocess.PIPE if quiet else sys.stdout, cwd=path)
        proc.wait()
        return (proc.returncode == 0)
    except KeyboardInterrupt:
        proc.terminate()
        raise KeyboardInterrupt
    except FileNotFoundError:
        err("mmt not found, is it installed?")
        return False
