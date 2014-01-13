"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: lmhXHTML
   :func: create_parser
   :prog: lmhXHTML

"""

import argparse
import lmhutil
import os
from subprocess import call
import ConfigParser
import glob
from lmhgen import do_gen
from lmhgen import create_parser as gen_parser
from lmhmmt import compile

p = gen_parser()
attr = p.parse_args(["--omdoc"]);

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub XHTML tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_status = subparsers.add_parser('xhtml', formatter_class=argparse.RawTextHelpFormatter, help='generate XHTML ')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('repository', type=lmhutil.parseRepo, nargs='*', help="a list of repositories for which to generate XHTML").completer = lmhutil.autocomplete_mathhub_repository
  parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs status on all repositories currently in lmh")
  pass

def do_xhtml(rep):
  rep_root = lmhutil.git_root_dir(rep);
  do_gen(rep, attr)
  compile(rep_root)
  pass

def do(args):
  if len(args.repository) == 0:
    args.repository = [lmhutil.tryRepo(".", lmhutil.lmh_root()+"/MathHub/*/*")]
  if args.all:
    args.repository = [lmhutil.tryRepo(lmhutil.lmh_root()+"/MathHub", lmhutil.lmh_root()+"/MathHub")]  

  for repo in args.repository:
    for rep in glob.glob(repo):
      do_xhtml(rep);