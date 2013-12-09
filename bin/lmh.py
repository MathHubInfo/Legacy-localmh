#!/usr/bin/python 

import argparse
import lmhutil
import lmhsetup
import lmhinstall
import subprocess
import os
import sys

parser = argparse.ArgumentParser(description='Local MathHub tool.')

init_choises = ['setup', 'install', 'update', 'drain', 'delete', 'init', 'root', 'depscrawl', 'path', 'update', 'drain', 'upgen', 'checkpaths', 'status', 'repos'];

parser.add_argument('action', metavar='action', choices=init_choises, 
                   help="action to be performed. Can be one of the following: "+", ".join(init_choises), nargs="?")

args, rest = parser.parse_known_args()

if args.action == None:
  parser.print_help()

if args.action == "install":
  lmhinstall.installrepo(rest[0])

if args.action == "setup":
  lmhsetup.setup();  

if args.action == "root":
  print lmhutil.lmh_root();

if args.action == "status":
  import lmhstatus
  lmhstatus.do(rest);

if args.action == "repos":
  rep = lmhutil.lmh_repos();
  if rep:
    print rep
  else:
    sys.exit(os.EX_DATAERR)

if args.action == "depscrawl":
  import lmhdepcrawler
  lmhdepcrawler.do(rest);

if args.action == "checkpaths":
  import lmhpathchecker
  lmhpathchecker.do(rest)

if args.action == "path":
  import lmhpath
  lmhpath.do(rest)

if args.action == "update":
  import lmhupdate
  lmhupdate.do(rest, "pull")

if args.action == "upgen":
  import lmhupdate
  lmhupdate.do(rest, "upgen")

if args.action == "drain":
  import lmhupdate
  lmhupdate.do(rest, "push")

if args.action == "init":
  import lmhinit
  lmhinit.init()
