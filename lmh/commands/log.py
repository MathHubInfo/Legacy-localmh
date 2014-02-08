#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: status
   :func: create_parser
   :prog: status

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

import re
import os
import glob
import subprocess
import argparse

from lmh import util

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Log tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="log"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='shows recent commits in all repositories')
  add_parser_args(parser_status)


def add_parser_args(parser):
  parser.add_argument('--ordered', "-o", default=False, const=True, action="store_const", help="Orders log output by time (instead of by repository). ")
  parser.add_argument('repository', type=util.parseRepo, nargs='*', help="a list of repositories for which to show the log. ").completer = util.autocomplete_mathhub_repository
  parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs log on all repositories currently in lmh")

  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would be equivalent to "git status ."
""";

def get_log(rep):

  repshort = rep[len(util.lmh_root()+"/MathHub/"):]

  def get_format(frm):
    cmd = [
      util.which("git"), "log", "--pretty=format:"+frm+""
    ];
    result = subprocess.Popen(cmd, 
                                  stdout=subprocess.PIPE,
                                  cwd=rep
                                 ).communicate()[0]
    return result.split("\n")

  hash_short = get_format("%h")
  commit_titles = get_format("%s")
  dates = get_format("%at")
  dates_human = get_format("%ad")
  author_names = get_format("%an")
  author_mails = get_format("%ae")

  res = []

  for i in range(len(hash_short)):
    res.append({
      "hash": hash_short[i], 
      "subject": commit_titles[i], 
      "date": int(dates[i]), 
      "date_human": dates_human[i], 
      "author": author_names[i], 
      "author_mail": author_mails[i],
      "repo": repshort
    })

  return res

def do(args):
  if len(args.repository) == 0:
    args.repository = [util.tryRepo(".", util.lmh_root()+"/MathHub/*/*")]
  if args.all:
    args.repository = [util.tryRepo(util.lmh_root()+"/MathHub", util.lmh_root()+"/MathHub")]

  entries = []
  for repo in args.repository:
    for rep in glob.glob(repo):
      entries.extend(get_log(rep));

  if args.ordered:
    entries.sort(key=lambda e: -e["date"])

  strout = ""

  for entry in entries:
    strout = strout + "\nRepo:    " + entry["repo"]
    strout = strout + "\nSubject: " + entry["subject"]
    strout = strout + "\nHash:    " + entry["hash"]
    strout = strout + "\nAuthor:  " + entry["author"] + " <" + entry["author_mail"] + ">"
    strout = strout + "\nDate:    " + entry["date_human"]
    strout = strout + "\n"

  #TODO: Pager
  print strout


