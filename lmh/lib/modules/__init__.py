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

import time


from lmh.lib import reduce, clean_list, remove_doubles
from lmh.lib.io import std, err, read_file, effectively_readable
from lmh.lib.env import install_dir, data_dir
from lmh.lib.git import root_dir

from lmh.lib.repos.local import find_repo_subdirs


# Hardcoded folder exclude list.
# really ugly workaround for #223
folder_exclude_list = ["tikz"]

def needsPreamble(file):
    """
        Checks if a file needs a preamble.

        @param file File to check.
    """

    # check if we need to add the premable
    return re.search(r"\\begin(\w)*{document}", read_file(file)) == None

def needsRegen(file, update_file):
    """
        Checks if a file needs to be regenerated.

        @param file Name of file to check.
        @param update_file File toc heck if newer.
    """

    # Get the time of the input file.
    # This is cached to be fast.
    if file in needsRegen.cache:
        filetime = needsRegen.cache[file]
    else:
        filetime = os.stat(file).st_atime
        needsRegen.cache[file] = filetime

    # Get the time of the output file to be updated
    # if it doesn't exist, we need to update anyways
    # This is cached to be fast.
    if update_file in needsRegen.cache:
        updatetime = needsRegen.cache[update_file]
    else:
        if os.path.isfile(update_file):
            updatetime = os.stat(update_file).st_atime
        else:
            updatetime = 0
        needsRegen.cache[updatetime] = updatetime

    # If the filetime is newer (bigger)
    # We need to update.
    return filetime > updatetime
needsRegen.cache = {}


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
        # what it is.
        "type": "file",
        # "original_selector": org_selected,
        "mod": os.path.basename(basepth),

        # Where it is
        "local_uri": uri,
        "file": path,
        "path": os.path.dirname(path),

        # The Repo
        "repo": git_root,
        "repo_name": repo_rel,

        # sms
        "sms": smspath,

        # Omdoc
        "omdoc": omdocpath,
        "omdoc_log": omdoclog,

        # xhtml
        "xhtml": xhtmlpath,

        # pdf
        "pdf": pdfpath,
        "pdf_log": pdflog
    }

    # We always add pre/postamble here.
    # But we do not say if we need it.

    # Find the extension.
    ext = re.search(r"(\.(.*)\.tex|.tex)$", f["file"]).group(1)

    # Load the correct preamble.
    f["file_pre"] = os.path.join(git_root, "lib", "pre"+ext)

    # Load the correct postable - this will problaly have to fallback to the default
    f["file_post"] = os.path.join(git_root, "lib", "post"+ext)

    return [f]


def locate_preamables(mods):
    # locate preambles for a given repository

    # TODO: We want to make this MUCH MUCH more efficient.

    res = []
    for y in mods:

        # only use the folders.
        if y["type"] != "folder":
            continue

        # find the library dir.
        libdir = os.path.join(y["repo"], "lib")

        if os.path.isdir(libdir):
            try:
                the_mods = y["modules"]
            except:
                continue # We have nothing to generate here, because we did not find anything

            # locate all the preambles.
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

                # Remove doubles
                langmods = remove_doubles(langmods)

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
                the_mods = remove_doubles(the_mods)
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
    #
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

    # HACK out the tikz directories.
    folders = filter(lambda f:not f.split("/")[-1] in folder_exclude_list, folders)

    modules = reduce([locate_module(file, git_root) for file in files])

    if len(modules) > 0:
        #
        # This line will be slow
        #
        youngest = max(map(lambda x : os.path.getmtime(x["path"]), modules))

        localpathstex = path + "/localpaths.tex"
        alltexpath = path + "/all.tex"

        # add localpaths.tex, all.tex
        # prepend this to the modules
        # so we can generate it before we
        # generate all the other files

        # We always need the folder first.
        # TODO: More stuff

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

            "file_pre": m["file_pre"],
            "file_post": m["file_post"]
        }]

        if find_files == False:
            modules = [modules[0]]

    # go into subdirectories if needed
    if depth != 0:
        modules.extend(reduce([locate_modules(folder, depth - 1, find_files = find_files) for folder in folders]))

    return modules

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
    #TODO: Use the pre-built functions for this.
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
