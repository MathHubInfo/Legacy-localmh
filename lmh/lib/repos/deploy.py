import os.path
import os
from lmh.lib.io import std, err, read_file, write_file
from lmh.lib.repos.local.package import get_metainf_lines
from lmh.lib.repos.local import match_repo
from lmh.lib.git import do, do_data, make_orphan_branch
from lmh.lib.config import get_config

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

def print_status(rep):
    """ Prints the status of the deploy branch. """
    std(    "Repository Name: ", rep)
    dbranch = get_deploy_branch(rep)
    if dbranch:
        std("Deploy Branch:   ", "'"+dbranch+"'")
        std("Installed:       ", "Yes" if installed(rep) else "No")
    else:
        std("Deploy Branch:   ", "None")
        std("Installed:       ", "N/A")

    return True

def installed(rep):
    # Check if the deploy folder exists.
    rpath = match_repo(rep, abs=True)
    dpath = os.path.join(rpath, "deploy")
    return os.path.isdir(dpath)

def init(rep):
    """
        Creates a new deploy branch, installs it locally and pushes it to the remote.
    """

    if get_deploy_branch(rep):
        err("A deploy branch already exists, can not create a new one. ")
        return False

    # Get all the info
    dbranch = get_config("gl::deploy_branch_name")
    rpath = match_repo(rep, abs=True)
    dpath = os.path.join(rpath, "deploy")
    meta_inf_path = os.path.join(rpath, "META-INF", "MANIFEST.MF")

    # If we already have a branch with the right name, we abort.
    if do(rpath, "rev-parse", "--verify", "--quiet", dbranch):
        err("A branch named '"+dbranch+"' already exists, exiting. ")
        return False

    # Write the branch name to META-INF/MANIFEST.MF
    mil = get_metainf_lines(rep)
    mil.extend(['deploy-branch: '+dbranch])
    write_file(meta_inf_path, mil)

    # Create the orphaned branch.
    if not make_orphan_branch(rpath, dbranch):
        return False

    # push it
    if not do(rpath, "push", "-u", "origin", dbranch):
        err("Pushing branch to origin failed. ")
        return False

    # Clear the deploy branch cache for this repository.
    get_deploy_branch.cache.pop(rep, None)

    # install it.
    if not install(rep):
        return False

    # change the commit message
    if not do(dpath, "commit", "--amend", "--allow-empty", "-m", "Create deploy branch. "):
        return False

    # and push it.
    if not do(dpath, "push", "--force", "origin", dbranch):
        return False

    std("Deploy branch '"+dbranch+"' created, installed and pushed. ")
    std("Please commit META-INF/MANIFEST.MF and push the change to update others. ")
    std("Move any files to deploy/ and run 'lmh dbranch --push' to commit and push them. ")

    return True


def install(rep):

    if installed(rep):
        std("Deploy branch for '"+rep+"' already installed. ")
        return False

    dbranch = get_deploy_branch(rep)
    if not dbranch:
        err("No deploy branch exists for '"+rep+"', can not install. ")
        return False

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



def pull(rep):
    rpath = match_repo(rep, abs=True)
    dpath = os.path.join(rpath, "deploy")

    if not installed(rep):
        err("Deploy branch for '"+rep+"' not installed, can not pull. ")
        return False

    dbranch = get_deploy_branch(rep)
    if not dbranch:
        err("No deploy branch exists for '"+rep+"', can not pull. ")
        return False

    # Fetch origin in the clone repo.
    if not do(rpath, "fetch", "--depth", "1", "origin", dbranch):
        return False

    # Hard reset this repository.
    if not do(dpath, "reset", "--hard", "origin/"+dbranch):
        return False

    # Run some housekeeping in the parent repo.
    # Removes hard commits.
    return do(rpath, "gc", "--auto")

def push(rep):
    rpath = match_repo(rep, abs=True)
    dpath = os.path.join(rpath, "deploy")

    if not installed(rep):
        err("Deploy branch for '"+rep+"' not installed, can not push. ")
        return False

    dbranch = get_deploy_branch(rep)
    if not dbranch:
        err("No deploy branch exists for '"+rep+"', can not push. ")
        return False

    # add all the changes.
    if not do(dpath, "add", "-A", "."):
        return False

    # commit them.
    if not do(dpath, "commit", "--amend", "--allow-empty", "-m", "Update deploy branch. "):
        return False

    # and force push them.
    if not do(dpath, "push", "--force", "origin", dbranch):
        return False
