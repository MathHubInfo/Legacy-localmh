#!/usr/bin/python 

import argparse
import lmhconfig
import lmhinstall
import subprocess
import os

parser = argparse.ArgumentParser(description='Local Math Hub tool.')

parser.add_argument('action', metavar='action', choices=['setup', 'install', 'update', 'drain', 'delete', 'init'], 
                   help="action to be performed. Can be either 'setup', 'init', install', 'update', 'drain' or 'delete' ")

args, rest = parser.parse_known_args()

if args.action == "install":
  lmhinstall.installrepo(rest[0])

if args.action == "init":
  rootdir = subprocess.Popen([lmhconfig.which("git"), "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE).communicate()[0]
  rootdir = rootdir.strip()
  metadir = rootdir+"/META-INF"

  if not os.path.exists(metadir):
    os.makedirs(metadir)

  if not os.path.exists(metadir+"/MANIFEST.MF"):
    f = open(metadir+"/MANIFEST.MF", 'w')
    f.write("id: \n")
    f.write("source-base: \n")
    f.write("narration-base: \n")
    f.write("dependencies: \n")
    f.close()