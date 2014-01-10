"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: lmhstatus
   :func: create_parser
   :prog: lmhstatus

"""

import lmhutil
import re
import os
import lmhutil
import glob
import subprocess
import argparse

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Status tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_status = subparsers.add_parser('status', formatter_class=argparse.RawTextHelpFormatter, help='shows the working tree status of repositories')
  add_parser_args(parser_status)
  parser_status = subparsers.add_parser('st', formatter_class=argparse.RawTextHelpFormatter, help='short form for status')
  add_parser_args(parser_status)


def add_parser_args(parser):
  parser.add_argument('repository', type=lmhutil.parseRepo, nargs='*', help="a list of repositories for which to show the status. ").completer = lmhutil.autocomplete_mathhub_repository
  parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs status on all repositories currently in lmh")

  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would be equivalent to "git status ."
""";

def do_status(rep):
  cmd = [lmhutil.which("git"), "status", "-u", "-s"];
  result = subprocess.Popen(cmd, 
                                stdout=subprocess.PIPE,
                                cwd=rep
                               ).communicate()[0]
  if len(result) == 0:
    return

  print rep
  print result

def do(args):
  if len(args.repository) == 0:
    args.repository = [lmhutil.tryRepo(".", lmhutil.lmh_root()+"/MathHub/*/*")]
  if args.all:
    args.repository = [lmhutil.tryRepo(lmhutil.lmh_root()+"/MathHub", lmhutil.lmh_root()+"/MathHub")]
  for repo in args.repository:
    for rep in glob.glob(repo):
      do_status(rep);
