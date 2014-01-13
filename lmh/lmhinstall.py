#!/usr/bin/python

"""
Local Math Hub repository installer

.. argparse::
   :module: lmhinstall
   :func: create_parser
   :prog: lmhinstall

"""


import re
import os
import sys
import argparse
from subprocess import call

from . import lmhutil

repoRegEx = lmhutil.repoRegEx;

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Install tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_status = subparsers.add_parser('install', help='fetches a MathHub repository and its dependencies')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('repository', default=["."], type=lmhutil.parseSimpleRepo, nargs='*', help="a list of remote repositories to fetch locally. Should have form mygroup/myproject. No wildcards allowed. ")

def do(args):
  for rep in args.repository:
    installrepo(rep)

def getURL(repoName):
  return "git@gl.mathhub.info:"+repoName

def cloneRepository(repoName):
  try:
    gitpath = lmhutil.which("git")
    if os.path.exists(repoName):
      return
    repoURL = getURL(repoName)
    print "cloning " + repoURL
    
    call([gitpath, "clone", repoURL, repoName])
  except Exception, e:
    print e
    pass

def installNoCycles(repoName, tried):
  if (repoName) in tried:
    return

  tried[repoName] = True
  cloneRepository(repoName)

  print "Checking dependencies for project "+repoName

  deps = lmhutil.get_dependencies(repoName);
  if deps == None:
    print("Error: META-INF/MANIFEST.MF file missing or invalid.\n You should consider running lmh init.")
    return

  for dep in deps:
    installNoCycles(dep, tried)


def installrepo(repoName):
  root = lmhutil.lmh_root()+"/MathHub"
  os.chdir(root)
  installNoCycles(repoName, {})

