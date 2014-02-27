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
import argparse
import datetime
import functools
import ConfigParser
import multiprocessing

from string import Template
from subprocess import call
from subprocess import Popen
from subprocess import PIPE

from lmh import agg
from lmh import util

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Generation tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="gen"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='updates generated content')
  add_parser_args(parser_status)

def add_parser_args(parser):

  flags = parser.add_argument_group("Generation options")

  f1 = flags.add_mutually_exclusive_group()
  f1.add_argument('-w', '--workers',  metavar='number', default=8, type=int, help='number of worker processes to use')
  f1.add_argument('-s', '--single',  action="store_const", dest="workers", const=1, help='Use only a single process. Shortcut for -w 1')

  f2 = flags.add_mutually_exclusive_group()
  f2.add_argument('-u', '--update', const=True, default=False, action="store_const", help="Only generate files which have been changed. Experimental. ")
  f2.add_argument('-f', '--force', const=False, dest="update", action="store_const", help="Force to regenerate all files. DEFAULT. ")

  f3 = flags.add_mutually_exclusive_group()
  f3.add_argument('-n', '--nice', type=int, default=1, help="Assign the worker processes the given niceness. ")
  f3.add_argument('-H', '--high', const=0, dest="nice", action="store_const", help="Generate files using the same priority as the main process. ")

  f4 = flags.add_mutually_exclusive_group()
  f4.add_argument('-v', '--verbose', '--simulate', const=True, default=False, action="store_const", help="Dump commands for generation to STDOUT instead of running them. ")
  f4.add_argument('-q', '--quiet', const=True, default=False, action="store_const", help="Do not write out log messages to STDOUT while generating files. ")


  whattogen = parser.add_argument_group("What to generate")

  whattogen.add_argument('--sms', action="store_const", const=True, default=False, help="generate sms files")
  whattogen.add_argument('--omdoc', action="store_const", const=True, default=False, help="generate omdoc files, implies --sms. ")
  whattogen.add_argument('--pdf', action="store_const", const=True, default=False, help="generate pdf files, implies --sms. ")
  whattogen.add_argument('--list', action="store_const", const=True, default=False, help="dump all found modules to stdout. If enabled, --sms --omdoc and --pdf are ignored. ")

  wheretogen = parser.add_argument_group("Where to generate")
  wheretogen.add_argument('-d', '--recursion-depth', type=int, default=-1, help="Recursion depth for paths and repositories. ")
  
  wheretogen = wheretogen.add_mutually_exclusive_group()
  wheretogen.add_argument('pathspec', metavar="PATH_OR_REPOSITORY", nargs='*', default=[], help="A list of paths or repositories to generate things in. ")
  wheretogen.add_argument('--all', "-a", default=False, const=True, action="store_const", help="generates files for all repositories")  

# the root of lmh
lmh_root = util.lmh_root()

# The special files
special_files = {"all.tex":True, "localpaths.tex": True}

# for gen_sms
ignore = re.compile(r'\\verb')
regStrings = [r'\\(guse|gadopt|symdef|abbrdef|symvariant|keydef|listkeydef|importmodule|gimport|adoptmodule|importmhmodule|adoptmhmodule)', r'\\begin{(module|importmodulevia)}', r'\\end{(module|importmodulevia)}']
regs = map(re.compile, regStrings)
# templates
all_pathstpl = Template(util.get_template("localpaths.tpl"))
all_modtpl = Template(util.get_template("alltex_mod.tpl"))
all_textpl = Template(util.get_template("alltex_struct.tpl"))

# Paths for latexml
latexmlc = lmh_root+"/ext/LaTeXML/bin/latexmlc"
pdflatex = util.which("pdflatex")
latexmlstydir = lmh_root+"/ext/sTeX/LaTeXML/lib/LaTeXML/texmf"
stydir = lmh_root+"/sty"

# pdf inputs
def genTEXInputs():
  res = ".:"+stydir+":";
  for (root, files, dirs) in os.walk(util.stexstydir):
    res += root+":"
  for (root, files, dirs) in os.walk(util.latexmlstydir):
    res += root+":"
  return res

TEXINPUTS = genTEXInputs()

def needsPreamble(file):
  # echsk if we need to add the premable
  return re.search(r"\\begin(\w)*{document}", util.get_file(file)) == None 

# For Error parsing
errorMsg = re.compile("Error:(.*)")
fatalMsg = re.compile("Fatal:(.*)")

def parseLateXMLOutput(file):
  mod = file[:-4]
  logfile = mod+".ltxlog"
  try:

    for idx, line in enumerate(open(logfile)):
      m = errorMsg.match(line)
      if m:
        agg.log_error(["compile", "omdoc", "error"], file, m.group(1))
      m = fatalMsg.match(line)
      if m:
        agg.log_error(["compile", "omdoc", "error"], file, m.group(1))
  except:
    print "ERROR: Failed to open logfile '"+logfile+"'. "
    print "Make sure latexmlc is working properly. "

# ==============
# SMS
# ==============

def gen_sms(modules, update, verbose, quiet, workers, nice):
  # general sms generation
  jobs = []
  for mod in modules:
    if mod["type"] == "file":
      if not update or mod["file_time"] > mod["sms_time"]:
        jobs.append(sms_gen_job(mod))
  try:
    if verbose:
      print "# SMS Generation"
      for job in jobs:
        sms_gen_dump(job)
    else:
      for job in jobs:
        sms_gen_do(job, quiet)
  except Exception as e:
    print "SMS generation failed. "
    print e
    return False

  return True

