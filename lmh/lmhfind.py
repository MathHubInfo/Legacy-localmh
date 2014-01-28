#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: lmhfind
   :func: create_parser
   :prog: lmhfind

"""

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

import os
import re
import functools
import argparse
import glob
from string import Template

from . import lmhutil

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
  

def doReplace(replacer, replace_args, fullPath, m):
  print "replacing at %r"%fullPath
  if replacer == None:
    return m.group(0)
  for idx, g in enumerate(m.groups()):
    replace_args["g"+str(idx)] = g

  res = Template(replacer).substitute(replace_args)

  return res

def replacePath(dir, matcher, replaceFnc, apply=False):
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
      if not os.access(fullpath, os.R_OK): # ignoring files I cannot read
        continue
      changes = False
      if apply:
        ft = open(fullpath+".tmp", "w")
      replaceContext = functools.partial(replaceFnc, fullpath)
      for line in open(fullpath, "r"):
        newLine = compMatch.sub(replaceContext, line)
        if newLine != line:
          changes = True          
          print fullpath + ": \n " + line + newLine;

        if apply:
          ft.write(newLine)
      if apply:
        if changes:
          os.rename(fullpath+".tmp", fullpath)
        else:
          os.remove(fullpath+".tmp")

def do_find(rep, args):
  replacer = None  
  repname = lmhutil.lmh_repos(rep);

  matcher = Template(args.matcher).substitute(repo=repname)

  if args.replace:
    replacer = args.replace[0]

  replace_args = {"repo" : repname}

  replaceFnc = functools.partial(doReplace, replacer, replace_args)

  replacePath(rep, matcher, replaceFnc, args.apply)

def do(args):
  if len(args.repository) == 0:
    args.repository = [lmhutil.tryRepo(".", lmhutil.lmh_root()+"/MathHub/*/*")]
  for repo in args.repository:
    for rep in glob.glob(repo):
      do_find(rep, args);