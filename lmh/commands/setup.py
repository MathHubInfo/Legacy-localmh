#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: setup
   :func: create_parser
   :prog: setup

"""

"""
This file is part of LMH.

LMH is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

LMH is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LMH.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import argparse
import ConfigParser
import shutil
from subprocess import call

from lmh import util
from lmh import config

gitpath = util.which("git")
python = util.which("python")

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Setup tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="setup"):
  parser_status = subparsers.add_parser('setup', formatter_class=argparse.RawTextHelpFormatter, help='sets up local math hub and fetches external requirements')
  add_parser_args(parser_status)

def add_parser_args(parser):
  action = parser.add_argument_group('Setup actions').add_mutually_exclusive_group()
  action.add_argument('--install', action="store_const", dest="m_action", const="in", default="", help='Perform initial setup of dependencies. Default if no other arguments are given. ')
  action.add_argument('--update', action="store_const", dest="m_action", const="up", help='Update existing versions of dependencies. Implies --update-* arguments. ')
  action.add_argument('--reinstall', action="store_const", dest="m_action", const="re", help='Perform initial setup of dependencies. ')
  action.add_argument('--skip', action="store_const", dest="m_action", const="sk", help='Skip everything which is not specified explicitly. ')

  parser.add_argument('-f', '--force', action="store_const", dest="force", const=True, default=False, help='Skip checking for lmh core requirements. ')
  parser.add_argument('--autocomplete', default=False, const=True, action="store_const", help="should install autocomplete for bash", metavar="")
  parser.add_argument('--add-private-token', nargs=1, help="add private token to use advanced MathHub functionality")
   
  source = parser.add_argument_group('Dependency versions')
  source.add_argument('--latexml-source', default="", metavar="source@branch", help='Get LaTeXML from the given source. ')
  source.add_argument('--latexmls-source', default="", metavar="source@branch", help='Get LaTeXMLs from the given source. ')
  source.add_argument('--stex-source', default="", metavar="source@branch", help='Get sTex from the given source. ')
  source.add_argument('--mmt-source', default="", metavar="source@branch", help='Get MMT from the given source. ')

  latexml = parser.add_argument_group('LaTeXML').add_mutually_exclusive_group()
  latexml.add_argument('--install-latexml', action="store_const", dest="latexml_action", const="in", default="", help='Install LaTexML. ')
  latexml.add_argument('--update-latexml', action="store_const", dest="latexml_action", const="up", help='Update LaTeXML. ')
  latexml.add_argument('--reinstall-latexml', action="store_const", dest="latexml_action", const="re", help='Reinstall LaTeXML. ')
  latexml.add_argument('--skip-latexml', action="store_const", dest="latexml_action", const="sk", help='Leave LaTeXML untouched. ')

  latexmls = parser.add_argument_group('LaTeXML::Plugin::latexmls').add_mutually_exclusive_group()
  latexmls.add_argument('--install-latexmls', action="store_const", dest="latexmls_action", const="in", default="", help='Install LaTexMLs. ')
  latexmls.add_argument('--update-latexmls', action="store_const", dest="latexmls_action", const="up", help='Update LaTeXMLs. ')
  latexmls.add_argument('--reinstall-latexmls', action="store_const", dest="latexmls_action", const="re", help='Reinstall LaTeXMLs. ')
  latexmls.add_argument('--skip-latexmls', action="store_const", dest="latexmls_action", const="sk", help='Leave LaTeXMLs untouched. ')


  stex = parser.add_argument_group('sTeX').add_mutually_exclusive_group()
  stex.add_argument('--install-stex', action="store_const", dest="stex_action", const="in", default="", help='Install sTeX. ')
  stex.add_argument('--update-stex', action="store_const", dest="stex_action", const="up", help='Update sTeX. ')
  stex.add_argument('--reinstall-stex', action="store_const", dest="stex_action", const="re", help='Reinstall sTeX. ')
  stex.add_argument('--skip-stex', action="store_const", dest="stex_action", const="sk", help='Leave sTeX untouched. ')

  mmt = parser.add_argument_group('MMT').add_mutually_exclusive_group()
  mmt.add_argument('--install-mmt', action="store_const", dest="mmt_action", const="in", default="", help='Install MMT. ')
  mmt.add_argument('--update-mmt', action="store_const", dest="mmt_action", const="up", help='Update MMT. ')
  mmt.add_argument('--reinstall-mmt', action="store_const", dest="mmt_action", const="re", help='Reinstall MMT. ')
  mmt.add_argument('--skip-mmt', action="store_const", dest="mmt_action", const="sk", help='Leave MMT untouched. ')


  parser.epilog = """
    lmh setup --- sets up additional software it requires to run correctly  

    To install and compile latexml you may need additional packages. On Ubuntu the package libgdbm-dev should be enough. 
  """;
  pass

