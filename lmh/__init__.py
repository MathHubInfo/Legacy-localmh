#!/usr/bin/env python

"""
Local Math Hub utility main parser. 

.. argparse::
   :module: lmh
   :func: create_parser
   :prog: lmh

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
import time
import subprocess
import traceback

from lmh import util
from lmh.commands import create_parser
from lmh.commands import gen
from lmh.commands import preparse_args

submods = {};

def install_excepthook():
  cwd = os.getcwd()
  def my_excepthook(exctype, value, tb):
    if exctype == KeyboardInterrupt:
      return
    err = ''.join(traceback.format_exception(exctype, value, tb))
    print err
    print "lmh seems to have crashed with %s"%exctype
    print "a report will be generated in "
    s = "cwd = {0}\n args = {1}\n".format(cwd, sys.argv)
    s = s + err 
    util.set_file(util.lmh_root()+"/logs/"+time.strftime("%Y-%m-%d-%H-%M-%S.log"), s)

  sys.excepthook = my_excepthook

def main(argv = sys.argv[1:]):
  """Calls the main program with given arguments. """
  parser = create_parser(submods)
  if len(argv) == 0:
    parser.print_help();
    return

  args = parser.parse_args(argv)

  if args.action == None:
    parser.print_help()
    return

  if args.action == "root":
    print util.lmh_root()
    return

  # gen aliases
  if args.action == "sms":
    argv[0] = "gen"
    argv.append("--sms")
    return submods["gen"].do(parser.parse_args(argv))

  if args.action == "omdoc":
    argv[0] = "gen"
    argv.append("--omdoc")
    return submods["gen"].do(parser.parse_args(argv))
    return    

  if args.action == "pdf":
    argv[0] = "gen"
    argv.append("--pdf")
    return submods["gen"].do(parser.parse_args(argv)) 

  if args.action == "repos":
    rep = util.lmh_repos()
    if rep:
      print rep
    else:
      sys.exit(os.EX_DATAERR)
    return

  submods[args.action].do(args)

def run(argv = sys.argv[1:]):
  install_excepthook()
  main(preparse_args(argv))