from lmh.lib.io import std, err, term_colors
from lmh.lib.env import data_dir
from lmh.lib.git import clone
from lmh.lib.repos.local.package import get_package_dependencies, is_installed
from lmh.lib.repos.indexer import find_source

def installation_preinstall_hook(rep):
    """
        Hook that runs before installation of a repository.
    """
    return True

def installation_postinstall_hook(rep):
    """
        Hook that runs after installation of a repository.
    """

    return True

def do_deps_install(rep):
    """
        Runs a dependency check.
    """

    # Scan for dependencies.
    std("Looking for dependencies ...")

    deps = []

    try:
        for dep in get_package_dependencies(rep):
            if not is_installed(dep):
                std("   unsatisfied dependency: ", "'"+dep+"'")
            else:
                std("   satisfied dependency:", "'"+dep+"'")
            deps.append(dep)
    except Exception as e:
        std(e)
        err("Failed.")
        return (False, deps)

    std("Done. ")

    return (True, deps)

def do_install(rep):
    """
        Installs a single repository.
    """

    # pre-installation hook.
    std("Running pre-installation hook for '"+rep+"' ...", newline=False)

    if not installation_preinstall_hook(rep):
        err("Failed. ")
        return (r, d)
    std("Done. ")

    # Find the remote.
    std("Finding remote for '"+rep+"' ... ")
    repoURL = find_source(rep)

    # Did we find a url?
    if repoURL == False:
        std("")
        err("   Could not find a remote. ")
        return (False, [])

    std("   OK, will clone from '"+repoURL+"'")

    # Clone the repository.
    if not clone(data_dir, repoURL, rep):
        err("Cloning failed, please make sure you have a network connection. ")
        return (False, [])

    std("   OK. ")

    # post-installation hook.
    std("Running post-installation hook for '"+rep+"' ...", newline=False)

    if not installation_postinstall_hook(rep):
        err("Failed. ")
        return (r, d)
    std("Done. ")

    # Check for dependencies.
    return do_deps_install(rep)

def install(*reps):
    """Install a repositories and its dependencies"""

    reps = [r for r in reps]

    for rep in reps:
        if not is_installed(rep):
            std("Starting installation:         ", term_colors("blue")+"'"+rep+"'"+term_colors("normal"))
            (res, deps) = do_install(rep)

            if not res:
                err("Failed installation:           ", term_colors("red")+"'"+rep+"'"+term_colors("normal"))
            else:
                std("Finished installation:         ", term_colors("green")+"'"+rep+"'"+term_colors("normal"))
                reps.extend([d for d in deps if not d in reps])
        else:
            std(    "Re-scanning for dependencies: ", term_colors("blue")+"'"+rep+"'"+term_colors("normal"))

            (res, deps) = do_deps_install(rep)

            if not res:
                err("Failed scan:                  ", term_colors("red")+"'"+rep+"'"+term_colors("normal"))
            else:
                std("Finished scan:                ", term_colors("green")+"'"+rep+"'"+term_colors("normal"))
                reps.extend([d for d in deps if not d in reps])
