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


from lmh.lib import reduce, clean_list, f7
from lmh.lib.io import std, err, read_file, effectively_readable
from lmh.lib.env import install_dir, data_dir
from lmh.lib.git import root_dir

from lmh.lib.repos.local import find_repo_subdirs

def needsPreamble(file):
    # check if we need to add the premable
    return re.search(r"\\begin(\w)*{document}", read_file(file)) == None

def locate_module(path, git_root):
    # locates a single module if it exists

    path = os.path.abspath(path)

    if git_root == None:
        std("Skipping "+path+", not in a valid git repository. ")

    org_selected = path

    if not path.endswith(".tex"):
        path = os.path.splitext(path)[0] + ".tex" # We go to the tex file

    if not effectively_readable(path):
        return []

    # you can use any directory, but if it is in the localmh directory,
    # it also has to be within MathHub
    if path.startswith(os.path.abspath(install_dir)) and not path.startswith(os.path.abspath(data_dir)):
        return []

    basepth = path[:-4]

    omdocpath = basepth+".omdoc"
    omdoclog = basepth+".ltxlog"
    pdfpath = basepth+".pdf"

    pdflog = basepth+".pdflog"
    smspath = basepth+".sms"

    uri = os.path.relpath(omdocpath, os.path.join(git_root, "source"))
    repo_rel = os.path.relpath(git_root, data_dir)
    xhtmlpath = os.path.join(git_root, "export", "planetary", "content", "http..mathhub.info", repo_rel, uri+"/")

    f = {
        "type": "file",
        "original_selector": org_selected,
        "mod": os.path.basename(basepth),

        "local_uri": uri,
        "file": path,

        "repo": git_root,
        "repo_name": repo_rel,

        "path": os.path.dirname(path),
        "file_time": os.path.getmtime(path),
        "file_root": git_root,

        "omdoc": omdocpath if os.path.isfile(omdocpath) else None,
        "omdoc_path": omdocpath,
        "omdoc_time": os.path.getmtime(omdocpath) if os.path.isfile(omdocpath) else 0,
        "omdoc_log": omdoclog,
        "omdoc_log_time": os.path.getmtime(omdoclog) if os.path.isfile(omdoclog) else 0,

        "xhtml": xhtmlpath,
        "pdf": pdfpath if os.path.isfile(pdfpath) else None,
        "pdf_path": pdfpath,
        "pdf_time": os.path.getmtime(pdfpath) if os.path.isfile(pdfpath) else 0,
        "pdf_log": pdflog,
        "pdf_log_time": os.path.getmtime(pdflog) if os.path.isfile(pdflog) else 0,
        "sms": smspath,
        "sms_time": os.path.getmtime(smspath) if os.path.isfile(smspath) else 0,
    }

    if needsPreamble(path):

        # Find the extension.
        ext = re.search(r"(\.(.*)\.tex|.tex)$", f["file"]).group(1)

        # Load the correct preamble.
        f["file_pre"] = os.path.join(git_root, "lib", "pre"+ext)
        f["file_pre"] = f["file_pre"] if os.path.isfile(f["file_pre"]) else os.path.join(git_root, "lib", "pre.tex")

        # Load the correct postable - this will problaly have to fallback to the default
        f["file_post"] = os.path.join(git_root, "lib", "post"+ext)
        f["file_post"] = f["file_post"] if os.path.isfile(f["file_post"]) else os.path.join(git_root, "lib", "post.tex")
    else:
        f["file_pre"] = None
        f["file_post"] = None
    return [f]

