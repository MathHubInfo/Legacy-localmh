#!/usr/bin/python
import subprocess
import os
import re

repoRegEx = '(\w+)/(\w+)';


def get_file(filePath):
    return open(filePath).read()

def set_file(filePath, fileContent):
    return open(filePath, "w").write(fileContent)
    
def get_template(name):
    return get_file(os.path.dirname(os.path.realpath(__file__)) + "/templates/" + name);

def git_push(dir):
    pass

def lmh_root():
    mypath = os.path.dirname(os.path.realpath(__file__))+"/.."
    return os.path.realpath(mypath)

def git_origin(rootdir="."):
    return subprocess.Popen([which("git"), "remote", "show", "origin", "-n"], 
                                stdout=subprocess.PIPE,
                                cwd=rootdir,
                               ).communicate()[0]


def git_root_dir(dir = "."):
    rootdir = subprocess.Popen([which("git"), "rev-parse", "--show-toplevel"], 
                                stdout=subprocess.PIPE,
                                cwd=dir,
                               ).communicate()[0]
    rootdir = rootdir.strip()
    return rootdir

def get_dependencies(dir):
    res = [];
    dir = git_root_dir(dir);
    try:
        with open (dir+"/META-INF/MANIFEST.MF", "r") as metafile:
          for line in metafile:
            if line.startswith("dependencies: "):
              for dep in re.findall(repoRegEx, line):
                res.push(dep)

    except IOError, e:
        print e

    return res


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
