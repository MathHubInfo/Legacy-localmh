import os
import os.path
import re
import glob

from lmh.lib.env import install_dir, data_dir
from lmh.lib.io import term_colors, find_files, std, std_paged, err, write_file, read_file, read_file_lines
from lmh.lib.repos.remote import install


# Git imports
from lmh.lib.git import push as git_push
from lmh.lib.git import pull as git_pull
from lmh.lib.git import status as git_status
from lmh.lib.git import commit as git_commit
from lmh.lib.git import git_do
from lmh.lib.git import git_do_data
from lmh.lib.git import get_remote_status
from lmh.lib.git import is_tracked, is_repo

from lmh.lib.repos.local.dirs import is_in_data, is_repo_dir, is_in_repo, find_repo_subdirs, match_repo, match_repos, find_repo_dir

from lmh.lib.repos.local.package import get_package_dependencies


def match_repo_args(spec, all=False, abs=True):
    """Matches repository arguments to an actual list of repositories"""

    if all:
        return match_repos(data_dir, abs=abs)
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
        write_file(file, os.linesep.join(installed))
        return True
    except:
        err("Unable to write "+file)
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
        res = git_clean(repo) and res
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
    given_dependencies = get_package_dependencies(match_repo(dirname))+[repo]
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
