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
import os.path
import sys
import re
import glob
import time
import signal
import shutil
import datetime
import functools
import traceback

from lmh.lib import reduce
from lmh.lib.io import std, err, read_file, effectively_readable
from lmh.lib.env import install_dir
from lmh.lib.git import root_dir


# The special files
special_files = {"all.tex":True, "localpaths.tex": True}

def needsPreamble(file):
  # echsk if we need to add the premable
  return re.search(r"\\begin(\w)*{document}", read_file(file)) == None 

def locate_module(path, git_root):
  # locates a single module if it exists

  path = os.path.abspath(path)

  if git_root == None:
    std("Skipping "+path+", not in a valid git repository. ")

  if not path.endswith(".tex") or os.path.basename(path) in special_files or not effectively_readable(path):
    return []

  # you can use any directory, but if it is in the localmh directory, 
  # it also has to be within MathHub
  if path.startswith(os.path.abspath(install_dir)) and not path.startswith(os.path.abspath(install_dir+"/MathHub")):
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
    "repo_name": os.path.relpath(git_root, install_dir+"/MathHub"), 

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
  if path.startswith(os.path.abspath(install_dir)) and not path.startswith(os.path.abspath(install_dir+"/MathHub")):
    return []

  # TODO: Implement per-directory config files
  modules = []

  if os.path.relpath(install_dir + "/MathHub/", path) == "../..":
    path = path + "/source"

  if not os.path.isdir(path):
    return []

  if not os.path.isdir(path):
    return []

  path = os.path.abspath(path)
  try:
    git_root = root_dir(path)
  except:
    git_root = None

  if os.path.isfile(path):
    return locate_module(path, git_root)

  if not os.path.isdir(path):
    err('Can not find directory: '+path)
    return []

  # find all the files and folders
  objects = [os.path.abspath(path + "/" + f) for f in os.listdir(path)]
  files = filter(lambda f:os.path.isfile(f), objects)
  folders = filter(lambda f:os.path.isdir(f), objects)

  modules = reduce([locate_module(file, git_root) for file in files])

  if len(modules) > 0:
    youngest = max(map(lambda x : x["file_time"], modules))

    localpathstex = path + "/localpaths.tex"
    alltexpath = path + "/all.tex"

    # add localpaths.tex, all.tex
    # prepend this to the modules
    # so we can generate it before we
    # generate all the other files

    pre = None
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
      "repo_name": os.path.relpath(git_root, install_dir+"/MathHub"), 
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
    modules.extend(reduce([locate_modules(folder, depth - 1) for folder in folders]))

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
  is_repo = lambda rep: os.path.relpath(install_dir + "/MathHub/", rep) == "../.."

  # expand path specification
  def expandpathspec(ps):
    repomatches = filter(is_repo, glob.glob(install_dir + "/MathHub/" + ps))
    if len(repomatches) != 0:
      return repomatches
    else:
      return glob.glob(ps)

  paths = reduce([expandpathspec(ps) for ps in args.pathspec])
  modules = reduce([locate_modules(path, depth=args.recursion_depth) for path in paths])

  return modules