

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: lmh
   :func: create_parser
   :prog: lmh

"""

#!/usr/bin/python 

import argparse
import lmhutil
import lmhsetup
import lmhstatus
import lmhinstall
import subprocess
import os
import sys
import traceback
import time
import lmhagg

submods = {};

def install_excepthook():
  cwd = os.getcwd();
  def my_excepthook(exctype, value, tb):
    if exctype == KeyboardInterrupt:
      return
    err = ''.join(traceback.format_exception(exctype, value, tb));
    print err;
    print "lmh seems to have crashed with %s"%exctype
    print "a report will be generated in "
    s = "cwd = {0}\n args = {1}\n".format(cwd, sys.argv)
    s = s + err 
    lmhutil.set_file(lmhutil.lmh_root()+"/logs/"+time.strftime("%Y-%m-%d-%H-%M-%S.log"), s)

  sys.excepthook = my_excepthook

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub XHTML conversion tool.')
  reps = [];

  subparsers = parser.add_subparsers(help='valid actions are:', dest="action", metavar='action')

  submodules = ["status", "log", "install", "setup", "xhtml", "init", "commit", "push", "update", "gen", "clean", "git", "find", "depcrawl", "checkpaths"];
  for mod in submodules:
    _mod = __import__("lmh"+mod)
    submods[mod] = _mod
    _mod.add_parser(subparsers)

  subparsers.add_parser('repos', help='prints the group/repository of the current  Math Hub repository')
  subparsers.add_parser('root', help='prints the root directory of the Local Math Hub repository')

  reps.append(subparsers.add_parser('sms', help='generates sms files'))
  reps.append(subparsers.add_parser('mods', help='generates omdoc module files'))
  reps.append(subparsers.add_parser('omdoc', help='generates omdoc for targets'))
  reps.append(subparsers.add_parser('pdf', help='generates pdf for targets'))
  reps.append(subparsers.add_parser('modspdf', help='generates omdoc module files'))

  for rep in reps:
    rep.add_argument('repository', type=lmhutil.parseRepo, nargs='*', help="a list of repositories. ").completer = lmhutil.autocomplete_mathhub_repository


  if lmhutil.module_exists("argcomplete"):
    __import__("argcomplete").autocomplete(parser)

  return parser

def main(argv = sys.argv[1:]):
  parser = create_parser()
  if len(argv) == 0:
    parser.print_help();
    return

  args = parser.parse_args(argv)

  if args.action == None:
    parser.print_help()
    return

  if args.action == "root":
    print lmhutil.lmh_root();
    return

  if args.action == "sms":
    import lmhgen
    cmd = ["gen"]; cmd.extend(args.repository);
    lmhgen.do(parser.parse_args(cmd));
    return    

  if args.action == "omdoc":
    import lmhgen
    if (len(args.repository) == 0):
      args.repository.append("all");
    cmd = ["gen", "--verbose", "--omdoc"]; cmd.extend(args.repository);
    lmhgen.do(parser.parse_args(cmd));
    return    

  if args.action == "pdf":
    import lmhgen
    if (len(args.repository) == 0):
      args.repository.append("all");
    cmd = ["gen", "--verbose", "--pdf"]; cmd.extend(args.repository);
    lmhgen.do(parser.parse_args(cmd));
    return    

  if args.action == "repos":
    rep = lmhutil.lmh_repos();
    if rep:
      print rep
    else:
      sys.exit(os.EX_DATAERR)
    return

  submods[args.action].do(args)

