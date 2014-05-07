#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: config
   :func: create_parser
   :prog: config

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
import shutil

from lmh import util
from lmh import config
from lmh import main

def create_parser():
  parser = argparse.ArgumentParser(description='Views or changes lmh configuration. ')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="mvmod"):
  parser_status = subparsers.add_parser(name, help='Moves a multilingual module to a new repository')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('sourcerepo', nargs=1, help="name of old repository")
  parser.add_argument('module', nargs=1, help="relative path of source module in old repository")
  parser.add_argument('dest', nargs=1, help="Name of new repository. Assumed to be initalised correctly. ", default=None)
  parser.add_argument('--simulate', action="store_const", default=False, const=True, help="Simulate only. ")


  parser.epilog = """
    Example: lmh mvmod smglom/smglom set smglom/set

    Which moves the multilingual set module from smglom/smglom into the new repository smglom/set
  """
def do(args):
  # change directory to MathHub root, makes paths easier

  args.sourcerepo = args.sourcerepo[0]
  args.module = args.module[0]
  args.dest = args.dest[0]

  if args.simulate: 
    print "cd "+util._lmh_root + "/MathHub/"
  else:
    os.chdir(util._lmh_root + "/MathHub/")

  # Figure out the full path to the source
  srcpath = args.sourcerepo + "/source/" +  args.module

  # Assemble source paths further
  srcargs = (args.sourcerepo + args.module).split("/")
  srcapath = "/".join(srcargs[:-1])
  srcbpath = srcargs[-1]
  
  # Assemble all the commands
  oldcall = "\\[" + srcapath + "\\]{"+srcbpath+"}"
  oldcall_long = "\\[(.*)repos=" + srcapath + "(.*)\\]{"+srcbpath+"}"
  oldcall_local = "{"+srcbpath+"}"
  newcall = "\\[" + args.dest + "\\]{"+srcbpath+"}"
  newcall_long = "\\[$g0" + args.dest + "$g1\\]{"+srcbpath+"}"

  # Move the files
  if args.simulate: 
    print "mv "+srcpath +".de.tex"+ " "+ args.dest
    print "mv "+srcpath +".en.tex"+ " "+ args.dest
  else:
    shutil.move(srcpath +".de.tex", args.dest)
    shutil.move(srcpath +".en.tex", args.dest)

  def run_lmh_command(cmd):
    if args.simulate:
      print "lmh '"+ "' '".join(cmd)+"'"
    else:
      main(cmd)

  # Run all the commands
  for m in ["gimport", "guse", "gadopt"]:
    run_lmh_command(['find', '\\\\'+m+oldcall, '--replace', '\\'+m+newcall, '--apply'])
    run_lmh_command(['find', '\\\\'+m+oldcall_local, '--replace', '\\'+m+newcall, '--apply'])

  for m in ["importmhmodule", "usemhmodule", "adoptmhmodule", "usemhvocab"]:
    run_lmh_command(['find', '\\'+m+oldcall_long, "--replace", '\\'+m+newcall_long, "--apply"])
    run_lmh_command(['find', '\\'+m+oldcall_local, '--replace', '\\'+m+newcall_long, '--apply'])
