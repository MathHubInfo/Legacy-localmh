import os
import re

def replacePath(dir="."):
  paths = {};
  for root, dirs, files in os.walk("."):
      path = root.split('/')
      for file in files:
        fileName, fileExtension = os.path.splitext(file)
        if fileExtension != ".tex":
          continue
        ft = open(root+"/"+file+".tmp", "w")
        print root+"/"+file
        for line in open(root+"/"+file, "r"):
          m = re.search("\MathHub{([\w/]+)}", line)
          if m:
            paths[m.group(1)] = True

          ft.write(ft)
        break