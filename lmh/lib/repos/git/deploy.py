import os.path
import os
from lmh.lib.io import std, write_file
from lmh.lib.repos.local.package import get_metainf_lines
from lmh.lib.repos.local import match_repo
from lmh.lib.git import do, do_data

def get_deploy_branch(rep):
    """
        Gets the deploy branch of a repository (if available).
    """

    # Check if we have the deploy branch cached.
    if rep in get_deploy_branch.cache:
        return get_deploy_branch.cache[rep]


    dbranchstring = "deploy-branch:"

    # Find the deploy branch.
    for l in get_metainf_lines(rep):
        if l.startswith(dbranchstring):
            get_deploy_branch.cache[rep] = l[len(dbranchstring):].strip()
            return get_deploy_branch.cache[rep]

    get_deploy_branch.cache[rep] = False
    return get_deploy_branch.cache[rep]

get_deploy_branch.cache = {}

def installed(rep):
    # Check if the deploy folder exists.
    rpath = match_repo(rep, abs=True)
    dpath = os.path.join(rpath, "deploy")
    return os.path.isdir(dpath)

def install(rep, dbranch):
    rpath = match_repo(rep, abs=True)
    dpath = os.path.join(rpath, "deploy")

    (o, e) = do_data(rpath, "config", "--local", "--get", "remote.origin.url")

    if not do(rpath, "rev-parse", "--verify", "--quiet", dbranch):
        if not do(rpath, "branch", dbranch, "--track", "origin/"+dbranch):
            return False

    # Clone it shared
    if not do(rpath, "clone", rpath, dpath, "--shared", "-b", dbranch):
        return False

    # set up .git/objects/info/alternates relatively
    if not write_file(os.path.join(dpath, ".git/objects/info/alternates"), "../../../.git/objects"):
        return False

    # and set the origin correctly.
    return do(dpath, "remote", "set-url", "origin", o.rstrip("\n"))



def pull(rep, dbranch):
    rpath = match_repo(rep, abs=True)
    dpath = os.path.join(rpath, "deploy")

    # Fetch origin in the clone repo.
    if not do(rpath, "fetch", "--depth", "1", "origin/"+dbranch):
        return False

    # Hard reset this repository.
    if not do(dpath, "reset", "--hard", "origin/"+dbranch):
        return False

    # Run some housekeeping in the parent repo.
    # Removes hard commits.
    return do(rpath, "gc", "--auto")

def push(rep, dbranch):
    rpath = match_repo(rep, abs=True)
    dpath = os.path.join(rpath, "deploy")

    # add all the changes.
    if not do(dpath, "add", "-A", "."):
        return False

    # commit them.
    if not do(dpath, "commit", "--amend", "--no-edit"):
        return False

    # and force push them.
    if not do(dpath, "commit", "--amend", "--no-edit"):
        return False
