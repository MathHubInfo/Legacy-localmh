#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: gen
   :func: create_parser
   :prog: gen

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

import os
import sys
import re
import glob
import time
import signal
import shutil
import argparse
import datetime
import functools
import traceback

from lmh.commands.gen.sms import gen_sms
from lmh.commands.gen.localpaths import gen_localpaths
from lmh.commands.gen.alltex import gen_alltex
from lmh.commands.gen.omdoc import gen_omdoc
from lmh.commands.gen.pdf import gen_pdf

from lmh import util


def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Generation tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="gen"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='updates generated content')
  add_parser_args(parser_status)

def add_parser_args(parser, add_types=True):

  flags = parser.add_argument_group("Generation options")

  f1 = flags.add_mutually_exclusive_group()
  f1.add_argument('-w', '--workers',  metavar='number', default=8, type=int, help='number of worker processes to use')
  f1.add_argument('-s', '--single',  action="store_const", dest="workers", const=1, help='Use only a single process. Shortcut for -w 1')

  f2 = flags.add_mutually_exclusive_group()
  f2.add_argument('-u', '--update', const=True, default=True, action="store_const", help="Only generate files which have been changed. DEFAULT. ")
  f2.add_argument('-f', '--force', const=False, dest="update", action="store_const", help="Force to regenerate all files. ")

  f3 = flags.add_mutually_exclusive_group()
  f3.add_argument('-n', '--nice', type=int, default=1, help="Assign the worker processes the given niceness. ")
  f3.add_argument('-H', '--high', const=0, dest="nice", action="store_const", help="Generate files using the same priority as the main process. ")

  f4 = flags.add_mutually_exclusive_group()
  f4.add_argument('-v', '--verbose', '--simulate', const=True, default=False, action="store_const", help="Dump commands for generation to STDOUT instead of running them. Implies --quiet. ")
  f4.add_argument('-q', '--quiet', const=True, default=False, action="store_const", help="Do not write log messages to STDOUT while generating files. ")
  f4.add_argument('-m', '--find-modules', const=True, default=False, action="store_const", help="Find modules to generate and dump them to STDOUT. Implies --skip-implies, --quiet. Incompatible with --localpaths and --alltex. ")

  whattogen = parser.add_argument_group("What to generate")

  if add_types:

    whattogen.add_argument('--sms', action="store_const", const=True, default=False, help="generate sms files")
    whattogen.add_argument('--omdoc', action="store_const", const=True, default=False, help="generate omdoc files, implies --sms, --alltex, --localpaths")
    whattogen.add_argument('--pdf', action="store_const", const=True, default=False, help="generate pdf files, implies --sms, --alltex, --localpaths")
    
    whattogen.add_argument('--alltex', action="store_const", const=True, default=False, help="Generate all.tex files")
    whattogen.add_argument('--localpaths', action="store_const", const=True, default=False, help="Generate localpaths.tex files")

    whattogen.add_argument('--list', action="store_const", const=True, default=False, help="Lists all modules which exist in the given paths. If enabled, --sms --omdoc and --pdf are ignored. ")

    parser.add_argument('--pdf-add-begin-document', action="store_const", const=True, default=False, help="add \\begin{document} to LaTeX sources when generating pdfs. Backward compatibility for issue #82")

  whattogen.add_argument('--skip-implies', action="store_const", const=True, default=False, help="Generate only what is requested explicitly. Might fail if some files are missing. ")

  wheretogen = parser.add_argument_group("Where to generate")
  wheretogen.add_argument('-d', '--recursion-depth', type=int, default=-1, help="Recursion depth for paths and repositories. ")
  
  wheretogen = wheretogen.add_mutually_exclusive_group()
  wheretogen.add_argument('pathspec', metavar="PATH_OR_REPOSITORY", nargs='*', default=[], help="A list of paths or repositories to generate things in. ")
  wheretogen.add_argument('--all', "-a", default=False, const=True, action="store_const", help="generates files for all repositories")  

  return parser

