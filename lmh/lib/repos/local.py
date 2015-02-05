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
import re
import glob

from lmh.lib.env import install_dir, data_dir
from lmh.lib.io import term_colors, find_files, std, std_paged, err, write_file, read_file, read_file_lines
from lmh.lib.repos import find_dependencies
from lmh.lib.config import get_config
from lmh.lib.repos.remote import install


# Git imports
from lmh.lib.git import push as git_push
from lmh.lib.git import pull as git_pull
from lmh.lib.git import status_pipe as git_status
from lmh.lib.git import commit as git_commit
from lmh.lib.git import do as git_do
from lmh.lib.git import do_data as git_do_data
from lmh.lib.git import do_quiet, get_remote_status
from lmh.lib.git import is_tracked, is_repo

#
# Repo Matching
#

def is_repo_dir(path, existence = True):
    """Checks if a directory is a repo directory. """
    if existence and (not os.path.isdir(path)):
        return False
    try:
        if not (os.path.relpath(data_dir, os.path.abspath(path)) == "../.."):
            return False

        return is_repo(path)
    except Exception as e:
        err(e)
        return False

def is_in_data(path):
    """Checks if a directory is contained within the data directory. """
    try:
        return os.path.abspath(path).startswith(os.path.abspath(data_dir))
    except:
        return False

def is_in_repo(path):
    """Checks if a directory is contained inside of a repo. """
    try:
        if is_in_data(path):
            return os.path.relpath(data_dir, os.path.abspath(path)).startswith("../..")
        else:
            return False
    except:
        return False

def find_repo_subdirs(root):
    """Finds repository subdirectories of a directory. """

    res = []

    # if we are not a directory, do nothing.
    if not os.path.isdir(root):
        return res

    #Subdirectories
    for d in [name for name in os.listdir(root) if os.path.isdir(os.path.join(root, name))]:
        d = os.path.join(root, d)
        if is_repo_dir(d):
            res = res + [d]
        else:
            res = res + find_repo_subdirs(d)

    return res

def find_repo_dir(root):
    """Finds the repository belonging to a file or directory. """
    root = os.path.abspath(root)
    if is_repo_dir(root):
        return root
    if not is_in_repo(root):
        return False
    else:
        return find_repo_dir(os.path.join(root, ".."))

def match_repo(repo, root=os.getcwd(), abs=False):
    """Matches a single specefier to a repository. """

    # 1) Resolve to absolute path repo (via root)
    # 2) If it is (inside) a repository, return that repository
    # 3) If not, try to repeat 1) and 2) with root = data_dir
    # 4) If that fails, return None

    # make sure the root is absolute
    root = os.path.abspath(root)

    # If repo is empty, make sure we use the current directory.
    if repo == "":
        repo = os.getcwd()

    # try the full repo_path
    repo_path = os.path.join(root, repo)

    if is_repo_dir(repo_path) or is_in_repo(repo_path):
        # figure out the path to the repository root
        repo_path = find_repo_dir(repo_path)
        if not repo_path:
            return None
        if abs:
            # return the absolute path to the repo
            return repo_path
        else:
            # return just the repo name, determined by the relative name
            return os.path.relpath(repo_path, os.path.abspath(data_dir))
    elif not (root == os.path.abspath(data_dir)):
        #if the root is not already the data_dir, try that
        return match_repo(repo, root=data_dir, abs=abs)
    else:
        # nothing found
        return None


