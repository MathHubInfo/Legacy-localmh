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

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Setup tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_status = subparsers.add_parser('setup', formatter_class=argparse.RawTextHelpFormatter, help='sets up local math hub and fetches external requirements')
  add_parser_args(parser_status)

def add_parser_args(parser):
  pass

def do(args):
  root = lmhutil.lmh_root()+"/ext"
  os.chdir(root)

  gitpath = lmhutil.which("git")

  print "cloning LaTeXML"
  call([gitpath, "clone", "https://github.com/KWARC/LaTeXML.git"])
  print "cloning sTeX"
  call([gitpath, "clone", "https://github.com/KWARC/sTeX.git"])
  