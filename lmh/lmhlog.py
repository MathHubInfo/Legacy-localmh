"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: lmhstatus
   :func: create_parser
   :prog: lmhstatus

"""

import lmhutil
import re
import os
import glob
import subprocess
import argparse

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Log tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_status = subparsers.add_parser('log', formatter_class=argparse.RawTextHelpFormatter, help='shows recent commits in all repositories')
  add_parser_args(parser_status)


def add_parser_args(parser):
  parser.add_argument('--ordered', "-o", default=False, const=True, action="store_const", help="Orders log output by time (instead of by repository). ")
  parser.add_argument('repository', type=lmhutil.parseRepo, nargs='*', help="a list of repositories for which to show the log. ").completer = lmhutil.autocomplete_mathhub_repository
  parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="runs log on all repositories currently in lmh")

  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would be equivalent to "git status ."
""";

def get_log(rep):

  repshort = rep[len(lmhutil.lmh_root()+"/MathHub/"):]

  def get_format(frm):
    cmd = [
      lmhutil.which("git"), "log", "--pretty=format:"+frm+""
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
    args.repository = [lmhutil.tryRepo(".", lmhutil.lmh_root()+"/MathHub/*/*")]
  if args.all:
    args.repository = [lmhutil.tryRepo(lmhutil.lmh_root()+"/MathHub", lmhutil.lmh_root()+"/MathHub")]

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


