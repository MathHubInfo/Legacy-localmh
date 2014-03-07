#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: selfupdate
   :func: create_parser
   :prog: selfupdate

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

from subprocess import Popen

from lmh import util



def create_parser():
  parser = argparse.ArgumentParser(description='Updates lmh itself. ')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="selfupdate"):
  subparsers.add_parser(name, help='Updates lmh itself. ')

def add_parser_args(parser):
  pass

def do(args):
  ps = Popen([util.which("git"), "pull"], stdout=sys.stdout, stdin=sys.stdin, stderr=sys.stderr)
  ps.wait()
  sys.exit(ps.returncode)