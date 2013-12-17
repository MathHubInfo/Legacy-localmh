"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: lmhclean
   :func: create_parser
   :prog: lmhclean

"""

import lmhutil
import re
import os
import lmhutil
import glob
import subprocess
import argparse

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Clean tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_clean = subparsers.add_parser('clean', formatter_class=argparse.RawTextHelpFormatter, help='clean repositories of generated files')
  add_parser_args(parser_clean)

def add_parser_args(parser):
  parser.add_argument('repository', type=lmhutil.parseRepo, nargs='*', help="a list of repositories for which to show the clean. ").completer = lmhutil.autocomplete_mathhub_repository

  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would be equivalent to "git clean ."
""";

def do_clean(rep):
  remove = [];
  rep_root = lmhutil.git_root_dir(rep);
  ignoreFile = rep_root+"/.gitignore";
  if not os.path.exists(ignoreFile):
    print "No .gitignore file found in %s"%rep_root
    return
  for line in open(ignoreFile):
    remove.append(line.strip());

  for root, dirs, files in os.walk(rep):
    for rem in remove:
      for file in glob.glob(root+"/"+rem):
        os.remove(file)

def do(args):
  if len(args.repository) == 0:
    args.repository = [lmhutil.tryRepo(".", lmhutil.lmh_root()+"/MathHub/*/*")]
  for repo in args.repository:
    for rep in glob.glob(repo):
      do_clean(rep);
