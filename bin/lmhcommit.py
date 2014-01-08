"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: lmhcommit
   :func: create_parser
   :prog: lmhcommit

"""

import argparse
import lmhutil
import os
import glob
from subprocess import call

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Commit tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_status = subparsers.add_parser('commit', formatter_class=argparse.RawTextHelpFormatter, help='commits all changed files')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('repository', type=lmhutil.parseRepo, nargs='*', help="a list of repositories for which to show the status. ").completer = lmhutil.autocomplete_mathhub_repository
  parser.add_argument('--message', "-m", default="autocommit", nargs=1, help="message to be used for commits")
  parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs commit on all repositories currently in lmh")

  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would be equivalent to "git status ."
""";

def do_drain(rep, msg):
  print "draining %r"%rep
  call([lmhutil.which("git"), "commit", "-a", "-m", msg], cwd=rep);    

def do(args):
  if len(args.repository) == 0:
    args.repository = [lmhutil.tryRepo(".", lmhutil.lmh_root()+"/MathHub/*/*")]
  if args.all:
    args.repository = [lmhutil.tryRepo(lmhutil.lmh_root()+"/MathHub", lmhutil.lmh_root()+"/MathHub")]
  for repo in args.repository:
    for rep in glob.glob(repo):
      do_drain(rep, args.message[0]);
