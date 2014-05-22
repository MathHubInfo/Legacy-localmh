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
  parser.add_argument('source', nargs=1, help="name of old repository. ")
  parser.add_argument('dest', nargs=1, help="Name of new repository. Assumed to be initalised correctly. ", default=None)
  parser.add_argument('module', nargs="+", help="Relative path(s) of source module(s) in old repository")
  parser.add_argument('--simulate', action="store_const", default=False, const=True, help="Simulate only. ")


  parser.epilog = """
    Example: lmh mvmod smglom/smglom smglom/set set 

    Which moves the multilingual set module from smglom/smglom into the new repository smglom/set. 

    It can be advisable to run an lmh clean before executing this command, as it speeds it up quite a lot. 
  """
def do(args):
  args.source = args.source[0]
  args.dest = args.dest[0]

  # change directory to MathHub root, makes paths easier
  if args.simulate: 
    print "cd "+util._lmh_root + "/MathHub/"
  else:
    os.chdir(util._lmh_root + "/MathHub/")

  for module in args.module:
    # Figure out the full path to the source
    srcpath = args.source + "/source/" +  module

    # Assemble source paths further
    srcargs = (args.source + "/" + module).split("/")
    srcapath = "/".join(srcargs[:-1])
    srcbpath = srcargs[-1]
    
    # Assemble all the commands
    oldcall = "[" + srcapath + "]{"+srcbpath+"}"
    oldcall_long = "[(.*)repos=" + srcapath + "(.*)]{"+srcbpath+"}"
    oldcall_local = "{"+srcbpath+"}"
    newcall = "[" + args.dest + "]{"+srcbpath+"}"
    newcall_long = "[$g0" + args.dest + "$g1]{"+srcbpath+"}"

    args.dest += "/source/"

    file_patterns = ["", ".de", ".en"]

    # Move the files
    if args.simulate:
      for pat in file_patterns:
        # try to move the file if it exists
        try:
          print "mv "+srcpath + pat +".tex"+ " "+ args.dest + " 2>/dev/null || true"
        except:
          pass
      
    else:
      for pat in file_patterns:
        # try to move the file if it exists
        try:
          shutil.move(srcpath + pat + ".tex", args.dest)
        except:
          pass
      

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
