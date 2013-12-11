#!/usr/bin/python
# PYTHON_ARGCOMPLETE_OK

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

submods = {};

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub tool.')

  subparsers = parser.add_subparsers(help='valid actions are:', dest="action", metavar='action')

  submodules = ["status", "install", "setup", "init", "drain", "update", "gen", "path", "depcrawl", "checkpaths"];
  for mod in submodules:
    _mod = __import__("lmh"+mod)
    submods[mod] = _mod
    _mod.add_parser(subparsers)

  subparsers.add_parser('repos', help='prints the group/repository of the current  Math Hub repository')
  subparsers.add_parser('root', help='prints the root directory of the Local Math Hub repository')

  if lmhutil.module_exists("argcomplete"):
    __import__("argcomplete").autocomplete(parser)

  return parser

def main():
  parser = create_parser()
  if len(sys.argv) == 1:
    parser.print_help();
    return

  args = parser.parse_args()

  if args.action == None:
    parser.print_help()
    return

  if args.action == "root":
    print lmhutil.lmh_root();
    return

  if args.action == "repos":
    rep = lmhutil.lmh_repos();
    if rep:
      print rep
    else:
      sys.exit(os.EX_DATAERR)
    return

  submods[args.action].do(args)

"""

  if args.action == "depscrawl":
    import lmhdepcrawler
    lmhdepcrawler.do(rest);

  if args.action == "checkpaths":
    import lmhpathchecker
    lmhpathchecker.do(rest)

  if args.action == "path":
    import lmhpath
    lmhpath.do(rest)

"""

if __name__ == "__main__":
    main()