def locate_preamables(mods):
    # locate preambles for a given repository


    res = []
    for y in mods:
        if y["type"] != "folder":
            continue
        libdir = os.path.join(y["repo"], "lib")
        if os.path.isdir(libdir):
            try:
                the_mods = y["modules"]
            except:
                continue # We have nothing to generate here, because we did not find anything
            for pre_file in glob.glob(libdir+"/pre.*.tex"):
                # The alltex file
                alltex_file = re.sub(r"^(.*)pre\.(.*)\.tex$", r"all.\2.tex", pre_file)
                alltex_file = os.path.join(y["path"], alltex_file)

                # The language and its mods
                language = "."+re.search(r"^(.*)pre\.(.*)\.tex$", pre_file).group(2)
                langmods = filter(lambda x:x.endswith(language), the_mods)

                # We need to find the youngest
                youngest = [os.path.join(y["path"], k+".tex") for k in langmods]
                if youngest == []:
                    youngest = float("inf")
                else:
                    youngest = max([os.path.getmtime(fn) if os.path.isfile(fn) else 0 for fn in youngest])
                # We dont want the others anymore.
                [the_mods.remove(l) for l in langmods]

                # Rmeovee doubles
                langmods = f7(langmods)

                # Now make the thing
                res.append({
                    "type": "alltex",
                    "language": language[1:],
                    "all_file": alltex_file,
                    "all_time": os.path.getmtime(alltex_file) if os.path.isfile(alltex_file) else 0,
                    "pre_file": pre_file,
                    "post_file": os.path.join(libdir, "post.tex"),
                    "youngest": youngest,
                    "mods": langmods
                })
            # Now take care of the others, if there are any.
            if len(the_mods) > 0:
                the_mods = f7(the_mods)
                alltex_file = os.path.join(y["path"], "all.tex")
                # Find the youngest one
                youngest = [os.path.join(y["path"], k+".tex") for k in the_mods]
                youngest = max([os.path.getmtime(fn) if os.path.isfile(fn) else 0 for fn in youngest])

                # Now make the thing
                res.append({
                    "type": "alltex",
                    "language": None,
                    "all_file": alltex_file,
                    "all_time": os.path.getmtime(alltex_file) if os.path.isfile(alltex_file) else 0,
                    "pre_file": os.path.join(libdir, "pre.tex"),
                    "post_file": os.path.join(libdir, "post.tex"),
                    "youngest": youngest,
                    "mods": the_mods
                })

    return res

def locate_modules(path, depth=-1, find_files = True):
    # locates the submodules

    # you can use any directory, but if it is in the localmh directory,
    # it also has to be within MathHub
    if path.startswith(os.path.abspath(install_dir)) and not path.startswith(os.path.abspath(data_dir)):
        return []

    # TODO: Implement per-directory config files here
    modules = []

    if os.path.relpath(data_dir, path) == "../..":
        path = path + "/source"

    path = os.path.abspath(path)
    try:
        git_root = root_dir(path)
    except:
        git_root = None

    if os.path.isfile(path):
        return locate_module(path, git_root)

    if not os.path.isdir(path):
        # fail silently for non-existing directories
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
            "repo_name": os.path.relpath(git_root, data_dir),
            "youngest": youngest,

            "localpaths": localpathstex if os.path.isfile(localpathstex) else None,
            "localpaths_path": localpathstex,
            "localpaths_time": os.path.getmtime(localpathstex) if os.path.isfile(localpathstex) else 0,

            "file_pre": pre,
            "file_post": post
        }]

        if find_files == False:
            modules = [modules[0]]

    # go into subdirectories if needed
    if depth != 0:
        modules.extend(reduce([locate_modules(folder, depth - 1, find_files = find_files) for folder in folders]))

    return modules

def locate_modfiles(dir = "."):
    files = filter(lambda x:x["type"] == "file", locate_modules(dir))
    return filter(lambda x:needsPreamble(x["file"]), files)

def makeIndex(dir = "."):
    index = {}

    files = filter(lambda x:x["type"] == "file", locate_modules(dir))

    for file in files:
        fname = file["mod"]+".tex"
        if not fname in index.keys():
            index[fname] = []
        index[fname].append(file["path"]+"/" + fname)

    return index

