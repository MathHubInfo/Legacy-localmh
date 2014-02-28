#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: xhtml
   :func: create_parser
   :prog: xhtml

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

import argparse

import os
from subprocess import call
import ConfigParser
import glob

#from lmh.commands.gen import prep_gen
from lmh.commands.gen import create_parser as gen_parser
from lmh.mmt import compile
from lmh import util

p = gen_parser()
attr = p.parse_args(["--omdoc"]);

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub XHTML tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="xhtml"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='generate XHTML ')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('repository', type=util.parseRepo, nargs='*', help="a list of repositories for which to generate XHTML").completer = util.autocomplete_mathhub_repository
  parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs status on all repositories currently in lmh")
  pass

def do_xhtml(rep):
  # TODO: Rebuild this

  rep_root = util.git_root_dir(rep)
  def msg(m):
    pass
  # prep_gen(rep, attr, msg)
  # compile(rep_root)
  pass

def do(args):
  if len(args.repository) == 0:
    args.repository = [util.tryRepo(".", util.lmh_root()+"/MathHub/*/*")]
  if args.all:
    args.repository = [util.tryRepo(util.lmh_root()+"/MathHub", util.lmh_root()+"/MathHub")]  

  for repo in args.repository:
    for rep in glob.glob(repo):
      do_xhtml(rep);