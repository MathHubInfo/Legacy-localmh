"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: lmhfind
   :func: create_parser
   :prog: lmhfind

"""

# lmh find '\\importmodule\[load=\\MathHub{$repo/source/([^\]]*)\]' --replace '\importmhmodule{$g0' --apply

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
  

def doReplace(fullPath, replacer, replace_args, m):
  print "replacing at %r"%fullPath
  for idx, g in enumerate(m.groups()):
    replace_args["g"+str(idx)] = g

  res = Template(replacer).substitute(replace_args)

  return res

def replacePath(dir, matcher, replacer, replace_args, apply=False):
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
      if apply:
        ft = open(fullpath+".tmp", "w")
      replaceContext = functools.partial(doReplace, fullpath, replacer, replace_args)
      for line in open(fullpath, "r"):
        newLine = compMatch.sub(replaceContext, line)
        if newLine != line:
          print fullpath + ": \n " + line + newLine;

        if apply:
          ft.write(newLine)
      if apply:
        os.rename(fullpath+".tmp", fullpath)

def do_find(rep, args):
  replacer = None  
  repname = lmhutil.lmh_repos(rep);

  matcher = Template(args.matcher).substitute(repo=repname)

  if args.replace:
    replacer = args.replace[0]

  replace_args = {"repo" : repname}
  replacePath(rep, matcher, replacer, replace_args, args.apply)

def do(args):
  if len(args.repository) == 0:
    args.repository = [lmhutil.parseRepo(".")]
  for repo in args.repository:
    for rep in glob.glob(repo):
      do_find(rep, args);