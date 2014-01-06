"""

.. argparse::
   :module: lmhupdate
   :func: create_parser
   :prog: lmhupdate

"""

import argparse
import lmhutil
import os
import glob
from subprocess import call
from lmhsetup import update as setup_update

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Update tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_status = subparsers.add_parser('update', formatter_class=argparse.RawTextHelpFormatter, help='get repository and tool updates')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('repository', type=lmhutil.parseRepo, nargs='*', help="a list of repositories for which to show the status. ").completer = lmhutil.autocomplete_mathhub_repository
  parser.epilog = """
Note: LMH will check for tool updates only if run at the root of the LMH folder 
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would be equivalent to updating current repository
""";

def do_pull(rep):
  print "pulling %r"%rep
  call([lmhutil.which("git"), "pull"], cwd=rep);

def do(args):
  if len(args.repository) == 0:
    if os.getcwd() == lmhutil.lmh_root()+"/ext":
      return setup_update();
    if os.getcwd() == lmhutil.lmh_root():
      setup_update();
    args.repository = [lmhutil.tryRepo(".", lmhutil.lmh_root()+"/MathHub/*/*")]

  for repo in args.repository:
    for rep in glob.glob(repo):
      do_pull(rep);
