#!/usr/bin/python 

import argparse
import lmhconfig
import lmhinstall

parser = argparse.ArgumentParser(description='Local Math Hub tool.')

parser.add_argument('action', metavar='action', choices=['setup', 'install', 'update', 'drain', 'delete'], 
                   help="action to be performed. Can be either 'setup', 'install', 'update', 'drain' or 'delete' ")

args, rest = parser.parse_known_args()

if args.action == "install":
  lmhinstall.installrepo(rest[0])
  