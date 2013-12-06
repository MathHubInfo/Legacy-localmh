#!/usr/bin/python

import lmhconfig;
import re
import os
from subprocess import call

repoRegEx = '(\w+)/(\w+)';

def parseRepoName(repoName):
  m = re.search(repoRegEx, repoName)
  return [m.group(1), m.group(2)]

def getURL(user, project):
  return "git@mathhub.info:"+user+"/"+project
#  return "/home/costea/tmp/GenCS"

def cloneRepository(user, project):
  try:
    gitpath = lmhconfig.which("git")
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
  if not os.path.exists(project):
    cloneRepository(user, project)
  else:
    print "Project "+project+" already exist."

  print "Checking dependencies for project "+project

  try:
    with open (user+"/"+project+"/META-INF/MANIFEST.MF", "r") as metafile:
      for line in metafile:
        if line.startswith("dependencies: "):
          for dep in re.findall(repoRegEx, line):
            installNoCycles(dep[0], dep[1], tried)
  except IOError, e:
    print e

def installrepo(repoName):
  root = lmhconfig.lmh_root()+"/MathHub"
  os.chdir(root)
  [user, project] = parseRepoName(repoName)
  installNoCycles(user, project, {})