def match_repos(repos, root=os.getcwd(), abs=False):
    """Matches a list of specefiers to repositories. """

    # For each element do the following:
    # 1) Check if given directory exists relatively from current root.
    #       1a) If it is a repository or repository subdir, return that
    #        1b) If it is inside the data_dir, return all repo subdirectories
    # 2) If it does not exist, resolve it as glob.glob from install_dir
    # 3) For each of the found directories, run 1)

    # If repos is a string, turn it into an array
    if isinstance(repos, basestring):
        repos = [repos]

    repo_dirs = []
    globs = []

    # Try and find actual directories from root
    for r in repos:
        r_abs = os.path.abspath(os.path.join(root, r))
        if os.path.isdir(r_abs):
            # its a directory
            repo_dirs.append(r_abs)
        else:
            # Its not => treat as glob
            globs.append(r)
            # Try and reolsve th globs
    os.chdir(data_dir)
    for g in globs:
        repo_dirs.extend(glob.glob(g))

    rdirs = []

    for d in repo_dirs:
        m = match_repo(d)
        if m:
            rdirs.append(m)
        elif is_in_data(d):
            rdirs.extend(find_repo_subdirs(d))
        elif os.path.abspath(d) == os.path.abspath(install_dir):
            rdirs.extend(find_repo_subdirs(install_dir))
        else:
            err("Warning: Unable to parse ", d, " as a repository, falling back to --all. ")
            rdirs.extend(find_repo_subdirs(install_dir))

    # Remove doubles
    rdirs = sorted(set(rdirs))

    if not abs:
        # its not absolute, return the relative paths
        rdirs = [os.path.relpath(d, data_dir) for d in rdirs]

    return rdirs


def match_repo_args(spec, all=False, abs=True):
    """Matches repository arguments to an actual list of repositories"""

    if all:
        return match_repos(install_dir, abs=abs)
    elif len(spec) == 0:
        return match_repos(".", abs=abs)
    else:
        return match_repos(spec, abs=abs)

#
# Import / Export of all existing repos to a certain file
#

def export(file = None):
    """Exports the list of currently installed repositories. """

    # Get all locally installed directories
    installed = match_repos(install_dir)

    if(file == None):
        for mod in installed:
            std(mod)
        return True
    try:
        write_file(file, s.linesep.join(things))
        return True
    except:
        err("Unable to write "+fn)
        return False

def restore(file = None):
    """Restores a list of currently installed repositories. """

    # read all lines from the file
    lines = read_file_lines(file)
    lines = [l.strip() for l in lines]
    return install(*lines)

#
# Git actions
#

def push(verbose, *repos):
    """Pushes all currently installed repositories. """

    # Check if we need to update the local repository
    def needs_updating(rep):
        state = get_remote_status(rep)
        return state == "push" or state == "failed" or state == "divergence"

    ret = True

    for rep in repos:
        std("git push", rep, "", newline = False)

        if verbose or needs_updating(rep):
            std()
            ret = git_push(rep) and ret
        else:
            std("OK, nothing to push. ")

    return ret

def pull(verbose, *repos):
    """Pulls all currently installed repositories and updates dependencies"""

    # Check if we need to update the local repository
    def needs_updating(rep):
        state = get_remote_status(rep)
        return state == "pull" or state == "failed" or state == "divergence"

    ret = True

    for rep in repos:
        std("git pull", rep, newline=False)

        if verbose or needs_updating(rep):
            std()
            rgp = git_pull(rep)
            ret = rgp and ret
            rep = match_repo(rep)
            if rgp:
                std("Updated repository", term_colors("green")+rep+term_colors("normal"))
                ret = install(rep) and ret
            else:
                std("Did not update", term_colors("red")+rep+term_colors("normal"), "(merge conflicts or network issues)")
        else:
            rep = match_repo(rep)
            std("")
            std("Nothing to pull for", term_colors("green")+rep+term_colors("normal"))

    return ret

def is_clean(repo):
    """Checks if a working directory is clean. """
    return git_do_data(repo, "status", "--porcelain")[0] == ""

