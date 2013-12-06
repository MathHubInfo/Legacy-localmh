#!/usr/bin/python
import subprocess
import os

def lmh_root():
    mypath = os.path.dirname(os.path.realpath(__file__))+"/.."
    return os.path.realpath(mypath)

def git_root_dir(dir = "."):
    rootdir = subprocess.Popen([which("git"), "rev-parse", "--show-toplevel"], 
                                stdout=subprocess.PIPE,
                                cwd=dir,
                               ).communicate()[0]
    rootdir = rootdir.strip()
    return rootdir

def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None
