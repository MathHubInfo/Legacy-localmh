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

import subprocess
import os
import re
import argparse
import ConfigParser
import urllib2
import json
import glob

def lmh_root():
    mypath = os.path.dirname(os.path.realpath(__file__))+"/.."
    return os.path.realpath(mypath)

def which(program):
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

repoRegEx = '[\w-]+/[\w-]+';
_lmh_root = lmh_root();
gitexec = which("git")
svnexec = which("svn")

def set_setting(key,  value):
  root = _lmh_root

  config = ConfigParser.ConfigParser()
  config.read(root+"/bin/lmh.cfg")
  if not config.has_section("lmh"):
    config.add_section("lmh");

  config.set("lmh", key, value)

  with open(root+"/bin/lmh.cfg", 'wb') as configfile:
    config.write(configfile)

def get_setting(key):
  root = _lmh_root;

  config = ConfigParser.ConfigParser()
  config.read(root+"/bin/lmh.cfg")
  return config.get("lmh", key)


def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True

def autocomplete_remote_mathhub_repository(prefix, parsed_args, **kwargs):
  key = get_setting("private_token")
  results = [];

  if key:
    resource = "http://gl.mathhub.info/api/v3/groups?private_token={token}".format(token=key)
    json_data = json.loads(urllib2.urlopen(resource).read())
    for rec in json_data:
      if rec["name"].startswith(prefix):
        results.append(rec["name"])

  return results

def autocomplete_mathhub_repository(prefix, parsed_args, **kwargs):
  results = [];
  root = _lmh_root+"/MathHub"
  for rep in glob.glob(root+"/*/*"):
    names = rep[len(root)+1:]
    results.append(names)

  return results


def lmh_repos(dir=os.getcwd()):
  t = os.path.realpath(dir);
  root = _lmh_root+"/MathHub";
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
  except Exception, e:
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
  args = [gitexec, "clone"];
  args.extend(arg);
  err = subprocess.Popen(args, stderr=subprocess.PIPE, cwd=dest).communicate()[1]

  if err.find("already exists") != -1:
    return

  print err

def git_pull(dest, *arg):
  args = [gitexec, "pull"];
  args.extend(arg);
  err = subprocess.Popen(args, stderr=subprocess.PIPE, cwd=dest).communicate()[1]

  print err

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
    rootdir = subprocess.Popen([which("git"), "rev-parse", "--show-toplevel"], 
                                stdout=subprocess.PIPE,
                                cwd=dir,
                               ).communicate()[0]
    rootdir = rootdir.strip()
    return rootdir

def get_dependencies(dir):
    res = [];
    try:
        dir = git_root_dir(dir);
        with open (dir+"/META-INF/MANIFEST.MF", "r") as metafile:
          for line in metafile:
            if line.startswith("dependencies: "):
              for dep in re.findall(repoRegEx, line):
                res.append(dep)

    except IOError, e:
        print e
    except OSError, e:
        print e

    return res