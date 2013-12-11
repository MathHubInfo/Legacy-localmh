"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: lmhfind
   :func: create_parser
   :prog: lmhfind

"""

import os
import re
import functools
import argparse
import lmhutil
import glob
from string import Template

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Find tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_status = subparsers.add_parser('find', formatter_class=argparse.RawTextHelpFormatter, help='find tool')
  add_parser_args(parser_status)


def add_parser_args(parser):
  parser.add_argument('matcher', metavar='matcher', help="RegEx matcher on the path of the module")
  parser.add_argument('--replace', nargs=1, help="Replace string")
  parser.add_argument('repository', type=lmhutil.parseRepo, nargs='*', help="a list of repositories for which to show the status. ").completer = lmhutil.autocomplete_mathhub_repository

  parser.add_argument('--apply', metavar='apply', const=True, default=False, action="store_const", help="Option specifying that files should be changed")
  

def doReplace(fullPath, replacer, m):
  print fullPath + "->" + m.group(0)
  return m.group(0)

def replacePath(dir, matcher, replacer, apply=False):
  try:
    compMatch = re.compile(matcher)
  except Exception, e:
    print "failed to compile matcher %r"%matcher
    print e
    return

  for root, dirs, files in os.walk(dir):
    path = root.split('/')
    for file in files:
      fileName, fileExtension = os.path.splitext(file)
      if fileExtension != ".tex":
        continue
      fullpath = root+"/"+file;
      print fullpath
      if apply:
        ft = open(fullpath+".tmp", "w")
      replaceContext = functools.partial(doReplace, fullpath, replacer)
      for line in open(fullpath, "r"):
        newLine = compMatch.sub(replaceContext, line)
        if newLine != line:
          print fullpath + ": " + newLine;

        if apply:
          ft.write(newLine)
      if apply:
        os.rename(fullpath+".tmp", fullpath)

def do_find(rep, args):
  replacer = None  
  repname = lmhutil.lmh_repos(rep);
  matcher = Template(args.matcher).substitute(repo=repname)
  if args.replace:
    replacer = Template(args.replace[0]).substitute(repo=repname)

  replacePath(rep, matcher, replacer, args.apply)

def do(args):
  if len(args.repository) == 0:
    args.repository = [lmhutil.parseRepo(".")]
  for repo in args.repository:
    for rep in glob.glob(repo):
      do_find(rep, args);