import os
import re

def getDeps(dir="."):
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

  deps = "dependencies: ";
  for rep in repos:
    deps+=rep+" "
  return deps