def status(repos, show_unchanged, remote, *args):
    """Does git status on all installed repositories """

    ret = True

    for rep in repos:

        # If we are clean, do nothing
        if is_clean(rep) and not show_unchanged:
            continue

        std("git status", rep)

        if remote:
            r_status = get_remote_status(rep)
            if r_status == "failed":
                std("Remote status:", term_colors("red")+"Unknown (network issues)", term_colors("normal"))
            elif r_status == "ok":
                std("Remote status:", term_colors("green")+"Up-to-date", term_colors("normal"))
            elif r_status == "pull":
                std("Remote status:", term_colors("yellow")+"New commits on remote, please pull. ", term_colors("normal"))
            elif r_status == "push":
                std("Remote status:", term_colors("yellow")+"New local commits, please push. ", term_colors("normal"))
            elif r_status == "divergence":
                std("Remote status:", term_colors("red")+"Remote and local versions have diverged. ", term_colors("normal"))

        val = git_status(rep, *args)
        if not val:
            err("Unable to run git status on", rep)
            ret = False

    return ret

def commit(msg, verbose, *repos):
    """Commits all installed repositories """

    ret = True

    for rep in repos:
        std("git commit", rep, "", newline=False)
        if verbose or git_do_data(rep, "status", "--porcelain")[0] != "":
            std()
            ret = git_commit(rep, "-a", "-m", msg) and ret
        else:
            std("Ok, nothing to commit. ")
    return ret

def do(cmd, args, *repos):
    """Does an arbitraty git commit on all repositories. """
    ret = True
    if args == None:
        args = [""]
    args = args[0].split(" ")
    for rep in repos:
        std("git "+cmd, args[0], rep)
        ret = git_do(rep, cmd, *args) and ret

    return ret

def git_clean(repo):
    """Cleans up repositories. """

    return do("clean", ["-f"], repo)

def rm_untracked(file, t = ""):
    if not is_tracked(file):
        try:
            os.remove(file)
            std("Removed", t, file)
        except:
            err("Unable to remove", file)
            return False
    return True

def clean_orphans(d):
    """Cleans out orphaned files int he given directory"""

    res = True

    (texs, omdocs, pdfs, sms) = find_files(d, "tex", "omdoc", "pdf", "sms")

    #
    # Orphaned omdocs
    #

    for file in omdocs:
        if not (file[:-len(".omdoc")]+".tex" in texs):
            if not rm_untracked(file, "orphaned omdoc"):
                res = False

    #
    # Orphaned pdf
    #

    for file in pdfs:
        if not (file[:-len(".pdf")]+".tex" in texs):
            if not rm_untracked(file, "orphaned pdf"):
                res = False

    #
    # Orphaned sms
    #

    for file in sms:
        if not (file[:-len(".sms")]+".tex" in texs):
            if not rm_untracked(file, "orphaned sms"):
                res = False

    return res

def clean_logs(d):
    """Cleans out logs in the given directory. """

    (ltxlog, pdflog) = find_files(d, "ltxlog", "pdflog")

    for f in ltxlog+pdflog:
        if not rm_untracked(f, "log file"):
            res = False
    res = True

    return res

def clean(repo, git_clean = False):
    res = clean_orphans(repo)
    res = clean_logs(repo) and res

    if git_clean:
        res = git_clean(repo, args) and res
    return res

def log(ordered, *repos):
    """Prints out log messages on all repositories. """
    ret = True

    def get_log(repo):
        get_format = lambda frm:git_do_data(repo, "log", "--pretty=format:"+frm+"")[0].split("\n")

        hash_short = get_format("%h")
        commit_titles = get_format("%s")
        dates = get_format("%at")
        dates_human = get_format("%ad")
        author_names = get_format("%an")
        author_mails = get_format("%ae")

        res = [{
                "hash": hash_short[i],
                "subject": commit_titles[i],
                "date": int(dates[i]),
                "date_human": dates_human[i],
                "author": author_names[i],
                "author_mail": author_mails[i],
                "repo": match_repo(repo)
        } for i in range(len(hash_short))]

        return res

    entries = []

    for rep in repos:
        try:
            entries.extend(get_log(rep))
        except Exception as e:
            err(e)
            ret = False


    if ordered:
        entries.sort(key=lambda e: -e["date"])

    strout = ""

    for entry in entries:
        strout += "\nRepo:    " + entry["repo"]
        strout += "\nSubject: " + entry["subject"]
        strout += "\nHash:    " + entry["hash"]
        strout += "\nAuthor:  " + entry["author"] + " <" + entry["author_mail"] + ">"
        strout += "\nDate:    " + entry["date_human"]
        strout += "\n"

    std_paged(strout, newline=False)

    return ret


