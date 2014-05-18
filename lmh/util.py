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

# This file is currently under rewriting and split up
# Will be removed once all code is completely ported
# This is the dev branch afterall

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
from lmh.lib.env import install_dir as _lmh_root

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
    return _lmh_root

from lmh.lib.repos import nameExpression as repoRegEx

from lmh.lib.extenv import git_executable as gitexec
from lmh.lib.extenv import svn_executable as svnexec

from lmh.lib.env import perl5root, perl5bindir, perl5libdir, stexstydir, latexmlstydir, perl5env

def autocomplete_mathhub_repository(prefix, parsed_args, **kwargs):
  results = [];
  root = _lmh_root+"/MathHub"
  for rep in glob.glob(root+"/*/*"):
    names = rep[len(root)+1:]
    results.append(names)

  return results

from lmh.lib.repos.local import match_repository as lmh_repos

def validRepoName(name):
  if name.find("..") != -1:
    return False
  if name == ".":
    return False
  if len(name) == 0:
    return False
  return True

from lmh.lib.repos import repoType as parseSimpleRepo

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

from lmh.lib.io import read_file as get_file
from lmh.lib.io import write_file as set_file
    
def get_template(name):
    return get_file(_lmh_root + "/bin/templates/" + name);

from lmh.lib.git import clone as git_clone
from lmh.lib.git import exists as git_exists
from lmh.lib.git import pull as git_pull
from lmh.lib.git import root_dir as git_root_dir
from lmh.lib.git import origin as git_origin

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

from lmh.lib.repos import find_dependencies as get_dependencies

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