def sms_gen_job(module):
  # store parameters for sms job generation
  return (module["file"], module["sms"])

def sms_gen_do(job, quiet, worker=None, cwd="."):
  # run a sms generation job 
  (input, out) = job

  if not quiet:
    print "SMS: Generating ", os.path.relpath(out, cwd)

  output = open(out, "w")

  for line in open(input):
    idx = line.find("%")
    if idx == -1:
      line = line[0:idx];

    if ignore.search(line):
      continue

    for reg in regs:
      if reg.search(line):
        text = line.strip()+"%\n"
        output.write(text)
        break
  
  output.close()

  if not quiet:
    print "SMS: Generated ", os.path.relpath(out, cwd)

def sms_gen_dump(job):
  # dump an sms generation jump to STDOUT
  (input, out) = job

  print "# generate ", out
  print "echo -n '' > "+util.shellquote(output)

  for line in open(input):
    idx = line.find("%")
    if idx == -1:
      line = line[0:idx];

    if ignore.search(line):
      continue

    for reg in regs:
      if reg.search(line):
        text = line.strip()+"%\n"
        print "echo -n "+util.shellquote(text)+" >> "+util.shellquote(output)
        break

# ==============
# localpaths
# ==============

def gen_localpaths(modules, update, verbose, quiet, workers, nice):
  # general all.tex localpaths.tex generation
  jobs = []
  for mod in modules:
    if mod["type"] == "folder":
      if not update or mod["youngest"] > mod["localpaths_time"]:
        jobs.append(localpaths_gen_job(mod))
  try:
    if verbose:
      print "# localpaths.tex Generation"
      for job in jobs:
        localpaths_gen_dump(job)
    else:
      for job in jobs:
        localpaths_gen_do(job, quiet)
  except Exception as e:
    print "LOCALPATHS generation failed. "
    print e
    return False

  return True

def localpaths_gen_job(module):
  # store parameters for locapath.tex job generation
  return (module["localpaths"], module["repo"], module["repo_name"])
  

def localpaths_gen_do(job, quiet, worker=None, cwd="."):
  # run a localpaths.tex job 
  (dest, repo, repo_name) = job

  if not quiet:
    print "LOCALPATHS: Generating "+dest

  text = all_pathstpl.substitute(mathhub=lmh_root, repo=repo, repo_name=repo_name)

  output = open(dest, "w")
  output.write(text)
  output.close()

  if not quiet:
    print "LOCALPATHS: Generated "+dest

def localpaths_gen_dump(job):
  # dump an localpaths.tex generation jump to STDOUT
  (dest, repo, repo_name) = job
  
  print "# generate", dest

  text = all_pathstpl.substitute(mathhub=lmh_root, repo=repo, repo_name=repo_name)
  
  print "echo -n " + util.shellquote(text)+ " > "+util.shellquote(dest)

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
    "omdoc_time": os.path.getmtime(omdocpath) if os.path.isfile(omdocpath) else 0, 
    "omdoc_log": omdoclog,
    "pdf": pdfpath if os.path.isfile(pdfpath) else None, 
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

    modules[:0] = [{
      "type": "folder", 
      "path": path, 
      "repo": git_root, 
      "repo_name": os.path.relpath(git_root, util.lmh_root()+"/MathHub"), 
      "youngest": youngest, 
      "alltex": alltexpath if os.path.isfile(alltexpath) else None, 
      "alltex_time": os.path.getmtime(alltexpath) if os.path.isfile(alltexpath) else 0,
      "localpaths": localpathstex if os.path.isfile(localpathstex) else None, 
      "localpaths_time": os.path.getmtime(localpathstex) if os.path.isfile(localpathstex) else 0,
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

  if not args.pdf and not args.omdoc and not args.sms and not args.list:
    if not args.quiet:
      print "Nothing to do ..."
    sys.exit(0)

  # Find all the modules
  try:
    if not args.quiet:
      print "Locating modules ..."
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
  if args.pdf or args.omdoc:
    args.sms = True

  if args.sms:
    if not gen_sms(modules, args.update, args.verbose, args.quiet, args.workers, args.nice):
      print "SMS: Generation aborted prematurely, skipping further generation. "
      sys.exit(1)

  if args.omdoc or args.pdf:
    # force generate localpaths.tex and all.tex

    if not gen_localpaths(modules, args.update, args.verbose, args.quiet, args.workers, args.nice):
      print "LOCALPATHS: Generation aborted prematurely, skipping further generation. "
      sys.exit(1)

    if not gen_alltex(modules, args.update, args.verbose, args.quiet, args.workers, args.nice):
      print "ALLTEX: Generation aborted prematurely, skipping further generation. "
      sys.exit(1)

  if args.omdoc:
    if not gen_omdoc(modules, args.update, args.verbose, args.quiet, args.workers, args.nice):
      print "OMDOC: Generation aborted prematurely, skipping further generation. "
      sys.exit(1)
  if args.pdf:
    #gen_pdf(modules, args.update, args.verbose, args.quiet, args.workers, args.nice)
    pass