# the root of lmh
lmh_root = util.lmh_root()

# The special files
special_files = {"all.tex":True, "localpaths.tex": True}

def needsPreamble(file):
  # echsk if we need to add the premable
  return re.search(r"\\begin(\w)*{document}", util.get_file(file)) == None 

def locate_module(path, git_root):
  # locates a single module if it exists

  path = os.path.abspath(path)

  if git_root == None:
    print "Skipping "+path+", not in a valid git repository. "

  if not path.endswith(".tex") or os.path.basename(path) in special_files or not util.effectively_readable(path):
    return []

  # you can use any directory, but if it is in the localmh directory, 
  # it also has to be within MathHub
  if path.startswith(os.path.abspath(util.lmh_root())) and not path.startswith(os.path.abspath(util.lmh_root()+"/MathHub")):
    return []

  basepth = path[:-4]


  omdocpath = basepth+".omdoc"
  omdoclog = basepth+".ltxlog"
  pdfpath = basepth+".pdf"
  pdflog = basepth+".pdflog"
  smspath = basepth+".sms"
  

  f = {
    "type": "file", 
    "mod": os.path.basename(basepth), 
    "file": path, 

    "repo": git_root, 
    "repo_name": os.path.relpath(git_root, util.lmh_root()+"/MathHub"), 

    "path": os.path.dirname(path), 
    "file_time": os.path.getmtime(path), 
    "file_root": git_root,

    "omdoc": omdocpath if os.path.isfile(omdocpath) else None, 
    "omdoc_path": omdocpath, 
    "omdoc_time": os.path.getmtime(omdocpath) if os.path.isfile(omdocpath) else 0, 
    "omdoc_log": omdoclog,
    "pdf": pdfpath if os.path.isfile(pdfpath) else None, 
    "pdf_path": pdfpath, 
    "pdf_time": os.path.getmtime(pdfpath) if os.path.isfile(pdfpath) else 0, 
    "pdf_log": pdflog, 
    "sms": smspath, 
    "sms_time": os.path.getmtime(smspath) if os.path.isfile(smspath) else 0, 
  }

  if needsPreamble(path):
    f["file_pre"] = git_root + "/lib/pre.tex"
    f["file_post"] = git_root + "/lib/post.tex"
  else:
    f["file_pre"] = None
    f["file_post"] = None

  return [f]


def locate_modules(path, depth=-1):
  # locates the submodules

  # you can use any directory, but if it is in the localmh directory, 
  # it also has to be within MathHub
  if path.startswith(os.path.abspath(util.lmh_root())) and not path.startswith(os.path.abspath(util.lmh_root()+"/MathHub")):
    return []

  # TODO: Implement per-directory config files
  modules = []

  if os.path.relpath(util.lmh_root() + "/MathHub/", path) == "../..":
    path = path + "/source"

  path = os.path.abspath(path)
  try:
    git_root = util.git_root_dir(path)
  except:
    git_root = None

  if os.path.isfile(path):
    return locate_module(path, git_root)

  if not os.path.isdir(path):
    sys.stderr.write('Can not find directory: '+path)
    return []

  # find all the files and folders
  objects = [os.path.abspath(path + "/" + f) for f in os.listdir(path)]
  files = filter(lambda f:os.path.isfile(f), objects)
  folders = filter(lambda f:os.path.isdir(f), objects)

  modules = util.reduce([locate_module(file, git_root) for file in files])

  if len(modules) > 0:
    youngest = max(map(lambda x : x["file_time"], modules))

    localpathstex = path + "/localpaths.tex"
    alltexpath = path + "/all.tex"

    # add localpaths.tex, all.tex
    # prepend this to the modules
    # so we can generate it before we
    # generate all the other files

    pre = None, 
    post = None

    for m in modules:
      if m["file_pre"] != None:
        pre = m["file_pre"]
        post = m["file_post"]

    modules[:0] = [{
      "type": "folder", 
      "path": path, 
      
      "modules": [m["mod"] for m in modules], 

      "repo": git_root, 
      "repo_name": os.path.relpath(git_root, util.lmh_root()+"/MathHub"), 
      "youngest": youngest, 

      "alltex": alltexpath if os.path.isfile(alltexpath) else None, 
      "alltex_path": alltexpath, 
      "alltex_time": os.path.getmtime(alltexpath) if os.path.isfile(alltexpath) else 0,

      "localpaths": localpathstex if os.path.isfile(localpathstex) else None, 
      "localpaths_path": localpathstex, 
      "localpaths_time": os.path.getmtime(localpathstex) if os.path.isfile(localpathstex) else 0,

      "file_pre": pre, 
      "file_post": post
    }]

  # go into subdirectories if needed
  if depth != 0:
    modules.extend(util.reduce([locate_modules(folder, depth - 1) for folder in folders]))

  return modules