def install_autocomplete():
  root = util.lmh_root()+"/ext"
  util.git_clone(root, "https://github.com/kislyuk/argcomplete.git", "arginstall")
  call([python, "setup.py", "install", "--user"], cwd=root+"/arginstall")
  activatecmd = root+"/arginstall/scripts/activate-global-python-argcomplete";
  print "running %r"%(activatecmd)
  call([root+"/arginstall/scripts/activate-global-python-argcomplete"])

def update():
  print "Updating LMH dependencies ..."
  do({
    "m_action": "up", 
    "force": True, 
    "autocomplete": False, 
    "latexml_source": "", 
    "stex_source": "", 
    "mmt_source": "",
    "latexml_action": "", 
    "stex_action": "", 
    "mmt_action": ""
  })

def check_deps():
  islinux = os.name == "posix"
  iswin = os.name == "nt"

  if util.which("svn") == None:
    print "Unable to locate the subversion executable 'svn'. "
    print "Please make sure it is in the $PATH environment variable. "
    if islinux: 
      print "On a typical Ubuntu system you may install this with:"
      print "    sudo apt-get install subversion"
    if iswin:
      print "On Windows, you can install the command line client from TortoiseSVN. Please see: "
      print "    http://tortoisesvn.net/"
    return False

  if util.which("git") == None:
    print "Unable to locate the git executable. "
    print "Please make sure it is in the $PATH environment variable. "
    if islinux: 
      print "On a typical Ubuntu system you may install this with:"
      print "    sudo apt-get install git"
    if iswin:
      print "On Windows, you can install Git for Windows. Please see: "
      print "    http://msysgit.github.io/"
    return False

  if util.which("pdflatex") == None:
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

  if util.which("perl") == None:
    print "Unable to locate perl executable. "
    print "Please make sure it is in the $PATH environment variable. "
    if islinux: 
      print "On Ubtuntu 13.10 or later you can install this with: "
      print "    sudo apt-get install perl"
    return False

  if util.which("cpanm") == None:
    print "Unable to locate cpanm executable. "
    print "Please make sure it is in the $PATH environment variable. "
    if islinux: 
      print "On Ubtuntu 13.10 or later you can install this with: "
      print "    sudo apt-get install cpanminus"
    return False

  if util.which("make") == None:
    print "Unable to locate make. "
    print "Please make sure it is in the $PATH environment variable. "
    return False

  if util.which("tar") == None:
    print "Unable to locate tar. "
    print "Please make sure it is in the $PATH environment variable. "
    return False


  try:
    import psutil
  except:
    print "Unable to locate python module 'psutil'. "
    print "Please make sure it is installed. "
    print "You may be able to install it with: "
    print "    pip install psutil"
    return False


  return True

def latexml_install(root, source, branch):
  try:
    if branch == "":
      util.git_clone(root, source, "LaTeXML")
    else:
      util.git_clone(root, source, "-b", branch, "LaTeXML")
  except:
    print "Failed to install LaTeXML (is the source available? )"
def latexml_update(root, source, branch):
  try:
    util.git_pull(root + "/LaTeXML")
  except:
    print "Failed to update LaTeXML (is it present? )"
