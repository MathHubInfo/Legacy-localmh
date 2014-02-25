#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: checkpaths
   :func: create_parser
   :prog: checkpaths

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
import glob
import difflib
import fileinput
import argparse
import functools

from lmh import util
from lmh.commands import find


mathroot = util.lmh_root()+"/MathHub";
fileIndex = {};
remChoices = {};

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Path Checking tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="checkpaths"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='check paths for validity')
  add_parser_args(parser_status)


def add_parser_args(parser):
  parser.add_argument('repository', type=util.parseRepo, nargs='*', help="a list of repositories for which to show the status. ").completer = util.autocomplete_mathhub_repository
  parser.add_argument('--interactive', metavar='interactive', const=True, default=False, action="store_const", help="Should check paths be interactive")
  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would run on local directory
""";

def replaceFnc(args, fullPath, m):
  if os.path.exists(mathroot+"/"+m.group(1)+".tex"):  # link is ok
    return m.group(0);

  if args.interactive:
    print "Following path is invalid "

  print fullPath, ": ", m.group(1);

  if not args.interactive:
    return m.group(0)

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
    for file in files:
      if not file.endswith(".tex"):
        continue;

      if file not in fileIndex:
        fileIndex[file]=[];

      fileIndex[file].append(root[len(mathroot)+1:]+"/"+file);

def checkpaths(dir, args):
  find.replacePath(dir, r"\\MathHub{([^}]*)", functools.partial(replaceFnc, args), True);

def do(args):
  if len(args.repository) == 0:
    args.repository = [util.tryRepo(".", util.lmh_root()+"/MathHub/*/*")]

  createIndex()
  for repo in args.repository:
    for rep in glob.glob(repo):
      checkpaths(rep, args);
