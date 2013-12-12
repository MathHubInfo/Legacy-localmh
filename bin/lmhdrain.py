"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: lmhdrain
   :func: create_parser
   :prog: lmhdrain

"""

import argparse
import lmhutil
import os
import glob
from subprocess import call

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Drain tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_status = subparsers.add_parser('drain', formatter_class=argparse.RawTextHelpFormatter, help='send changes to mathhub')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('repository', type=lmhutil.parseRepo, nargs='*', help="a list of repositories for which to show the status. ").completer = lmhutil.autocomplete_mathhub_repository
  parser.add_argument('--autocommit', "-f", default=False, const=True, action="store_const", help="should autocommit changes", metavar="")
  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would be equivalent to "git status ."
""";

def do_drain(rep, force = False):
  print "draining %r"%rep
  if force:
    call([lmhutil.which("git"), "commit", "-a", "-m", "autocommiting"], cwd=rep);    
  call([lmhutil.which("git"), "push"], cwd=rep);

def do(args):
  if len(args.repository) == 0:
    args.repository = [lmhutil.parseRepo(".")]
  for repo in args.repository:
    for rep in glob.glob(repo):
      do_drain(rep, args.autocommit);
