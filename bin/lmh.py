#!/usr/bin/python 

import argparse
import lmhconfig
import lmhsetup
import lmhinstall
import subprocess
import os

parser = argparse.ArgumentParser(description='Local MathHub tool.')

init_choises = ['setup', 'install', 'update', 'drain', 'delete', 'init', 'root', 'depscrawl', 'path', 'update', 'drain', 'upgen', 'checkpaths', 'status'];

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
  print lmhconfig.lmh_root();

if args.action == "status":
  import lmhstatus
  lmhstatus.do(rest);

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
