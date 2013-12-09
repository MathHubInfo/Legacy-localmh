#!/usr/bin/python

import lmhconfig;
import re
import os
import sys
from subprocess import call

repoRegEx = lmhconfig.repoRegEx;

def parseRepoName(repoName):
  m = re.search(repoRegEx, repoName)
  if not m:
    print repoName + " is not a valid repository name"
    sys.exit(os.EX_DATAERR)
  return [m.group(1), m.group(2)]

def getURL(user, project):
  return "git@mathhub.info:"+user+"/"+project
#  return "/home/costea/tmp/GenCS"

def cloneRepository(user, project):
  try:
    gitpath = lmhconfig.which("git")
    if os.path.exists(user+"/"+project):
      return
    repoURL = getURL(user, project)
    print "cloning " + repoURL
    
    call([gitpath, "clone", repoURL, user+"/"+project])
  except Exception, e:
    print e
    pass

def installNoCycles(user, project, tried):
  if (user+"/"+project) in tried:
    return

  tried[user+"/"+project] = True
  cloneRepository(user, project)

  print "Checking dependencies for project "+project

  deps = lmhconfig.get_dependencies(user+"/"+project);
  if deps == None:
    print("Error: META-INF/MANIFEST.MF file missing or invalid.")
    return

  for dep in deps:
    installNoCycles(dep[0], dep[1], tried)


def installrepo(repoName):
  root = lmhconfig.lmh_root()+"/MathHub"
  os.chdir(root)
  [user, project] = parseRepoName(repoName)
  installNoCycles(user, project, {})

