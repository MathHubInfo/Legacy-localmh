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
from lmhgen import do as do_gen

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub XHTML tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_status = subparsers.add_parser('xhtml', formatter_class=argparse.RawTextHelpFormatter, help='sets up local math hub and fetches external requirements')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('repository', type=lmhutil.parseRepo, nargs='*', help="a list of repositories for which to show the status. ").completer = lmhutil.autocomplete_mathhub_repository
  pass

def install_autocomplete():
  root = lmhutil.lmh_root()+"/ext"
  lmhutil.git_clone(root, "https://github.com/kislyuk/argcomplete.git", "arginstall")
  call([python, "XHTML.py", "install", "--user"], cwd=root+"/arginstall")
  activatecmd = root+"/arginstall/scripts/activate-global-python-argcomplete";
  print "running %r"%(activatecmd)
  call([root+"/arginstall/scripts/activate-global-python-argcomplete"])

def do_xhtml(rep):
  pass

def do(args):
  if len(args.repository) == 0:
    args.repository = [lmhutil.tryRepo(".", lmhutil.lmh_root()+"/MathHub/*/*")]
  for repo in args.repository:
    for rep in glob.glob(repo):
      do_xhtml(rep);