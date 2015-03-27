
from lmh.lib.io import std, err
from lmh.lib.env import data_dir
from lmh.lib.git import clone
from lmh.lib.repos.local.package import get_package_dependencies, is_installed
from lmh.lib.config import get_config

from lmh.lib.repos.remote.indexer import find_source

#
# Installing a repository
#

def force_install(rep):
    """Forces installation of a repository"""
    std("Installing", rep)

    # Find the source for the repository
    repoURL = find_source(rep)

    if repoURL == False:
        return False

    # Clone the repo
    return clone(data_dir, repoURL, rep)


def install(no_manifest, *reps):
    """Install a repositories and its dependencies"""

    reps = [r for r in reps]

    if no_manifest == False:
        no_manifest = get_config("install::nomanifest")

    #
    #
    #

    for rep in reps:
        if not is_installed(rep):
            if not force_install(rep):
                err("Unable to install", rep)
                return False
        else:
            std("Already installed:", "'"+rep+"'")

        try:
            std("Resolving dependencies for", rep)
            for dep in get_package_dependencies(rep):
                if not (dep in reps) and not is_installed(dep):
                    std("Found unsatisfied dependency:", "'"+dep+"'")
                    reps.append(dep)
                else:
                    std("Found statisfied dependency:", "'"+dep+"'")
        except:
            if no_manifest:
                err("Error parsing dependencies for", rep)
                err("Set install::nomanifest to True to disable this. ")
                return False
