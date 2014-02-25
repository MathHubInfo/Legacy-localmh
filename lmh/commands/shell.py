#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: git
   :func: create_parser
   :prog: git

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
from subprocess import Popen

from lmh import util

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Shell wrapper. ')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="shell"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='launch a shell with everything set to run build commands. ')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('shell', nargs="?", help="shell to use")

def do(args):
  if args.shell == None:
    shell = os.environ["SHELL"] or util.which("bash")
  else:
    shell = util.which(args.shell)
    if shell == None:
      shell = args.shell

  _env = os.environ
  _env = util.perl5env(_env)

  try:
      runner = Popen([shell], env=_env, cwd=util.lmh_root(), stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
  except:
      sys.exit(1)

  def do_the_run():
      try:
          runner.wait()
      except KeyboardInterrupt:
          runner.send_signal(signal.SIGINT)
          do_the_run()

  print "Opening a shell ready to compile for you. "
  do_the_run()
  
  sys.exit(runner.returncode)