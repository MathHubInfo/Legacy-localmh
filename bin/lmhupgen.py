"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: lmhupgen
   :func: create_parser
   :prog: lmhupgen

"""

import argparse
import lmhutil
import os
import glob
from subprocess import call
import re
import time

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub UpGen tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_status = subparsers.add_parser('upgen', formatter_class=argparse.RawTextHelpFormatter, help='updates generated content')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('repository', default=[lmhutil.parseRepo("*/*")], type=lmhutil.parseRepo, nargs='*', help="a list of repositories for which to show the status. ").completer = lmhutil.autocomplete_mathhub_repository
  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would be equivalent to "git status ."
""";

#\begin{module}....
#\end{module}
#\begin{importmodulevia}...
#\end{importmodulevia}

#\symdef...
#\abbrdef...
#\symvariant...
#keydef
#\listkeydef
#\importmodule...
#\gimport...
#\adoptmodule...
#\importmhmodule
#\adoptmhmodule

regStrings = [r'\\(symdef|abbrdef|symvariant|keydef|listkeydef|importmodule|gimport|adoptmodule|importmhmodule|adoptmhmodule)', r'\\begin{(module|importmodulevia)}', r'\\end{(module|importmodulevia)}']
regs = map(re.compile, regStrings)

def genSMS(input, output):
  print "generating %r"%output
  output = open(output, "w")
  for line in open(input):
    for reg in regs:
      if reg.search(line):
        output.write(line.strip()+"%\n")
        break
  output.close()


def do_upgen(rep):
  for root, dirs, files in os.walk(rep):
    for file in files:
      if not file.endswith(".tex"):
        continue
      smsfileName = root+"/"+file[:-4]+".sms";
      fullFile = root+"/"+file;
      if not os.path.exists(smsfileName):
        genSMS(fullFile, smsfileName)
        continue
      if os.path.getmtime(fullFile) > os.path.getmtime(smsfileName):
        genSMS(fullFile, smsfileName)
        continue

def do(args):
  for repo in args.repository:
    for rep in glob.glob(repo):
      do_upgen(rep);