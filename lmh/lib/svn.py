import subprocess

import sys

from lmh.lib.env import which
from lmh.lib.io import std, err
from lmh.lib.config import get_config
from lmh.lib.extenv import svn_executable

def clone(dest, *arg):
    """Clones an svn repository repository. """

    args = [svn_executable, "co", "--non-interactive", "--trust-server-cert"]
    args.extend(arg)

    proc = subprocess.Popen(args, stdout=sys.stdout, stderr=subprocess.PIPE, cwd=dest)
    err_msg = proc.communicate()[1]

    if err_msg.find("already exists") != -1:
        return True

    err(err_msg)
    return (proc.returncode == 0)

def pull(dest, *arg):
    """Pulls an svn repository. """

    args = [svn_executable, "up"]
    args.extend(arg)

    proc = subprocess.Popen(args, stderr=subprocess.PIPE, cwd=dest)
    err_msg = proc.communicate()[1]

    err(err_msg)
    return (proc.returncode == 0)