def latexml_make(root):
  cpanm = util.which("cpanm")
  perl = util.which("perl")
  make = util.which("make")
  _env = util.perl5env(os.environ)
  _env.pop("STEXSTYDIR", None)
  try:
    call([cpanm, "-L", util.perl5root[0], "--installdeps", "--prompt", "."], env=_env, cwd=root+"/LaTeXML", stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    call([cpanm, "-L", util.perl5root[0], "--notest", "--prompt", "."], env=_env, cwd=root+"/LaTeXML", stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
  
    # MANUAL INSTALLATION
    #call([perl, "Makefile.PL"], env=_env, cwd=root+"/LaTeXML")
    #call([make], env=_env, cwd=root+"/LaTeXML")
    #call([make, "test"], env=_env, cwd=root+"/LaTeXML")
  except Exception as e:
    print "Unable to run make commands for latexml. "
    print e
def latexmls_make(root):
  cpanm = util.which("cpanm")
  perl = util.which("perl")
  make = util.which("make")
  _env = util.perl5env(os.environ)
  _env.pop("STEXSTYDIR", None)
  try:
    call([cpanm, "-L", util.perl5root[0], "--installdeps", "--prompt", "."], env=_env, cwd=root+"/LaTeXMLs", stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    call([cpanm, "-L", util.perl5root[0], "--notest", "--prompt", "."], env=_env, cwd=root+"/LaTeXMLs", stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    
    # MANUAL INSTALLATION
    #call([perl, "Makefile.PL"], env=_env, cwd=root+"/LaTeXMLs")
    #call([make], env=_env, cwd=root+"/LaTeXMLs")
    #call([make, "test"], env=_env, cwd=root+"/LaTeXMLs")
  except Exception as e:
    print "Unable to run make commands for latexmls. "
    print e
def latexml_remove(root, source, branch):
  try:
     shutil.rmtree(root + "/LaTeXML")
  except:
    print "Failed to remove LaTeXML (is it present? )"

def latexmls_install(root, source, branch):
  try:
    if branch == "":
      util.git_clone(root, source, "LaTeXMLs")
    else:
      util.git_clone(root, source, "-b", branch, "LaTeXMLs")
  except:
    print "Failed to install LaTeXMLs (is the source available? )"
def latexmls_update(root, source, branch):
  try:
    util.git_pull(root + "/LaTeXMLs")
  except:
    print "Failed to update LaTeXMLs (is it present? )"
def latexmls_remove(root, source, branch):
  try:
     shutil.rmtree(root + "/LaTeXMLs")
  except:
    print "Failed to remove LaTeXMLs (is it present? )"

def stex_install(root, source, branch):
  try:
    if branch == "":
      util.git_clone(root, source, "sTeX")
    else:
      util.git_clone(root, source, "-b", branch, "sTeX")
  except:
    print "Failed to install sTex (is the source available? )"
 
def stex_update(root, source, branch):
  try:
    util.git_pull(root + "/sTeX")
  except:
    print "Failed to update sTex (is it present? )"
def stex_remove(root, source, branch):
  try:
    shutil.rmtree(root + "/sTeX")
  except: 
    print "Failed to remove sTex (is it present? )"

def mmt_install(root, source, branch):
  try:
    if branch == "":
      util.svn_clone(root, source, "MMT")
    else:
      util.svn_clone(root, source + "@" + branch, "MMT")
  except:
    print "Failed to install MMT (is it present? )"
def mmt_update(root, source, branch):
  try:
    util.svn_pull(root + "/MMT")
  except:
    print "Failed to update MMT (is it present? )"
def mmt_remove(root, source, branch):
  try:
    shutil.rmtree(root + "/MMT")
  except: 
    print "Failed to remove MMT (is it present? )"

def do(args):

  # Dependency check
  if (not args.force) and (not check_deps()):
    print "Dependency check failed, either install dependencies manually "
    print "or use --force to ignore dependency checks. "
    return

  root = util.lmh_root()+"/ext"
  action = args.m_action
  if action == "":
    if args.latexml_action == "" and args.stex_action == "" and args.mmt_action == "":
      action = "in"
    else:
      action = "sk"

  # LaTeXML
  latexml_action = args.latexml_action or action
  latexml_source = "https://github.com/KWARC/LaTeXML.git"
  latexml_branch = ""

  if not args.latexml_source == "":
    index = args.latexml_source.find("@")
    if index == 0:
      latexml_branch = args.latexml_source[1:]
    elif index > 0:
      latexml_source = args.latexml_source[:index]
      latexml_branch = args.latexml_source[index+1:]
    else:
      latexml_source = args.latexml_source

    print "Using LaTexML Version: "+latexml_source+"@"+latexml_branch


  if latexml_action == "re":
    print "Reinstalling LaTexML ..."
    latexml_remove(root, latexml_source, latexml_branch)
    latexml_install(root, latexml_source, latexml_branch)
    latexml_make(root)
  if latexml_action == "in":
    print "Installing LaTeXML ..."
    latexml_install(root, latexml_source, latexml_branch)
    latexml_make(root)
  if latexml_action == "up":
    print "Updating LaTexML ..."
    latexml_update(root, latexml_source, latexml_branch)
    latexml_make(root)

  # LaTeXMLs
  latexmls_action = args.latexml_action or action
  latexmls_source = "https://github.com/dginev/LaTeXML-Plugin-latexmls"
  latexmls_branch = ""

  if not args.latexmls_source == "":
    index = args.latexmls_source.find("@")
    if index == 0:
      latexmls_branch = args.latexmls_source[1:]
    elif index > 0:
      latexmls_source = args.latexmls_source[:index]
      latexmls_branch = args.latexmls_source[index+1:]
    else:
      latexmls_source = args.latexmls_source

    print "Using LaTexML Version: "+latexmls_source+"@"+latexmls_branch


  if latexmls_action == "re":
    print "Reinstalling LaTexMLs ..."
    latexmls_remove(root, latexmls_source, latexmls_branch)
    latexmls_install(root, latexmls_source, latexmls_branch)
    latexmls_make(root)
  if latexmls_action == "in":
    print "Installing LaTeXMLs ..."
    latexmls_install(root, latexmls_source, latexmls_branch)
    latexmls_make(root)
  if latexmls_action == "up":
    print "Updating LaTexMLs ..."
    latexmls_update(root, latexmls_source, latexmls_branch)
    latexmls_make(root)

  # sTex
  stex_action = args.stex_action or action
  stex_source = "https://github.com/KWARC/sTeX.git"
  stex_branch = ""

  if not args.stex_source == "":
    index = args.stex_source.find("@")
    if index == 0:
      stex_branch = args.stex_source[1:]
    elif index > 0:
      stex_source = args.stex_source[:index]
      stex_branch = args.stex_source[index+1:]
    else:
      stex_source = args.stex_source

    print "Using sTeX Version: "+stex_source+"@"+stex_branch

  if stex_action == "re":
    print "Reinstalling sTeX ..."
    stex_remove(root, stex_source, stex_branch)
    stex_install(root, stex_source, stex_branch)
  if stex_action == "in":
    print "Installing sTex ..."
    stex_install(root, stex_source, stex_branch)
  if stex_action == "up":
    print "Updating sTex ..."
    stex_update(root, stex_source, stex_branch)

  # MMT
  mmt_action = args.mmt_action or action
  mmt_source = "https://svn.kwarc.info/repos/MMT/deploy/"
  mmt_branch = ""

  if not args.mmt_source == "":
    index = args.mmt_source.find("@")
    if index == 0:
      mmt_branch = args.mmt_source[1:]
    elif index > 0:
      mmt_source = args.mmt_source[:index]
      mmt_branch = args.mmt_source[index+1:]
    else:
      mmt_source = args.mmt_source

    print "Using MMT Version: "+mmt_source+"@"+mmt_branch

  if mmt_action == "re":
    print "Reinstalling MMT ..."
    mmt_remove(root, mmt_source, mmt_branch)
    mmt_install(root, mmt_source, mmt_branch)
  if mmt_action == "in":
    print "Installing MMT ..."
    mmt_install(root, mmt_source, mmt_branch)
  if mmt_action == "up":
    print "Updating MMT ..."
    mmt_update(root, mmt_source, mmt_branch)


  if args.autocomplete:
    print "Installing autocomplete ..."
    install_autocomplete()

  if args.add_private_token and len(args.add_private_token) == 1:
    print "Adding private token ..."
    config.set_config("gl::private_token", args.add_private_token[0])