def write_deps(dirname, deps):
    """Writes dependencies into a given module. """

    f = os.path.join(data_dir, match_repo(dirname), "META-INF", "MANIFEST.MF")
    n = re.sub(r"dependencies: (.*)", "dependencies: "+",".join(deps), read_file(f))
    write_file(f, n)
    std("Wrote new dependencies to", f)


def calc_deps(apply = False, dirname="."):
    """Crawls for dependencies in a given directory. """

    repo = match_repo(dirname)

    if not repo:
        return False

    std("Checking dependencies for:   ", repo)

    # Getting the real dependencies
    given_dependencies = find_dependencies(match_repo(dirname))+[repo]
    given_dependencies = list(set(given_dependencies))

    # All the required paths
    real_paths = {}

    for root, dirs, files in os.walk(dirname):
        path = root.split('/')
        for file in files:
            fileName, fileExtension = os.path.splitext(file)
            if fileExtension != ".tex":
                continue

            # read the file
            for f in read_file_lines(os.path.join(root, file)):

                for find in re.findall(r"\\(usemhvocab|usemhmodule|adoptmhmodule|importmhmodule)\[(([^\]]*),)?repos=([^,\]]+)(\s*)(,([^\]])*)?\]", f):
                    real_paths[find[3]] = True

                for find in re.findall(r"\\(usemodule|adoptmodule|importmodule|usevocab)\[([^\]]+)\]", f):
                    real_paths[find[1]] = True

                for find in re.findall(r"\\(MathHub){([^\}]+)}", f):
                    real_paths[find[1]] = True

                for find in re.findall(r"\\(gimport|guse|gadpot)\[([^\]]+)\]", f):
                    real_paths[find[1]] = True

    # Now only take paths which have exactly two parts
    real_dependencies = []
    for path in real_paths:
        comps = path.split("/")
        if len(comps) < 2:
            continue
        real_dependencies.append(comps[0]+"/"+comps[1])

    real_dependencies = list(set(real_dependencies))

    # No need to require itself
    while repo in real_dependencies: real_dependencies.remove(repo)
    while repo in given_dependencies: given_dependencies.remove(repo)


    # we are missing the ones that are real but not given
    missing = filter(lambda x:not x in given_dependencies, real_dependencies)

    # we do not need those that are given but not real
    not_needed = filter(lambda x:not x in real_dependencies, given_dependencies)

    # the others are fine
    fine  = filter(lambda x:x in real_dependencies, given_dependencies)

    ret = {
            "fine": fine,
            "missing": missing,
            "not_needed": not_needed,
            "should_be": real_dependencies
    }

    std("---")
    if len(ret["fine"]) > 0:
        std(term_colors("green"),  "Used dependencies:         ", term_colors("normal"), ", ".join(ret["fine"]))
    if len(ret["not_needed"]) > 0:
        std(term_colors("yellow"), "Superfluous dependencies:  ", term_colors("normal"), ", ".join(ret["not_needed"]))
    if len(ret["missing"]) > 0:
        std(term_colors("red"),    "Missing dependencies:      ", term_colors("normal"), ", ".join(ret["missing"]))
    std("---")
    if len(ret["missing"]) > 0 or len(ret["not_needed"]) > 0:
        std("Dependencies should be: ", ", ".join(ret["should_be"]))

    if apply:
        write_deps(dirname, ret["should_be"])

    return ret
