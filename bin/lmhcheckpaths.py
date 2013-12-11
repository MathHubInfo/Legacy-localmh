"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: lmhcheckpaths
   :func: create_parser
   :prog: lmhcheckpaths

"""

import lmhpath;
import lmhutil;
import os;
import glob
import difflib;
import fileinput
import argparse

mathroot = lmhutil.lmh_root()+"/MathHub";
fileIndex = {};
remChoices = {};

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Path Checking tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_status = subparsers.add_parser('checkpaths', formatter_class=argparse.RawTextHelpFormatter, help='check paths for validity')
  add_parser_args(parser_status)


def add_parser_args(parser):
  parser.add_argument('repository', default=[lmhutil.parseRepo(".")], type=lmhutil.parseRepo, nargs='*', help="a list of repositories for which to show the status. ").completer = lmhutil.autocomplete_mathhub_repository
  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would run on local directory
""";

def replaceFnc(fullPath, m):
  if os.path.exists(mathroot+"/"+m.group(1)+".tex"):  # link is ok
    return m.group(0);

  print "in ",fullPath, ": path ", m.group(1), "is invalid";

  if m.group(0) in remChoices:
    print "Remembered replacement to "+remChoices[m.group(0)];
    return remChoices[m.group(0)];

  comps = m.group(1).split("/");
  fileName = comps[len(comps)-1]+".tex";
  if not fileName in fileIndex:
    print "Error: No suitable index file found "+fileName;
    return m.group(0);

  results = [];
  for validPath in fileIndex[fileName]:
    cnt = 0;
    s = difflib.SequenceMatcher(None, validPath, m.group(1))
    results.append((s.ratio(), validPath));

  results = sorted(results, key=lambda result: result[0], reverse=True)

  print "Possible results: "
  print "1 ) Don't change"

  for idx, result in enumerate(results):
    print idx+2,")",result[1]

  while True:
    choice = raw_input('Enter your input:')
    try:
      choice = int(choice)
    except ValueError:
      print "invalid choice"
      continue
    if choice < 1 or choice > len(results) + 1:
      print "Not valid choice"
    break

  while True:
    remember = raw_input('Remember choice (y/n)?:')
    if remember == 'y' or remember == "n":
      break
    print "invalid choice";

  result = m.group(0);

  if choice > 1:
    replacePath = results[choice - 2][1][:-4];
    result = "MathHub{"+replacePath+"}";

  if remember == 'y':
    remChoices[m.group(0)] = result;

  return result;

def createIndex():
  for root, dirs, files in os.walk(mathroot):
    if root == "/home/costea/kwarc/localmh/MathHub/MathHub/physics/source/units/en":
      print files
    for file in files:
      if not file.endswith(".tex"):
        continue;

      if file not in fileIndex:
        fileIndex[file]=[];

      fileIndex[file].append(root[len(mathroot)+1:]+"/"+file);

def checkpaths(dir="."):
  print "creating index";

  lmhpath.replacePath(dir, replaceFnc, False);

def do(args):
  createIndex()
  for repo in args.repository:
    for rep in glob.glob(repo):
      checkpaths(rep);
