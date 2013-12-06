import os
import re
import functools
import argparse

def doNothing(fullPath, m):
  print fullPath + "->" + m.group(1)
  return m.group(0)

def replacePath(dir=".", replaceFnc = doNothing, readonly=True):
  print readonly
  for root, dirs, files in os.walk("."):
      path = root.split('/')
      for file in files:
        fileName, fileExtension = os.path.splitext(file)
        if fileExtension != ".tex":
          continue
        fullpath = root+"/"+file;
        if not readonly:
          ft = open(fullpath+".tmp", "w")
        replaceContext = functools.partial(replaceFnc, fullpath)
        for line in open(fullpath, "r"):
          newLine = re.sub("\\MathHub{([\w/]+)}", replaceContext, line)
          if newLine != line:
            print fullpath + ": " + newLine;

          if not readonly:
            ft.write(newLine)
        if not readonly:
          os.rename(fullpath+".tmp", fullpath)

def repl(search, replace, fullPath, m):
  p = re.sub(search, replace, m.group(1));
  return "MathHub{"+p+"}";

def list(match, fullPath, m):
  if re.search(match, m.group(1)):
    print fullPath + ": " + m.group(1)
  return m.group(0)


def do(rest):
  parser = argparse.ArgumentParser(description='MathHub path management tool.')

  parser.add_argument('matcher', metavar='matcher', help="RegEx matcher on the path of the module")
  parser.add_argument('replace', metavar='replace', nargs="?", help="Replace string")
  parser.add_argument('--apply', metavar='apply', const=True, default=False, nargs="?", help="Option specifying that files should be changed")

  if len(rest) == 0:
    return parser.print_help()

  args, _ = parser.parse_known_args(rest)

  if len(args.replace) == None:
    replacePath(".", functools.partial(list, args.matcher))
    return

  replacePath(".", functools.partial(repl, args.matcher, args.replace), not args.apply)
