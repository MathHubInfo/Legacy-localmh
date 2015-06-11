from lmh.lib.git import clone
from lmh.lib.io import std
from lmh.lib.repos.remote.indexer import find_source
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

    # Clone the repo
    return clone(data_dir, repoURL, repo)

def install(repos, upgradable):
    pass