def resolve_pathspec(args, allow_files = True, allow_local = True, find_files = True, find_alltex = True, recursion_depth=None):
    # Resolves the path specification given by the arguments

    """
      Resolving of paths:

      1) If --all is given, assume **only** data_dir as argument.
      2) If no arguments are given, assume **only** . as argument

      If no arguments are given, assume "." as argument.



      Each argument s is treatde as glob. Then:

      1) Do a glob.glob($PATHSPEC). Then for each $GLOB:
        A) Check if a file $GLOB.tex exists => treat as module
        B) Check if a directory $GLOB exists
          B.1) Are we inside a repository => treat as a normal repo
          B.2) are we outside of a repository => search for all repositories contained in it
      2) If that gives no results, do a glob.glob($PATHSPEC) realtive to data_dir and repeat 1B)
    """

    # We support both JSON and namespace notation
    if hasattr(args, "all"):
        args_all = args.all
    else:
        args_all = args["all"]

    if hasattr(args, "pathspec"):
        args_pathspec = args.pathspec
    else:
        args_pathspec = args["pathspec"]

    if hasattr(args, "recursion_depth"):
        args_recursion_depth = args.recursion_depth
    else:
        args_recursion_depth = args["recursion_depth"]

    # args_all is given => generate everywhere
    if args_all:
        args_pathspec = [data_dir]

    if recursion_depth == None:
        recursion_depth = args_recursion_depth

    # We do not have any arguments, use nothing at all.
    if(len(args_pathspec) == 0):
        args_pathspec = ["."]

    paths = []
    mods = []

    oldpwd = os.getcwd()

    # Are we a repository
    is_repo = lambda x:os.path.relpath(data_dir, x) == "../.."
    is_in_repo = lambda x:os.path.relpath(data_dir, x).startswith("../../")
    is_in_data = lambda x: not os.path.relpath(x, data_dir).startswith("..")

    for f in args_pathspec:
        # We did not do anything

        cont = True

        if allow_local:
            for gl in glob.glob(f):
                gl_abs = os.path.abspath(gl)
                # Is it a file => add to modules
                if allow_files and os.path.isfile(gl_abs):
                    if not is_in_data(gl_abs):
                        err("Warning: Path", gl_abs, "is not within the lmh data directory, ignoring. ")
                        cont = False
                    if not (gl_abs.endswith(".tex") or gl_abs.endswith(".omdoc") or gl_abs.endswith(".pdf")):
                        err("Warning: Path", gl_abs, "is not a valid file, ignoring. ")
                        cont = False
                    mods.append(gl_abs)
                    cont = False
                # Is it a directory => check if we are inside a module
                elif os.path.isdir(gl_abs):
                    # we are a repository
                    if is_repo(gl_abs) or is_in_repo(gl_abs):
                        paths.append(gl_abs)
                        cont = False
                    elif is_in_data(gl_abs):
                        # Find all the subdirectories which match
                        paths = paths + find_repo_subdirs(gl_abs)
                        cont = False
                    else:
                        err("Warning: Path", gl_abs, "is not within the lmh data directory, ignoring. ")
                        cont = False

        if not cont:
            continue

        os.chdir(data_dir)

        for gl in glob.glob(f):
            gl_abs = os.path.abspath(gl)
            if os.path.isdir(gl_abs):
                if is_repo(gl_abs) or is_in_repo(gl_abs):
                    paths.append(gl_abs)
                    didthings = True
                elif is_in_data(gl_abs):
                    didthings = True
                    # Find all the subdirectories which match
                    paths = paths + find_repo_subdirs(gl_abs)
                else:
                    err("Warning: Path", gl_abs, "is not within the lmh data directory, ignoring. ")
                    continue
            else:
                err("Warning: Pathspec", gl, "has no matches, ignoring. ")

        os.chdir(oldpwd)

    def thekey(item):
        if item["type"] == "folder":
            return item["path"]
        elif item["type"] == "file":
            return item["file"]
        else:
            return item

    modules = reduce([locate_modules(path, depth=recursion_depth, find_files = find_files) for path in paths])

    # Remove doubles
    modules = clean_list(modules, thekey)

    modules = modules + reduce([locate_module(f, root_dir(f)) for f in mods])

    if find_alltex:
        modules = modules + locate_preamables(modules)

    return modules
