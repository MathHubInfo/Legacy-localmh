from lmh.lib.git import clone
from lmh.lib.io import std
from lmh.lib.repos.remote.indexer import find_source, ls_remote
from lmh.lib.env import data_dir

def force_install(repo):
    """
        Installs a repository without checking for dependencies.
    """

    std("Installing", repo)

    # Find the source for the repository
    repoURL = find_source(repo)

    # If we can not find the repo
    # then we just failed.
    if repoURL == False:
        return False

    # Clone the repo and thats it.
    return clone(data_dir, repoURL, repo)

def install(repos, no_confirm = False):
    # Clear up repositories.
    repos = [s.strip() for s in repos]

    # tell the user that we are resolving specififcations.
    std("Resolving packages, this may take a while: \n"+" ".join(repos))

    # and resolve them.
    repos = ls_remote(repos)

    # now build the dep r
