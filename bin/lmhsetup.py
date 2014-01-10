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
  parser.epilog = """
    lmh setup --- downloads additional software it requires to run correctly  
  """;
  pass

def install_autocomplete():
  root = lmhutil.lmh_root()+"/ext"
  lmhutil.git_clone(root, "https://github.com/kislyuk/argcomplete.git", "arginstall")
  call([python, "setup.py", "install", "--user"], cwd=root+"/arginstall")
  activatecmd = root+"/arginstall/scripts/activate-global-python-argcomplete";
  print "running %r"%(activatecmd)
  call([root+"/arginstall/scripts/activate-global-python-argcomplete"])

def update():
  print "Updating LMH dependencies"
  root = lmhutil.lmh_root()+"/ext"
  lmhutil.git_pull(root+"/LaTeXML")
  lmhutil.git_pull(root+"/sTeX")
  lmhutil.svn_pull(root+"/MMT")

def check_deps():
  # Checks depencies as in issue #63

  islinux = os.name == "posix"
  iswin = os.name == "nt"

  if lmhutil.which("svn") == None:
    print "Unable to locate the subversion executable 'svn'. "
    print "Please make sure it is in the $PATH environment variable. "
    if islinux: 
      print "On a typical Ubuntu system you may install this with:"
      print "    sudo apt-get install subversion"
    if iswin:
      print "On Windows, you can install the command line client from TortoiseSVN. Please see: "
      print "    http://tortoisesvn.net/"
    return False

  if lmhutil.which("git") == None:
    print "Unable to locate the git executable. "
    print "Please make sure it is in the $PATH environment variable. "
    if islinux: 
      print "On a typical Ubuntu system you may install this with:"
      print "    sudo apt-get install git"
    if iswin:
      print "On Windows, you can install Git for Windows. Please see: "
      print "    http://msysgit.github.io/"
    return False

  if lmhutil.which("pdflatex") == None:
    print "Unable to locate latex executable 'pdflatex'. "
    print "Please make sure it is in the $PATH environment variable. "
    print "It is recommened to use TeXLive 2013 or later. "
    if islinux: 
      print "On Ubtuntu 13.10 or later you can install this with: "
      print "    sudo apt-get install texlive"
      print "For older Ubtuntu versions please see: "
      print "    http://askubuntu.com/a/163683"
    if iswin:
      print "For Windows, find installation instructions at: "
      print "    https://www.tug.org/texlive/windows.html"
    return False

  return True



def do(args):
  if not check_deps():
    return

  root = lmhutil.lmh_root()+"/ext"
  lmhutil.git_clone(root, "https://github.com/KWARC/LaTeXML.git")
  lmhutil.git_clone(root, "https://github.com/KWARC/sTeX.git")
  lmhutil.svn_clone(root, "https://svn.kwarc.info/repos/MMT/deploy/", "MMT")

  if args.autocomplete:
    install_autocomplete()

  if args.add_private_token and len(args.add_private_token) == 1:
    lmhutil.set_setting("private_token", args.add_private_token[0])