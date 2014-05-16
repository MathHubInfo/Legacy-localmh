#!/usr/bin/env python

"""

.. argparse::
   :module: update
   :func: create_parser
   :prog: update

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
import glob
from subprocess import call

from lmh.commands.setup import update as setup_update
from lmh.commands import selfupdate
from lmh import util
from lmh import config

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Update tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="update"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='get repository and tool updates')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('repository', type=util.parseRepo, nargs='*', help="a list of repositories which should be updated. ").completer = util.autocomplete_mathhub_repository
  parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="updates all repositories currently in lmh")
  parser.epilog = """
If update::selfupdate is set to True, calling lomh update without any arguments will also call lmh selfupdate. 

Note: LMH will check for tool updates only if run at the root of the LMH folder 
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would be equivalent to updating current repository
""";

def do_pull(rep):
  print "pulling %r"%rep
  call([util.which("git"), "pull"], cwd=rep);

def do(args):
  if len(args.repository) == 0:
    args.repository = [util.tryRepo(".", util.lmh_root()+"/MathHub/*/*")]

    if config.get_config("update::selfupdate"):
      print "Selfupdate: "
      selfupdate.do(None)


  if args.all:
    args.repository = [util.tryRepo(util.lmh_root()+"/MathHub", util.lmh_root()+"/MathHub")]

  for repo in args.repository:
    for rep in glob.glob(repo):
      do_pull(rep);
