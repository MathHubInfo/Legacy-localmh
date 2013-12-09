import os
import re
import argparse
import lmhutil

def calcDeps(dir="."):
  currentdeps = {};
  for dep in lmhutil.get_dependencies(dir):
    currentdeps["/".join(dep)] = True

  paths = {};
  for root, dirs, files in os.walk("."):
      path = root.split('/')
      for file in files:
        fileName, fileExtension = os.path.splitext(file)
        if fileExtension != ".tex":
          continue
        file = open(root+"/"+file, "r")
        for line in file:
          m = re.search("\MathHub{([\w/]+)}", line)
          if m:
            paths[m.group(1)] = True

  repos = {};
  for path in paths:
    comps = path.split("/")
    if len(comps) < 2:
      continue
    repos[comps[0]+"/"+comps[1]] = True

  toAdd = [];
  for rep in repos:
    if rep not in currentdeps:
      toAdd.append(rep);

  return " ".join(toAdd);

def do(rest):
  parser = argparse.ArgumentParser(description='MathHub repository dependency crawler.')
  parser.add_argument('--apply', metavar='apply', const=True, default=False, nargs="?", help="Dependencies should be updated")

  args, _ = parser.parse_known_args(rest)
  print calcDeps()