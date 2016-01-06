import os
import glob
import json
import shutil

from lmh.lib.utils import reduce
from lmh.lib.io import find_files, std, err
from lmh.lib.dirs import data_dir

from lmh.lib.repos.local import match_repo, match_repos, calc_deps
from lmh.lib.repos.find_and_replace import find_cached

def movemod(source, dest, modules, no_depcrawl, simulate = False):
    """Moves modules from source to dest. """

    # change directory to MathHub root, makes paths easier
    if simulate:
        std("cd "+data_dir)
    else:
        os.chdir(data_dir)

    finds = []
    replaces = []

    # Match the repos
    source = match_repo(source, root=data_dir)
    dest = match_repo(dest, root=data_dir)

    if source == None:
        err("Source repository does not exist, make sure it is installed. ")
        return False
    if dest == None:
        err("Destination repository does not exist, make sure it is installed. ")
        return False

    if source == dest:
        err("Cannot move modules when source and destination are the same. ")
        return False

    # Store original source and destination
    osource = source
    odest = dest

    # Make a list of all the moved files.
    moved_files = []

    local_finds = []
    local_replaces = []

    def run_lmh_find_moved(find, replace):
        if simulate:
            # We will run it over dest only.
            std("lmh", "find", json.dumps(find), "--replace", json.dumps(replace), "--apply", odest)
        else:
            # Append it to to a list.
            local_finds.append(find)
            local_replaces.append(replace)

    for module in modules:

        dest = odest

        # Figure out the full path to the source
        srcpath = source + "/source/" +  module

        # Assemble source paths further
        srcargs = (source + "/" + module).split("/")
        srcapath = "\\/".join(srcargs[:-1])
        srcbpath = srcargs[-1]

        # Assemble all the commands
        oldcall = "\[" + srcapath + "\]\{"+srcbpath+"\}"
        oldcall_long = "\[(.*)repos=" + srcapath + "(.*)\]\{"+srcbpath+"\}"
        oldcall_local = "\{"+srcbpath+ "\}"
        newcall = "[" + dest + "]{"+srcbpath+"}"
        newcall_long = "[$g1" + dest + "$g2]{"+srcbpath+"}"

        dest += "/source/"

        # Move the files
        if simulate:
            std("mv "+srcpath + ".*.tex"+ " "+ dest + " 2>/dev/null || true")
            std("mv "+srcpath + ".tex"+ " "+ dest + " 2>/dev/null || true")
        else:
            try:
                shutil.move(srcpath + ".tex", dest)
                moved_files.append(os.path.join(dest, os.path.basename(srcpath + ".tex")))
            except:
                pass

            for pat in glob.glob(srcpath + ".*.tex"):
                # try to move the file if it exists
                try:
                    shutil.move(pat, dest)
                    moved_files.append(os.path.join(dest, os.path.basename(pat)))
                except:
                    pass


        def run_lmh_find(find, replace):
            finds.append(find)
            replaces.append(replace)

        # Run all the commands
        m = "("+"|".join(["gimport", "guse", "gadopt"])+")"
        run_lmh_find(r'\\'+m+oldcall, '\\$g0'+newcall)
        run_lmh_find(r'\\'+m+oldcall_local, '\\$g0'+newcall)

        m = "("+ "|".join(["importmhmodule", "usemhmodule", "adoptmhmodule", "usemhvocab"]) + ")"
        run_lmh_find(r'\\'+m+oldcall_long, '\\$g0'+newcall_long)
        run_lmh_find(r'\\'+m+oldcall_local, '\\$g0'+newcall_long)

        # For the moved files, repalce gimport, guse, gadpot
        run_lmh_find_moved(r"\\("+"|".join(["gimport", "guse", "gadopt"])+")\["+dest[-len("/source/")]+"\]\{(.*)\}", "\\$g1{$g2}")

    # Update the moved files.
    run_lmh_find_moved(r"\\("+"|".join(["gimport", "guse", "gadopt"])+")\{(((?!(?<=\{)("+"|".join(modules)+")\}).)*?)\}", "\\$g1{$g2}")

    # Make the repo paths absolute
    osource = match_repo(osource, abs=True)
    odest = match_repo(odest, abs=True)

    files = reduce([find_files(r, "tex")[0] for r in match_repos(data_dir, abs=True)])

    if simulate:
        for (f, r) in zip(finds, replaces):
            std("lmh find", json.dumps(f), "--replace", json.dumps(r), "--apply")

        if not no_depcrawl:
            calc_deps(False, dirname=osource)
            calc_deps(False, dirname=odest)

        return True

    else:
        std("updating paths in the following files: ")

        res1 = find_cached(files, finds, replace=replaces)
        res2 = find_cached(moved_files, local_finds, replace=local_replaces)

        if not no_depcrawl:
            res3 = calc_deps(True, osource)
            res4 = calc_deps(True, odest)
        else:
            res3 = True
            res4 = True

        return res1 and res2 and res3 and res4
