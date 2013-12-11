"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: lmhsetup
   :func: create_parser
   :prog: lmhsetup

"""

import argparse
import lmhutil
import os
from subprocess import call
import ConfigParser

gitpath = lmhutil.which("git")
python = lmhutil.which("python")

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Setup tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_status = subparsers.add_parser('setup', formatter_class=argparse.RawTextHelpFormatter, help='sets up local math hub and fetches external requirements')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('--autocomplete', default=False, const=True, action="store_const", help="should install autocomplete for bash", metavar="")
  parser.add_argument('--add-private-token', nargs=1, help="add private token to use advanced MathHub functionality")
  pass

def install_autocomplete():
  root = lmhutil.lmh_root()+"/ext"
  lmhutil.git_clone(root, "https://github.com/kislyuk/argcomplete.git", "arginstall")
  call([python, "setup.py", "install", "--user"], cwd=root+"/arginstall")
  activatecmd = root+"/arginstall/scripts/activate-global-python-argcomplete";
  print "running %r"%(activatecmd)
  call([root+"/arginstall/scripts/activate-global-python-argcomplete"])

def do(args):
  root = lmhutil.lmh_root()+"/ext"
  lmhutil.git_clone(root, "https://github.com/KWARC/LaTeXML.git")
  lmhutil.git_clone(root, "https://github.com/KWARC/sTeX.git")

  if args.autocomplete:
    install_autocomplete()

  if args.add_private_token and len(args.add_private_token) == 1:
    lmhutil.set_setting("private_token", args.add_private_token[0])