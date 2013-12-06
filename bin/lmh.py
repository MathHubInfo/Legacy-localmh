#!/usr/bin/python 

import argparse
import lmhconfig
import lmhsetup
import lmhinstall
import subprocess
import os

parser = argparse.ArgumentParser(description='Local Math Hub tool.')

parser.add_argument('action', metavar='action', choices=['setup', 'install', 'update', 'drain', 'delete', 'init', 'root', 'depscrawl', 'path'], 
                   help="action to be performed. Can be either 'setup', 'init', install', 'update', 'drain' or 'delete' ")

args, rest = parser.parse_known_args()

if args.action == "install":
  lmhinstall.installrepo(rest[0])

if args.action == "setup":
  lmhsetup.setup();  

if args.action == "root":
  print lmhconfig.lmh_root();

if args.action == "depscrawl":
  import lmhdepcrawler
  print lmhdepcrawler.getDeps();

if args.action == "path":
  import lmhmove
  lmhmove.do(rest)

if args.action == "init":
  import lmhinit
  lmhinit.init()
