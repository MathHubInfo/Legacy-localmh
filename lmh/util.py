#!/usr/bin/env python

"""
This file is part of LMH.

LMH is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

LMH is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LMH.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import os
import sys
import stat
import json
import glob
import psutil
import signal
import urllib2
import itertools
import argparse
import subprocess
import ConfigParser

from lmh import config

from lmh.lib.env import which

def effectively_readable(path):
    uid = os.getuid()
    euid = os.geteuid()
    gid = os.getgid()
    egid = os.getegid()

    # This is probably true most of the time, so just let os.access()
    # handle it.  Avoids potential bugs in the rest of this function.
    if uid == euid and gid == egid:
        return os.access(path, os.R_OK)

    st = os.stat(path)

    # This may be wrong depending on the semantics of your OS.
    # i.e. if the file is -------r--, does the owner have access or not?
    if st.st_uid == euid:
        return st.st_mode & stat.S_IRUSR != 0

    # See comment for UID check above.
    groups = os.getgroups()
    if st.st_gid == egid or st.st_gid in groups:
        return st.st_mode & stat.S_IRGRP != 0

def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"
    
def lmh_root():
    mypath = os.path.dirname(os.path.realpath(__file__))+"/.."
    return os.path.realpath(mypath)



repoRegEx = '[\w-]+/[\w-]+'
_lmh_root = lmh_root()
gitexec = which("git")
svnexec = which("svn")
perl5root = [_lmh_root+"/ext/perl5lib/", os.path.expanduser("~/")]

perl5bindir = ":".join([p5r+"bin" for p5r in perl5root])+":"+_lmh_root+"/ext/LaTeXML/bin"+":"+_lmh_root+"/ext/LaTeXMLs/bin"
perl5libdir = ":".join([p5r+"lib/perl5" for p5r in perl5root])+":"+_lmh_root+"/ext/LaTeXML/blib/lib"+":"+_lmh_root+"/ext/LaTeXMLs/blib/lib"
stexstydir = _lmh_root+"/ext/sTeX/sty"
latexmlstydir = _lmh_root+"/ext/sTeX/LaTeXML/lib/LaTeXML/texmf"

def perl5env(_env = {}):
  _env["PATH"]=perl5bindir+":"+_env["PATH"]
  try:
     _env["PERL5LIB"] = perl5libdir+":"+ _env["PERL5LIB"]
  except:
    _env["PERL5LIB"] = perl5libdir
  _env["STEXSTYDIR"]=stexstydir
  return _env


def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True

def autocomplete_mathhub_repository(prefix, parsed_args, **kwargs):
  results = [];
  root = _lmh_root+"/MathHub"
  for rep in glob.glob(root+"/*/*"):
    names = rep[len(root)+1:]
    results.append(names)

  return results


def lmh_repos(dir=os.getcwd()):
  t = os.path.realpath(dir);
  root = _lmh_root+"/MathHub"
  if not t.startswith(root):
    return None
  comp = t[len(root)+1:].split("/")
  if len(comp) < 2:
    return None
  return "/".join(comp[:2]);

def validRepoName(name):
  if name.find("..") != -1:
    return False
  if name == ".":
    return False
  if len(name) == 0:
    return False
  return True

def parseSimpleRepo(repoName):
  m = re.match(repoRegEx, repoName);
  if m and len(m.group(0)) == len(repoName):
    return repoName;
  else:
    raise argparse.ArgumentTypeError("%r is not a valid repository name"%repoName)

def tryRepo(repoName, default):
  try:
    return parseRepo(repoName)
  except Exception as e:
    return default

def parseRepo(repoName):
  # if repoName looks like the user meant to write a whole repository
  r = repoName.split("/");
  if len(r) == 2 and validRepoName(r[0]) and validRepoName(r[1]):
    repoPath = "/".join([_lmh_root+"/MathHub", r[0], r[1]]);
    if os.path.exists(repoPath):
      return repoPath

  fullPath = os.path.normpath(os.path.realpath(repoName))

  if not fullPath.startswith(_lmh_root):
    raise argparse.ArgumentTypeError("%r is not a valid repository"%fullPath)

  relPath = filter(len, fullPath[len(_lmh_root)+1:].split(os.sep))

  if len(relPath) == 0 or (len(relPath)==1 and relPath[0]=="MathHub"):
    return _lmh_root+"/MathHub/*/*";

  if len(relPath) == 2 and relPath[0]=="MathHub":
    return _lmh_root+"/MathHub/"+relPath[1]+"/*";

  if len(relPath) > 2:
    return fullPath

  raise argparse.ArgumentTypeError("%r is not a valid repository name"%repoName)

def get_file(filePath):
    return open(filePath).read()

def set_file(filePath, fileContent):
    return open(filePath, "w").write(fileContent)
    
def get_template(name):
    return get_file(_lmh_root + "/bin/templates/" + name);

def git_clone(dest, *arg):
  args = [gitexec, "clone"]
  args.extend(arg)
  proc = subprocess.Popen(args, stderr=sys.stderr, stdout=sys.stdout, cwd=dest)
  proc.wait()

def git_exists(dest):
  args = [gitexec, "ls-remote", dest]
  proc = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
  proc.wait()
  return (proc.returncode == 0)

def git_pull(dest, *arg):
  args = [gitexec, "pull"];
  args.extend(arg);
  proc = subprocess.Popen(args, stderr=sys.stderr, stdout=sys.stdout, cwd=dest).communicate()[1]
  proc.wait()

def svn_clone(dest, *arg):
  args = [svnexec, "co"];
  args.extend(arg);
  
  err = subprocess.Popen(args, stderr=subprocess.PIPE, cwd=dest).communicate()[1]

  if err.find("already exists") != -1:
    return

  print err

def svn_pull(dest, *arg):
  args = [svnexec, "up"];
  args.extend(arg);
  
  err = subprocess.Popen(args, stderr=subprocess.PIPE, cwd=dest).communicate()[1]

  print err

def git_origin(rootdir="."):
    return subprocess.Popen([which("git"), "remote", "show", "origin", "-n"], 
                                stdout=subprocess.PIPE,
                                cwd=rootdir,
                               ).communicate()[0]


def git_root_dir(dir = "."):
    if os.path.isfile(dir):
      dir = os.path.dirname(dir)
    rootdir = subprocess.Popen([which("git"), "rev-parse", "--show-toplevel"], 
                                stdout=subprocess.PIPE,
                                cwd=dir,
                               ).communicate()[0]
    rootdir = rootdir.strip()
    return rootdir

def get_dependencies(dir):
    res = []
    try:
        dir = git_root_dir(dir);
        with open (dir+"/META-INF/MANIFEST.MF", "r") as metafile:
          for line in metafile:
            if line.startswith("dependencies: "):
              for dep in re.findall(repoRegEx, line):
                res.append(dep)

    except IOError, e:
        #print e
        return None
    
    except OSError, e:
        #print e
        return None

    return res

def setnice(nice, pid = None):
    """ Set the priority of the process to below-normal."""


    import psutil, os
    if pid == None:
      pid = os.getpid()

    p = psutil.Process(pid)
    p.nice = nice

def kill_child_processes(parent_pid, sig=signal.SIGTERM, recursive=True,self=True):
    try:
      p = psutil.Process(parent_pid)
    except psutil.error.NoSuchProcess:
      return
    child_pid = p.get_children(recursive=recursive)
    for pid in child_pid:
      os.kill(pid.pid, sig) 

    if self:
      os.kill(parent_pid, sig) 
def reduce(lst):
  return sum( ([x] if not isinstance(x, list) else reduce(x)
         for x in lst), [] )