def resolve_pathspec(args):
  # Resolves the path specification given by the arguments

  if(len(args.pathspec) == 0):
    if args.all:
      # generate everywhere
      args.pathspec = ["*/*"]
    else:
      # generate in the current directory only
      args.pathspec = ["."]

  # is this path a repository
  is_repo = lambda rep: os.path.relpath(util.lmh_root() + "/MathHub/", rep) == "../.."

  # expand path specification
  def expandpathspec(ps):
    repomatches = filter(is_repo, glob.glob(util.lmh_root() + "/MathHub/" + ps))
    if len(repomatches) != 0:
      return repomatches
    else:
      return glob.glob(ps)

  paths = util.reduce([expandpathspec(ps) for ps in args.pathspec])
  modules = util.reduce([locate_modules(path, depth=args.recursion_depth) for path in paths])

  return modules

def do(args):
  if args.nice != 0:
    # set niceness
    util.setnice(args.nice)

  if args.verbose:
    args.quiet = True

  if args.find_modules:
    args.skip_implies = True
    args.quiet = True

  if not args.pdf and not args.omdoc and not args.sms and not args.list and not args.localpaths and not args.alltex:
    if not args.quiet:
      print "Nothing to do ..."
    sys.exit(0)

  # Find all the modules
  try:
    if not args.quiet:
      print "Checking modules ..."
    modules = resolve_pathspec(args)
    if not args.quiet:
      print "Found", len(modules), "paths to work on. "
  except KeyboardInterrupt:
    print "<<KeyboardInterrupt>>"
    sys.exit(1)

  # if we just need to list modules
  if args.list:
    for m in modules:
      if m["type"] == "file":
        print "./"+os.path.relpath(m["file"], "./")
    return

  # Check what we need to do
  if (args.pdf or args.omdoc) and not args.skip_implies:
    args.sms = True
    args.localpaths = True
    args.alltex = True

  if args.sms:
    if not gen_sms(modules, args.update, args.verbose, args.quiet, args.workers, args.nice, args.find_modules):
      print "SMS: Generation aborted prematurely, skipping further generation. "
      sys.exit(1)

  if args.localpaths and not args.find_modules:
    if not gen_localpaths(modules, args.update, args.verbose, args.quiet, args.workers, args.nice):
      print "LOCALPATHS: Generation aborted prematurely, skipping further generation. "
      sys.exit(1)

  if args.alltex and not args.find_modules:
    if not gen_alltex(modules, args.update, args.verbose, args.quiet, args.workers, args.nice):
      print "ALLTEX: Generation aborted prematurely, skipping further generation. "
      sys.exit(1)

  if args.omdoc:
    if not gen_omdoc(modules, args.update, args.verbose, args.quiet, args.workers, args.nice, args.find_modules):
      print "OMDOC: Generation aborted prematurely, skipping further generation. "
      sys.exit(1)

  if args.pdf:
    if not gen_pdf(modules, args.update, args.verbose, args.quiet, args.workers, args.nice, args.pdf_add_begin_document, args.find_modules):
      print "PDF: Generation aborted prematurely, skipping further generation. "
      sys.exit(1)
